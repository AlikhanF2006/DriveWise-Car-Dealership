"""Run the actual Django development server and save its real console output."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
folder = root / '.evidence'
folder.mkdir(exist_ok=True)
log_file = folder / 'django_server.txt'
command = [sys.executable, '-u', str(root / 'manage.py'), 'runserver', '--noreload', '127.0.0.1:8000']
print('Real Django console output is saved to:', log_file, flush=True)
try:
    with log_file.open('w', encoding='utf-8') as log:
        with subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                              errors='replace', bufsize=1) as process:
            for line in process.stdout:
                print(line, end='', flush=True)
                log.write(line)
                log.flush()
            sys.exit(process.wait())
except KeyboardInterrupt:
    print('Server stopped.')
