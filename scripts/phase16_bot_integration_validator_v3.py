"""Versioned schema receipt validation; no transport or execution entrypoint."""
import json
from pathlib import Path
import re
from scripts.vps import phase16_bot_integration_readback_v3 as core
from scripts.phase16_bot_integration_readback_gate import (
    canonical, exact_dict, validate_host, validate_units, validate_source,
    validate_dependencies, validate_database_files, validate_process,
    validate_holders, validate_unit_probe, validate_file_map,
)
ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST_RELATIVE = Path('research/amn2/phase16-bot-integration-manifest-v3-6e68235.json')

def source_manifest(root=ROOT):
    try:
        value = json.loads(canonical(Path(root) / SOURCE_MANIFEST_RELATIVE))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise core.Stop("manifest_binding") from None
    core.require(isinstance(value, dict) and value.get("schema") ==
                 "phase16.integration-manifest.v2", "manifest_binding")
    return value


def validate_database(value, manifest):
    def need(condition):
        core.require(condition, 'receipt_binding')
    exact_dict(value, {'schema', 'status', 'sqlite_version', 'schema_version', 'user_version',
                       'journal_mode', 'tables', 'triggers', 'compatibility'})
    allowed = manifest['schema_allowlist']
    need(value['schema'] == 'phase16.database-shape.v2' and
         value['status'] == 'SHAPE_ONLY' and value['compatibility'] == 'UNKNOWN' and
         type(value['sqlite_version']) is str and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', value['sqlite_version']) and
         type(value['schema_version']) is int and type(value['user_version']) is int and
         value['journal_mode'] in ('delete','truncate','persist','memory','wal','off') and
         type(value['tables']) is list and len(value['tables']) <= 128 and type(value['triggers']) is list)
    seen_tables, seen_indexes, seen_triggers = set(), set(), set()
    counts = [0, 0, 0]
    for table in value['tables']:
        exact_dict(table, {'name', 'columns', 'indexes', 'foreign_keys'})
        name = table['name']
        need(type(name) is str and name in allowed['tables'] and name not in seen_tables)
        seen_tables.add(name)
        need(all(type(table[key]) is list for key in ('columns','indexes','foreign_keys')))
        columns, ids = set(), {}
        for column in table['columns']:
            need(type(column) is list and len(column) == 6 and type(column[0]) is str and
                 column[0] in allowed['tables'][name] and column[0] not in columns and
                 column[1] in ('INTEGER','INT','TEXT','REAL','BLOB','NUMERIC','') and
                 all(type(c) is int for c in column[2:]) and column[2] in (0,1) and
                 column[3] >= 0 and column[4] in (0,1,2,3) and column[5] >= 0 and column[5] not in ids)
            columns.add(column[0]); ids[column[5]] = column[0]
        for index in table['indexes']:
            exact_dict(index, {'name','unique','partial','terms'})
            index_name = index['name']
            need(type(index_name) is str and index_name not in seen_indexes and
                 (index_name in allowed['indexes'] or re.fullmatch('sqlite_autoindex_'+re.escape(name)+'_[0-9]+',index_name)) and
                 type(index['unique']) is int and index['unique'] in (0,1) and
                 type(index['partial']) is int and index['partial'] in (0,1) and
                 type(index['terms']) is list and 0 < len(index['terms']) <= 512)
            seen_indexes.add(index_name)
            for sequence, term in enumerate(index['terms']):
                exact_dict(term, {'sequence','cid','kind','name'})
                need(type(term['sequence']) is int and term['sequence'] == sequence and type(term['cid']) is int)
                cid, column = term['cid'], term['name']
                need((term['kind'] == 'COLUMN' and cid >= 0 and type(column) is str and ids.get(cid) == column) or
                     (term['kind'] == 'EXPRESSION' and cid == -2 and column is None) or
                     (term['kind'] == 'ROWID' and cid == -1 and column is None))
        for foreign in table['foreign_keys']:
            exact_dict(foreign, {'table','from','to','sequence','on_update','on_delete'})
            target = foreign['table']
            need(type(target) is str and target in allowed['tables'] and foreign['from'] in columns and
                 (foreign['to'] is None or foreign['to'] in allowed['tables'][target]) and
                 type(foreign['sequence']) is int and foreign['sequence'] >= 0 and
                 all(foreign[k] in ('NO ACTION','RESTRICT','SET NULL','SET DEFAULT','CASCADE') for k in ('on_update','on_delete')))
        for n, key in enumerate(('columns','indexes','foreign_keys')):
            counts[n] += len(table[key])
    need(all(n <= cap for n,cap in zip(counts,(512,128,128))))
    need(len(value['triggers']) <= 128)
    for trigger in value['triggers']:
        exact_dict(trigger, {'name','table'})
        name, table = trigger['name'], trigger['table']
        need(type(name) is str and name in allowed['triggers'] and name not in seen_triggers and
             type(table) is str and table in seen_tables and allowed['triggers'][name] == table)
        seen_triggers.add(name)


def validate_partial(value, manifest):
    core.require(isinstance(value, dict) and set(value) <= {"host", "units_before", "source",
                 "dependencies", "database_files_before", "database", "database_child",
                 "holders", "units_after", "unit_probe", "summary"}, "receipt_binding")
    validators = {"host": validate_host, "units_before": validate_units,
                  "source": lambda item: validate_source(item, manifest),
                  "dependencies": lambda item: validate_dependencies(item, manifest),
                  "database_files_before": validate_file_map,
                  "database": lambda item: validate_database(item, manifest),
                  "database_child": validate_process, "holders": validate_holders,
                  "units_after": validate_units, "unit_probe": validate_unit_probe}
    for name, item in value.items():
        if name == "summary":
            exact_dict(item, {"stages", "digests"})
            allowed = set(validators)
            core.require(isinstance(item["stages"], list) and set(item["stages"]) <= allowed and
                         isinstance(item["digests"], dict) and
                         set(item["digests"]) == set(item["stages"]) and
                         all(re.fullmatch(r"[0-9a-f]{64}", digest)
                             for digest in item["digests"].values()), "receipt_binding")
        else:
            validators[name](item)


def validate_receipt(result, returncode):
    manifest = source_manifest(ROOT)
    common = {"schema", "status", "service_actions", "database_write_attempted",
              "application_imported", "runtime_activation"}
    core.require(isinstance(result, dict) and result.get("schema") ==
                 "phase16.integration-readback-remote.v2" and
                 result.get("service_actions") == 0 and
                 result.get("database_write_attempted") is False and
                 result.get("application_imported") is False and
                 result.get("runtime_activation") is False, "receipt_binding")
    if result.get("status") == "READBACK_COMPLETE_WITH_LIMITATIONS":
        expected = common | {"host", "units_before", "source", "dependencies",
                             "database_files", "database", "database_child", "holders",
                             "units_after", "unit_identity_stable", "production_source_read",
                             "production_units_read", "completed_at", "limitations"}
        core.require(set(result) == expected and returncode == 0 and
                     result.get("production_source_read") is True and
                     result.get("production_units_read") is True and
                     result.get("unit_identity_stable") is True and
                     all(isinstance(result.get(name), dict) for name in
                         ("host", "units_before", "source", "dependencies", "database_files",
                          "database", "database_child", "holders", "units_after")) and
                     isinstance(result.get("limitations"), list) and
                     result.get("database", {}).get("status") == "SHAPE_ONLY" and
                     isinstance(result.get("completed_at"), str) and
                     len(result["completed_at"]) <= 40 and
                     re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.+\-]{8,32}",
                                  result["completed_at"]),
                     "receipt_binding")
        validate_host(result["host"])
        validate_units(result["units_before"])
        validate_source(result["source"], manifest)
        validate_dependencies(result["dependencies"], manifest)
        validate_database_files(result["database_files"])
        validate_database(result["database"], manifest)
        validate_process(result["database_child"])
        validate_holders(result["holders"])
        validate_units(result["units_after"])
        core.require(result["limitations"] == [
            "STATIC_SOURCE_SCOPE_ONLY", "STATIC_DEPENDENCY_METADATA_ONLY",
            "SCHEMA_SHAPE_ONLY", "RUNTIME_BINDING_UNKNOWN",
            "WRITER_COMPLETENESS_UNKNOWN", "SEMANTIC_COMPATIBILITY_UNKNOWN"],
            "receipt_binding")
    else:
        core.require(set(result) == common | {"reason", "partial"} and returncode == 3 and
                     result.get("status") == "STOP_NO_RETRY" and
                     re.fullmatch(r"[a-z0-9_]{1,80}", result.get("reason", "")) and
                     isinstance(result.get("partial"), dict),
                     "receipt_binding")
        validate_partial(result["partial"], manifest)
    return result
