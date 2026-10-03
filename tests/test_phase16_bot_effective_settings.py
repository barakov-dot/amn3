"""Synthetic settings precedence; no service/app import or secret output."""
import copy
import hashlib
import importlib.util
import json
import unittest
from unittest.mock import patch

AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_effective_settings') is not None
if AVAILABLE: from scripts import phase16_bot_effective_settings as m

class Availability(unittest.TestCase):
    def test_collector_exists(self): self.assertTrue(AVAILABLE)

@unittest.skipUnless(AVAILABLE,'missing module fails availability')
class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.source=b'verified synthetic settings'
        self.env=['DATABASE_PATH=/var/lib/amn2-spain/amn2.sqlite3',
                  'DEFAULT_VPN_NETWORK_CIDR=10.212.12.0/24',
                  'TELEGRAM_EXPECTED_BOT_USERNAME=NeobyatnayaAMNZ_bot',
                  'WEB_ADMIN_PORT=3031','TELEGRAM_BOT_TOKEN=PRIVATE_TOKEN']
        self.files={'/etc/amn2.env':b'VPS_APPLY_ENABLED=false\n'}
        self.unit={'Environment':self.env,'EnvironmentFiles':[['/etc/amn2.env',False]],
                   'UnsetEnvironment':[],'PassEnvironment':[],'PAMName':'',
                   'RootDirectory':'','RootImage':'',
                   'WorkingDirectory':'/opt/amn2-spain/runtime/source'}
    def resolve(self,**kw):
        with patch.object(m,'SETTINGS_SHA256',hashlib.sha256(self.source).hexdigest()):
            return m.resolve(self.source,self.unit,manager_environment=[],
                files=self.files,dotenv=None,**kw)
    def test_safe_defaults_are_bound_to_exact_candidate_source(self):
        v=self.resolve();self.assertIs(v['vps_apply_enabled'],False)
        self.assertIs(v['awg3_bootstrap_enabled'],False)
        self.assertEqual(v['admission_seconds'],30)
        self.assertNotIn('PRIVATE_TOKEN',json.dumps(v));self.assertNotIn('token',json.dumps(v))
        self.assertEqual(v['scope'],'SELECTED_EFFECTIVE_SETTINGS')
    def test_environment_file_overrides_environment(self):
        self.env.append('VPS_APPLY_ENABLED=true')
        self.assertIs(self.resolve()['vps_apply_enabled'],False)
        self.files['/etc/amn2.env']=b'VPS_APPLY_ENABLED=true\n'
        with self.assertRaises(m.SettingsError):self.resolve()
    def test_dotenv_is_lower_priority_and_case_collisions_fail(self):
        with patch.object(m,'SETTINGS_SHA256',hashlib.sha256(self.source).hexdigest()):
            v=m.resolve(self.source,self.unit,manager_environment=[],files=self.files,
                        dotenv=b'WEB_ADMIN_PORT=9999\n')
        self.assertEqual(v['web_port'],3031)
        self.env.append('web_admin_port=3031')
        with self.assertRaises(m.SettingsError):self.resolve()
    def test_last_file_wins_and_unset_is_applied_last(self):
        self.unit['EnvironmentFiles'].append(['/etc/second.env',False])
        self.files['/etc/second.env']=b'VPS_APPLY_ENABLED=true\n'
        self.unit['UnsetEnvironment']=['VPS_APPLY_ENABLED=true']
        self.assertIs(self.resolve()['vps_apply_enabled'],False)
    def test_no_application_import_or_unbound_source_defaults(self):
        with self.assertRaises(m.SettingsError):
            m.resolve(self.source,self.unit,manager_environment=[],files=self.files,dotenv=None)
    def test_unsupported_inputs_stop_without_echoing_secret(self):
        for content in (b'X="PRIVATE_TOKEN',b'export X=PRIVATE_TOKEN',
                        b'X=PRIVATE_TOKEN\\\nmore',b'X=PRIVATE_TOKEN\x00'):
            with self.subTest(content=content):
                self.files['/etc/amn2.env']=content
                with self.assertRaises(m.SettingsError) as cm:self.resolve()
                self.assertNotIn('PRIVATE_TOKEN',str(cm.exception))
    def test_optional_absent_file_only_if_declared_optional(self):
        self.files['/etc/amn2.env']=None
        with self.assertRaises(m.SettingsError):self.resolve()
        self.unit['EnvironmentFiles'][0][1]=True
        self.assertIs(self.resolve()['vps_apply_enabled'],False)
    def test_unsupported_contexts_and_wildcards_stop(self):
        for key,value in [('PAMName','login'),('PassEnvironment',['VPS_APPLY_ENABLED']),
                          ('RootDirectory','/other'),('RootImage','/image')]:
            with self.subTest(key=key):
                old=self.unit[key];self.unit[key]=value
                with self.assertRaises(m.SettingsError):self.resolve()
                self.unit[key]=old
        self.unit['EnvironmentFiles'][0][0]='/etc/*.env'
        with self.assertRaises(m.SettingsError):self.resolve()
    def test_manager_selected_environment_is_not_assumed_absent(self):
        with patch.object(m,'SETTINGS_SHA256',hashlib.sha256(self.source).hexdigest()):
            with self.assertRaises(m.SettingsError):
                m.resolve(self.source,self.unit,manager_environment=['AWG3_BOOTSTRAP_ENABLED=true'],
                          files=self.files,dotenv=None)
    def test_invalid_db_username_network_or_budget_stops(self):
        for key,value in [('DATABASE_PATH','/tmp/other.sqlite'),('WEB_ADMIN_PORT','3030'),
                          ('DEFAULT_VPN_NETWORK_CIDR','10.0.0.0/8'),
                          ('TELEGRAM_EXPECTED_BOT_USERNAME','OTHER_bot'),
                          ('TELEGRAM_ADMISSION_TIMEOUT_SECONDS','40'),('AWG3_BOOTSTRAP_ENABLED','1')]:
            with self.subTest(key=key):
                self.files['/etc/amn2.env']=(key+'='+value+'\n').encode()
                with self.assertRaises(m.SettingsError):self.resolve()
    def test_bound_reader_collects_current_files_and_detects_manager_change(self):
        calls=[]
        def read(path):
            calls.append(path)
            if path==m.CANDIDATE_SETTINGS:return self.source
            if path==m.DOTENV:return None
            return self.files[path]
        def props():return copy.deepcopy(self.unit)
        with patch.object(m,'SETTINGS_SHA256',hashlib.sha256(self.source).hexdigest()):
            result=m.collect(props,lambda:[],read,lambda:None)
        self.assertEqual(result['web_port'],3031)
        self.assertIn('/etc/amn2.env',calls)
        count=[0]
        def changing():
            count[0]+=1;v=props()
            if count[0]>1:v['Environment'].append('AWG3_BOOTSTRAP_ENABLED=true')
            return v
        with patch.object(m,'SETTINGS_SHA256',hashlib.sha256(self.source).hexdigest()):
            with self.assertRaises(m.SettingsError):m.collect(changing,lambda:[],read,lambda:None)

    def test_non_systemd_line_separators_cannot_disable_true_flag(self):
        self.env.append('VPS_APPLY_ENABLED=true')
        for separator in ('\v','\f','\x85','\u2028','\u2029','\u2000'):
            with self.subTest(separator=repr(separator)):
                self.files['/etc/amn2.env']=('IGNORE=x'+separator+'VPS_APPLY_ENABLED=false\n').encode()
                with self.assertRaises(m.SettingsError):self.resolve()
