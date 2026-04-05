#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Applying database migrations..."
python manage.py makemigrations users proxy
python manage.py makemigrations
python manage.py migrate

echo "Checking/Creating Superuser..."
# We use Django's shell to safely check if the user exists before creating
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()

email = os.environ.get('SUPERUSER_EMAIL', 'admin@example.com    ')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print(f'Superuser {email} created successfully.')
else:
    print(f'Superuser {email} already exists. Skipping creation.')
"

echo "Starting Django development server..."
# The 'exec' command replaces the shell with the Django process
gunicorn inference_gateway.wsgi:application --bind 0.0.0.0:$PORT