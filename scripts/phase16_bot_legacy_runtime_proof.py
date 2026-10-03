"""Bounded old-runtime content snapshot and portable continuity evidence.

No CLI, app import, bytecode decoding, service call or mutation. Root/OS trust is
assumed. Hashes authenticate the OBSERVED bytes and two fixed legacy-policy files;
they do not authenticate every dependency against a publisher or prove deployed
Git HEAD. Existing pycache files are included as opaque bytes, never blindly
skipped. Subsequent creation/removal/change, including caches, requires fresh
admission; a cheap continuity check never silently takes a new baseline.

Saved records MUST be authenticated by the parent's root-private signed dossier
and prepared observation digest. A self-consistent record hash is not provenance.
"""
from __future__ import annotations

from contextlib import ExitStack
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import PurePosixPath
import re
import stat
import sys
import time

from scripts import phase16_legacy_stop_policy as policy
from scripts.phase16_bot_stage_access import UnixStageReader
from scripts.vps.phase16_bot_stage_readback_remote import BoundTree
from scripts.vps.phase16_bot_retained_stage_remote import fingerprint

SOURCE_ROOT = '/opt/amn2-spain/runtime/source/app'
DEPENDENCIES_ROOT = '/opt/amn2-spain/runtime/site-packages'
ROOTS = {'source': SOURCE_ROOT, 'dependencies': DEPENDENCIES_ROOT}
POLICY_PINS = {'bot/handlers.py': policy.OLD_HANDLERS, 'bot/workflows.py': policy.OLD_WORKFLOWS}
SCOPE = 'OBSERVED_CONTENT_SNAPSHOT_NOT_PACKAGE_PROVENANCE'
NOT_PROVEN = ('deployed_git_revision', 'dependency_publisher_provenance', 'bytecode_execution_safety',
              'other_import_paths', 'interpreter_stdlib_os', 'service_access')


class LegacyProofError(ValueError):
    """Fixed non-sensitive admission failure."""


def require(condition, reason):
    if not condition:
        raise LegacyProofError(reason)


@dataclass(frozen=True)
class Limits:
    max_nodes: int = 20000
    max_file_bytes: int = 64 * 1024 * 1024
    max_total_bytes: int = 512 * 1024 * 1024
    max_children: int = 1024
    max_record_bytes: int = 8 * 1024 * 1024
    collect_seconds: int = 120
    check_seconds: int = 30


class UnixLegacyReader(UnixStageReader):
    """Reuse descriptor-pinned no-follow/ACL reads for these two roots only."""
    def __init__(self, root, *, syscalls=None):
        require(sys.platform == 'linux' and root in ROOTS.values(), 'legacy_reader_platform')
        if syscalls is None:
            BoundTree.__init__(self, root)
        else:
            BoundTree.__init__(self, root, syscalls=syscalls)


def _path(name):
    require(isinstance(name, str) and 0 < len(name) <= 512 and '\\' not in name and ':' not in name
            and all(ord(c) >= 32 and ord(c) != 127 for c in name), 'unsafe_path')
    require(len(name.split('/')) <= 32 and all(part not in ('', '.', '..') for part in name.split('/')), 'unsafe_path')
    return name


def _meta(value):
    require(value.st_uid == 0 and not value.st_mode & 0o7022
            and not getattr(value, 'st_file_attributes', 0) & 0x400
            and (stat.S_ISDIR(value.st_mode) or stat.S_ISREG(value.st_mode))
            and (not stat.S_ISREG(value.st_mode) or value.st_nlink == 1), 'unsafe_metadata')
    return list(fingerprint(value))


def _acl(reader, name):
    value = reader.acl_names(name)
    require(type(value) in (tuple, list) and not value, 'acl_not_clear')


def _ancestors(reader):
    values = []
    for name, meta, acls in reader.ancestors():
        require(isinstance(name, str) and name.startswith('/') and len(name) <= 512, 'unsafe_path')
        require(type(acls) in (tuple, list) and not acls, 'acl_not_clear')
        require(stat.S_ISDIR(meta.st_mode), 'unsafe_metadata')
        values.append({'path': name, 'fingerprint': _meta(meta)})
    require(0 < len(values) <= 32, 'proof_limit')
    return values


def _encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def _sha(value):
    return hashlib.sha256(_encoded(value)).hexdigest()


def _content(nodes):
    # Names/types cover empty namespaces too. Metadata continuity is separately
    # retained, while rollback digest binds actual file bytes independent of inode.
    values = []
    for name, item in sorted(nodes.items()):
        values.append([name, item['kind'], item['fingerprint'][6] if item['kind'] == 'file' else None, item['sha256']])
    return _sha(values)


def _capture(reader, limits, counters, deadline):
    ancestors = _ancestors(reader)
    nodes = {}
    def visit(name):
        require(time.monotonic() < deadline, 'proof_timeout')
        if name != '.':
            _path(name)
        counters[0] += 1
        require(counters[0] <= limits.max_nodes, 'proof_limit')
        before = reader.info(name)
        saved = _meta(before)
        _acl(reader, name)
        if stat.S_ISDIR(before.st_mode):
            children = reader.entries(name)
            require(type(children) in (list, tuple) and len(children) <= limits.max_children
                    and len(children) == len(set(children)), 'proof_limit')
            for child in children:
                _path(child)
                require('/' not in child, 'unsafe_path')
            nodes[name] = {'kind': 'directory', 'fingerprint': saved, 'children': sorted(children), 'sha256': None}
            for child in sorted(children):
                visit(child if name == '.' else name + '/' + child)
        else:
            # .env reads are outside this component; discovering one is a gate.
            leaf = name.rsplit('/', 1)[-1]
            require(leaf != '.env' and not leaf.startswith('.env.'), 'protected_surface')
            counters[1] += before.st_size
            require(0 <= before.st_size <= limits.max_file_bytes and counters[1] <= limits.max_total_bytes, 'proof_limit')
            data = reader.read_file(name, limits.max_file_bytes, expected_size=before.st_size)
            require(isinstance(data, bytes) and len(data) == before.st_size, 'proof_read')
            nodes[name] = {'kind': 'file', 'fingerprint': saved, 'children': None, 'sha256': hashlib.sha256(data).hexdigest()}
        require(_meta(reader.info(name)) == saved, 'continuity_changed')
    visit('.')
    return {'ancestors': ancestors, 'nodes': nodes, 'content_sha256': _content(nodes)}


def _check_tree(reader, tree, deadline):
    require(time.monotonic() < deadline, 'proof_timeout')
    require(_ancestors(reader) == tree['ancestors'], 'continuity_changed')
    for name, saved in tree['nodes'].items():
        require(time.monotonic() < deadline, 'proof_timeout')
        before = reader.info(name)
        require(_meta(before) == saved['fingerprint'], 'continuity_changed')
        _acl(reader, name)
        if saved['children'] is not None:
            require(sorted(reader.entries(name)) == saved['children'], 'continuity_changed')
        require(_meta(reader.info(name)) == saved['fingerprint'], 'continuity_changed')
    reader.stable()


def _validate_record(record):
    try:
        require(type(record) is dict and set(record) == {'schema', 'scope', 'roots', 'rollback', 'policy_source', 'limits', 'not_proven', 'sha256'}, 'record_binding')
        require(record['schema'] == 'phase16.legacy-runtime-proof.v1' and record['scope'] == SCOPE
                and record['not_proven'] == list(NOT_PROVEN), 'record_binding')
        limits = Limits(**record['limits'])
        require(all(type(value) is int and value > 0 for value in asdict(limits).values()), 'proof_limit')
        # Saved data may tighten limits but cannot authorize a larger check.
        require(all(value <= getattr(Limits(), key) for key, value in asdict(limits).items()), 'proof_limit')
        require(len(_encoded(record)) <= limits.max_record_bytes and set(record['roots']) == set(ROOTS), 'proof_limit')
        require(record['sha256'] == _sha({key: value for key, value in record.items() if key != 'sha256'}), 'record_binding')
        count = 0
        total = 0
        for label, tree in record['roots'].items():
            require(set(tree) == {'root', 'ancestors', 'nodes', 'content_sha256'} and tree['root'] == ROOTS[label]
                    and '.' in tree['nodes'], 'record_binding')
            children_by_parent = {}
            for path in tree['nodes']:
                if path != '.':
                    parent = path.rpartition('/')[0] or '.'
                    require(parent in tree['nodes'] and tree['nodes'][parent]['kind'] == 'directory', 'record_binding')
                    children_by_parent.setdefault(parent, set()).add(path)
            for name, node in tree['nodes'].items():
                if name != '.':
                    _path(name)
                count += 1
                require(count <= limits.max_nodes and set(node) == {'kind', 'fingerprint', 'children', 'sha256'}, 'proof_limit')
                fp = node['fingerprint']
                require(type(fp) is list and len(fp) == 9 and all(type(value) is int for value in fp), 'record_binding')
                require(fp[3] == 0 and not fp[2] & 0o7022 and fp[6] >= 0, 'record_binding')
                if node['kind'] == 'file':
                    require(stat.S_ISREG(fp[2]) and fp[5] == 1 and node['children'] is None
                            and re.fullmatch('[a-f0-9]{64}', node['sha256']), 'record_binding')
                    total += fp[6]
                    require(fp[6] <= limits.max_file_bytes and total <= limits.max_total_bytes, 'proof_limit')
                else:
                    require(node['kind'] == 'directory' and stat.S_ISDIR(fp[2]) and node['sha256'] is None
                            and type(node['children']) is list and node['children'] == sorted(set(node['children']))
                            and len(node['children']) <= limits.max_children, 'record_binding')
                    prefix = '' if name == '.' else name + '/'
                    require({prefix + child for child in node['children']} ==
                            children_by_parent.get(name, set()), 'record_binding')
            require(tree['content_sha256'] == _content(tree['nodes']), 'record_binding')
        require(record['rollback'] == {label + '_sha256': record['roots'][label]['content_sha256'] for label in ROOTS}, 'record_binding')
        require(record['policy_source'] == _policy_source(record['roots']['source']['nodes']), 'record_binding')
        return limits
    except LegacyProofError:
        raise
    except Exception:
        raise LegacyProofError('record_binding') from None


def _policy_source(nodes):
    require(all(name in nodes and nodes[name]['kind'] == 'file' and nodes[name]['sha256'] == digest
                for name, digest in POLICY_PINS.items()), 'policy_source')
    return {'old_commit': policy.OLD_COMMIT, 'old_handlers_sha256': nodes['bot/handlers.py']['sha256'],
            'old_workflows_sha256': nodes['bot/workflows.py']['sha256'],
            'commit_evidence': 'POLICY_REFERENCE_ONLY', 'deployed_git_verified': False}


class LegacyRuntimeProof:
    def __init__(self, record, readers, stack):
        self._record = record
        self._readers = readers
        self._stack = stack
        self._closed = False

    @property
    def rollback(self):
        return dict(self._record['rollback'])

    @property
    def policy_source(self):
        return dict(self._record['policy_source'])

    def record(self):
        return json.loads(_encoded(self._record))

    def check(self):
        require(not self._closed, 'proof_closed')
        limits = _validate_record(self._record)
        deadline = time.monotonic() + limits.check_seconds
        try:
            for label, reader in self._readers.items():
                _check_tree(reader, self._record['roots'][label], deadline)
            return self.rollback
        except LegacyProofError:
            raise
        except Exception:
            raise LegacyProofError('continuity_changed') from None

    def close(self):
        if not self._closed:
            self._closed = True
            try:
                self._stack.close()
            except Exception:
                raise LegacyProofError('continuity_changed') from None

    def __enter__(self):
        require(not self._closed, 'proof_closed')
        return self

    def __exit__(self, kind, error, traceback):
        self.close()


def collect_live(*, reader_factory=UnixLegacyReader, limits=Limits()) -> LegacyRuntimeProof:
    """Explicit Linux read-only collection; retain descriptors until proof.close()."""
    require(type(limits) is Limits and all(type(value) is int and 0 < value <= getattr(Limits(), key)
                                         for key, value in asdict(limits).items()), 'proof_limit')
    stack = ExitStack()
    try:
        readers = {label: stack.enter_context(reader_factory(root)) for label, root in ROOTS.items()}
        deadline = time.monotonic() + limits.collect_seconds
        counters = [0, 0]
        trees = {label: dict(root=ROOTS[label], **_capture(reader, limits, counters, deadline)) for label, reader in readers.items()}
        source = _policy_source(trees['source']['nodes'])
        record = {'schema': 'phase16.legacy-runtime-proof.v1', 'scope': SCOPE, 'roots': trees,
                  'rollback': {label + '_sha256': trees[label]['content_sha256'] for label in ROOTS},
                  'policy_source': source, 'limits': asdict(limits), 'not_proven': list(NOT_PROVEN)}
        record['sha256'] = _sha(record)
        _validate_record(record)
        for label, reader in readers.items():
            # Compare to metadata captured DURING hashing; never baseline again.
            _check_tree(reader, trees[label], deadline)
        return LegacyRuntimeProof(record, readers, stack)
    except BaseException as error:
        try:
            stack.close()
        except Exception:
            if not isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise LegacyProofError('continuity_changed') from None
        if isinstance(error, (LegacyProofError, KeyboardInterrupt, SystemExit)):
            raise
        raise LegacyProofError('proof_read') from None


def check_saved(record, *, reader_factory=UnixLegacyReader):
    """Verify authenticated saved continuity metadata; never rehash file contents."""
    limits = _validate_record(record)
    deadline = time.monotonic() + limits.check_seconds
    try:
        with ExitStack() as stack:
            readers = {label: stack.enter_context(reader_factory(root)) for label, root in ROOTS.items()}
            for label, reader in readers.items():
                _check_tree(reader, record['roots'][label], deadline)
            return dict(record['rollback'])
    except LegacyProofError:
        raise
    except Exception:
        raise LegacyProofError('continuity_changed') from None
