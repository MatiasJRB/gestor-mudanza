"""Audit the candidate distribution, including staged + untracked source files."""
from pathlib import Path
import re
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'.gitignore', 'LICENSE', 'README.md', 'AGENTS.md'}
PREFIXES = ('bin/', 'src/', 'tests/', 'examples/', 'docs/', 'scripts/', 'skills/')
patterns = [r'/Users/', r'/var/folders/', r'(?:sk|ghp|github_pat)[-_][A-Za-z0-9_]{16,}',
            r'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY', r'\b549\d{10}\b',
            r'(?i)[A-Z0-9._%+-]+@(?![A-Z0-9.-]*\.invalid\b)[A-Z0-9.-]+\.[A-Z]{2,}',
            r'(?i)mail-attachment.googleusercontent|whatsapp\.net|@lid']
files = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
errors = []
for name in sorted(set(filter(None, files))):
    path = ROOT / name
    if name not in ALLOWED and not name.startswith(PREFIXES):
        errors.append(f'Unexpected public path: {name}')
    if path.is_symlink():
        errors.append(f'Symlink rejected: {name}'); continue
    if not path.is_file():
        errors.append(f'Missing candidate file: {name}'); continue
    if path.suffix.lower() in {'.pdf', '.xlsx', '.db', '.sqlite', '.env', '.opus'}:
        errors.append(f'Private/binary extension: {name}'); continue
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeError:
        errors.append(f'Unreviewed binary: {name}'); continue
    # This scanner necessarily names its own detection patterns.
    if name == 'scripts/check_public_bundle.py': continue
    for pattern in patterns:
        if re.search(pattern, text): errors.append(f'Sensitive pattern: {name}')
if errors:
    print('\n'.join(errors), file=sys.stderr); sys.exit(1)
print(f'PASS: {len(set(filter(None, files)))} candidate files; no flagged paths or sensitive patterns. Human review still required.')
