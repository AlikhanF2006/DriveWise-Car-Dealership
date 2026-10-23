"""Create local superuser with a randomly generated password. Never committed."""
import secrets
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates an administrator for local screenshots, records credentials only locally.'

    def handle(self, *args, **kwargs):
        username = 'localadmin'
        user_model = get_user_model()
        path = Path(settings.BASE_DIR) / '.local_admin_credentials.txt'
        if user_model.objects.filter(username=username).exists():
            self.stdout.write('Local admin already exists. Credentials were not changed.')
            return
        password = secrets.token_urlsafe(18) + 'A1!'
        user_model.objects.create_superuser(username, 'localadmin@example.invalid', password)
        path.write_text(f'LOCAL DEVELOPMENT ONLY\nusername: {username}\npassword: {password}\n', encoding='utf-8')
        self.stdout.write(self.style.SUCCESS('Created local administrator. Read .local_admin_credentials.txt (gitignored).'))
