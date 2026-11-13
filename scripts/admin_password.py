"""Print only a password hash for server Secrets; never store the plaintext."""
import getpass
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.authoring import password_hash
password = getpass.getpass('Admin password (at least 16 characters): ')
if password != getpass.getpass('Repeat password: '):
    raise SystemExit('Passwords do not match')
print('AE_ADMIN_PASSWORD_HASH = "' + password_hash(password) + '"')
