"""Offline target binding and typed input validation, NOT a live executor.

Historical stage evidence selects immutable paths; it cannot supply fresh host
facts or operator ownership. Even valid synthetic inputs grant no authority.
Future adapters must collect inputs in one target/boot/window and recheck before
mutation. No CLI accepts observations or executes SSH, SQLite, systemd or app code.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_stage_readback_gate as readback
from scripts.vps import phase16_bot_stage_readback_remote as remote
from scripts.phase16_bot_db_rehearsal import Stop, require

TARGET='87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6'
STAGE='/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001'
SAVED_RECEIPT='de51f2e6905ae6860eefaf455e40e4512377d92d97c6024319e01b2cbb5d1694'
BOUND={
 'record':('research/amn2/phase16-bot-stage-readback-execution-001-2026-09-29.json','043cb988f3221c8672b7468a71687a416535f42c66042e91802452830a415122'),
 'inventory':('research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json','647a32f7a538028a8debbe8169ade373ea08b5d1c1b0467a36a9253380852aec'),
 'integration':('research/amn2/phase16-bot-integration-manifest-v3-6e68235.json','faac75cf5f2d136344bdfc54fd6cfe3bab8271cc7424ca1050775634860723a4')}
MANIFEST=ROOT/'research/amn2/phase16-bot-maintenance-target-manifest-2026-09-30.json'
BLOCKERS=['fresh_server_observation','operator_window_declaration','maintenance_operation_adapters']
UNITS=(core.BOT,core.WEB)


def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(path):return Path(path).read_bytes().replace(b'\r\n',b'\n')
def exact(value,fields,reason):require(isinstance(value,dict) and set(value)==set(fields),'inputs_'+reason)
def hexsha(value):require(isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value),'inputs_digest')


def bound_sources():return {name:canonical(ROOT/path) for name,(path,_) in BOUND.items()}


def stage_snapshot(*,blobs=None):
    blobs=bound_sources() if blobs is None else blobs
    exact(blobs,BOUND,'stage_sources')
    for name,(_,digest) in BOUND.items():
        require(isinstance(blobs[name],bytes) and sha(blobs[name])==digest,'stage_evidence_binding')
    record=json.loads(blobs['record']);inventory=json.loads(blobs['inventory']);contract=json.loads(blobs['integration'])
    result=record['local_result'];claim=result['claim'];transport=result['transport']
    require(record['execution_commit']=='07e7769f181ab851f0aa5a532ee9aa31eb80049f' and
            result['status']=='VERIFIED_NOT_ACTIVATED' and result['ssh_attempts']==1 and
            claim['target_binding_sha256']==TARGET and claim['destination']==STAGE,'stage_evidence_binding')
    observation=result['remote_observation']
    wire=b''.join(json.dumps(e).encode()+b'\n' for e in observation['events'])
    try:require(readback.parse_events(wire)==observation,'stage_events')
    except remote.legacy.GateError:raise Stop('stage_events') from None
    require(transport['returncode']==0 and transport['stdin_complete'] is True and transport['output_complete'] is True and
            sha(wire)==transport['stdout']['prefix_sha256'],'stage_events')
    require(observation['result']['saved_receipt_sha256']==SAVED_RECEIPT,'stage_receipt')
    source={name[len('source/app/'):]:dict(bytes=size,sha256=digest)
            for name,(size,digest) in inventory['files'].items() if name.startswith('source/app/') and name.endswith('.py')}
    require(len(source)==126 and len(inventory['files'])==200 and inventory['pins']==contract['runtime_pins'],'stage_inventory')
    mapped=dict(source=source,runtime_pins=inventory['pins'],runtime_lock_sha256=contract['runtime_lock_sha256'],
                archive_sha256=core.ARCHIVE,isolated_venv=True,pth_count=0,system_site_packages=False)
    core.verify_stage(ROOT/BOUND['integration'][0],mapped)
    return dict(status='HISTORICAL_STAGE_BOUND',source_files=126,content_files=200,runtime_pins=40,
                source=source,pins=inventory['pins'],verified_at=claim['claimed_at'],
                fresh_for_maintenance=False,saved_receipt_sha256=SAVED_RECEIPT)


def artifact_bindings():
    paths=['scripts/phase16_bot_maintenance_binding.py','scripts/phase16_bot_maintenance.py',
           'scripts/phase16_bot_db_rehearsal.py','scripts/phase16_bot_stage_readback_gate.py',
           'scripts/vps/phase16_bot_stage_readback_remote.py']
    # Include the transitive runtime bindings already frozen by the readback packet.
    rb=json.loads(canonical(readback.MANIFEST));readback.validate_manifest(rb)
    return {name:sha(canonical(ROOT/name)) for name in sorted(set(paths)|set(rb['artifacts_sha256_lf']))}


def expected_manifest():
    snapshot=stage_snapshot()
    return dict(schema='phase16.maintenance-target-manifest.v1',status='LOCAL_BINDINGS_ONLY',
        base_commit='360ef0c5746c05e1926ca54a39c58879dab07d88',target_binding_sha256=TARGET,
        candidate_commit=core.CANDIDATE,bundle_sha256=core.ARCHIVE,stage_directory=STAGE,
        historical_stage_verified_at=snapshot['verified_at'],saved_stage_receipt_sha256=SAVED_RECEIPT,
        bound_evidence={name:dict(path=path,sha256_lf=digest) for name,(path,digest) in BOUND.items()},
        artifacts_sha256_lf=artifact_bindings(),
        input_contract=dict(max_observation_age_seconds=300,min_ownership_remaining_seconds=900,
                            max_ownership_remaining_seconds=3600,requires_same_operation_target_boot=True),
        live_executor_ready=False,authorized=False,blockers=BLOCKERS,
        future_scope='LOCAL_BINDINGS_AND_TYPED_INPUT_VALIDATION_ONLY')


def validate_packet():
    raw=canonical(MANIFEST)
    try:value=remote.strict_json(raw)
    except Exception:raise Stop('target_manifest') from None
    require(core.encoded(value)==core.encoded(expected_manifest()),'target_manifest')
    return value


def timestamp(value):
    require(isinstance(value,str) and len(value)<=40,'inputs_time')
    try:parsed=datetime.fromisoformat(value)
    except (ValueError,TypeError):raise Stop('inputs_time') from None
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None,'inputs_time')
    return parsed.astimezone(timezone.utc)


def target_paths(operation):
    require(isinstance(operation,str) and re.fullmatch('phase16-[a-z0-9-]{1,80}',operation),'inputs_operation')
    base=PurePosixPath('/var/lib/amn2-spain/phase16-maintenance')/operation
    return dict(candidate_source=STAGE+'/source',candidate_interpreter=STAGE+'/runtime-venv/bin/python',
                old_source='/opt/amn2-spain/runtime/source/app',old_dependencies='/opt/amn2-spain/runtime/site-packages',
                database='/var/lib/amn2-spain/amn2.sqlite3',maintenance_directory=str(base),
                backup=str(base/'backup.sqlite3'),rehearsal=str(base/'rehearsal.sqlite3'),journal=str(base/'journal'))


def prepare_inputs(observation,ownership,*,now=None):
    """Validate caller-provided facts; cannot establish that they were collected.

    A future approved runner must provide provenance and enforce OS deadlines,
    isolation, fresh fences/drain, storage ownership and per-action checks. The
    result is unsuitable for unattended live execution and has no execute method.
    """
    validate_packet();stage_snapshot()
    exact(observation,{'schema','operation_id','target_binding_sha256','boot_id','observed_at','stage','units',
        'inventory','settings','rollback','pending_operations'},'fields')
    exact(ownership,{'schema','operation_id','target_binding_sha256','boot_id','valid_until',
        'exclusive_maintenance_owner','external_pollers_excluded','manual_cli_paused'},'ownership')
    require(observation['schema']=='phase16.maintenance-inputs.v1' and ownership['schema']=='phase16.maintenance-ownership.v1','inputs_schema')
    operation=observation['operation_id'];paths=target_paths(operation)
    boot=observation['boot_id']
    require(isinstance(boot,str) and re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',boot),'inputs_boot')
    require(observation['target_binding_sha256']==ownership['target_binding_sha256']==TARGET and
            ownership['operation_id']==operation and ownership['boot_id']==boot,'inputs_binding')
    current=datetime.now(timezone.utc) if now is None else timestamp(now)
    age=(current-timestamp(observation['observed_at'])).total_seconds()
    remaining=(timestamp(ownership['valid_until'])-current).total_seconds()
    require(0<=age<=300 and 900<=remaining<=3600,'inputs_window')
    for field in ('exclusive_maintenance_owner','external_pollers_excluded','manual_cli_paused'):
        require(ownership[field] is True,'inputs_ownership')
    try:readback.validate_result(observation['stage'],['RECEIPT','CONTENT','METADATA'])
    except Exception:raise Stop('inputs_stage') from None
    require(observation['stage']['status']=='VERIFIED' and observation['stage']['saved_receipt_sha256']==SAVED_RECEIPT,'inputs_stage')
    require(observation['pending_operations']=='none_observed','inputs_pending')
    units=observation['units'];exact(units,UNITS,'units');identities={};launches={};baseline={}
    for unit,value in units.items():
        exact(value,{'baseline','user','group','launch_sha256','kill_mode','kill_signal','final_kill_signal'},'unit')
        for field in ('user','group'):
            require(isinstance(value[field],str) and re.fullmatch('[a-zA-Z_][a-zA-Z0-9_-]{0,63}[$]?',value[field]),'inputs_identity')
        require(value['kill_mode']=='control-group' and type(value['kill_signal']) is int and value['kill_signal']==15 and
                type(value['final_kill_signal']) is int and value['final_kill_signal']==9,'inputs_unit_policy')
        hexsha(value['launch_sha256']);launches[unit]=value['launch_sha256']
        identities[unit]={field:value[field] for field in ('user','group')};baseline[unit]=value['baseline']
    inventory=observation['inventory'];exact(inventory,{'writers','other_writer_classes','process_scan','scan_sha256'},'inventory')
    require(inventory['process_scan']=='complete_bot_web_only','inputs_inventory')
    hexsha(inventory['scan_sha256'])
    settings=observation['settings'];exact(settings,{'vps_apply_enabled','awg3_bootstrap_enabled','admission_seconds','startup_bound_seconds','network_cidr'},'settings')
    admission=settings['admission_seconds'];bound=settings['startup_bound_seconds']
    require(type(admission) is int and type(bound) is int and 1<=admission<=bound<40,'inputs_startup_budget')
    require(isinstance(settings['network_cidr'],str) and len(settings['network_cidr'])<=64,'inputs_network')
    try:network=ipaddress.ip_network(settings['network_cidr'],strict=True)
    except ValueError:raise Stop('inputs_network') from None
    require(network.version==4,'inputs_network')
    rollback=observation['rollback'];exact(rollback,{'source_sha256','dependencies_sha256'},'rollback')
    for value in rollback.values():hexsha(value)
    target=dict(schema='phase16.maintenance-target.v1',operation_id=operation,target_binding_sha256=TARGET,
        boot_id=boot,stage_receipt_sha256=SAVED_RECEIPT,**paths,service_identity=identities,
        original_launch_sha256=launches,original_runtime=rollback,network_cidr=str(network),
        observation_sha256=core.digest(observation),ownership_sha256=core.digest(ownership),
        observed_at=observation['observed_at'],ownership_valid_until=ownership['valid_until'])
    manifest=dict(operation_id=operation,boot_id=boot,candidate_commit=core.CANDIDATE,source_archive_sha256=core.ARCHIVE,
        runtime_pins=40,vps_apply_enabled=settings['vps_apply_enabled'],awg3_bootstrap_enabled=settings['awg3_bootstrap_enabled'],
        admission_seconds=admission,startup_budget_assessed=True,inventory_complete=True,
        exclusive_maintenance_owner=True,external_pollers_excluded=True,manual_cli_paused=True,
        writers=inventory['writers'],other_writer_classes=inventory['other_writer_classes'],unit_baseline=baseline,
        target_contract_sha256=core.digest(target))
    core.validate_manifest(manifest)
    payload=dict(status='PRECONDITIONS_VALIDATED_NOT_AUTHORIZED',live_executor_ready=False,authorized=False,
                 target_contract=target,coordinator_manifest=manifest)
    # Copy caller-owned dictionaries; later mutation cannot silently alter prepared inputs.
    payload=json.loads(core.encoded(payload));payload['prepared_sha256']=core.digest(payload)
    validate_prepared(payload,now=current.isoformat());return payload


def validate_prepared(value,*,now=None):
    exact(value,{'status','live_executor_ready','authorized','target_contract','coordinator_manifest','prepared_sha256'},'prepared')
    require(value['status']=='PRECONDITIONS_VALIDATED_NOT_AUTHORIZED' and value['live_executor_ready'] is False and value['authorized'] is False,'inputs_authority')
    core.validate_manifest(value['coordinator_manifest']);hexsha(value['prepared_sha256'])
    require(value['coordinator_manifest'].get('target_contract_sha256')==core.digest(value['target_contract']) and
            value['prepared_sha256']==core.digest({k:v for k,v in value.items() if k!='prepared_sha256'}),'inputs_pair_binding')
    target=value['target_contract'];manifest=value['coordinator_manifest']
    paths=target_paths(manifest['operation_id'])
    exact(target,set(paths)|{'schema','operation_id','target_binding_sha256','boot_id','stage_receipt_sha256',
        'service_identity','original_launch_sha256','original_runtime','network_cidr','observation_sha256',
        'ownership_sha256','observed_at','ownership_valid_until'},'target')
    require(target['schema']=='phase16.maintenance-target.v1' and target['operation_id']==manifest['operation_id'] and
            target['boot_id']==manifest['boot_id'] and target['target_binding_sha256']==TARGET and
            target['stage_receipt_sha256']==SAVED_RECEIPT,'inputs_target_binding')
    require(isinstance(target['boot_id'],str) and re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',target['boot_id']),'inputs_boot')
    require(all(target[name]==path for name,path in paths.items()),'inputs_target_path')
    exact(target['service_identity'],UNITS,'identity')
    exact(target['original_launch_sha256'],UNITS,'launch')
    for unit in UNITS:
        exact(target['service_identity'][unit],{'user','group'},'identity')
        for identity in target['service_identity'][unit].values():
            require(isinstance(identity,str) and re.fullmatch('[a-zA-Z_][a-zA-Z0-9_-]{0,63}[$]?',identity),'inputs_identity')
        hexsha(target['original_launch_sha256'][unit])
    exact(target['original_runtime'],{'source_sha256','dependencies_sha256'},'rollback')
    for digest in [*target['original_runtime'].values(),target['observation_sha256'],target['ownership_sha256']]:hexsha(digest)
    try:network=ipaddress.ip_network(target['network_cidr'],strict=True)
    except (ValueError,TypeError):raise Stop('inputs_network') from None
    require(network.version==4 and str(network)==target['network_cidr'],'inputs_network')
    current=datetime.now(timezone.utc) if now is None else timestamp(now)
    age=(current-timestamp(target['observed_at'])).total_seconds()
    remaining=(timestamp(target['ownership_valid_until'])-current).total_seconds()
    require(0<=age<=300 and 900<=remaining<=3600,'inputs_window')



def safe_prepare_inputs(*args,**kwargs):
    try:return prepare_inputs(*args,**kwargs)
    except Exception:return dict(status='STOP_INPUTS',reason='binding_or_precondition_failed',authorized=False,live_executor_ready=False)


def preview():
    manifest=validate_packet();snapshot=stage_snapshot()
    return dict(status='BLOCKED_UNKNOWN_PRECONDITIONS',historical_stage='VERIFIED_NOT_ACTIVATED',
        historical_stage_verified_at=snapshot['verified_at'],fresh_stage_required=True,
        source_files=126,content_files=200,runtime_pins=40,target_binding_sha256=TARGET,
        manifest_sha256_lf=sha(canonical(MANIFEST)),live_executor_ready=False,authorized=False,
        blockers=manifest['blockers'],coordinator_manifest=None,ssh_attempts=0,database_operations=0,service_actions=0)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:result=preview()
    except Exception:result=dict(status='LOCAL_STOP',reason='binding_failed',authorized=False)
    print(json.dumps(result,indent=2));return 2 if result['status']=='LOCAL_STOP' else 0


if __name__=='__main__':raise SystemExit(main())
