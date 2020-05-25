#!/bin/bash

RETRIES=15

until [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
  sleep 1
done

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

python manage.py crontab add

cron -f &

# Load fixtures that will create all default users.
echo "Load Fixtures"
python manage.py initdata

# Create admin user
echo "Create Admin"
echo "from users.models import User; User.objects.create_superuser(username='admin', email='admin@admin.com', password='password')" | python manage.py shell

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
