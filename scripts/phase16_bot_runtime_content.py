"""Read-only, bounded Python 3.12 import-path content verification.

Trust enters ONLY through externally authenticated WheelPin descriptors. Callers
must not construct pins from mutable installed METADATA/RECORD. No wheel code is
imported, installed or executed. Verified source may be compiled (never executed)
to compare generated pyc bytes; untrusted marshal data is never deserialized.

The injected reader must securely bind its root and ancestors, reject symlinks/
reparse points and concurrent replacement, and implement BoundTree's info,
entries, read_file and stable methods. This module performs its own bounded walk;
BoundTree.file_set's source-tree cap is too small for installed dependencies.

PASS_SITE_CONTENT_ONLY covers site-packages bytes. It does not prove interpreter,
stdlib, OS, other sys.path entries, permissions, or console wrapper bytes. Bootstrap
pip requires a separately authenticated wheel pin. No CLI or implicit execution.
"""
from __future__ import annotations

import base64
import configparser
import csv
from dataclasses import dataclass
from email.parser import BytesParser
import hashlib
import importlib.util
import io
import itertools
import marshal
from pathlib import PurePosixPath
import re
import stat
import struct
import sys
import time
from types import MappingProxyType
from typing import Mapping, Protocol, Sequence
import zipfile

SITE_PREFIX = 'runtime-venv/lib/python3.12/site-packages'
INSTALLED_SITE_PATH = '/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001/' + SITE_PREFIX
OUT_OF_SCOPE = ('interpreter_stdlib_os', 'console_wrapper_content', 'other_import_paths', 'access_permissions')


class ContentError(ValueError):
    """A fixed, non-sensitive admission reason (no path or raw exception text)."""


def _require(condition, reason):
    if not condition:
        raise ContentError(reason)


@dataclass(frozen=True)
class Limits:
    max_wheels: int = 64
    max_wheel_bytes: int = 32 * 1024 * 1024
    max_total_wheel_bytes: int = 64 * 1024 * 1024
    max_file_bytes: int = 64 * 1024 * 1024
    max_uncompressed_bytes: int = 256 * 1024 * 1024
    max_members: int = 20000
    max_compression_ratio: int = 300
    max_installed_nodes: int = 40000
    max_installed_bytes: int = 384 * 1024 * 1024
    max_directory_entries: int = 1024
    max_metadata_bytes: int = 4 * 1024 * 1024
    max_seconds: int = 60


@dataclass(frozen=True)
class WheelPin:
    file: str
    size: int
    sha256: str
    name: str
    version: str
    role: str = 'runtime'


@dataclass(frozen=True)
class Distribution:
    name: str
    version: str
    role: str
    dist_info: str
    files: frozenset[str]
    entrypoints: frozenset[str]


@dataclass(frozen=True)
class ExpectedRuntime:
    files: Mapping[str, bytes]
    distributions: tuple[Distribution, ...]
    limits: Limits


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str
    runtime_status: str = 'NOT_PROVEN'
    bootstrap_status: str = 'NOT_PROVEN'
    scope: str = 'IMPORT_PATH_CONTENT'
    verified_files: int = 0
    verified_bytecode: int = 0
    excluded_entrypoints: tuple[str, ...] = ()
    out_of_scope: tuple[str, ...] = OUT_OF_SCOPE


class Reader(Protocol):
    def info(self, name): ...
    def entries(self, name): ...
    def read_file(self, name, maximum, expected_size=None): ...
    def stable(self): ...


def _name(value):
    _require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', value), 'wheel_metadata')
    return re.sub(r'[-_.]+', '-', value).lower()


def _path(value):
    _require(isinstance(value, str) and 0 < len(value) <= 512 and not any(ord(c) < 32 or ord(c) == 127 for c in value)
             and '\\' not in value and ':' not in value, 'unsafe_path')
    parts = value.split('/')
    _require(len(parts) <= 32 and all(p not in ('', '.', '..') and len(p) <= 255
                                    and p == p.rstrip(' .') for p in parts), 'unsafe_path')
    return value


def _clock(deadline):
    _require(time.monotonic() < deadline, 'content_timeout')


def _fingerprint(data):
    return 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode('ascii')


def _record(data, files, record_path, reason, *, bytecode=frozenset(), entrypoints=frozenset()):
    """Validate RECORD against independently trusted/already verified bytes."""
    try:
        rows = csv.reader(io.StringIO(data.decode('utf-8'), newline=''), strict=True)
        seen = set()
        external = set()
        for row in rows:
            _require(len(row) == 3, reason)
            name, hash_value, size = row
            _require(name not in seen, reason)
            seen.add(name)
            if name.startswith('../../../bin/'):
                _require(name in entrypoints, 'entrypoint_not_proven')
                _require(re.fullmatch(r'sha256=[A-Za-z0-9_-]{43}', hash_value)
                         and re.fullmatch(r'0|[1-9][0-9]{0,9}', size), reason)
                external.add(name)
                continue
            _path(name)
            _require(name in files, reason)
            if name == record_path or (name in bytecode and hash_value == size == ''):
                _require(hash_value == size == '', reason)
            else:
                value = files[name]
                _require(hash_value == _fingerprint(value) and size == str(len(value)), reason)
        _require(seen - external == set(files), reason)
        return external
    except ContentError as error:
        if str(error) in ('unsafe_path', 'entrypoint_not_proven'):
            raise ContentError('entrypoint_not_proven' if str(error) == 'entrypoint_not_proven' else reason) from None
        raise
    except (UnicodeError, csv.Error, ValueError, OverflowError):
        raise ContentError(reason) from None


def _headers(data, limit):
    _require(len(data) <= limit, 'wheel_metadata')
    result = BytesParser().parsebytes(data, headersonly=True)
    _require(not result.defects, 'wheel_metadata')
    return result


def _one(message, key):
    values = message.get_all(key, [])
    _require(len(values) == 1 and isinstance(values[0], str), 'wheel_metadata')
    return values[0]


def _metadata(files, pin, limits):
    fields = pin.file[:-4].split('-')
    _require(pin.file.endswith('.whl') and len(fields) in (5, 6), 'wheel_metadata')
    _require(_name(fields[0]) == _name(pin.name) and fields[1] == pin.version, 'wheel_metadata')
    stem = fields[0] + '-' + fields[1]
    dist = stem + '.dist-info'
    roots = {name.split('/')[0] for name in files if name.split('/')[0].endswith('.dist-info')}
    _require(roots == {dist}, 'wheel_metadata')
    _require(all(dist + '/' + name in files for name in ('METADATA', 'WHEEL', 'RECORD')), 'wheel_metadata')
    message = _headers(files[dist + '/METADATA'], limits.max_metadata_bytes)
    _require(_name(_one(message, 'Name')) == _name(pin.name) and _one(message, 'Version') == pin.version, 'wheel_metadata')
    wheel = _headers(files[dist + '/WHEEL'], limits.max_metadata_bytes)
    _require(_one(wheel, 'Wheel-Version') == '1.0' and _one(wheel, 'Root-Is-Purelib') in ('true', 'false'), 'wheel_metadata')
    tags = wheel.get_all('Tag', [])
    expected_tags = {'-'.join(parts) for parts in itertools.product(*(part.split('.') for part in fields[-3:]))}
    _require(tags and len(tags) == len(set(tags)) and set(tags) == expected_tags
             and all(re.fullmatch(r'[A-Za-z0-9_]+-[A-Za-z0-9_]+-[A-Za-z0-9_]+', tag) for tag in tags), 'wheel_metadata')
    if len(fields) == 6:
        _require(_one(wheel, 'Build') == fields[2] and re.fullmatch(r'[0-9][A-Za-z0-9_]*', fields[2]), 'wheel_metadata')
    else:
        _require(not wheel.get_all('Build'), 'wheel_metadata')
    _require(len(files[dist + '/RECORD']) <= limits.max_metadata_bytes, 'wheel_limit')
    _record(files[dist + '/RECORD'], files, dist + '/RECORD', 'wheel_record')
    entries = set()
    if dist + '/entry_points.txt' in files:
        data = files[dist + '/entry_points.txt']
        _require(len(data) <= limits.max_metadata_bytes, 'wheel_metadata')
        try:
            parser = configparser.ConfigParser(interpolation=None, strict=True)
            parser.optionxform = str
            parser.read_string(data.decode('utf-8'))
            _require(not parser.defaults(), 'wheel_metadata')
            for group in ('console_scripts', 'gui_scripts'):
                if parser.has_section(group):
                    for key, value in parser.items(group):
                        _require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', key)
                                 and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*:[A-Za-z_][A-Za-z0-9_.]*(?:\s*\[[A-Za-z0-9_., -]+\])?', value), 'wheel_metadata')
                        entries.add('../../../bin/' + key)
                        # pip rewrites its versioned console names for this Python
                        # minor. These rows remain EXCLUDED wrapper content.
                        if (pin.role == 'bootstrap' and _name(pin.name) == 'pip'
                                and group == 'console_scripts' and key == 'pip'
                                and value == 'pip._internal.cli.main:main'):
                            entries.update({'../../../bin/pip3', '../../../bin/pip3.12'})
        except (UnicodeError, configparser.Error):
            raise ContentError('wheel_metadata') from None
    return stem, dist, frozenset(entries)


def _archive(data, limits, counters, deadline):
    files = {}
    seen = set()
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            counters[0] += len(infos)
            _require(counters[0] <= limits.max_members, 'wheel_limit')
            for info in infos:
                _clock(deadline)
                raw = info.orig_filename
                name = _path(raw[:-1] if raw.endswith('/') else raw)
                _require(raw == info.filename, 'unsafe_path')
                _require(name.casefold() not in seen, 'wheel_duplicate')
                seen.add(name.casefold())
                _require(not info.flag_bits & 0x41, 'wheel_encrypted')
                mode = stat.S_IFMT(info.external_attr >> 16)
                allowed_modes = (0, stat.S_IFDIR) if info.is_dir() else (0, stat.S_IFREG)
                _require(mode in allowed_modes, 'wheel_type')
                _require(info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), 'wheel_type')
                _require(0 <= info.file_size <= limits.max_file_bytes and info.compress_size >= 0
                         and info.file_size <= max(1, info.compress_size) * limits.max_compression_ratio, 'wheel_limit')
                counters[1] += info.file_size
                _require(counters[1] <= limits.max_uncompressed_bytes, 'wheel_limit')
                if info.is_dir():
                    _require(info.file_size == 0, 'wheel_type')
                    continue
                with archive.open(info) as stream:
                    value = stream.read(info.file_size + 1)
                _require(len(value) == info.file_size, 'wheel_archive')
                files[name] = value
    except ContentError:
        raise
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError, ValueError, EOFError):
        raise ContentError('wheel_archive') from None
    return files


def _conflicts(paths):
    files = set()
    directories = set()
    for path in paths:
        lower = path.casefold()
        parents = {str(p).casefold() for p in PurePosixPath(path).parents if str(p) != '.'}
        _require(lower not in files and lower not in directories and not parents & files, 'destination_conflict')
        files.add(lower)
        directories.update(parents)


def build_expected(wheels: Mapping[str, bytes], pins: Sequence[WheelPin], *, limits=Limits()) -> ExpectedRuntime:
    """Bind wheel bytes to trusted descriptors and derive exact site destinations.

    purelib/platlib .data relocation is supported within the same site root.
    Scripts/headers/data relocation and archive startup hooks are rejected.
    """
    _require(all(type(value) is int and value > 0 for value in vars(limits).values()), 'wheel_limit')
    _require(0 < len(pins) <= limits.max_wheels and len(wheels) == len(pins), 'wheel_inventory')
    _require(len({pin.file for pin in pins}) == len(pins) and set(wheels) == {pin.file for pin in pins}, 'wheel_inventory')
    names = set()
    total = 0
    deadline = time.monotonic() + limits.max_seconds
    counters = [0, 0]
    result = {}
    distributions = []
    for pin in pins:
        _clock(deadline)
        _path(pin.file)
        _require('/' not in pin.file and pin.role in ('runtime', 'bootstrap'), 'wheel_metadata')
        name = _name(pin.name)
        _require(name not in names and (pin.role != 'bootstrap' or name in ('pip', 'setuptools', 'wheel'))
                 and (pin.role != 'runtime' or name not in ('pip', 'setuptools', 'wheel')), 'wheel_inventory')
        names.add(name)
        data = wheels[pin.file]
        _require(isinstance(data, bytes) and type(pin.size) is int and 0 < pin.size <= limits.max_wheel_bytes, 'wheel_binding')
        total += len(data)
        _require(total <= limits.max_total_wheel_bytes, 'wheel_limit')
        _require(len(data) == pin.size and re.fullmatch(r'[a-f0-9]{64}', pin.sha256)
                 and hashlib.sha256(data).hexdigest() == pin.sha256, 'wheel_binding')
        files = _archive(data, limits, counters, deadline)
        _conflicts(files)
        stem, dist, entries = _metadata(files, pin, limits)
        mapped = set()
        for source, value in files.items():
            parts = source.split('/')
            destination = source
            if parts[0].endswith('.data'):
                _require(parts[0] == stem + '.data' and len(parts) >= 3
                         and parts[1] in ('purelib', 'platlib'), 'wheel_relocation')
                destination = '/'.join(parts[2:])
                _require(not any(p.endswith(('.dist-info', '.data')) for p in parts[2:]), 'wheel_relocation')
            _path(destination)
            _require(destination not in result, 'destination_conflict')
            _require(not destination.endswith(('.pyc', '.pyo')), 'bytecode_not_proven')
            _require(not _startup_hook(destination), 'startup_hook')
            result[destination] = value
            mapped.add(destination)
        distributions.append(Distribution(name, pin.version, pin.role, dist, frozenset(mapped), entries))
    _conflicts(result)
    _require(any(d.role == 'runtime' for d in distributions), 'wheel_inventory')
    return ExpectedRuntime(MappingProxyType(result), tuple(distributions), limits)


def _startup_hook(path):
    first = path.split('/')[0].lower()
    return first.endswith('.pth') or first in ('sitecustomize.py', 'sitecustomize.pyc', 'sitecustomize',
                                             'usercustomize.py', 'usercustomize.pyc', 'usercustomize')


def _walk(reader, prefix, limits, deadline):
    found = {}
    directories = set()
    count = 0
    total = 0
    def visit(path):
        nonlocal count, total
        _clock(deadline)
        _path(path)
        count += 1
        _require(count <= limits.max_installed_nodes, 'installed_limit')
        meta = reader.info(path)
        _require(not getattr(meta, 'st_file_attributes', 0) & 0x400, 'installed_type')
        if stat.S_ISDIR(meta.st_mode):
            if path != prefix:
                directories.add(path[len(prefix) + 1:])
            children = reader.entries(path)
            _require(len(children) <= limits.max_directory_entries and len(children) == len(set(children)), 'installed_limit')
            for child in sorted(children):
                _path(child)
                _require('/' not in child, 'unsafe_path')
                visit(path + '/' + child)
        else:
            _require(stat.S_ISREG(meta.st_mode) and meta.st_nlink == 1, 'installed_type')
            total += meta.st_size
            _require(0 <= meta.st_size <= limits.max_file_bytes and total <= limits.max_installed_bytes, 'installed_limit')
            found[path[len(prefix) + 1:]] = meta
    visit(prefix)
    return found, directories


def _bytecode_source(path, files):
    match = re.fullmatch(r'(.*/)?__pycache__/([^/]+)\.cpython-312(?:\.opt-([12]))?\.pyc', path)
    _require(match is not None, 'bytecode_not_proven')
    source = (match[1] or '') + match[2] + '.py'
    _require(source in files, 'bytecode_not_proven')
    return source, int(match[3] or '0')


def _bytecode(data, source, filename, meta, optimize):
    _require(sys.version_info[:2] == (3, 12), 'bytecode_python_version')
    _require(len(data) >= 16 and data[:4] == importlib.util.MAGIC_NUMBER, 'bytecode_content')
    flags = struct.unpack('<I', data[4:8])[0]
    _require(flags in (0, 1, 3), 'bytecode_content')
    header = (importlib.util.source_hash(source) if flags & 1 else
              struct.pack('<II', int(meta.st_mtime) & 0xffffffff, len(source)))
    _require(data[8:16] == header, 'bytecode_content')
    try:
        code = compile(source, filename, 'exec', dont_inherit=True, optimize=optimize)
        _require(data[16:] == marshal.dumps(code), 'bytecode_content')
    except (SyntaxError, ValueError, OverflowError, RecursionError):
        raise ContentError('bytecode_content') from None


def verify_installed(expected: ExpectedRuntime, reader: Reader, *, site_prefix=SITE_PREFIX,
                     installed_site_path=INSTALLED_SITE_PATH) -> VerificationResult:
    """Verify the complete site tree, including narrow installer-generated files.

    Optional INSTALLER must equal b'pip\\n'; REQUESTED must be empty. Generated
    RECORD must describe exactly each wheel's mapped files and verified caches.
    A trusted entry_points name may appear as ../../../bin/name in RECORD, but
    wrapper bytes are deliberately excluded and never authorize execute access.
    """
    checked = 0
    caches = 0
    excluded = set()
    try:
        _path(site_prefix)
        _require(isinstance(installed_site_path, str) and installed_site_path.startswith('/'), 'unsafe_path')
        _path(installed_site_path[1:])
        limits = expected.limits
        deadline = time.monotonic() + limits.max_seconds
        found, directories = _walk(reader, site_prefix, limits, deadline)
        allowed_directories = {str(parent) for name in expected.files for parent in PurePosixPath(name).parents if str(parent) != '.'}
        allowed_directories.update(str(PurePosixPath(name).parent / '__pycache__') for name in expected.files if name.endswith('.py'))
        _require(not any(_startup_hook(name) for name in directories), 'startup_hook')
        _require(directories <= allowed_directories, 'installed_extra')
        _require(set(expected.files) <= set(found), 'installed_missing')
        _conflicts(found)
        actual = {}
        generated = {d.dist_info + '/' + name for d in expected.distributions for name in ('INSTALLER', 'REQUESTED')}
        cache_sources = {}
        records = {d.dist_info + '/RECORD' for d in expected.distributions}
        for name in found:
            _clock(deadline)
            _require(not _startup_hook(name), 'startup_hook')
            if name.endswith(('.pyc', '.pyo')):
                cache_sources[name] = _bytecode_source(name, expected.files)
            else:
                _require(name in expected.files or name in generated, 'installed_extra')
        for name, meta in found.items():
            _clock(deadline)
            maximum = limits.max_metadata_bytes if name in records else limits.max_file_bytes
            _require(meta.st_size <= maximum, 'installed_limit')
            data = reader.read_file(site_prefix + '/' + name, maximum, expected_size=meta.st_size)
            _require(isinstance(data, bytes) and len(data) == meta.st_size, 'installed_read')
            actual[name] = data
            if name in cache_sources or name in records:
                continue
            if name in generated and name not in expected.files:
                _require(data == (b'pip\n' if name.endswith('/INSTALLER') else b''), 'generated_content')
            else:
                _require(data == expected.files[name], 'installed_content')
            checked += 1
        for name, (source, optimize) in cache_sources.items():
            _clock(deadline)
            _bytecode(actual[name], expected.files[source], installed_site_path + '/' + source, found[source], optimize)
            checked += 1
            caches += 1
        for distribution in expected.distributions:
            _clock(deadline)
            record = distribution.dist_info + '/RECORD'
            owned = set(distribution.files) | {name for name in generated if name in actual and name.startswith(distribution.dist_info + '/')}
            owned_caches = {name for name, (source, _) in cache_sources.items() if source in distribution.files}
            owned |= owned_caches
            excluded.update(_record(actual[record], {name: actual[name] for name in owned}, record, 'installed_record',
                                    bytecode=owned_caches, entrypoints=distribution.entrypoints))
            checked += 1
        reader.stable()
        _clock(deadline)
        bootstrap = any(d.role == 'bootstrap' and d.name == 'pip' for d in expected.distributions)
        return VerificationResult('PASS_SITE_CONTENT_ONLY' if bootstrap else 'NOT_PROVEN',
                                  'verified' if bootstrap else 'bootstrap_not_proven', 'PASS',
                                  'PASS' if bootstrap else 'NOT_PROVEN', verified_files=checked,
                                  verified_bytecode=caches, excluded_entrypoints=tuple(sorted(excluded)))
    except ContentError as error:
        return VerificationResult('STOP', str(error), verified_files=checked, verified_bytecode=caches)
    except Exception:
        return VerificationResult('STOP', 'installed_read', verified_files=checked, verified_bytecode=caches)
