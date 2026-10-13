import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class CLITests(unittest.TestCase):
    def run_cli(self, command, data):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'input.json'
            path.write_text(data)
            result = subprocess.run(['python3', str(ROOT/'bin/mudanza'), command, '--input', str(path)], capture_output=True, text=True)
            self.assertEqual(path.read_text(), data)
            return result

    def test_demo_commands(self):
        data = (ROOT/'examples/demo.json').read_text()
        for command in ('validate', 'status', 'costs'):
            result = self.run_cli(command, data)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)

    def test_invalid_json(self):
        result = self.run_cli('validate', '{')
        self.assertEqual(result.returncode, 1)
        self.assertIn('error', json.loads(result.stderr))

    def test_wrong_root(self):
        result = self.run_cli('validate', '[]')
        self.assertEqual(result.returncode, 1)
        self.assertIn('error', json.loads(result.stderr))

    def test_malformed_records(self):
        for data in ({'schema_version':1, 'conversations':[{}]}, {'schema_version':1,'properties':[None]}, {'schema_version':1,'costs':'bad'}):
            result = self.run_cli('status', json.dumps(data))
            self.assertEqual(result.returncode,1)
            self.assertIn('error',json.loads(result.stderr))

    def test_generated_demo_is_reproducible(self):
        path = ROOT/'docs/demo/index.html'
        before = path.read_bytes()
        subprocess.run(['python3',str(ROOT/'scripts/build_demo.py')],check=True,capture_output=True)
        self.assertEqual(before,path.read_bytes())

    def test_invalid_amount(self):
        result = self.run_cli('costs', json.dumps({'schema_version':1, 'costs':[{'id':'a','currency':'ARS','amount':'not-a-number'}]}))
        self.assertEqual(result.returncode,1)
        self.assertIn('error',json.loads(result.stderr))
