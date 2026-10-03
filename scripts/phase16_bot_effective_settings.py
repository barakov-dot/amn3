"""Read-only selected future settings. No app imports, secret output or CLI.

This collector understands a deliberately bounded literal configuration subset.
It follows systemd Environment -> ordered EnvironmentFiles -> UnsetEnvironment,
then environment-over-dotenv precedence for the pinned candidate Settings source.
PAM/chroot/pass-through/selected manager variables and ambiguous syntax STOP.
A pass proves only selected values, not startup duration or all app validation.
Documentation: https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.exec.xml
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from scripts import phase16_bot_maintenance as core
from scripts.vps import phase16_bot_integration_readback_v3 as safe

SETTINGS_SHA256='6cb3ef9889422dc4d229ef90a5c558ddd100290253b77a8a6525f91676f5b9fe'
CANDIDATE_SETTINGS='/opt/amn2-spain/bot-candidates/phase16-bot-runtime40-20260929-6e68235-001/source/app/config/settings.py'
DOTENV='/opt/amn2-spain/runtime/source/.env'
CWD='/opt/amn2-spain/runtime/source'
DB='/var/lib/amn2-spain/amn2.sqlite3'
DEFAULTS={'VPS_APPLY_ENABLED':'false','AWG3_BOOTSTRAP_ENABLED':'false',
    'TELEGRAM_ADMISSION_TIMEOUT_SECONDS':'30','TELEGRAM_EXPECTED_BOT_USERNAME':'',
    'DATABASE_PATH':'data/amneziya.sqlite3','DEFAULT_VPN_NETWORK_CIDR':'10.8.0.0/24',
    'WEB_ADMIN_PORT':'3030'}
FIELDS={'Environment':'as','EnvironmentFiles':'a(sb)','UnsetEnvironment':'as',
        'PassEnvironment':'as','PAMName':'s','RootDirectory':'s','RootImage':'s',
        'WorkingDirectory':'s'}

class SettingsError(ValueError): pass

def require(value,reason):
    if not value:raise SettingsError(reason)

def assignments(values):
    require(isinstance(values,list) and len(values)<=512,'settings_environment_shape')
    result={}
    for item in values:
        require(isinstance(item,str) and len(item)<=16384 and '=' in item and
                not any(c in item for c in ('\x00','\r','\n')),'settings_assignment')
        name,value=item.split('=',1)
        require(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',name) and name not in result,'settings_assignment')
        result[name]=value
    return result

def literals(raw,*,dotenv=False):
    require(isinstance(raw,bytes) and len(raw)<=262144,'settings_file_size')
    try:text=raw.decode('utf-8')
    except UnicodeError:raise SettingsError('settings_file_encoding') from None
    require(not any(c in text for c in ('\x00','\ufeff','\\')),'settings_literal_syntax')
    require(all(c in '\r\n\t' or (c.isprintable() and (not c.isspace() or c==' ')) for c in text),
            'settings_literal_syntax')
    result={}
    for line in text.split('\n'):
        if line.endswith('\r'):line=line[:-1]
        require('\r' not in line,'settings_literal_syntax')
        line=line.strip(' \t')
        if not line or line.startswith('#') or (not dotenv and line.startswith(';')):continue
        if dotenv and line.startswith('export '):line=line[7:].lstrip()
        require('=' in line,'settings_literal_syntax')
        name,value=line.split('=',1);name=name.strip();value=value.strip()
        require(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',name) and name not in result,'settings_literal_syntax')
        if value.startswith(('"',"'")):
            require(len(value)>=2 and value[-1]==value[0] and value[0] not in value[1:-1],
                    'settings_literal_syntax')
            value=value[1:-1]
        else:
            require('"' not in value and "'" not in value,'settings_literal_syntax')
            if dotenv:value=re.split(r'\s+#',value,maxsplit=1)[0].rstrip()
        require(not dotenv or '${' not in value,'settings_dotenv_expansion')
        result[name]=value
    return result

def selected(values):
    result={}
    for name,value in values.items():
        key=name.upper()
        if key not in DEFAULTS:continue
        require(key not in result,'settings_case_collision')
        result[key]=value
    return result

def context(unit):
    require(isinstance(unit,dict) and set(unit)==set(FIELDS),'settings_context')
    require(unit['WorkingDirectory']==CWD and unit['PAMName']=='' and unit['RootDirectory']=='' and
            unit['RootImage']=='' and unit['PassEnvironment']==[],'settings_unsupported_context')
    entries=unit['EnvironmentFiles']
    require(isinstance(entries,list) and len(entries)<=8,'settings_environment_files')
    paths=[]
    for item in entries:
        require(isinstance(item,list) and len(item)==2 and isinstance(item[0],str) and
                type(item[1]) is bool,'settings_environment_files')
        path=item[0]
        require(len(path)<=256 and re.fullmatch('/[A-Za-z0-9_./-]+',path) and
                str(PurePosixPath(path))==path and all(p not in ('','..','.') for p in path[1:].split('/')),
                'settings_environment_path')
        require(path not in paths,'settings_environment_files');paths.append(path)
    return paths

def resolve(source,unit,*,manager_environment,files,dotenv):
    require(isinstance(source,bytes) and hashlib.sha256(source).hexdigest()==SETTINGS_SHA256,
            'settings_source_binding')
    paths=context(unit)
    # Manager global/default/pass-through ambiguity is never guessed from /proc.
    require(not selected(assignments(manager_environment)),'settings_manager_environment')
    env=assignments(unit['Environment'])
    require(isinstance(files,dict) and set(files)==set(paths),'settings_environment_files')
    for path,optional in unit['EnvironmentFiles']:
        raw=files[path]
        if raw is None:
            require(optional,'settings_required_file_absent');continue
        env.update(literals(raw))
    unset=unit['UnsetEnvironment']
    require(isinstance(unset,list) and len(unset)<=512,'settings_unset')
    for item in unset:
        require(isinstance(item,str) and len(item)<=16384,'settings_unset')
        name,separator,value=item.partition('=')
        require(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',name),'settings_unset')
        if not separator or env.get(name)==value:env.pop(name,None)
    values=dict(DEFAULTS)
    if dotenv is not None:values.update(selected(literals(dotenv,dotenv=True)))
    values.update(selected(env))
    def disabled(name):
        require(values[name].lower() in ('0','off','f','false','n','no'),'settings_mutation_flag')
        return False
    admission=values['TELEGRAM_ADMISSION_TIMEOUT_SECONDS']
    require(re.fullmatch('[0-9]{1,2}',admission) and 1<=int(admission)<40,'settings_admission_budget')
    require(values['DATABASE_PATH']==DB and values['DEFAULT_VPN_NETWORK_CIDR']=='10.212.12.0/24' and
            values['WEB_ADMIN_PORT']=='3031' and
            values['TELEGRAM_EXPECTED_BOT_USERNAME'].strip()=='NeobyatnayaAMNZ_bot','settings_target')
    return dict(scope='SELECTED_EFFECTIVE_SETTINGS',vps_apply_enabled=disabled('VPS_APPLY_ENABLED'),
        awg3_bootstrap_enabled=disabled('AWG3_BOOTSTRAP_ENABLED'),admission_seconds=int(admission),
        expected_username='NeobyatnayaAMNZ_bot',database_matches=True,
        network_cidr='10.212.12.0/24',web_port=3031,startup_bound='NOT_ESTABLISHED')

def collect(properties,manager_environment,read,stable):
    # All potentially sensitive inputs stay in this call. No hashes of raw secret
    # files are returned. The reader must bind file/ancestor identities and absence.
    unit=properties();paths=context(unit);manager=manager_environment()
    files={path:read(path) for path in paths}
    result=resolve(read(CANDIDATE_SETTINGS),unit,manager_environment=manager,
                   files=files,dotenv=read(DOTENV))
    require(unit==properties() and manager==manager_environment(),'settings_changed')
    stable()
    return result

class RootSettingsReader:
    """Root-owned/no-link bounded files, with observed absence and stat continuity."""
    def __init__(self):self.observed={}
    def record(self,path):
        try:value=path.lstat()
        except FileNotFoundError:value=None
        fingerprint=None if value is None else (value.st_dev,value.st_ino,value.st_mode,
            value.st_uid,value.st_gid,value.st_size,value.st_mtime_ns,value.st_ctime_ns)
        if path in self.observed:require(self.observed[path]==fingerprint,'settings_file_changed')
        self.observed[path]=fingerprint
        return value
    def __call__(self,name):
        path=Path(name)
        require(path.is_absolute(),'settings_file_path')
        absent=False
        for current in reversed((path,*path.parents)):
            value=self.record(current)
            if value is None:absent=True;continue
            require(not absent and value.st_uid==0 and not value.st_mode & 0o022 and
                    not stat.S_ISLNK(value.st_mode),'settings_file_owner')
            if current!=path:require(stat.S_ISDIR(value.st_mode),'settings_file_type')
        if absent:return None
        require(stat.S_ISREG(value.st_mode) and value.st_nlink==1,'settings_file_type')
        raw=safe.safe_read(path,262144);self.record(path)
        return raw
    def stable(self):
        for path in tuple(self.observed):self.record(path)

def collect_live(client):
    """Call only inside a separately authorized host packet. No commands mutate."""
    reader=RootSettingsReader()
    def props():return {key:client.bus_property(core.BOT,'Service',key,kind) for key,kind in FIELDS.items()}
    def manager():
        raw=client.run(['busctl','--json=short','get-property','org.freedesktop.systemd1',
            '/org/freedesktop/systemd1','org.freedesktop.systemd1.Manager','Environment'],5)
        try:value=json.loads(raw)
        except (ValueError,TypeError):raise SettingsError('settings_manager_shape') from None
        require(isinstance(value,dict) and set(value)=={'type','data'} and value['type']=='as',
                'settings_manager_shape')
        return value['data']
    try:return collect(props,manager,reader,reader.stable)
    except SettingsError:raise
    except Exception:raise SettingsError('settings_collection_failed') from None
