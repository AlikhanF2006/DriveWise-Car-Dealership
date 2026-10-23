"""Run REAL curl.exe requests against a local server and capture output.
Files under .evidence are ignored by Git. Outputs are not fabricated.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.evidence'
OUT.mkdir(exist_ok=True)
CURL = shutil.which('curl.exe') or shutil.which('curl')
BASE = 'http://127.0.0.1:8000'

if not CURL:
    sys.exit('curl.exe missing. On Windows 10/11 it is normally available.')
try:
    urlopen(BASE + '/api/dealerships/', timeout=4).read()
except Exception as exc:
    sys.exit(f'Django server is not running on port 8000: {exc}\nStart RUN_SERVER.bat, then run this again.')

print(f'Writing genuine curl requests/responses to {OUT}')

def run(filename, endpoint, *args):
    command = [CURL, '-sS', '-i', '--max-time', '10', *args, BASE + endpoint]
    display = 'curl.exe ' + ' '.join(f'"{x}"' if ' ' in x else x for x in command[1:])
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (OUT / (filename + '.txt')).write_text(f'$ {display}\n\n{result.stdout}\n{result.stderr}', encoding='utf-8')
    print(filename, 'OK' if result.returncode == 0 else 'FAILED')
    return result

run('getalldealers', '/api/dealerships/')
run('getdealerreviews', '/api/reviews/dealer/1/')
run('getdealerbyid', '/api/dealerships/1/')
run('getdealersbyState', '/api/dealerships/state/KS/')
run('getallcarmakes', '/api/car-makes/')
run('analyzereview', '/api/sentiment/?text=Fantastic%20services')
# These are real requests, using Django's CSRF token and cookie jar.
from urllib.request import build_opener, HTTPCookieProcessor, Request
import http.cookiejar
jar = http.cookiejar.CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))
csrf = json.load(opener.open(BASE + '/api/auth/csrf/'))['csrfToken']
# curl's own cookie jar is needed for the login/logout sequence.
cookie_path = OUT / 'cookies.txt'
csrf_response = subprocess.run([CURL, '-sS', '-c', str(cookie_path), BASE + '/api/auth/csrf/'], capture_output=True, text=True)
if csrf_response.returncode != 0:
    sys.exit('Could not request CSRF cookie.')
csrf = json.loads(csrf_response.stdout)['csrfToken']
password = __import__('os').environ.get('DRIVEWISE_DEMO_PASSWORD', 'DemoPass2026!')
# Store masked command (avoid writing any passwords into the evidence folder).
def auth_run(filename, endpoint, payload):
    command = [CURL, '-sS', '-i', '-b', str(cookie_path), '-c', str(cookie_path),
               '-H', 'Content-Type: application/json', '-H', 'X-CSRFToken: ' + csrf,
               '-d', json.dumps(payload), BASE + endpoint]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    safe_payload = {**payload, 'password': '<REDACTED>'} if 'password' in payload else payload
    display = f'curl.exe -i -b cookies.txt -c cookies.txt -H "Content-Type: application/json" -H "X-CSRFToken: [LOCAL CSRF TOKEN]" -d {json.dumps(safe_payload)} {BASE + endpoint}'
    # Avoid storing session cookies or Set-Cookie response headers.
    response = result.stdout.split('\r\n\r\n')[-1] if '\r\n\r\n' in result.stdout else result.stdout.split('\n\n')[-1]
    (OUT / (filename + '.txt')).write_text(display + '\n\n' + response + '\n', encoding='utf-8')
    print(filename, 'OK' if result.returncode == 0 else 'FAILED')

auth_run('loginuser', '/api/auth/login/', {'username': 'demo', 'password': password})
# Django rotates the CSRF token at login; fetch a fresh one for logout.
csrf_response = subprocess.run([CURL, '-sS', '-b', str(cookie_path), '-c', str(cookie_path), BASE + '/api/auth/csrf/'], capture_output=True, text=True)
if csrf_response.returncode != 0:
    sys.exit('Could not refresh CSRF cookie after login.')
csrf = json.loads(csrf_response.stdout)['csrfToken']
auth_run('logoutuser', '/api/auth/logout/', {})
if cookie_path.exists():
    cookie_path.unlink()
print('\nFinished. Only submit outputs that match the Coursera instructions and your real running project.')
