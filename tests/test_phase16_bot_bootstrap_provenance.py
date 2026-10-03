"""The OS package baseline is a declared trust boundary, not a remote signature."""
import hashlib
import importlib.util
import unittest
AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_bootstrap_provenance') is not None
if AVAILABLE:from scripts import phase16_bot_bootstrap_provenance as m

class Availability(unittest.TestCase):
    def test_bootstrap_provenance_exists(self):self.assertTrue(AVAILABLE)

@unittest.skipUnless(AVAILABLE,'availability fails first')
class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.data=b'OS_SEED_WHEEL_FIXTURE'
        self.path='usr/share/python-wheels/pip-24.0-py3-none-any.whl'
        self.md5=hashlib.md5(self.data).hexdigest()
        self.manifest=(self.md5+'  '+self.path+'\n').encode()
        self.package=b'install ok installed\t24.0+dfsg-1ubuntu1\tall\n'
    def test_pin_uses_os_seed_and_declares_exact_trust_boundary(self):
        pin,receipt=m.pin_os_seed(self.path,self.data,self.manifest,self.package)
        self.assertEqual(pin.sha256,hashlib.sha256(self.data).hexdigest())
        self.assertEqual(pin.role,'bootstrap');self.assertEqual(pin.name,'pip')
        self.assertEqual(receipt['trust'],'EXISTING_OS_PACKAGE_BASELINE')
        self.assertFalse(receipt['publisher_signature_verified'])
        self.assertEqual(receipt['package'],'python3-pip-whl')
    def test_modified_wheel_is_rejected(self):
        with self.assertRaises(m.ProvenanceError):
            m.pin_os_seed(self.path,b'changed',self.manifest,self.package)
    def test_unrelated_or_duplicate_package_manifest_entry_rejected(self):
        for raw in (b'',self.manifest+self.manifest,(self.md5+'  etc/other\n').encode()):
            with self.subTest(raw=raw),self.assertRaises(m.ProvenanceError):
                m.pin_os_seed(self.path,self.data,raw,self.package)
    def test_non_installed_or_unknown_package_is_not_trusted(self):
        for raw in (b'deinstall ok config-files\t24.0\tall\n',b'PRIVATE_TOKEN',b'install ok installed\t24.0\tamd64\n'):
            with self.assertRaises(m.ProvenanceError) as cm:
                m.pin_os_seed(self.path,self.data,self.manifest,raw)
            self.assertNotIn('PRIVATE_TOKEN',str(cm.exception))
    def test_seed_selection_is_fixed_directory_regular_name_and_one_version(self):
        self.assertEqual(m.seed_name(['pip-24.0-py3-none-any.whl','setuptools-1-py3-none-any.whl']),self.path)
        for names in ([],['pip-24.0-py3-none-any.whl','pip-25.0-py3-none-any.whl'],['pip-../bad.whl']):
            with self.subTest(names=names),self.assertRaises(m.ProvenanceError):m.seed_name(names)
    def test_future_collection_rechecks_package_and_os_seed_without_install(self):
        calls=[]
        def run(argv,seconds):
            calls.append(argv)
            if argv[-1]=='md5sums':return self.manifest
            return self.package
        files={'/'+self.path:self.data}
        pin,raw,receipt=m.collect(run,lambda:list([self.path.split('/')[-1]]),files.__getitem__,lambda:None)
        self.assertEqual(raw,self.data);self.assertEqual(len(calls),4)
        self.assertTrue(all(argv[0]=='dpkg-query' for argv in calls))
    def test_changed_package_evidence_stops(self):
        count=[0]
        def run(argv,seconds):
            count[0]+=1
            if argv[-1]=='md5sums':return self.manifest if count[0]<4 else b'changed'
            return self.package
        with self.assertRaises(m.ProvenanceError):
            m.collect(run,lambda:[self.path.split('/')[-1]],lambda _:self.data,lambda:None)
