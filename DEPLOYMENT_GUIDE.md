# Django Entrepreneurship LMS - Deployment Guide

## 🚀 Production Deployment Setup

This guide covers deploying the Django Entrepreneurship LMS to production using PostgreSQL and cloud hosting platforms.

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL database (cloud or self-hosted)
- Git repository access
- Cloud hosting account (Render, Heroku, DigitalOcean, etc.)

## 🗄️ Database Configuration

### PostgreSQL Setup

The application is configured to use PostgreSQL in production. You have several options:

#### Option 1: Neon (Recommended for quick setup)
- Free tier available with 0.5GB storage
- Automatic backups and scaling
- Already configured in this project

#### Option 2: Other PostgreSQL providers
- AWS RDS
- Google Cloud SQL
- DigitalOcean Managed Databases
- Heroku Postgres

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Configuration
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Security Settings
SECURE_SSL_REDIRECT=True

# Logging
DJANGO_LOG_LEVEL=INFO

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🌐 Deployment Platforms

### Option 1: Render (Recommended)

1. **Connect Repository**
   - Fork/clone this repository
   - Connect your GitHub account to Render
   - Create a new Web Service

2. **Configuration**
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn entrepreneurship_lms.wsgi:application`
   - Environment: Python 3.12

3. **Environment Variables**
   - Add all variables from the `.env` example above
   - Render will auto-generate `SECRET_KEY` if you don't provide one

4. **Database**
   - Use the provided Neon PostgreSQL connection string
   - Or create a new PostgreSQL database on Render

### Option 2: Heroku

1. **Install Heroku CLI**
   ```bash
   # Install Heroku CLI
   npm install -g heroku
   ```

2. **Deploy**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create app
   heroku create your-app-name
   
   # Add PostgreSQL addon
   heroku addons:create heroku-postgresql:mini
   
   # Set environment variables
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   
   # Deploy
   git push heroku main
   
   # Run migrations
   heroku run python manage.py migrate
   ```

### Option 3: DigitalOcean App Platform

1. **Create App**
   - Connect your repository
   - Choose Python as the environment

2. **Configuration**
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn entrepreneurship_lms.wsgi:application`

3. **Database**
   - Create a managed PostgreSQL database
   - Add the connection string to environment variables

## 🔧 Production Settings

The application includes production-ready settings:

### Security Features
- HTTPS enforcement
- Secure cookies
- XSS protection
- Content type sniffing protection
- HSTS headers

### Static Files
- WhiteNoise for static file serving
- Compressed and cached static files
- CDN-ready configuration

### Database
- Connection pooling
- Query optimization
- Automatic migrations

## 📦 Dependencies

All production dependencies are included in `requirements.txt`:

```txt
Django==5.2.2
psycopg2-binary==2.9.9
gunicorn==22.0.0
whitenoise==6.7.0
django-environ==0.11.2
dj-database-url==2.2.0
django-cors-headers==4.4.0
djangorestframework==3.15.2
django-allauth==64.0.0
django-crispy-forms==2.3
crispy-bootstrap5==2024.2
Pillow==10.4.0
```

## 🚀 Deployment Steps

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Prepare for production deployment"
   git push origin main
   ```

2. **Set Environment Variables**
   - Configure all required environment variables
   - Ensure `DEBUG=False` in production
   - Set proper `ALLOWED_HOSTS`

3. **Database Migration**
   ```bash
   python manage.py migrate
   ```

4. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Create Superuser** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

## 🔍 Testing Deployment

1. **Health Check**
   - Visit your deployed URL
   - Check that the home page loads
   - Verify database connectivity

2. **Admin Access**
   - Go to `/admin/`
   - Login with superuser credentials
   - Verify admin functionality

3. **API Endpoints**
   - Test `/api/` endpoints
   - Verify authentication works

## 📊 Monitoring

### Logging
- Application logs are configured for production
- Error tracking with detailed stack traces
- Performance monitoring ready

### Database Monitoring
- Query performance tracking
- Connection pool monitoring
- Automatic backup verification

## 🔒 Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` generated
- ✅ HTTPS enforced
- ✅ Secure headers configured
- ✅ Database credentials secured
- ✅ CORS properly configured
- ✅ Static files served securely

## 🆘 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` configuration

2. **Database Connection Errors**
   - Verify `DATABASE_URL` format
   - Check database server accessibility
   - Ensure SSL requirements are met

3. **CORS Errors**
   - Update `CORS_ALLOWED_ORIGINS`
   - Check domain configuration

4. **500 Internal Server Error**
   - Check application logs
   - Verify environment variables
   - Run `python manage.py check --deploy`

### Support

For deployment issues:
1. Check the application logs
2. Verify environment variables
3. Test database connectivity
4. Review security settings

## 📈 Scaling

The application is ready for scaling:
- Database connection pooling
- Static file CDN integration
- Horizontal scaling support
- Load balancer ready

---

**🎉 Your Django Entrepreneurship LMS is now ready for production deployment!**

Access your application at: http://127.0.0.1:8000/ (development) or your production domain.
