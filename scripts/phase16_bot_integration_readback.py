"""Prepare a pinned, offline manifest. Live execution intentionally unavailable."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.vps import phase16_bot_integration_readback as core

SOURCE_COMMIT = '6e682356ed14a62d636ee58039fd3a389e794809'
SCHEMA_FILES = ('app/db/schema.py','app/db/phase14_dual_protocol.py','app/db/phase15_bootstrap.py')


def parse_lock(text):
    pins = {}
    for line in text.splitlines():
        value = line.strip()
        if not value or value.startswith('#'):
            continue
        if re.fullmatch(r'--hash=sha256:[0-9a-f]{64} ?\\?', value):
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([0-9][A-Za-z0-9.!+_-]{0,63}) ?\\?', value)
        core.require(match is not None, 'lock_unpinned')
        name = core.normalize_name(match[1])
        core.require(name not in pins, 'lock_duplicate')
        pins[name] = match[2]
    core.require(bool(pins), 'lock_empty')
    return dict(sorted(pins.items()))


def schema_allowlist(texts):
    """Conservative static identifier extraction, never an app import or SQL execution.

    Includes historical/rebuild declarations: this is a disclosure allowlist, not
    a canonical schema assertion. Unknown constructs remain unknown at readback.
    """
    tables, indexes = {}, set()
    for text in texts:
        tree = ast.parse(text)
        dynamic = {id(part) for value in ast.walk(tree) if isinstance(value, ast.JoinedStr)
                   for part in ast.walk(value)}
        for node in ast.walk(tree):
            if id(node) in dynamic:
                continue
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                sql = re.sub(r"'(?:''|[^'])*'", "''", node.value)
                for match in re.finditer(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-z_][a-z0-9_]*)\s*\(',sql,re.I):
                    table = match[1]
                    # Match the balanced definition, ignoring already stripped SQL strings.
                    depth, end = 1, match.end()
                    while end < len(sql) and depth:
                        depth += (sql[end] == '(') - (sql[end] == ')')
                        end += 1
                    core.require(depth == 0, 'schema_parse')
                    body = sql[match.end():end-1]
                    cols = re.findall(r'(?:^|,)\s*([a-z_][a-z0-9_]*)\s+(?:INTEGER|INT|TEXT|REAL|BLOB|NUMERIC)\b',body,re.I)
                    tables.setdefault(table,set()).update(cols)
                indexes.update(re.findall(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-z_][a-z0-9_]*)\b',sql,re.I))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '_ensure_column':
                args = node.args
                if len(args) >= 3 and all(isinstance(a,ast.Constant) and isinstance(a.value,str) for a in args[1:3]):
                    tables.setdefault(args[1].value,set()).add(args[2].value)
    core.require(bool(tables) and all(tables.values()), 'schema_parse')
    return {'tables': {k: sorted(v) for k,v in sorted(tables.items())}, 'indexes':sorted(indexes)}


def git(root, *args):
    process = subprocess.run(['git','-C',str(root),*args],capture_output=True,timeout=10,
                             stdin=subprocess.DEVNULL, shell=False)
    core.require(process.returncode == 0, 'source_git')
    core.require(len(process.stdout) <= 8388608 and len(process.stderr) <= 8192, 'git_output_cap')
    return process.stdout


def build_manifest(root):
    core.require(git(root,'rev-parse','HEAD').strip().decode('ascii') == SOURCE_COMMIT, 'source_commit')
    core.require(not git(root,'status','--porcelain','--untracked-files=no').strip(), 'source_dirty')
    names = git(root,'ls-tree','-r','--name-only',SOURCE_COMMIT,'--','app/').decode().splitlines()
    names = [n for n in names if n.endswith('.py')]
    core.require(0 < len(names) <= 256, 'source_cap')
    source, texts, total = {}, {}, 0
    for name in names:
        relative = core.safe_relative(name.removeprefix('app/'))
        data = git(root,'show',SOURCE_COMMIT+':'+name)
        total += len(data)
        core.require(len(data) <= 1048576 and total <= 8388608, 'source_cap')
        source[relative] = {'sha256':core.digest(data),'bytes':len(data)}
        if name in SCHEMA_FILES:
            texts[name] = data.decode('utf-8')
    lock = git(root,'show',SOURCE_COMMIT+':requirements/phase15-runtime-py312.lock')
    pins = parse_lock(lock.decode('utf-8'))
    core.require(len(pins) == 40 and len(texts) == len(SCHEMA_FILES), 'source_binding')
    return {'schema':'phase16.integration-manifest.v1','source_commit':SOURCE_COMMIT,
            'source_hash_policy':'git_blob_bytes_no_checkout_conversion',
            'source':source,'runtime_pins':pins,'runtime_lock_sha256':core.digest(lock),
            'schema_allowlist':schema_allowlist([texts[n] for n in SCHEMA_FILES]),
            'limitations':['STATIC_IDENTIFIER_ALLOWLIST_NOT_COMPATIBILITY','RUNTIME_BINDING_UNKNOWN',
                           'WRITER_COMPLETENESS_UNKNOWN','LINUX_GUARD_NOT_VALIDATED','LIVE_EXECUTION_DISABLED']}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if any(a == '--execute' or a.startswith('--execute=') for a in argv):
        print('{"status":"LIVE_EXECUTION_DISABLED"}')
        return 3
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True)
    parser.add_argument('--manifest-out',type=Path,required=True)
    args = parser.parse_args(argv)
    try:
        result = build_manifest(args.source_root)
        data = core.encode_result(result)+b'\n'
        # Exclusive creation; no overwriting previous evidence.
        with args.manifest_out.open('xb') as stream:
            stream.write(data)
        print(json.dumps({'status':'OFFLINE_MANIFEST_READY_NOT_LIVE','sha256':core.digest(data),
                          'source_files':len(result['source']),'runtime_pins':len(result['runtime_pins']),
                          'schema_tables':len(result['schema_allowlist']['tables']),
                          'live_execution':'DISABLED'},sort_keys=True))
        return 0
    except core.Stop as error:
        print(json.dumps({'status':'STOP','reason':str(error)}))
    except (OSError,ValueError,subprocess.SubprocessError,SyntaxError):
        print('{"status":"STOP","reason":"local_preparation"}')
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
