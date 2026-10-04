"""Separate v2 parent repair: private directory predicate, hashed sibling audit.

Preserve consumed v1 gate/core/manifest. No egress unless exact new approval.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_ancestor_repair_gate as v1
base=v1.base
packet=v1.packet
APPROVAL='PHASE16_CANDIDATE_ANCESTOR_REPAIR_20261004_002'
OP='phase16-ancestor-traverse-20261004-002'
MANIFEST=ROOT/'research/amn2/phase16-bot-ancestor-repair-v2-manifest-2026-10-04.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-ancestor-repair-v2-20261004/execution-001')
TRIGGER=ROOT/'research/amn2/phase16-bot-ancestor-repair-execution-001-2026-10-04.json'
TRIGGER_SHA='104ed3975d64495396374b307918232514d5109a986eef9fea0fd156e036e6d4'
FROZEN={
 'scripts/phase16_bot_ancestor_repair_gate.py':'d19311db909d801d9f09fab9f45fa178d12359fdd6b1d3870ddff8af35ae5e51',
 'scripts/phase16_bot_ancestor_repair.py':'c6f5adeca61cf96951247bd416b3e2deaa7f773bab8a51b38116034f465abc88',
 'research/amn2/phase16-bot-ancestor-repair-manifest-2026-10-03.json':'e1f014f0a655aa9dde3d74eec1f6e03197d71608a25709ee2e89de3d20d1be7e'}
REMOTE_SECONDS=180
TRANSPORT_SECONDS=210

def require(value,reason):
    if not value:raise ValueError(reason)

def trigger():
    require(packet.sha(packet.canonical(TRIGGER))==TRIGGER_SHA,'trigger_changed')
    result=json.loads(TRIGGER.read_bytes())
    r=result['local_result']['receipt'];v1.validate_receipt(r,result['local_result']['transport']['returncode'])
    require(result['approval_consumed'] is True and r['status']=='STOP_NO_REMOTE_CHANGE' and r['reason']=='sibling_inventory' and r['operation'] is None and r['audit_creation_attempted'] is False,'trigger_state')
    return result

def materialized_core():
    for path,digest in FROZEN.items():require(packet.sha(packet.canonical(ROOT/path))==digest,'predecessor_changed')
    core=packet.canonical(Path(v1.repair.__file__)).decode()
    patches=(
        ('import json\nimport stat','import hashlib\nimport json\nimport stat'),
        ("OP='"+v1.repair.OP+"'","OP='"+OP+"'"),
        (' and set(names)<=set(KNOWN)',''),
        ('siblings={n:list(v) for n,v in session.siblings.items()}',"siblings={hashlib.sha256(n.encode('utf-8','surrogatepass')).hexdigest():list(v) for n,v in session.siblings.items()}"))
    for old,new in patches:
        require(core.count(old)==1,'core_shape');core=core.replace(old,new,1)
    compile(core,'<private-sibling-repair-core>','exec');return core

def script():
    trigger();core=materialized_core();v1.script()  # authenticate inherited helper/code closure, never execute main
    original=base.source_packet()
    constants=dict(APPROVAL=APPROVAL,ORIGINAL=base.ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=original['files_sha256_lf'],REASONS=v1.reasons(),COMPONENT_REASONS=v1.reasons(),KINDS=v1.diagnostic.KINDS,RETURNS=v1.diagnostic.RETURNS,WITNESS_FACTS=v1.witness(),WITNESS_SHA=v1.WITNESS_SHA,REMOTE_SECONDS=REMOTE_SECONDS)
    prefix=base.REMOTE.split('def collect():',1)[0]
    helpers=v1.diagnostic.EXTRA.split('_readback_main=main',1)[0]
    load='import types\nrepair=types.ModuleType("phase16_frozen_ancestor_repair_v2")\nexec(compile('+repr(core)+',"<private-sibling-repair-core>","exec"),repair.__dict__)\n'
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+'\n'.join(k+'='+repr(v) for k,v in constants.items())+'\n'+load+prefix+'\n'+helpers+'\n'+v1.EXTRA).encode()
    require(len(raw)<=131072,'remote_size');compile(raw,'<ancestor-repair-v2>','exec');return raw

def remote_definitions():
    raw=script();env={'__name__':'repair_v2_fixture'};exec(compile(raw,'<ancestor-repair-v2>','exec'),env);env['READBACK_STARTED']=time.monotonic();env['REMOTE_SELF_SHA']=packet.sha(raw);return env

def wire(raw):
    command=v1.wire(raw);suffix=' '+v1.APPROVAL;require(command.endswith(suffix),'wire_shape')
    command=command[:-len(suffix)]+' '+APPROVAL;require(base.old.command_units([command])+2048<=30000,'command_length');return command

def expected_manifest():
    value=v1.expected_manifest()
    value.update(schema='phase16.ancestor-repair-packet.v2',approval=APPROVAL,remote_sha256=packet.sha(script()),gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),repair_core_materialized_sha256=packet.sha(materialized_core().encode()),frozen_predecessor_artifacts_sha256_lf=FROZEN,trigger_execution_sha256_lf=TRIGGER_SHA,evidence_directory=EVIDENCE.as_posix())
    value['scope'].update(audit_directory='/var/lib/amn2-spain/phase16-maintenance/'+OP,audit_records=['stage-access.'+OP+'.'+k+'.json' for k in ('claim','plan','intent','result')])
    value['reads'][1]='exact four-parent/retained-stage witness; metadata only of every direct child directory, max16; never sibling contents'
    value['sibling_policy']='All direct children must be root:root0700 directories, no links/xattrs; fixed retained stage present; unknown names stay in memory, only SHA256 keys in private audit. Names are not authorization.'
    value['limits'].update(remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS)
    return value

def validate_receipt(value,rc):
    require(isinstance(value,dict) and value.get('approval')==APPROVAL,'receipt_approval')
    # Reuse frozen validation semantics without rebinding any predecessor globals.
    v1.validate_receipt({**value,'approval':v1.APPROVAL},rc)
    return value

def preview():
    m=expected_manifest();raw=script();wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(m),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=REMOTE_SECONDS,transport_seconds=TRANSPORT_SECONDS,permission_syscalls_max=2)

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
    result=dict(schema='phase16.ancestor-repair-v2-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=base.ssh_environment(),timeout=TRANSPORT_SECONDS,cap=65536,input_bytes=b'',diagnostics=result['transport'])
        require(result['transport'].get('stdin_complete') is True and result['transport'].get('output_complete') is True,'transport_incomplete')
        receipt=validate_receipt(json.loads(out),rc);result['receipt']=receipt;result['status']=receipt['status']
    except Exception:result['reason']='TRANSPORT_OR_RECEIPT_UNVERIFIED'
    finally:packet.core.write_new(EVIDENCE/'result.json',packet.core.encoded(result))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--approve');p.add_argument('--approved-manifest-sha256');p.add_argument('--approved-remote-sha256');args=p.parse_args()
    try:
        result=preview()
        if args.execute:
            from scripts.phase13_bot_web_migration_fresh_inputs import load_fixed_role_binding
            result=execute_once(json.loads(MANIFEST.read_bytes()),approval=args.approve,manifest_sha=args.approved_manifest_sha256,remote_sha=args.approved_remote_sha256,loader=load_fixed_role_binding)
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','PARENT_REPAIRED_CANDIDATE_CHECKED') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
