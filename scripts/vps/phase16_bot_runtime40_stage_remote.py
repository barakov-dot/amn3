"""One new runtime40 stage; no shared DB, unit, old-runtime or application access."""
from __future__ import annotations
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import stat
import sys
import time
from scripts.vps import phase16_bot_linux_gate_remote as legacy

APPROVAL='PHASE16_BOT_RUNTIME40_STAGE_20260924_001'
ARTIFACT_ID='phase16-bot-runtime40-20260924-6e68235-001'
DESTINATION=Path('/opt/amn2-spain/bot-candidates')/ARTIFACT_ID
REMOTE_SECONDS=300
WORK_SECONDS=280
STEPS=['network_namespace','venv','offline_install','pip_check','metadata','source_readback']
SUCCESS='RUNTIME40_STAGED_NOT_ACTIVATED'
SCHEMA='phase16.bot-runtime40-stage.v1'
LOCK='requirements/phase15-runtime-py312.lock'
REASONS=frozenset({
    'bundle_binding','manifest_binding','source_binding','payload_inventory','payload_binding',
    'archive_path','archive_size','archive_type','archive_duplicate','source_inventory','source_duplicate',
    'platform_python','platform_abi','unsafe_parent','destination_exists','disk_space','root_required',
    'network_namespace_unavailable','runtime_inventory','runtime_scope','source_inventory',
    'process_limits','process_output_cap','process_timeout','process_unclosed_pipe','process_io',
    'wall_cap','venv_exit','offline_install_exit','pip_check_exit','metadata_exit',
    'metadata_shape','dependency_binding','dependency_extra','dependency_origin','dependency_duplicate',
    'venv_config','pth_present','import_origin','source_after_test','approval_argument','bundle_size',
    'stage_exception','result_write_failed'})


def reason(error):
    value=str(error) if isinstance(error,legacy.GateError) else None
    return value if value in REASONS else 'stage_exception'


def select_runtime(payload,manifest):
    wheels=manifest['wheels']
    legacy.require(all(w['scope'] in ('runtime','test-only') for w in wheels),'runtime_scope')
    runtime=[w for w in wheels if w['scope']=='runtime']
    legacy.require(len(runtime)==40 and len(wheels)==48,'runtime_inventory')
    expected={}
    files={LOCK:payload[LOCK]}
    for wheel in runtime:
        name=re.sub(r'[-_.]+','-',wheel['name']).lower()
        legacy.require(name not in expected and wheel['file'].startswith('wheelhouse/runtime/'),'runtime_inventory')
        expected[name]=wheel['version'];files[wheel['file']]=payload[wheel['file']]
    source=legacy.tar_inventory(payload[manifest['source']['file']])
    legacy.require(len([n for n in source if n.startswith('app/') and n.endswith('.py')])==126 and
                   'app/main.py' in source and 'app/__init__.py' in source,'source_inventory')
    return files,source,expected


def precheck():
    legacy.require(sys.platform=='linux' and sys.version_info[:2]==(3,12),'platform_python')
    legacy.require(platform.machine()=='x86_64' and platform.libc_ver()==('glibc','2.39'),'platform_abi')
    legacy.require(os.geteuid()==0,'root_required')
    for parent in (Path('/opt'),Path('/opt/amn2-spain'),DESTINATION.parent):
        metadata=parent.lstat()
        legacy.require(stat.S_ISDIR(metadata.st_mode) and metadata.st_uid==0 and
                       not metadata.st_mode & 0o022,'unsafe_parent')
    legacy.require(not DESTINATION.exists() and not DESTINATION.is_symlink(),'destination_exists')
    legacy.require(shutil.disk_usage(DESTINATION.parent).free>=512*1024*1024,'disk_space')
    legacy.require(Path('/usr/bin/unshare').is_file(),'network_namespace_unavailable')


# -S prevents .pth execution. No app/dependency imports: metadata and PathFinder only.
METADATA_CODE = r"""
import importlib.metadata as md
from importlib.machinery import PathFinder
import json,sys
from pathlib import Path
venv,source=map(Path,sys.argv[-2:])
site=venv/'lib/python3.12/site-packages'
config={}
for line in (venv/'pyvenv.cfg').read_text().splitlines():
    if '=' in line:
        key,value=line.split('=',1)
        if key.strip() in config:raise RuntimeError('duplicate venv key')
        config[key.strip()]=value.strip()
origins={}
for name,directory in [('app',source),('app.main',source/'app')]:
    spec=PathFinder.find_spec(name,[str(directory)])
    origins[name]=spec.origin if spec else None
packages=[]
for distribution in md.distributions(path=[str(site)]):
    packages.append([distribution.metadata['Name'],distribution.version,
                     Path(distribution.locate_file('')).resolve()==site.resolve()])
print(json.dumps(dict(executable=sys.executable,site_root=str(site),
                     venv_config_correct=config.get('include-system-site-packages')=='false',
                     pth_count=len(list(site.glob('*.pth'))),packages=packages,origins=origins)))
"""


def validate_metadata(value,expected,root):
    legacy.require(isinstance(value,dict) and set(value)=={
        'executable','site_root','venv_config_correct','pth_count','packages','origins'},'metadata_shape')
    venv=root/'runtime-venv'
    legacy.require(value['executable']==str(venv/'bin/python') and
                   value['site_root']==str(venv/'lib/python3.12/site-packages') and
                   value['venv_config_correct'] is True,'venv_config')
    legacy.require(type(value['pth_count']) is int and value['pth_count']==0,'pth_present')
    legacy.require(isinstance(value['packages'],list) and 40<=len(value['packages'])<=42,'metadata_shape')
    installed={}
    for entry in value['packages']:
        legacy.require(isinstance(entry,list) and len(entry)==3,'metadata_shape')
        name,version,inside=entry
        legacy.require(isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,128}',name) and
                       isinstance(version,str) and len(version)<=64,'metadata_shape')
        name=re.sub(r'[-_.]+','-',name).lower()
        legacy.require(inside is True,'dependency_origin')
        legacy.require(name not in installed,'dependency_duplicate')
        installed[name]=version
    legacy.require(all(installed.get(n)==v for n,v in expected.items()),'dependency_binding')
    legacy.require(set(installed)-set(expected)<={'pip','setuptools'},'dependency_extra')
    legacy.require(value['origins']=={'app':str(root/'source/app/__init__.py'),
                                      'app.main':str(root/'source/app/main.py')},'import_origin')
    return {'runtime_pins':len(expected),'bootstrap_distributions':len(installed)-len(expected),
            'candidate_import_origins':'MATCH_NO_APPLICATION_IMPORT','pth_count':0}


def base_result():
    return dict(schema=SCHEMA,artifact_id=ARTIFACT_ID,approval=APPROVAL,
                bundle_sha256=legacy.BUNDLE_SHA,source_commit=legacy.SOURCE_SHA,
                destination=DESTINATION.as_posix(),status='STOP_BEFORE_STAGE_OR_UNKNOWN',
                service_actions=0,live_database_opened=False,telegram_polling=False,
                runtime_activation=False,old_runtime_modified=False,steps=[])


def write_result(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def execute(data):
    started=time.monotonic();deadline=started+WORK_SECONDS
    payload,_,manifest=legacy.validate_bundle(data)
    selected,source,expected=select_runtime(payload,manifest)
    precheck()
    # Repeat claim check even when a test substitutes the platform precheck.
    legacy.require(not DESTINATION.exists() and not DESTINATION.is_symlink(),'destination_exists')
    rc,_=legacy.run_process(['/usr/bin/unshare','--net','/usr/bin/true'],cwd=str(DESTINATION.parent),
                            env=legacy.clean_environment(Path('/nonexistent')),timeout=5)
    legacy.require(rc==0,'network_namespace_unavailable')
    legacy.claim_directory(DESTINATION)
    result=base_result();result['status']='STOP_RETAINED_NO_RETRY'
    result['steps'].append({'step':'network_namespace','returncode':0})
    try:
        write_result(DESTINATION/'claim.json',dict(approval=APPROVAL,artifact_id=ARTIFACT_ID,
                                                 bundle_sha256=legacy.BUNDLE_SHA,attempts=1))
        legacy.write_tree(DESTINATION/'payload',selected)
        legacy.write_tree(DESTINATION/'source',source)
        scratch=DESTINATION/'scratch';scratch.mkdir(mode=0o700)
        env=legacy.clean_environment(scratch);venv=DESTINATION/'runtime-venv';python=venv/'bin/python'
        def run(label,args,seconds):
            remaining=deadline-time.monotonic();legacy.require(remaining>0,'wall_cap')
            rc,output=legacy.run_process(['/usr/bin/unshare','--net',*map(str,args)],cwd=str(scratch),env=env,
                                         timeout=min(seconds,remaining))
            result['steps'].append(dict(step=label,returncode=rc,output_bytes=len(output),output_sha256=legacy.sha(output)))
            legacy.require(rc==0,label+'_exit')
            return output
        run('venv',['/usr/bin/python3','-I','-B','-m','venv',venv],45)
        run('offline_install',[python,'-I','-B','-m','pip','--isolated','--disable-pip-version-check',
            '--no-cache-dir','install','--no-index','--no-deps','--require-hashes','--only-binary=:all:',
            '--find-links',DESTINATION/'payload/wheelhouse/runtime','-r',DESTINATION/'payload'/LOCK],120)
        run('pip_check',[python,'-I','-B','-m','pip','--isolated','check'],20)
        metadata=json.loads(run('metadata',[python,'-I','-S','-B','-c',METADATA_CODE,'--stage-metadata',
                                            venv,DESTINATION/'source'],20))
        result.update(validate_metadata(metadata,expected,DESTINATION))
        legacy.verify_tree(DESTINATION/'source',source)
        legacy.verify_tree(DESTINATION/'payload',selected)
        legacy.require(time.monotonic()<deadline,'wall_cap')
        result['steps'].append({'step':'source_readback','returncode':0})
        result['app_python_files']=126
        result['runtime_lock_sha256']=legacy.sha(selected[LOCK])
        result['status']=SUCCESS
    except BaseException as error:
        result['reason']=reason(error)
    finally:
        result['seconds']=round(time.monotonic()-started,3)
        try:write_result(DESTINATION/'result.json',result)
        except BaseException:
            result['status']='STOP_RETAINED_NO_RETRY';result['reason']='result_write_failed'
    return result


def main():
    def alarm(signum,frame):raise legacy.GateError('wall_cap')
    if sys.platform=='linux':signal.signal(signal.SIGALRM,alarm);signal.alarm(REMOTE_SECONDS)
    try:
        legacy.require(sys.argv[1:]==[APPROVAL],'approval_argument')
        data=sys.stdin.buffer.read(legacy.MAX_BUNDLE+1)
        legacy.require(len(data)<=legacy.MAX_BUNDLE,'bundle_size')
        result=execute(data)
    except BaseException as error:
        result=base_result();result['reason']=reason(error)
    finally:
        if sys.platform=='linux':signal.alarm(0)
    print(json.dumps(result),flush=True)
    return 0 if result['status']==SUCCESS else 3


if __name__=='__main__':raise SystemExit(main())
