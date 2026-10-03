"""Real zip/file controls for the read-only runtime-content admission library."""
from __future__ import annotations

import base64
import csv
from dataclasses import replace
import hashlib
import importlib
import io
import os
from pathlib import Path
import stat
import struct
import tempfile
import unittest
import warnings
import zipfile

try:
    content = importlib.import_module('scripts.phase16_bot_runtime_content')
except ModuleNotFoundError as error:
    if error.name != 'scripts.phase16_bot_runtime_content':
        raise
    content = None


SITE = 'runtime-venv/lib/python3.12/site-packages'
DIST = 'demo_pkg-1.0.dist-info'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record_bytes(files, record):
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    for name, data in sorted(files.items()):
        if name != record:
            value = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()
            writer.writerow([name, 'sha256=' + value, str(len(data))])
    writer.writerow([record, '', ''])
    return output.getvalue().encode()


def wheel_files(name='demo_pkg', version='1.0', extras=None):
    dist = f'{name}-{version}.dist-info'
    files = {
        name + '/__init__.py': b'VALUE = 7\n',
        dist + '/METADATA': f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n\n'.encode(),
        dist + '/WHEEL': b'Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n',
    }
    files.update(extras or {})
    files[dist + '/RECORD'] = record_bytes(files, dist + '/RECORD')
    return files


def zipped(files, extra_members=()):
    output = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in list(files.items()) + list(extra_members):
                archive.writestr(name, data)
    return output.getvalue()


class DiskReader:
    """Portable test reader; admission still checks types and every file's bytes."""
    def __init__(self, root):
        self.root = root
        self.seen = {}

    def info(self, name):
        meta = self.root.joinpath(*name.split('/')).lstat()
        self.seen.setdefault(name, (meta.st_size, meta.st_mtime_ns, meta.st_ino))
        return meta

    def entries(self, name):
        return [entry.name for entry in self.root.joinpath(*name.split('/')).iterdir()]

    def read_file(self, name, maximum, expected_size=None):
        path = self.root.joinpath(*name.split('/'))
        meta = path.lstat()
        if not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1:
            raise ValueError('unsafe test read')
        with path.open('rb') as stream:
            data = stream.read(maximum + 1)
        if len(data) > maximum or (expected_size is not None and len(data) != expected_size):
            raise ValueError('bounded test read')
        return data

    def stable(self):
        for name, before in self.seen.items():
            meta = self.root.joinpath(*name.split('/')).lstat()
            if before != (meta.st_size, meta.st_mtime_ns, meta.st_ino):
                raise ValueError('changed')


class RuntimeContentTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(content, 'runtime-content admission library is missing')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = wheel_files()
        self.data = zipped(self.files)
        self.pin = self.pin_for(self.data)

    def pin_for(self, data, name='demo-pkg', version='1.0', file='demo_pkg-1.0-py3-none-any.whl', role='runtime'):
        return content.WheelPin(file=file, size=len(data), sha256=digest(data), name=name, version=version, role=role)

    def build(self, data=None, **kwargs):
        data = self.data if data is None else data
        pin = self.pin_for(data)
        # The zip is persisted and read back, never installed or imported.
        path = self.root / pin.file
        path.write_bytes(data)
        return content.build_expected({pin.file: path.read_bytes()}, [pin], **kwargs)

    def install(self, files=None):
        files = dict(self.files if files is None else files)
        files[DIST + '/INSTALLER'] = b'pip\n'
        files[DIST + '/REQUESTED'] = b''
        files[DIST + '/RECORD'] = record_bytes(files, DIST + '/RECORD')
        for name, data in files.items():
            path = self.root / SITE / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return files

    def verify(self, expected=None, reader=None):
        return content.verify_installed(expected or self.build(), reader or DiskReader(self.root))

    def test_exact_wheel_bytes_prove_runtime_but_not_unbound_bootstrap(self):
        self.install()
        result = self.verify()
        self.assertEqual(result.runtime_status, 'PASS')
        self.assertEqual(result.bootstrap_status, 'NOT_PROVEN')
        self.assertEqual(result.status, 'NOT_PROVEN')
        self.assertIn('interpreter_stdlib_os', result.out_of_scope)

    def test_separately_pinned_pip_proves_bootstrap_site_content(self):
        pip_files = wheel_files('pip', '24.0')
        pip_data = zipped(pip_files)
        pip_pin = self.pin_for(pip_data, 'pip', '24.0', 'pip-24.0-py3-none-any.whl', 'bootstrap')
        expected = content.build_expected({self.pin.file: self.data, pip_pin.file: pip_data}, [self.pin, pip_pin])
        self.install()
        for name, data in pip_files.items():
            path = self.root / SITE / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        result = self.verify(expected)
        self.assertEqual(result.status, 'PASS_SITE_CONTENT_ONLY')
        self.assertEqual(result.bootstrap_status, 'PASS')

    def test_rehashed_local_record_cannot_hide_tampered_module(self):
        altered = dict(self.files)
        altered['demo_pkg/__init__.py'] = b'VALUE = 9\n'
        self.install(altered)
        result = self.verify()
        self.assertEqual(result.status, 'STOP')
        self.assertEqual(result.reason, 'installed_content')

    def test_extra_importable_file_even_with_rehashed_record_stops(self):
        altered = dict(self.files, **{'demo_pkg/evil.py': b'raise RuntimeError()\n'})
        self.install(altered)
        self.assertEqual(self.verify().reason, 'installed_extra')

    def test_changed_installed_record_is_checked_but_never_used_as_trust(self):
        self.install()
        (self.root / SITE / DIST / 'RECORD').write_bytes(b'wrong.py,sha256=x,3\n')
        self.assertEqual(self.verify().reason, 'installed_record')

    def test_record_duplicate_or_self_hash_stops(self):
        for value in (self.files[DIST + '/RECORD'] * 2, b'demo_pkg-1.0.dist-info/RECORD,sha256=x,1\n'):
            with self.subTest(value=value):
                self.install()
                (self.root / SITE / DIST / 'RECORD').write_bytes(value)
                self.assertEqual(self.verify().reason, 'installed_record')

    def test_installer_and_requested_are_exact_noncode_generated_files(self):
        for name, data in [('INSTALLER', b'evil\n'), ('REQUESTED', b'x')]:
            with self.subTest(name=name):
                self.install()
                (self.root / SITE / DIST / name).write_bytes(data)
                self.assertEqual(self.verify().reason, 'generated_content')

    def test_malformed_generated_bytecode_is_rejected(self):
        self.install()
        path = self.root / SITE / 'demo_pkg/__pycache__/__init__.cpython-312.pyc'
        path.parent.mkdir()
        path.write_bytes(b'fake-pyc')
        self.assertEqual(self.verify().reason, 'bytecode_content')

    def test_unbound_pip_is_not_blindly_skipped(self):
        self.install()
        path = self.root / SITE / 'pip/__init__.py'
        path.parent.mkdir()
        path.write_bytes(b'print(42)\n')
        result = self.verify()
        self.assertEqual(result.status, 'STOP')
        self.assertEqual(result.bootstrap_status, 'NOT_PROVEN')

    def test_pth_and_startup_customization_stop(self):
        for name in ('evil.pth', 'sitecustomize.py', 'usercustomize.py'):
            with self.subTest(name=name):
                path = self.root / SITE / name
                self.install()
                path.write_bytes(b'import os\n')
                self.assertEqual(self.verify().reason, 'startup_hook')
                path.unlink()

    def test_generated_external_entrypoint_record_is_explicit_stop(self):
        self.install()
        path = self.root / SITE / DIST / 'RECORD'
        path.write_bytes(path.read_bytes() + b'../../../bin/demo,sha256=unknown,8\n')
        self.assertEqual(self.verify().reason, 'entrypoint_not_proven')

    def test_missing_expected_file_stops(self):
        self.install()
        (self.root / SITE / 'demo_pkg/__init__.py').unlink()
        self.assertEqual(self.verify().reason, 'installed_missing')

    def test_wheel_hash_and_size_bind_bytes_before_zip_parsing(self):
        for pin in (replace(self.pin, sha256='0' * 64), replace(self.pin, size=self.pin.size + 1)):
            with self.subTest(pin=pin):
                with self.assertRaisesRegex(content.ContentError, 'wheel_binding'):
                    content.build_expected({pin.file: self.data}, [pin])

    def test_unpinned_or_missing_wheels_stop(self):
        for wheels in ({}, {self.pin.file: self.data, 'extra.whl': self.data}):
            with self.subTest(wheels=list(wheels)):
                with self.assertRaisesRegex(content.ContentError, 'wheel_inventory'):
                    content.build_expected(wheels, [self.pin])

    def test_duplicate_zip_member_stops(self):
        with self.assertRaisesRegex(content.ContentError, 'wheel_duplicate'):
            self.build(zipped(self.files, [('demo_pkg/__init__.py', b'other')]))

    def test_path_traversal_absolute_backslash_and_null_paths_stop(self):
        for name in ('../evil.py', '/evil.py', 'a/../../evil.py', 'a\\evil.py', 'a//evil.py', 'C:/evil.py'):
            with self.subTest(name=name):
                with self.assertRaisesRegex(content.ContentError, 'unsafe_path'):
                    raw = zipped(dict(self.files, **{name.replace(chr(92), '/'): b'x'}))
                    if chr(92) in name:
                        raw = raw.replace(name.replace(chr(92), '/').encode(), name.encode())
                    self.build(raw)

    def test_zip_symlink_and_special_members_stop(self):
        for mode in (stat.S_IFLNK | 0o777, stat.S_IFIFO | 0o600, stat.S_IFCHR | 0o600):
            with self.subTest(mode=mode):
                info = zipfile.ZipInfo('demo_pkg/unsafe')
                info.create_system = 3
                info.external_attr = mode << 16
                with self.assertRaisesRegex(content.ContentError, 'wheel_type'):
                    self.build(zipped(self.files, [(info, b'target')]))

    def test_zip_encryption_flag_stops(self):
        data = bytearray(self.data)
        offset = data.index(b'PK\x01\x02')
        flags = struct.unpack_from('<H', data, offset + 8)[0]
        struct.pack_into('<H', data, offset + 8, flags | 1)
        with self.assertRaisesRegex(content.ContentError, 'wheel_encrypted'):
            self.build(bytes(data))

    def test_expansion_size_member_count_and_ratio_are_bounded(self):
        limits = content.Limits()
        for changed in (replace(limits, max_file_bytes=5), replace(limits, max_members=2),
                        replace(limits, max_uncompressed_bytes=20), replace(limits, max_compression_ratio=1)):
            with self.subTest(changed=changed):
                with self.assertRaisesRegex(content.ContentError, 'wheel_limit'):
                    self.build(limits=changed)

    def test_invalid_zip_bytes_have_safe_error(self):
        with self.assertRaisesRegex(content.ContentError, 'wheel_archive'):
            self.build(b'not-a-zip')

    def test_metadata_name_version_and_duplicates_are_bound(self):
        for data in (b'Name: wrong\nVersion: 1.0\n\n', b'Name: demo-pkg\nVersion: 2.0\n\n',
                     b'Name: demo-pkg\nName: demo-pkg\nVersion: 1.0\n\n'):
            with self.subTest(data=data):
                files = dict(self.files)
                files[DIST + '/METADATA'] = data
                with self.assertRaisesRegex(content.ContentError, 'wheel_metadata'):
                    self.build(zipped(files))

    def test_wheel_version_purelib_and_tag_are_validated(self):
        for data in (b'Wheel-Version: 2.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n',
                     b'Wheel-Version: 1.0\nRoot-Is-Purelib: maybe\nTag: py3-none-any\n\n',
                     b'Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: cp311-cp311-linux_x86_64\n\n'):
            with self.subTest(data=data):
                files = dict(self.files)
                files[DIST + '/WHEEL'] = data
                with self.assertRaisesRegex(content.ContentError, 'wheel_metadata'):
                    self.build(zipped(files))

    def test_wheel_record_must_match_trusted_archive_inventory(self):
        files = dict(self.files)
        files[DIST + '/RECORD'] = b'demo_pkg/__init__.py,sha256=bad,10\n'
        with self.assertRaisesRegex(content.ContentError, 'wheel_record'):
            self.build(zipped(files))

    def test_purelib_and_platlib_data_map_to_site_paths(self):
        files = wheel_files(extras={'demo_pkg-1.0.data/purelib/extra.py': b'X = 1\n',
                                  'demo_pkg-1.0.data/platlib/native.so': b'ELF fixture'})
        expected = self.build(zipped(files))
        installed = {name: data for name, data in files.items() if '.data/' not in name}
        installed['extra.py'] = b'X = 1\n'
        installed['native.so'] = b'ELF fixture'
        self.install(installed)
        self.assertEqual(self.verify(expected).runtime_status, 'PASS')

    def test_unsupported_data_relocation_stops(self):
        for category in ('scripts', 'headers', 'data', 'unknown'):
            with self.subTest(category=category):
                files = wheel_files(extras={f'demo_pkg-1.0.data/{category}/x': b'1'})
                with self.assertRaisesRegex(content.ContentError, 'wheel_relocation'):
                    self.build(zipped(files))

    def test_conflicting_relocated_destination_stops_even_equal_bytes(self):
        files = wheel_files(extras={'demo_pkg-1.0.data/purelib/demo_pkg/__init__.py': b'VALUE = 7\n'})
        with self.assertRaisesRegex(content.ContentError, 'destination_conflict'):
            self.build(zipped(files))

    def test_cross_wheel_destination_collision_stops(self):
        files = wheel_files('other', extras={'demo_pkg/__init__.py': b'VALUE = 7\n'})
        data = zipped(files)
        pin = self.pin_for(data, 'other', file='other-1.0-py3-none-any.whl')
        with self.assertRaisesRegex(content.ContentError, 'destination_conflict'):
            content.build_expected({self.pin.file: self.data, pin.file: data}, [self.pin, pin])

    def test_directory_file_collision_and_case_alias_stop(self):
        for extra in ({'demo_pkg': b'x'}, {'demo_pkg/INIT.py': b'x', 'demo_pkg/init.py': b'y'}):
            with self.subTest(extra=extra):
                with self.assertRaisesRegex(content.ContentError, 'destination_conflict|wheel_duplicate'):
                    self.build(zipped(wheel_files(extras=extra)))

    def test_installed_hardlink_stops(self):
        self.install()
        source = self.root / SITE / 'demo_pkg/__init__.py'
        os.link(source, self.root / 'outside-link')
        self.assertEqual(self.verify().reason, 'installed_type')

    def test_installed_tree_and_read_errors_fail_closed(self):
        self.install()
        expected = self.build(limits=replace(content.Limits(), max_installed_nodes=2))
        self.assertEqual(self.verify(expected).reason, 'installed_limit')
        class BrokenReader(DiskReader):
            def stable(self):
                raise OSError('sensitive pathname must not leak')
        result = self.verify(reader=BrokenReader(self.root))
        self.assertEqual(result.status, 'STOP')
        self.assertEqual(result.reason, 'installed_read')
        self.assertNotIn('sensitive', repr(result))

    def test_installed_total_bytes_are_bounded_before_reads(self):
        self.install()
        expected = self.build(limits=replace(content.Limits(), max_installed_bytes=100))
        self.assertEqual(self.verify(expected).reason, 'installed_limit')

    def test_unknown_empty_import_directory_stops(self):
        self.install()
        (self.root / SITE / 'untrusted_namespace').mkdir()
        self.assertEqual(self.verify().reason, 'installed_extra')

    def test_empty_startup_hook_directory_stops(self):
        self.install()
        (self.root / SITE / 'sitecustomize').mkdir()
        self.assertEqual(self.verify().reason, 'startup_hook')

    def write_cache(self, source=b'VALUE = 7\n', filename=None, optimize=0, flags=0):
        import importlib.util
        import marshal
        source_path = self.root / SITE / 'demo_pkg/__init__.py'
        filename = filename or content.INSTALLED_SITE_PATH + '/demo_pkg/__init__.py'
        code = compile(source, filename, 'exec', dont_inherit=True, optimize=optimize)
        if flags & 1:
            header = importlib.util.source_hash(source)
        else:
            header = struct.pack('<II', int(source_path.stat().st_mtime) & 0xffffffff, len(source))
        data = importlib.util.MAGIC_NUMBER + struct.pack('<I', flags) + header + marshal.dumps(code)
        suffix = '' if optimize == 0 else f'.opt-{optimize}'
        relative = f'demo_pkg/__pycache__/__init__.cpython-312{suffix}.pyc'
        path = self.root / SITE / relative
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        record = self.root / SITE / DIST / 'RECORD'
        record.write_bytes(record.read_bytes() + (relative + ',,\n').encode())
        return path

    def test_verified_source_timestamp_and_hash_pyc_pass(self):
        for flags in (0, 1, 3):
            for optimize in (0, 1, 2):
                with self.subTest(flags=flags, optimize=optimize):
                    self.install()
                    path = self.write_cache(flags=flags, optimize=optimize)
                    self.assertEqual(self.verify().runtime_status, 'PASS')
                    path.unlink()

    def test_forged_pyc_with_valid_source_header_stops(self):
        self.install()
        path = self.write_cache()
        original = path.read_bytes()
        import marshal
        malicious = compile('VALUE = 9\n', content.INSTALLED_SITE_PATH + '/demo_pkg/__init__.py', 'exec')
        path.write_bytes(original[:16] + marshal.dumps(malicious))
        self.assertEqual(self.verify().reason, 'bytecode_content')

    def test_wrong_code_filename_magic_hash_and_flags_stop(self):
        for change in ('filename', 'magic', 'hash', 'flags'):
            with self.subTest(change=change):
                self.install()
                path = self.write_cache(filename='/wrong/path.py' if change == 'filename' else None, flags=3)
                data = bytearray(path.read_bytes())
                if change == 'magic':
                    data[0] ^= 1
                elif change == 'hash':
                    data[8] ^= 1
                elif change == 'flags':
                    data[4] = 2
                path.write_bytes(data)
                self.assertEqual(self.verify().reason, 'bytecode_content')

    def test_known_console_record_row_is_reported_excluded(self):
        files = wheel_files(extras={DIST + '/entry_points.txt': b'[console_scripts]\ndemo = demo_pkg:main\n'})
        expected = self.build(zipped(files))
        self.install(files)
        record = self.root / SITE / DIST / 'RECORD'
        record.write_bytes(record.read_bytes() + b'../../../bin/demo,sha256=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,8\n')
        result = self.verify(expected)
        self.assertEqual(result.runtime_status, 'PASS')
        self.assertEqual(result.excluded_entrypoints, ('../../../bin/demo',))
        self.assertEqual(result.scope, 'IMPORT_PATH_CONTENT')


    def test_trusted_bootstrap_pip_versioned_console_alias_is_excluded(self):
        pip_files = wheel_files('pip', '24.0', {'pip-24.0.dist-info/entry_points.txt': b'[console_scripts]\npip = pip._internal.cli.main:main\n'})
        pip_data = zipped(pip_files)
        pip_pin = self.pin_for(pip_data, 'pip', '24.0', 'pip-24.0-py3-none-any.whl', 'bootstrap')
        expected = content.build_expected({self.pin.file: self.data, pip_pin.file: pip_data}, [self.pin, pip_pin])
        self.install()
        for name, data in pip_files.items():
            path = self.root / SITE / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        record = self.root / SITE / 'pip-24.0.dist-info/RECORD'
        record.write_bytes(record.read_bytes() + b'../../../bin/pip3.12,sha256=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,8\n')
        result = self.verify(expected)
        self.assertEqual(result.status, 'PASS_SITE_CONTENT_ONLY')
        self.assertEqual(result.excluded_entrypoints, ('../../../bin/pip3.12',))


if __name__ == '__main__':
    unittest.main()
