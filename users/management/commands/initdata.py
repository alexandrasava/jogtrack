from django.core.management import BaseCommand, call_command
from django.contrib.auth.models import User
from users.models import User


class Command(BaseCommand):
    help = "Fill databasse with a set of users for testing purposes"

    def handle(self, *args, **options):
        call_command('loaddata', 'users')

        # Fixtures will set password in clear text, so we need to update
        # it as hash.
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()
