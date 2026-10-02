"""One bounded read-only maintenance fact collection. Never an admission/activation."""
import contextlib
from datetime import datetime,timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import threading
import time
import types
from scripts.phase16_bot_maintenance_linux import BoundedCommand
from scripts.phase16_bot_service_operations import LAUNCH_FIELDS, launch_fingerprint

APPROVAL='PHASE16_MAINTENANCE_FACTS_20261002_001'
TARGET='87b33ab0769b0f98670289e66e230407d82caebc05c6e459baf564564789d0c6'
UNITS=('amn2-spain-bot.service','amn2-spain-web.service')
OLD='/opt/amn2-spain/runtime/source'
CANDIDATE='/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001/source'
DATABASE='/var/lib/amn2-spain/amn2.sqlite3'
SECONDS=45
KEYS={'VPS_APPLY_ENABLED','AWG3_BOOTSTRAP_ENABLED','TELEGRAM_ADMISSION_TIMEOUT_SECONDS',
      'TELEGRAM_EXPECTED_BOT_USERNAME','DEFAULT_VPN_NETWORK_CIDR','DATABASE_PATH','WEB_ADMIN_PORT'}
FIELDS=('Id','LoadState','ActiveState','SubState','MainPID','InvocationID','User','Group',
    'Type','Restart','KillMode','KillSignal','FinalKillSignal','TimeoutStartUSec','TimeoutStopUSec',
    'NeedDaemonReload','UnitFileState','WorkingDirectory','NRestarts','ControlGroup')
REASONS={'read_contract','read_limit','read_changed','property_contract','command_contract',
    'inventory_cap','unit_changed','source_changed','platform_contract','deadline','collection_error'}
class Stop(RuntimeError):pass
def require(value,reason):
    if not value:raise Stop(reason)
def digest(value):return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')).hexdigest()
core=types.SimpleNamespace(digest=digest)

def read(path,limit=262144,*,proc=False):
    p=Path(path)
    if not proc:
        for q in (p,*p.parents):require(not q.is_symlink(),'read_contract')
    flags=os.O_RDONLY|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)
    fd=os.open(p,flags)
    try:
        before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size<=limit,'read_contract')
        if not proc:require(before.st_nlink==1 and before.st_uid==0 and not before.st_mode&0o022,'read_contract')
        data=bytearray()
        while len(data)<=limit:
            block=os.read(fd,min(65536,limit+1-len(data)))
            if not block:break
            data.extend(block)
        require(len(data)<=limit,'read_limit')
        after=os.fstat(fd)
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'read_changed')
        return bytes(data)
    finally:os.close(fd)


def selected(values):
    """No arbitrary values, keys, paths or exception text can reach the receipt."""
    answer={}
    for key in KEYS:
        found=[v for k,v in values if k.upper()==key]
        if not found:answer[key]={'status':'ABSENT'};continue
        if len(found)!=1:answer[key]={'status':'AMBIGUOUS'};continue
        value=found[0].strip();safe=None
        if key in ('VPS_APPLY_ENABLED','AWG3_BOOTSTRAP_ENABLED'):
            if value.lower() in ('1','on','t','true','y','yes'):safe=True
            elif value.lower() in ('0','off','f','false','n','no'):safe=False
        elif key in ('TELEGRAM_ADMISSION_TIMEOUT_SECONDS','WEB_ADMIN_PORT'):
            if re.fullmatch('[0-9]{1,5}',value):
                number=int(value);maximum=120 if key.startswith('TELEGRAM') else 65535
                if 1<=number<=maximum:safe=number
        elif key=='DATABASE_PATH':safe=value==DATABASE
        elif key=='TELEGRAM_EXPECTED_BOT_USERNAME':
            if re.fullmatch('@?[A-Za-z0-9_]{5,32}',value):safe=value.lstrip('@')
        else:
            try:
                network=ipaddress.ip_network(value,strict=True)
                if network.version==4:safe=str(network)
            except ValueError:pass
        answer[key]={'status':'VALID','value':safe} if safe is not None else {'status':'UNSUPPORTED'}
    return answer


def env_pairs(raw):
    require(len(raw)<=262144,'read_limit')
    return [part.decode('utf-8').split('=',1) for part in raw.split(b'\0') if b'=' in part]


def literal_dotenv(raw):
    # Deliberately limited. Multiline, expansion and escapes cannot be guessed.
    values=[]
    for line in raw.decode('utf-8').splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        match=re.fullmatch(r'(?:export +)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)',line)
        if not match:return None
        key,value=match.groups()
        if any(x in value for x in ('\\','$','`')):return None
        if value.startswith(('"',"'")):
            if len(value)<2 or value[-1]!=value[0] or value[0] in value[1:-1]:return None
            value=value[1:-1]
        elif any(x.isspace() for x in value) or '"' in value or "'" in value:return None
        values.append((key,value))
    return selected(values)


class Collector:
    def __init__(self,run=None,clock=time.monotonic):
        self.run_command=run or BoundedCommand(maximum=1048576)
        self.clock=clock;self.deadline=clock()+SECONDS
    def run(self,argv,seconds=5):
        show=len(argv)==5 and argv[:4]==['systemctl','show','--no-pager','--property='+','.join(FIELDS)] and argv[-1] in UNITS
        listing=argv==['systemctl','list-unit-files','--type=service,timer,socket','--no-legend','--no-pager','--plain']
        paths=['/org/freedesktop/systemd1/unit/'+''.join(c if c.isascii() and c.isalnum() else '_'+format(ord(c),'02x') for c in u) for u in UNITS]
        bus=len(argv)==7 and argv[:4]==['busctl','--json=short','get-property','org.freedesktop.systemd1'] and argv[4] in paths and argv[5]=='org.freedesktop.systemd1.Service' and argv[6] in set(LAUNCH_FIELDS)|{'ExecStart'}
        require(show or listing or bus,'command_contract')
        remaining=self.deadline-self.clock();require(remaining>0,'deadline')
        result=self.run_command(argv,min(seconds,remaining))
        require(self.clock()<self.deadline,'deadline');return result
    def bus_property(self,unit,interface,name,signature):
        require(unit in UNITS and interface=='Service','property_contract')
        code=''.join(c if c.isascii() and c.isalnum() else '_'+format(ord(c),'02x') for c in unit)
        raw=self.run(['busctl','--json=short','get-property','org.freedesktop.systemd1',
            '/org/freedesktop/systemd1/unit/'+code,'org.freedesktop.systemd1.Service',name])
        value=json.loads(raw)
        require(set(value)=={'type','data'} and value['type']==signature,'property_contract')
        return value['data']
    def unit(self,unit):
        raw=self.run(['systemctl','show','--no-pager','--property='+','.join(FIELDS),unit])
        pairs=[line.split('=',1) for line in raw.decode().splitlines()]
        require(all(len(v)==2 for v in pairs),'property_contract');v=dict(pairs)
        require(len(pairs)==len(v) and set(v)==set(FIELDS) and v['Id']==unit,'property_contract')
        require(v['MainPID'].isdigit() and int(v['MainPID'])>0 and re.fullmatch('[a-f0-9]{32}',v['InvocationID']),'property_contract')
        # All exported property values are enumerations/numbers or fixed expected paths.
        out={k:v[k] for k in FIELDS if k not in ('WorkingDirectory','ControlGroup','User','Group')}
        for key,value in out.items():require(re.fullmatch('[A-Za-z0-9_. /-]{0,128}',value),'property_contract')
        for key in ('User','Group'):
            require(re.fullmatch('[A-Za-z_][A-Za-z0-9_-]{0,63}[$]?|',v[key]),'property_contract');out[key]=v[key]
        out['cwd_expected']=v['WorkingDirectory']==OLD
        out['cgroup_expected']=v['ControlGroup']=='/system.slice/'+unit
        return out
    def process_environment(self,pid):return selected(env_pairs(read('/proc/'+pid+'/environ',proc=True)))
    def inventory(self):
        raw=self.run(['systemctl','list-unit-files','--type=service,timer,socket','--no-legend','--no-pager','--plain'],8)
        names=[line.split()[0] for line in raw.decode().splitlines() if line.strip()]
        require(len(names)<=1024 and len(set(names))==len(names),'inventory_cap')
        require(all(re.fullmatch(r'[A-Za-z0-9_.:@\\-]+\.(service|timer|socket)',n) for n in names),'property_contract')
        # Static unit-file inventory, not proof that arbitrary wrappers cannot write.
        matches=[n for n in names if 'amn2' in n.lower() or 'phase16' in n.lower()]
        require(len(matches)<=64,'inventory_cap')
        cron={};count=0
        roots=[Path('/etc/crontab'),Path('/etc/cron.d'),Path('/var/spool/cron/crontabs')]
        for root in roots:
            if not root.exists():continue
            paths=[root] if root.is_file() else list(root.iterdir())
            require(len(paths)<=256,'inventory_cap')
            for path in paths:
                if path.name.startswith('.'):continue
                count+=1;require(count<=256,'inventory_cap')
                blob=read(path)
                cron[hashlib.sha256(str(path).encode()).hexdigest()]=dict(sha256=hashlib.sha256(blob).hexdigest(),
                    amn2_reference=any(s in blob.lower() for s in (b'amn2',b'phase16')))
        processes=[];exited=0;count=0
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():continue
            count+=1;require(count<=4096,'inventory_cap')
            try:cmd=read(entry/'cmdline',proc=True)
            except FileNotFoundError:exited+=1;continue
            if any(marker in cmd for marker in (b'amn2',b'app.main',b'app.web')):
                processes.append(dict(pid=int(entry.name),command_sha256=hashlib.sha256(cmd).hexdigest()))
                require(len(processes)<=128,'inventory_cap')
        return dict(unit_count=len(names),unit_names_sha256=digest(sorted(names)),related_units=matches,
            cron_files=len(cron),cron=cron,process_count=count,related_processes=processes,
            exited_during_scan=exited,writer_exclusion='NOT_ESTABLISHED_BY_STATIC_SCAN',
            external_pollers='REQUIRES_OPERATOR_OWNERSHIP',opaque_wrappers='REQUIRES_REVIEW')
    def collect(self):
        boot=read('/proc/sys/kernel/random/boot_id',128,proc=True).decode().strip()
        require(re.fullmatch('[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',boot),'property_contract')
        before={u:self.unit(u) for u in UNITS}
        launches={u:launch_fingerprint(self,u) for u in UNITS}
        env={u:self.process_environment(before[u]['MainPID']) for u in UNITS}
        dotenv=Path(OLD)/'.env'
        config=literal_dotenv(read(dotenv)) if dotenv.exists() else 'ABSENT'
        sources={}
        for path,wanted in [(OLD+'/app/config/settings.py','1db81553dbcbf4dafc710efdd69c2db0cc1a869f0754d7bb67c7adfa3dcac631'),
                (CANDIDATE+'/app/config/settings.py','6cb3ef9889422dc4d229ef90a5c558ddd100290253b77a8a6525f91676f5b9fe')]:
            actual=hashlib.sha256(read(path,1048576)).hexdigest()
            require(actual==wanted,'source_changed');sources['old' if path.startswith(OLD) else 'candidate']=actual
        inventory=self.inventory()
        after={u:self.unit(u) for u in UNITS};require(before==after,'unit_changed')
        require(launches=={u:launch_fingerprint(self,u) for u in UNITS},'unit_changed')
        require(read('/proc/sys/kernel/random/boot_id',128,proc=True).decode().strip()==boot,'unit_changed')
        return dict(boot_id=boot,units=after,launch_sha256=launches,process_environment=env,
            dotenv_selected=config,settings_source_sha256=sources,inventory=inventory,
            effective_settings='REQUIRES_SOURCE_AND_ENVIRONMENT_PRECEDENCE_REVIEW',
            startup_bound='NOT_ESTABLISHED',installed_binary_integrity='NOT_ESTABLISHED')


def main():
    result=dict(schema='phase16.maintenance-facts.v1',approval=APPROVAL,target_binding_sha256=TARGET,
        status='UNKNOWN',reason='collection_error',facts=None,remote_writes=0,database_opened=False,
        service_actions=0,application_imports=0,activation=False,live_admission=False)
    def alarm(*args):raise Stop('deadline')
    try:
        require(sys.argv[1:]==[APPROVAL] and sys.platform=='linux' and os.geteuid()==0,'platform_contract')
        signal.signal(signal.SIGALRM,alarm);signal.alarm(SECONDS)
        result['facts']=Collector().collect()
        result.update(status='FACTS_COLLECTED_NOT_ADMITTED',reason='bounded_observation',
            completed_at=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        code=str(error) if isinstance(error,Stop) else ''
        result['reason']=code if code in REASONS else 'collection_error'
    finally:
        if sys.platform=='linux':signal.alarm(0)
    payload=json.dumps(result,sort_keys=True,separators=(',',':'))
    if len(payload)>65536:result.update(status='UNKNOWN',reason='read_limit',facts=None);payload=json.dumps(result)
    print(payload,flush=True)
    return 0 if result['status']=='FACTS_COLLECTED_NOT_ADMITTED' else 3
if __name__=='__main__':raise SystemExit(main())
