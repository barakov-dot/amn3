"""Proposed one-shot component telemetry for candidate STOP; default preview only.

No maintenance replay, DB open, app execution, legacy proof, permission apply or
service action. Frozen predecessor and original packet remain unchanged.
"""
import argparse
import ast
from datetime import datetime,timezone
import json
import re
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_maintenance_readback as base
packet=base.packet
APPROVAL='PHASE16_CANDIDATE_COMPONENT_DIAGNOSTIC_20261003_001'
PREDECESSOR_SHA='b0e35c25317b94cafa2ff2b1aa6af15336b4e7e9ec57ac8997d43b600029bb0b'
MANIFEST=ROOT/'research/amn2/phase16-bot-candidate-diagnostic-manifest-2026-10-03.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-candidate-component-diagnostic-20261003/execution-001')
LABELS=('catalog','stage_observation','settings','bootstrap','identity','nss_groups','settings_file_read','secure_tree_open','secure_file_read','readonly_command','runtime_expected','venv','access_plan','collection')
KINDS=('AdmissionError','SettingsError','ProvenanceError','ContentError','AccessError','GateError','FileNotFoundError','PermissionError','OSError','ValueError','KeyError','TypeError','RuntimeError','Stop','OTHER_ERROR')
RETURNS=('UNKNOWN','ABSENT','INCOMPLETE','VERIFIED','PASS','STOP')
EXTRA=r"""
COMPONENTS={}

def component_reason(error):
    return error.args[0] if len(error.args)==1 and isinstance(error.args[0],str) and error.args[0] in COMPONENT_REASONS else 'UNCLASSIFIED_ERROR'

def watch(owner,name,label,undo):
    original=getattr(owner,name);own=name in vars(owner)
    def traced(*args,**kwargs):
        record=COMPONENTS.setdefault(label,dict(calls=0,status='STARTED',reason=None,exception_kind=None,returned_status=None))
        record.update(calls=min(65536,record['calls']+1),status='STARTED',reason=None,exception_kind=None,returned_status=None)
        try:
            value=original(*args,**kwargs)
            returned=value.get('status') if isinstance(value,dict) else None
            record.update(status='PASS',returned_status=returned if returned in RETURNS else None)
            return value
        except Exception as error:
            kind=type(error).__name__
            record.update(status='STOP',reason=component_reason(error),exception_kind=kind if kind in KINDS else 'OTHER_ERROR')
            raise
    undo.append((owner,name,original,own));setattr(owner,name,traced)

def restore(undo):
    for owner,name,original,own in reversed(undo):
        if own:setattr(owner,name,original)
        else:delattr(owner,name)

def diagnose_candidate(m,client,inventory):
    undo=[]
    try:
        for owner,name,label in (
            (m,'catalog','catalog'),(m.readback,'observe','stage_observation'),
            (m.settings,'collect_live','settings'),(m.bootstrap,'collect_live','bootstrap'),
            (m,'local_identity','identity'),(m.os,'getgrouplist','nss_groups'),
            (m.settings.RootSettingsReader,'__call__','settings_file_read'),
            (m.readback.BoundTree,'__enter__','secure_tree_open'),
            (m.readback.BoundTree,'read_file','secure_file_read'),
            (m.runtime,'build_expected','runtime_expected'),(m,'venv_pin','venv'),
            (m.access,'build_access_plan','access_plan'),(m,'collect_live','collection')):
            watch(owner,name,label,undo)
        if callable(getattr(client,'run',None)):watch(client,'run','readonly_command',undo)
        return m.collect_live(client,inventory)
    finally:restore(undo)

_readback_main=main

def main(approval):
    COMPONENTS.clear()
    result=_readback_main(approval)
    result['schema']='phase16.candidate-component-diagnostic.v1'
    if result['status']=='READBACK_COLLECTED_NOT_RECOVERY':
        result['status']='DIAGNOSTIC_COLLECTED_NOT_ADMITTED';result['reason']='bounded_component_observation'
    result['component_steps']=dict(COMPONENTS)
    return result
if __name__=='__main__':
    value=main(sys.argv[1] if len(sys.argv)==2 else '')
    print(json.dumps(value,sort_keys=True,separators=(',',':')),flush=True)
    raise SystemExit(0 if value['status']=='DIAGNOSTIC_COLLECTED_NOT_ADMITTED' else 3)
"""

def require(value,reason):
    if not value:raise ValueError(reason)

def component_reasons():
    # Extend only component telemetry; retain predecessor record/probe semantics.
    found=set(base.literal_reasons())
    for name in base.source_packet()['files_sha256_lf']:
        if not name.endswith('.py'):continue
        for node in ast.walk(ast.parse(packet.canonical(ROOT/name))):
            if isinstance(node,ast.Call) and node.args and (getattr(node.func,'id',None)=='_require' or getattr(node.func,'attr',None)=='_require'):
                value=node.args[-1]
                if isinstance(value,ast.Constant) and isinstance(value.value,str) and re.fullmatch('[a-z][a-z0-9_]{0,80}',value.value):found.add(value.value)
    return sorted(found)

def script():
    require(packet.sha(packet.canonical(Path(base.__file__)))==PREDECESSOR_SHA,'predecessor_changed')
    original=base.source_packet()
    remote=base.REMOTE.rsplit("if __name__=='__main__':",1)[0]
    needle="steps['candidate_content']=probe(lambda:candidate.collect_live(client,inventory))"
    require(remote.count(needle)==1,'predecessor_shape')
    remote=remote.replace(needle,"steps['candidate_content']=probe(lambda:diagnose_candidate(candidate,client,inventory))")
    legacy="""            if steps['candidate_content']['status']=='PASS':
                def old_proof():
                    proof=legacy.collect_live()
                    try:proof.check()
                    finally:proof.close()
                steps['legacy_content']=probe(old_proof)
"""
    require(remote.count(legacy)==1,'predecessor_shape');remote=remote.replace(legacy,'')
    constants='\n'.join(name+'='+repr(value) for name,value in dict(APPROVAL=APPROVAL,ORIGINAL=base.ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=original['files_sha256_lf'],REASONS=base.literal_reasons(),COMPONENT_REASONS=component_reasons(),PHASES=[packet.core.Journal._phase_at(i) for i in range(17)],LABELS=LABELS,KINDS=KINDS,RETURNS=RETURNS).items())
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+constants+'\n'+remote+'\n'+EXTRA).encode()
    require(len(raw)<=131072,'remote_size');compile(raw,'<candidate-diagnostic>','exec');return raw

def remote_definitions():
    env={'__name__':'candidate_diagnostic_fixture'};exec(compile(script(),'<candidate-diagnostic>','exec'),env);env['READBACK_STARTED']=time.monotonic();return env

def wire(raw):
    command=base.wire(raw);suffix=' '+base.APPROVAL
    require(command.endswith(suffix),'predecessor_wire')
    command=command[:-len(suffix)]+' '+APPROVAL
    require(base.old.command_units([command])+2048<=30000,'command_length');return command

def expected_manifest():
    value=base.expected_manifest();raw=script()
    value.update(schema='phase16.candidate-component-diagnostic-packet.v1',approval=APPROVAL,remote_sha256=packet.sha(raw),gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),predecessor_gate_sha256_lf=PREDECESSOR_SHA,component_labels=list(LABELS),evidence_directory=EVIDENCE.as_posix())
    value['reads'][-1]='when no access/coordinator claim exists: authenticated unit/candidate read-only steps; legacy collector omitted'
    value['reads'].append('candidate original read-only collector with in-memory wrappers; fixed step/status/literal reason/error category only')
    value['prohibited'].append('legacy live proof; no widening past candidate diagnosis')
    return value

def validate_receipt(value,rc):
    require(isinstance(value,dict) and value.get('schema')=='phase16.candidate-component-diagnostic.v1' and value.get('approval')==APPROVAL,'diagnostic_binding')
    require(isinstance(value.get('component_steps'),dict) and set(value['component_steps'])<=set(LABELS),'component_shape')
    reasons=set(component_reasons())|{'UNCLASSIFIED_ERROR'}
    for item in value['component_steps'].values():
        require(isinstance(item,dict) and set(item)=={'calls','status','reason','exception_kind','returned_status'},'component_shape')
        require(type(item['calls']) is int and 1<=item['calls']<=65536,'component_count')
        require(item['status'] in ('STARTED','PASS','STOP'),'component_status')
        require(item['returned_status'] is None or item['returned_status'] in RETURNS,'component_return')
        if item['status']=='STOP':require(item['reason'] in reasons and item['exception_kind'] in KINDS and item['returned_status'] is None,'component_reason')
        else:require(item['reason'] is None and item['exception_kind'] is None,'component_reason')
    normalized={k:v for k,v in value.items() if k!='component_steps'}
    normalized.update(schema='phase16.maintenance-readback.v1',approval=base.APPROVAL)
    if value.get('status')=='DIAGNOSTIC_COLLECTED_NOT_ADMITTED':
        require(value['reason']=='bounded_component_observation','diagnostic_reason')
        normalized.update(status='READBACK_COLLECTED_NOT_RECOVERY',reason='bounded_observation')
    else:require(value.get('status')=='UNKNOWN_NO_RETRY','diagnostic_status')
    base.validate_receipt(normalized,rc)
    require(normalized['snapshot'] is None or 'legacy_content' not in normalized['snapshot']['readonly_probes'],'legacy_scope')
    return value

def preview():
    manifest=expected_manifest();raw=script();wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(manifest),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=120,transport_seconds=150,database_open=0,remote_file_writes=0,service_actions=0)

def execute_once(manifest,*,approval,manifest_sha,remote_sha,loader):
    require(packet.core.encoded(manifest)==packet.core.encoded(expected_manifest()),'manifest_changed')
    require(approval==APPROVAL and manifest_sha==packet.core.digest(manifest) and remote_sha==packet.sha(script()),'approval_binding')
    require(not EVIDENCE.exists() and all(not p.is_symlink() for p in (EVIDENCE,*EVIDENCE.parents)),'claim_exists')
    target=loader('spain');require(target.role=='spain' and base.binding_digest(target)==packet.entry.binding.TARGET,'target_binding')
    argv=['C:/Windows/System32/OpenSSH/ssh.exe','-n','-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(target.known_hosts_path),'-o','ConnectTimeout=10','-o','ConnectionAttempts=1','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=6','-i',str(target.key_path),'-p','22',target.target_user+'@'+target.target_host,wire(script())]
    require(base.old.command_units(argv)<=30000,'command_length')
    EVIDENCE.parent.mkdir(parents=True,exist_ok=True);EVIDENCE.mkdir()
    claim=dict(approval=APPROVAL,manifest_sha256=manifest_sha,remote_sha256=remote_sha,attempts=1,claimed_at=datetime.now(timezone.utc).isoformat())
    packet.core.write_new(EVIDENCE/'claim.json',packet.core.encoded(claim))
    result=dict(schema='phase16.candidate-diagnostic-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=base.ssh_environment(),timeout=150,cap=65536,input_bytes=b'',diagnostics=result['transport'])
        require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'transport_incomplete')
        value=validate_receipt(json.loads(out),rc);result['receipt']=value;result['status']=value['status']
    except Exception:result['reason']='TRANSPORT_OR_RECEIPT_UNVERIFIED'
    finally:packet.core.write_new(EVIDENCE/'result.json',packet.core.encoded(result))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--approve');parser.add_argument('--approved-manifest-sha256');parser.add_argument('--approved-remote-sha256');args=parser.parse_args()
    try:
        result=preview()
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(json.loads(MANIFEST.read_bytes()),approval=args.approve,manifest_sha=args.approved_manifest_sha256,remote_sha=args.approved_remote_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','DIAGNOSTIC_COLLECTED_NOT_ADMITTED') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
