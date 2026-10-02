"""Concrete service switch/start/release operations, not host admission or GO.

Call only after separately proven writer inventory, source/runtime/settings and
operator ownership. The journal/lease/fence checks here do not collect those
initial facts. No CLI, SSH, implicit recovery, restore, cleanup or retry.
"""
from functools import wraps
import hashlib
import os
import json
from pathlib import Path
import re
import time
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_maintenance_jobs as jobs
from scripts import phase16_bot_maintenance_linux as linux
from scripts import phase16_bot_maintenance_binding as binding
from scripts import phase16_bot_db_rehearsal as db
from scripts.phase16_bot_maintenance_operations import regular

require=core.require
ACTIONS=('candidate_start','web_start','release')

# Executed only as a bounded direct child. No proxy, redirects, authentication,
# uploads or non-loopback endpoint. Check listener ownership before HTTP.
WEB_HTTP_PROBE = r"""import http.client,os,re,sys
port,pid=int(sys.argv[1]),int(sys.argv[2])
assert 1<=port<=65535 and pid>0
assert os.readlink('/proc/self/ns/net')==os.readlink('/proc/'+str(pid)+'/ns/net')
fds=os.listdir('/proc/'+str(pid)+'/fd');assert len(fds)<=4096
sockets=set()
for fd in fds:
 try:target=os.readlink('/proc/'+str(pid)+'/fd/'+fd)
 except FileNotFoundError:continue
 m=re.fullmatch(r'socket:\[([0-9]+)\]',target)
 if m:sockets.add(m[1])
with open('/proc/net/tcp','rb') as stream:raw=stream.read(1048577)
assert len(raw)<=1048576
listeners=[]
for row in raw.decode('ascii').splitlines()[1:]:
 fields=row.split();assert len(fields)>=10
 address,number=fields[1].split(':')
 if fields[3]=='0A' and int(number,16)==port and address in ('00000000','0100007F'):
  listeners.append(fields[9])
assert listeners and all(inode in sockets for inode in listeners)
connection=http.client.HTTPConnection('127.0.0.1',port,timeout=4)
try:
 connection.request('GET','/login',headers={'Connection':'close'})
 response=connection.getresponse()
 body=response.read(65537)
 assert response.status==200 and response.getheader('Content-Type','').lower().startswith('text/html') and 0<len(body)<=65536
finally:connection.close()
sys.stdout.write('WEB_HTTP_READY')
"""


def bounded_action(method):
    """Bound the whole action, not each command in isolation; never retry late results."""
    @wraps(method)
    def call(self):
        deadline=self.clock()+linux.ACTION_SECONDS[method.__name__]
        original=self.client.run
        def run(argv,seconds):
            remaining=deadline-self.clock()
            require(remaining>0,'service_action_deadline')
            result=original(argv,min(seconds,remaining))
            require(self.clock()<deadline,'service_action_deadline')
            return result
        self.client.run=run
        try:
            value=method(self)
            require(self.clock()<deadline,'service_action_deadline')
            return value
        finally:self.client.run=original
    return call


def candidate_argv(target):
    source=linux.safe_linux_path(target['candidate_source'])
    interpreter=linux.safe_linux_path(target['candidate_interpreter'])
    bootstrap="import runpy,sys; sys.path.insert(0,'"+source+"'); runpy.run_module('app.main',run_name='__main__')"
    return [interpreter,'-I','-B','-u','-c',bootstrap]


# Canonical launch semantics for initial admission and web continuity. Dynamic
# ExecStart timestamps/PID/exit status and our owned Conditions are excluded.
LAUNCH_FIELDS={'WorkingDirectory':'s','User':'s','Group':'s','Environment':'as',
    'EnvironmentFiles':'a(sb)','Type':'s','Restart':'s','KillMode':'s',
    'KillSignal':'i','FinalKillSignal':'i','TimeoutStartUSec':'t','TimeoutStopUSec':'t'}

def launch_fingerprint(client,unit):
    start=client.bus_property(unit,'Service','ExecStart','a(sasbttttuii)')
    require(isinstance(start,list) and len(start)==1 and len(start[0])==10
            and isinstance(start[0][0],str) and isinstance(start[0][1],list)
            and all(isinstance(v,str) for v in start[0][1]) and type(start[0][2]) is bool,'launch_shape')
    value={'ExecStart':start[0][:3]}
    for name,signature in LAUNCH_FIELDS.items():
        value[name]=client.bus_property(unit,'Service',name,signature)
    # Environment may contain secrets: keep only the digest, never this object.
    return core.digest(value)


class CandidateFiles:
    """Recheck the fixed app source only; installed runtime integrity is separate."""
    def __init__(self,target,root,manifest_path):
        self.path=Path(root)/target['candidate_source'].lstrip('/')/'app'
        raw=regular(manifest_path).read_bytes().replace(b'\r\n',b'\n')
        require(hashlib.sha256(raw).hexdigest()=='faac75cf5f2d136344bdfc54fd6cfe3bab8271cc7424ca1050775634860723a4','candidate_manifest')
        self.expected=json.loads(raw)['source']
    def __call__(self):
        found={}
        db._check_path(self.path)
        require(self.path.is_dir(),'candidate_source')
        # Bound directories as well as files, and never traverse an unchecked link.
        pending=[self.path];entries=0
        paths=[]
        while pending:
            directory=pending.pop()
            with os.scandir(directory) as children:
                for child in children:
                    entries+=1;require(entries<=512,'candidate_source')
                    p=db._check_path(Path(child.path))
                    if p.is_dir():pending.append(p)
                    else:paths.append(p)
        for p in paths:
            db._check_path(p)
            require(len(found)<=126,'candidate_source')
            if p.is_dir():continue
            regular(p)
            name=p.relative_to(self.path).as_posix()
            require(name in self.expected and p.stat().st_size==self.expected[name]['bytes'],'candidate_source')
            digest=db.file_sha256(p)
            require(digest==self.expected[name]['sha256'],'candidate_source')
            found[name]=digest
        require(set(found)==set(self.expected),'candidate_source')
        return core.digest(found)


class ServiceOperations:
    def __init__(self,journal,client,fence,supervisor,*,expected_username,
                 source_verifier,web_port,clock=time.monotonic,sleep=time.sleep):
        require(isinstance(expected_username,str) and re.fullmatch('[A-Za-z0-9_]{5,32}',expected_username),'bot_identity')
        require(callable(source_verifier),'source_verifier')
        require(type(web_port) is int and 1<=web_port<=65535,'web_port')
        self.web_port=web_port
        self.journal,self.client,self.fence,self.supervisor=journal,client,fence,supervisor
        require(supervisor.journal is journal and supervisor.client is client and supervisor.fence is fence,'service_binding')
        self.username,self.source_verifier=expected_username,source_verifier
        self.clock,self.sleep=clock,sleep
        self.target=supervisor.context()
        self.dropin=client.root/'etc/systemd/system'/ (core.BOT+'.d')/('60-'+journal.manifest['operation_id']+'-candidate.conf')
        self.receipts=journal.directory.parent/'service-receipts'

    def guard(self,action):
        require(action in ACTIONS,'service_action')
        self.fence._intent(self.journal,action+'_intent')
        target=self.supervisor.context()
        require(target==self.target and jobs.boot_id(self.client)==self.journal.manifest['boot_id'],'service_binding')
        remaining=binding.timestamp(target['ownership_valid_until']).timestamp()-self.supervisor.utc_now()
        require(remaining>=linux.ACTION_SECONDS[action]+linux.RECOVERY_RESERVE,'ownership_window')
        require(self.client.fence_effective(self.fence),'fence_lost')
        require(launch_fingerprint(self.client,core.WEB)==self.target['original_launch_sha256'][core.WEB],'web_launch_changed')
        fingerprint=self.source_verifier()
        require(isinstance(fingerprint,str) and re.fullmatch('[0-9a-f]{64}',fingerprint),'candidate_source')
        return fingerprint

    def identity(self,unit):
        value=self.client.show(unit)
        require(value['ActiveState']=='active' and value['SubState']=='running' and value['Result']=='success'
                and value['MainPID'].isdigit() and int(value['MainPID'])>0
                and re.fullmatch('[0-9a-f]{32}',value['InvocationID'])
                and value['Type']==('notify' if unit==core.BOT else 'simple'),'service_not_running')
        return {key:value[key] for key in ('Id','InvocationID','MainPID','Type','NRestarts')}

    def candidate_loaded(self):
        require(regular(self.dropin).read_bytes()==linux.candidate_dropin(self.target).encode(),'candidate_dropin')
        value=self.client.show(core.BOT)
        path='/'+self.dropin.relative_to(self.client.root).as_posix()
        require(path in value['DropInPaths'].split(),'candidate_not_loaded')
        command=self.client.bus_property(core.BOT,'Service','ExecStart','a(sasbttttuii)')
        argv=candidate_argv(self.target)
        require(isinstance(command,list) and len(command)==1 and len(command[0])==10
                and command[0][0]==argv[0] and command[0][1]==argv and command[0][2] is False,'candidate_command')
        expected={'WorkingDirectory':str(Path(self.target['old_source']).parent).replace('\\','/'),
                  'User':self.target['service_identity'][core.BOT]['user'],
                  'Group':self.target['service_identity'][core.BOT]['group']}
        for key,wanted in expected.items():
            require(self.client.bus_property(core.BOT,'Service',key,'s')==wanted,'candidate_identity')

    def admission(self,identity):
        boot=self.journal.manifest['boot_id'].replace('-','')
        raw=self.client.run(['journalctl','--no-pager','--output=json','--lines=64',
            '--output-fields=_SYSTEMD_UNIT,_SYSTEMD_INVOCATION_ID,_BOOT_ID,_PID,MESSAGE',
            '_SYSTEMD_UNIT='+core.BOT,'_SYSTEMD_INVOCATION_ID='+identity['InvocationID'],
            '_BOOT_ID='+boot,'_PID='+identity['MainPID']],5)
        require(len(raw)<=65536,'admission_output')
        try:records=[json.loads(line) for line in raw.splitlines() if line]
        except (ValueError,UnicodeError):raise core.Stop('admission_encoding') from None
        require(linux.admission_receipt(records,invocation=identity['InvocationID'],boot=boot,
            pid=int(identity['MainPID']),expected_username=self.username),'admission_missing')
        require(self.identity(core.BOT)==identity,'candidate_changed')

    def web_ready(self,identity):
        raw=self.client.run(['/usr/bin/python3','-I','-S','-B','-c',WEB_HTTP_PROBE,
                             str(self.web_port),identity['MainPID']],5)
        require(raw==b'WEB_HTTP_READY' and self.identity(core.WEB)==identity,'web_readiness')

    def predecessor(self,action):
        if action!='candidate_start':
            return self.receipt('candidate_start' if action=='web_start' else 'web_start')
        data=jobs.load_signed(self.journal.directory.parent/'receipts/migrate.json')
        intent=next((e for e in self.journal.events if e['phase']=='migrate_intent'),None)
        require(intent is not None and data.get('schema')=='phase16.maintenance-data.v1'
                and data.get('action')=='migrate' and data.get('binding')==self.journal.binding
                and data.get('intent_sha256')==intent['sha256'],'migration_receipt')
        paths=jobs.job_paths(self.journal,'migrate')
        result=jobs.load_signed(paths['result']);complete=jobs.load_signed(paths['complete'])
        require(result.get('data_receipt_sha256')==data['sha256'] and result.get('result')=='DATA_VERIFIED'
                and result.get('boot_id')==self.journal.manifest['boot_id']
                and complete.get('result_sha256')==result['sha256']
                and complete.get('invocation')==result.get('invocation')
                and complete.get('claim_sha256')==result.get('claim_sha256'),'migration_receipt')
        return data

    def save(self,action,details):
        self.receipts.mkdir(mode=0o700,exist_ok=True)
        previous=self.predecessor(action)
        jobs.write_signed(self.receipts/(action+'.json'),dict(schema='phase16.service-operation.v1',action=action,
            binding=self.journal.binding,intent_sha256=self.journal.events[-1]['sha256'],
            predecessor_sha256=previous['sha256'],details=details))

    def receipt(self,action):
        value=jobs.load_signed(self.receipts/(action+'.json'))
        intent=next((e for e in self.journal.events if e['phase']==action+'_intent'),None)
        require(set(value)=={'schema','action','binding','intent_sha256','predecessor_sha256','details','sha256'}
            and intent is not None and value['schema']=='phase16.service-operation.v1'
            and value['action']==action and value['binding']==self.journal.binding
            and value['intent_sha256']==intent['sha256'],'service_receipt')
        require(value['predecessor_sha256']==self.predecessor(action)['sha256'],'service_receipt_chain')
        return value

    @bounded_action
    def candidate_start(self):
        source=self.guard('candidate_start')
        self.predecessor('candidate_start')
        jobs.check_stop_witness(self.journal,self.client,self.fence)
        db._check_path(self.dropin)
        self.dropin.parent.mkdir(parents=True,exist_ok=True)
        core.write_new(self.dropin,linux.candidate_dropin(self.target).encode(),0o644)
        self.client.control(['systemctl','daemon-reload'],15)
        require(self.client.fence_effective(self.fence),'fence_lost')
        self.candidate_loaded()
        self.fence.start(core.BOT,self.journal)
        identity=self.identity(core.BOT)
        self.candidate_loaded();self.admission(identity)
        require(self.guard('candidate_start')==source,'candidate_source_changed')
        self.save('candidate_start',dict(identity=identity,source_sha256=source,admission='PASS',ready='SYSTEMD_NOTIFY_ACTIVE'))

    @bounded_action
    def web_start(self):
        source=self.guard('web_start')
        receipt=self.receipt('candidate_start')['details']
        require(source==receipt['source_sha256'],'candidate_source_changed')
        candidate=receipt['identity']
        require(self.identity(core.BOT)==candidate,'candidate_changed')
        self.candidate_loaded();self.admission(candidate)
        self.client.stopped(core.WEB)
        self.fence.start(core.WEB,self.journal)
        identity=self.identity(core.WEB)
        # Observe process continuity, then separately check the owned HTTP listener.
        for unused in range(3):
            self.sleep(1)
            require(self.identity(core.WEB)==identity and self.identity(core.BOT)==candidate,'service_changed')
        self.web_ready(identity)
        require(self.guard('web_start')==source,'candidate_source_changed')
        self.save('web_start',dict(identity=identity,candidate_identity=candidate,process_observation_seconds=3,
                                  application_health='OWNED_LOOPBACK_LOGIN_HTTP_200'))

    @bounded_action
    def release(self):
        source=self.guard('release');self.candidate_loaded()
        require(source==self.receipt('candidate_start')['details']['source_sha256'],'candidate_source_changed')
        bot=self.receipt('candidate_start')['details']['identity']
        web=self.receipt('web_start')['details']['identity']
        require(self.identity(core.BOT)==bot and self.identity(core.WEB)==web,'service_changed')
        self.admission(bot);self.web_ready(web)
        self.fence.remove(self.journal)
        for unit in linux.UNITS:
            require(not self.fence.dropin(unit).exists() and not self.fence.permit(unit).exists(),'fence_release')
            loaded=self.client.show(unit)['DropInPaths'].split()
            require('/'+self.fence.dropin(unit).relative_to(self.client.root).as_posix() not in loaded,'fence_release')
        require(self.identity(core.BOT)==bot and self.identity(core.WEB)==web,'service_changed')
        self.candidate_loaded()
        require(launch_fingerprint(self.client,core.WEB)==self.target['original_launch_sha256'][core.WEB],'web_launch_changed')
        self.save('release',dict(candidate_identity=bot,web_identity=web,owned_fence_removed=True,
                                application_acceptance='NOT_ESTABLISHED'))

    def verify(self,action):
        value=self.receipt(action)
        if action=='candidate_start':
            require(self.identity(core.BOT)==value['details']['identity'],'candidate_changed')
            require(self.client.fence_effective(self.fence),'fence_lost')
        elif action=='web_start':
            require(self.identity(core.WEB)==value['details']['identity'],'web_changed')
            require(self.client.fence_effective(self.fence),'fence_lost')
        elif action=='release':
            require(self.identity(core.BOT)==value['details']['candidate_identity']
                    and self.identity(core.WEB)==value['details']['web_identity'],'service_changed')
            self.candidate_loaded()
            require(not any(self.fence.dropin(u).exists() or self.fence.permit(u).exists() for u in linux.UNITS),'fence_release')
        else:raise core.Stop('service_action')
        return True
