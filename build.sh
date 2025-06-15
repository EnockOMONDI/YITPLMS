#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process for Entrepreneurship LMS..."

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run Django checks
python manage.py check

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()

admin_email = os.environ.get('ADMIN_EMAIL', 'admin@entrepreneurship-lms.com')
admin_password = os.environ.get('ADMIN_PASSWORD', 'LMSAdmin2024!')

if not User.objects.filter(email=admin_email).exists():
    User.objects.create_superuser(
        username='lmsadmin',
        email=admin_email,
        password=admin_password,
        first_name='LMS',
        last_name='Administrator'
    )
    print(f'Superuser created: {admin_email}')
else:
    print(f'Superuser already exists: {admin_email}')
EOF

echo "Build completed successfully for Entrepreneurship LMS!"
