"""One proposed metadata read of fixed retained-stage ancestors; default preview.

No candidate replay, content scan, DB, app, permission apply, service or writes.
Existing ancestor denial stays enforced; this packet only supplies repair facts.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts import phase16_bot_maintenance_readback as base
packet=base.packet
APPROVAL='PHASE16_CANDIDATE_ANCESTOR_FACTS_20261003_001'
PREDECESSOR_SHA='b0e35c25317b94cafa2ff2b1aa6af15336b4e7e9ec57ac8997d43b600029bb0b'
MANIFEST=ROOT/'research/amn2/phase16-bot-ancestor-readback-manifest-2026-10-03.json'
EVIDENCE=Path('C:/Users/SooL/Documents/VPS-OPS-LAB/worktrees/phase16-ancestor-facts-20261003/execution-001')
ANCESTORS=packet.entry.access.ANCESTOR_PATHS
BOUNDARIES=('platform','boot','code_binding','unit_states','identity','ancestor_metadata','final_continuity')
FIELDS=('mode','uid','gid','device','inode','mtime_ns','ctime_ns','directory','metadata_safe','acl_clear','service_traverse')
EXTRA=r"""
def ancestor_row(access,meta,names,identity):
    directory=stat.S_ISDIR(meta.st_mode)
    safe=directory and meta.st_uid==0 and not meta.st_mode&0o7022 and not getattr(meta,'st_file_attributes',0)&0x400
    return dict(mode=stat.S_IMODE(meta.st_mode),uid=meta.st_uid,gid=meta.st_gid,device=meta.st_dev,inode=meta.st_ino,mtime_ns=meta.st_mtime_ns,ctime_ns=meta.st_ctime_ns,directory=directory,metadata_safe=bool(safe),acl_clear=type(names) in (list,tuple) and not names,service_traverse=access._allows(meta,identity,1))

def ancestor_facts(access,tree,identity):
    values=tree.ancestors()
    if tuple(item[0] for item in values)!=ANCESTORS:raise ValueError('ancestor_inventory')
    rows={path:ancestor_row(access,meta,names,identity) for path,meta,names in values}
    stage=ancestor_row(access,tree.info('.'),tree.acl_names('.'),identity)
    tree.stable()
    return dict(ancestors=rows,stage_root=stage,ancestor_ready=all(row['metadata_safe'] and row['acl_clear'] and row['service_traverse'] for row in rows.values()))

def collect():
    global BOUNDARY
    BOUNDARY='boot'
    if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('boot_changed')
    BOUNDARY='code_binding';_phase16_import_root(DIRECTORY+'/code',PINS,ORIGINAL)
    from scripts import phase16_bot_maintenance_linux as linux
    from scripts import phase16_bot_candidate_admission as candidate
    BOUNDARY='unit_states';before=unit_states()
    if any(item['state']!='OBSERVED' for item in before.values()):raise ValueError('unit_output')
    client=linux.SystemdClient(linux.BoundedCommand(maximum=65536))
    def properties():return {u:{k:client.bus_property(u,'Service',k,s) for k,s in candidate.IDENTITY_FIELDS.items()} for u in UNITS[:2]}
    BOUNDARY='identity';original=properties();reader=candidate.settings.RootSettingsReader()
    identity=candidate.local_identity(reader('/etc/passwd'),reader('/etc/group'),original[UNITS[0]])
    if original[UNITS[0]]!=original[UNITS[1]] or set(os.getgrouplist('amn2-spain',identity.gid))!={identity.gid}:raise ValueError('ancestor_identity_changed')
    BOUNDARY='ancestor_metadata'
    with candidate.access.UnixStageReader() as tree:
        facts=ancestor_facts(candidate.access,tree,identity)
        BOUNDARY='final_continuity'
        after=unit_states()
        if properties()!=original or set(os.getgrouplist('amn2-spain',identity.gid))!={identity.gid}:raise ValueError('ancestor_identity_changed')
        if before!=after:raise ValueError('ancestor_unit_changed')
        reader.stable();tree.stable()
    return dict(**facts,service_identity=dict(uid=identity.uid,gid=identity.gid,supplementary_gids=list(identity.supplementary_gids)),units_before=before,units_after=after)

_readback_main=main
def main(approval):
    result=_readback_main(approval)
    result.update(schema='phase16.ancestor-facts.v1',permission_actions=0)
    if result['status']=='READBACK_COLLECTED_NOT_RECOVERY':result.update(status='ANCESTOR_FACTS_COLLECTED_NOT_REPAIRED',reason='bounded_ancestor_observation')
    return result
if __name__=='__main__':
    result=main(sys.argv[1] if len(sys.argv)==2 else '')
    print(json.dumps(result,sort_keys=True,separators=(',',':')),flush=True)
    raise SystemExit(0 if result['status']=='ANCESTOR_FACTS_COLLECTED_NOT_REPAIRED' else 3)
"""
def require(value,reason):
    if not value:raise ValueError(reason)

def reasons():return sorted(set(base.literal_reasons())|{'ancestor_inventory','ancestor_identity_changed','ancestor_unit_changed'})

def script():
    require(packet.sha(packet.canonical(Path(base.__file__)))==PREDECESSOR_SHA,'predecessor_changed')
    original=base.source_packet()
    prefix=base.REMOTE.split('def collect():',1)[0]
    main=base.REMOTE.split('def main(approval):',1)[1].rsplit("if __name__=='__main__':",1)[0]
    require(main.count('READBACK_STARTED+120-')==1,'predecessor_shape');main=main.replace('READBACK_STARTED+120-','READBACK_STARTED+30-')
    constants='\n'.join(name+'='+repr(value) for name,value in dict(APPROVAL=APPROVAL,ORIGINAL=base.ORIGINAL,TARGET=packet.entry.binding.TARGET,BOOT=packet.entry.BOOT,PINS=original['files_sha256_lf'],REASONS=reasons(),ANCESTORS=ANCESTORS).items())
    # Override inherited fixed boundary names after its prefix; original collect omitted.
    remote=prefix+'\nBOUNDARIES='+repr(BOUNDARIES)+'\ndef main(approval):'+main+'\n'+EXTRA
    raw=(packet.storage.IMPORT_BOOTSTRAP+'\n'+constants+'\n'+remote).encode();require(len(raw)<=131072,'remote_size');compile(raw,'<ancestor-facts>','exec');return raw

def remote_definitions():
    env={'__name__':'ancestor_fixture'};exec(compile(script(),'<ancestor-facts>','exec'),env);env['READBACK_STARTED']=time.monotonic();return env

def platform_fixture():
    from unittest.mock import patch
    env=remote_definitions()
    with patch.object(env['sys'],'platform','win32'):return env['main'](APPROVAL)

def wire(raw):
    command=base.wire(raw);suffix=' '+base.APPROVAL;require(command.endswith(suffix),'predecessor_wire')
    command=command[:-len(suffix)]+' '+APPROVAL;require(base.old.command_units([command])+2048<=30000,'command_length');return command

def expected_manifest():
    value=base.expected_manifest();value.update(schema='phase16.ancestor-facts-packet.v1',approval=APPROVAL,remote_sha256=packet.sha(script()),gate_sha256_lf=packet.sha(packet.canonical(Path(__file__))),predecessor_gate_sha256_lf=PREDECESSOR_SHA,evidence_directory=EVIDENCE.as_posix(),ancestor_paths=list(ANCESTORS))
    value['limits'].update(remote_seconds=30,transport_seconds=45)
    value['reads']=['fixed boot and original authenticated code only','bot/web/coordinator allowlisted unit properties; validated local service identity/NSS','metadata and xattr-clear boolean of exactly four ancestors and retained-stage root; no child enumeration or content read']
    value['prohibited']+=['candidate/legacy collector replay','runtime/source/payload scan','ancestor mutation or proposed permission grant']
    return value

def validate_receipt(value,rc):
    env=remote_definitions()
    fields={'schema','approval','original_manifest_sha256','target_binding_sha256','status','reason','snapshot','failure_boundary','remote_file_writes','database_open','service_actions','app_imports','activation','replay_allowed','permission_actions'}
    require(isinstance(value,dict) and set(value)==fields,'receipt_shape')
    require(value['schema']=='phase16.ancestor-facts.v1' and value['approval']==APPROVAL and value['original_manifest_sha256']==base.ORIGINAL and value['target_binding_sha256']==packet.entry.binding.TARGET,'receipt_binding')
    for key in ('remote_file_writes','database_open','service_actions','app_imports','permission_actions'):require(type(value[key]) is int and value[key]==0,'receipt_scope')
    require(value['activation'] is False and value['replay_allowed'] is False,'receipt_scope')
    if value['status']=='UNKNOWN_NO_RETRY':
        require(rc==3 and value['snapshot'] is None and value['reason'] in set(reasons())|{'platform_or_precondition'} and value['failure_boundary'] in BOUNDARIES,'receipt_unknown');return value
    require(rc==0 and value['status']=='ANCESTOR_FACTS_COLLECTED_NOT_REPAIRED' and value['reason']=='bounded_ancestor_observation' and value['failure_boundary'] is None,'receipt_status')
    s=value['snapshot'];require(isinstance(s,dict) and set(s)=={'ancestors','stage_root','ancestor_ready','service_identity','units_before','units_after'},'snapshot_shape')
    identity=s['service_identity'];require(isinstance(identity,dict) and set(identity)=={'uid','gid','supplementary_gids'},'identity_shape')
    for key in ('uid','gid'):require(type(identity[key]) is int and 0<identity[key]<2**31,'identity_shape')
    require(type(identity['supplementary_gids']) is list and all(type(g) is int for g in identity['supplementary_gids']) and identity['supplementary_gids']==[identity['gid']],'identity_shape')
    require(isinstance(s['ancestors'],dict) and set(s['ancestors'])==set(ANCESTORS),'ancestor_shape')
    for row in (*s['ancestors'].values(),s['stage_root']):
        require(isinstance(row,dict) and set(row)==set(FIELDS),'ancestor_shape')
        for key in FIELDS[:7]:require(type(row[key]) is int and 0<=row[key]<2**64,'ancestor_number')
        require(row['mode']<=0o7777,'ancestor_mode')
        for key in FIELDS[7:]:require(type(row[key]) is bool,'ancestor_boolean')
        require(row['metadata_safe']==(row['directory'] and row['uid']==0 and not row['mode']&0o7022),'ancestor_metadata')
        bits=row['mode']>>6 if row['uid']==identity['uid'] else row['mode']>>3 if row['gid']==identity['gid'] else row['mode']
        require(row['service_traverse']==(bits&1==1),'ancestor_access')
    require(type(s['ancestor_ready']) is bool and s['ancestor_ready']==all(r['metadata_safe'] and r['acl_clear'] and r['service_traverse'] for r in s['ancestors'].values()),'ancestor_ready')
    for field in ('units_before','units_after'):
        require(isinstance(s[field],dict) and set(s[field])==set(env['UNITS']),'receipt_units')
        for unit,item in s[field].items():
            require(isinstance(item,dict) and set(item)=={'state','properties'} and item['state']=='OBSERVED' and isinstance(item['properties'],dict) and set(item['properties'])==set(env['FIELDS']),'receipt_units')
            require(all(isinstance(v,str) and re.fullmatch('[A-Za-z0-9_.:@/-]{0,128}',v) for v in item['properties'].values()) and item['properties']['Id'] in ('',unit),'receipt_units')
    require(s['units_before']==s['units_after'],'receipt_unit_changed');return value

def preview():
    manifest=expected_manifest();raw=script();wire(raw)
    return dict(status='OFFLINE_READY_NOT_EXECUTED',approval=APPROVAL,manifest_sha256=packet.core.digest(manifest),remote_sha256=packet.sha(raw),ssh_attempts=0,remote_seconds=30,transport_seconds=45,database_open=0,remote_file_writes=0,permission_actions=0,service_actions=0)

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
    result=dict(schema='phase16.ancestor-facts-local.v1',status='UNKNOWN_NO_RETRY',claim=claim,transport={},receipt=None,replay_allowed=False)
    try:
        rc,out=packet.transport.run_transport(argv,cwd=EVIDENCE,env=base.ssh_environment(),timeout=45,cap=65536,input_bytes=b'',diagnostics=result['transport'])
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
        print(json.dumps(result,indent=2));return 0 if result['status'] in ('OFFLINE_READY_NOT_EXECUTED','ANCESTOR_FACTS_COLLECTED_NOT_REPAIRED') else 3
    except Exception:print('{"status":"LOCAL_STOP"}');return 2
if __name__=='__main__':raise SystemExit(main())
