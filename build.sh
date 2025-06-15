#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting build process for Entrepreneurship LMS..."

# Modify pip.conf to use a faster index
echo "📦 Configuring pip for faster package installation..."
pip config set global.index-url https://pypi.org/simple/
pip config set global.trusted-host pypi.org

# Upgrade pip to the latest version
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies with PostgreSQL adapter compatibility check
echo "📚 Installing Python dependencies from requirements.txt..."
echo "🐍 Python version: $(python --version)"

# Try installing with psycopg2-binary first
if pip install -r requirements.txt; then
    echo "✅ Successfully installed dependencies with psycopg2-binary"
else
    echo "⚠️ Failed to install psycopg2-binary, trying psycopg3 alternative..."
    pip install -r requirements-psycopg3.txt
    echo "✅ Successfully installed dependencies with psycopg3"
fi

# Verify Django installation
echo "🔍 Verifying Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Verify PostgreSQL adapter installation
echo "🗄️ Verifying PostgreSQL adapter..."
python -c "
import sys
print(f'🐍 Python version: {sys.version}')

# Try psycopg2 first
try:
    import psycopg2
    print(f'✅ psycopg2 version: {psycopg2.__version__}')
    print(f'✅ PostgreSQL adapter (psycopg2) loaded successfully')
except ImportError:
    # Try psycopg3 as fallback
    try:
        import psycopg
        print(f'✅ psycopg version: {psycopg.__version__}')
        print(f'✅ PostgreSQL adapter (psycopg3) loaded successfully')
    except ImportError as e:
        print(f'❌ No PostgreSQL adapter found: {e}')
        print('🔧 This will cause Django to fail. Check requirements.txt')
        sys.exit(1)
"

# Run Django system checks
echo "🔧 Running Django system checks..."
python manage.py check --deploy

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create cache table (if using database cache)
echo "💾 Creating cache table..."
python manage.py createcachetable || echo "Cache table already exists or not configured"

# Create superuser if it doesn't exist (for LMS admin)
echo "👤 Setting up admin user for Entrepreneurship LMS..."
python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

# Admin credentials for LMS
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@yitp.com')
admin_password = os.environ.get('ADMIN_PASSWORD', 'yitpadmin')
admin_username = os.environ.get('ADMIN_USERNAME', 'yitpadmin')

try:
    if not User.objects.filter(email=admin_email).exists():
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='LMS',
            last_name='Administrator'
        )
        print(f'✅ Superuser created: {admin_email} (username: {admin_username})')
    else:
        print(f'ℹ️ Superuser already exists: {admin_email}')
except IntegrityError as e:
    print(f'⚠️ Error creating superuser: {e}')
except Exception as e:
    print(f'❌ Unexpected error: {e}')
EOF

# Load initial data (if fixtures exist)
echo "📊 Loading initial data..."
if [ -f "fixtures/initial_data.json" ]; then
    python manage.py loaddata fixtures/initial_data.json
    echo "✅ Initial data loaded successfully"
else
    echo "ℹ️ No initial data fixtures found"
fi

# Create sample course categories (if none exist)
echo "📚 Setting up initial course categories..."
python manage.py shell << EOF
from courses.models import Category

categories = [
    {'name': 'Business Fundamentals', 'slug': 'business-fundamentals', 'description': 'Core business concepts and principles'},
    {'name': 'Marketing & Sales', 'slug': 'marketing-sales', 'description': 'Marketing strategies and sales techniques'},
    {'name': 'Finance & Accounting', 'slug': 'finance-accounting', 'description': 'Financial management and accounting basics'},
    {'name': 'Leadership & Management', 'slug': 'leadership-management', 'description': 'Leadership skills and team management'},
    {'name': 'Technology & Innovation', 'slug': 'technology-innovation', 'description': 'Tech trends and innovation strategies'},
    {'name': 'Legal & Compliance', 'slug': 'legal-compliance', 'description': 'Business law and regulatory compliance'},
]

created_count = 0
for cat_data in categories:
    category, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={
            'name': cat_data['name'],
            'description': cat_data['description'],
            'is_active': True,
            'sort_order': created_count + 1
        }
    )
    if created:
        created_count += 1
        print(f'✅ Created category: {category.name}')
    else:
        print(f'ℹ️ Category already exists: {category.name}')

print(f'📚 Course categories setup complete. Created {created_count} new categories.')
EOF

# Verify deployment readiness
echo "🔍 Verifying deployment readiness..."

# Check if static files were collected
if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
    echo "✅ Static files collected successfully"
else
    echo "⚠️ Warning: Static files directory is empty"
fi

# Check database connectivity
echo "🗄️ Testing database connectivity..."
python manage.py shell << EOF
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)
EOF

# Display build summary
echo "📋 Build Summary:"
echo "  🐍 Python version: $(python --version)"
echo "  🌐 Django version: $(python -c 'import django; print(django.get_version())')"
echo "  📦 Installed packages: $(pip list | wc -l) packages"
echo "  📁 Static files: $(find staticfiles -type f 2>/dev/null | wc -l) files"
echo "  🗄️ Database: Connected and migrated"

echo "🎉 Build completed successfully for Entrepreneurship LMS!"
echo "🚀 Ready for deployment..."
