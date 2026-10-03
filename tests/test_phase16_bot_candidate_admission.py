"""Composition rejects unbound inputs before reading installed runtime."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
AVAILABLE=importlib.util.find_spec('scripts.phase16_bot_candidate_admission') is not None
if AVAILABLE:from scripts import phase16_bot_candidate_admission as m

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/'research/amn2/phase16-bot-stage-readback-inventory-2026-09-29.json'
class Availability(unittest.TestCase):
    def test_candidate_composition_exists(self):self.assertTrue(AVAILABLE)

@unittest.skipUnless(AVAILABLE,'availability fails first')
class CandidateTests(unittest.TestCase):
    def test_real_catalog_contains_exact40wheels159sources(self):
        catalog=m.catalog(INVENTORY.read_bytes())
        self.assertEqual(len(catalog.wheels),40);self.assertEqual(len(catalog.source_pins),159)
        self.assertEqual(sum(n.startswith('app/') for n in catalog.source_pins),155)
        self.assertEqual(sum(n.startswith('app/') and n.endswith('.py') for n in catalog.source_pins),126)
        self.assertEqual(set(p.name for p in catalog.wheels.values()),set(catalog.inventory['pins']))
    def test_tampered_catalog_fails_before_wheel_reads(self):
        raw=INVENTORY.read_bytes().replace(b'25.1.0',b'25.1.1')
        with self.assertRaises(m.AdmissionError):m.catalog(raw)
    def cfg(self):
        return ('home = /usr/bin\ninclude-system-site-packages = false\nversion = 3.12.3\n'
                'executable = /usr/bin/python3.12\ncommand = /usr/bin/python3 -m venv '+m.STAGE+'/runtime-venv\n').encode()
    def test_generated_cfg_requires_semantic_proof_before_continuity_pin(self):
        raw=self.cfg();pin=m.venv_pin(raw,os_python_version='3.12.3')
        self.assertEqual(pin,(len(raw),hashlib.sha256(raw).hexdigest()))
        for replacement in (raw.replace(b'false',b'true'),raw.replace(b'/usr/bin',b'/tmp/bin'),
                            raw.replace(b'3.12.3',b'3.11.3'),raw+b'unknown=other\n'):
            with self.subTest(raw=replacement),self.assertRaises(m.AdmissionError):
                m.venv_pin(replacement,os_python_version='3.12.3')
    def test_other_cfg_command_or_duplicate_key_cannot_self_pin(self):
        for raw in (self.cfg().replace(b' -m venv ',b' -m arbitrary '),self.cfg()+b'home = /usr/bin\n'):
            with self.assertRaises(m.AdmissionError):m.venv_pin(raw,os_python_version='3.12.3')
    def test_system_identity_rejects_extra_membership_and_wrong_uid(self):
        passwd=b'root:x:0:0:root:/root:/bin/bash\namn2-spain:x:995:995:app:/var/lib/amn2-spain:/usr/sbin/nologin\n'
        groups=b'root:x:0:\namn2-spain:x:995:amn2-spain\n'
        who=m.local_identity(passwd,groups,dict(User='amn2-spain',Group='amn2-spain',SupplementaryGroups=[],DynamicUser=False))
        self.assertEqual((who.uid,who.gid,who.supplementary_gids),(995,995,(995,)))
        with self.assertRaises(m.AdmissionError):
            m.local_identity(passwd,groups+b'other:x:999:amn2-spain\n',dict(User='amn2-spain',Group='amn2-spain',SupplementaryGroups=[],DynamicUser=False))

    def test_bound_catalog_flows_through_real_access_verification(self):
        import contextlib
        from types import MappingProxyType
        from unittest.mock import patch
        from tests.test_phase16_bot_stage_access import StageAccessTests
        fixture=StageAccessTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        fixture.write('runtime-venv/pyvenv.cfg',self.cfg())
        runtime_pin,bootstrap_pin=fixture.pins
        path='payload/wheelhouse/runtime/'+runtime_pin.file
        fixture.write(path,fixture.wheels[runtime_pin.file])
        cat=m.Catalog({},MappingProxyType({path:runtime_pin}),MappingProxyType(fixture.source_pins))
        props=dict(User='amn2-spain',Group='amn2-spain',SupplementaryGroups=[],DynamicUser=False)
        class Client:
            def bus_property(self,unit,interface,name,signature):return props[name]
        class IdentityReader:
            def __call__(self,path):
                return (b'amn2-spain:x:1001:1001:app:/app:/bin/false\n' if path=='/etc/passwd'
                        else b'amn2-spain:x:1001:\n')
            def stable(self):pass
        with contextlib.ExitStack() as stack:
            for target,value in [
                ('catalog',lambda raw:cat),
                ('readback.observe',lambda inv:dict(status='VERIFIED',saved_receipt_sha256=m.SAVED_RECEIPT_SHA256)),
                ('settings.collect_live',lambda client:dict(vps_apply_enabled=False)),
                ('settings.RootSettingsReader',IdentityReader),
                ('bootstrap.collect_live',lambda client:(bootstrap_pin,fixture.wheels[bootstrap_pin.file],{})),
                ('access.UnixStageReader',lambda:contextlib.nullcontext(fixture.reader())),
                ('os.getgrouplist',lambda name,gid:[1001]),
                ('platform.python_version',lambda:'3.12.3')]:
                stack.enter_context(patch('scripts.phase16_bot_candidate_admission.'+target,value,create=True))
            proof=m.collect_live(Client(),b'bound catalog fixture')
        self.assertEqual(proof.access_plan.status,'ACCESS_PLAN_READY_NOT_APPLIED')
        self.assertEqual(proof.status,'CANDIDATE_CONTENT_VERIFIED_ACCESS_NOT_APPLIED')
