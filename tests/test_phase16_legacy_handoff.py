"""Source-bound characterization, not evidence of deployed aiogram shutdown.

Exact function from old 55dc243b8e6c6bdb57f8301b56326e4cd4072d19,
app/bot/handlers.py LF SHA256
31987a5fb46c9cee35c16817e805da76eef8fde178a7ce8cf86a5c9a6adf7d39.
Only this function executes with local doubles; no app import/Telegram/network.
"""
import ast
import asyncio
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest


class LegacyHandoffTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        path = Path(__file__).parent / 'fixtures/phase16_legacy_admin_handoff.txt'
        raw = path.read_bytes().replace(b'\r\n', b'\n')
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '05ec1880e74f6e762082446c7dae5e0c2f49eda223485dc1a4634d3d50819543')
        tree = ast.parse(raw)
        self.assertEqual(len(tree.body), 1)
        self.assertIsInstance(tree.body[0], ast.AsyncFunctionDef)
        self.assertEqual(tree.body[0].name, '_send_admin_config_handoff')
        namespace = dict(BufferedInputFile=lambda content, filename: (content, filename))
        exec(compile(tree, str(path), 'exec'), namespace)
        self.handoff = namespace['_send_admin_config_handoff']
        self.started, self.response = asyncio.Event(), asyncio.Event()
        self.audit, self.answers = [], []
        async def send_document(**kwargs):
            self.started.set()
            await self.response.wait()
            return SimpleNamespace(message_id=123)
        async def answer(text): self.answers.append(text)
        self.message = SimpleNamespace(bot=SimpleNamespace(send_document=send_document), answer=answer)
        self.workflow = SimpleNamespace(record_admin_config_delivery=lambda **fields: self.audit.append(fields))

    async def invoke(self):
        await self.handoff(self.message, workflow=self.workflow, admin_telegram_id=1,
            result=SimpleNamespace(config_bytes=b'synthetic', filename='fixture', passport_device_id=1),
            success_text='sent', failure_text='failed')

    async def test_normal_response_has_one_delivery_audit(self):
        self.response.set()
        await self.invoke()
        self.assertTrue(self.started.is_set())
        self.assertEqual(len(self.audit), 1)
        self.assertTrue(self.audit[0]['delivered'])
        self.assertEqual(self.answers, ['sent'])

    async def test_cancellation_after_send_starts_has_no_delivery_outcome(self):
        task = asyncio.create_task(self.invoke())
        await self.started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError): await task
        self.assertEqual(self.audit, [])
        self.assertEqual(self.answers, [])
        # This does not tell us whether the external Telegram endpoint accepted
        # the request. Process exit/persisted issuance counts cannot answer that.

if __name__ == '__main__': unittest.main()
