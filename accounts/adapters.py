from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email
import logging

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for the Youth Impact Training Programme.
    Handles email sending and user account management.
    """
    
    def send_mail(self, template_prefix, email, context):
        """
        Override the default send_mail method to use our custom email templates
        and add better error handling.
        """
        try:
            # Call the parent method first
            super().send_mail(template_prefix, email, context)
            logger.info(f"Email sent successfully to {email} with template {template_prefix}")
        except Exception as e:
            logger.error(f"Failed to send email to {email} with template {template_prefix}: {str(e)}")
            # Re-raise the exception so the user knows there was an issue
            raise
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send email confirmation with custom template and enhanced context.
        """
        current_site = self.get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        
        # Enhanced context for email templates
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
            "signup": signup,
            "request": request,
        }
        
        # Add user's first name if available
        user = emailconfirmation.email_address.user
        if hasattr(user, 'first_name') and user.first_name:
            ctx['user_first_name'] = user.first_name
        
        try:
            # Send the confirmation email
            self.send_mail("account/email/email_confirmation", 
                          emailconfirmation.email_address.email, ctx)
            
            logger.info(f"Email confirmation sent to {emailconfirmation.email_address.email}")
            
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {emailconfirmation.email_address.email}: {str(e)}")
            raise
    
    def send_welcome_email(self, user):
        """
        Send a welcome email after successful email confirmation.
        This is called manually after email confirmation.
        """
        try:
            # Prepare context for welcome email
            ctx = {
                'user': user,
                'site_name': 'Youth Impact Training Programme',
                'dashboard_url': f"{settings.SITE_URL}/dashboard/",
                'courses_url': f"{settings.SITE_URL}/courses/",
                'support_url': f"{settings.SITE_URL}/admin-support/",
            }
            
            # Render email content
            subject = "Welcome to Youth Impact Training Programme!"
            html_message = render_to_string('account/email/welcome_message.html', ctx)
            plain_message = strip_tags(html_message)
            
            # Send welcome email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email(user)],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Welcome email sent to {user_email(user)}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_email(user)}: {str(e)}")
            # Don't raise exception for welcome email failures
            # as the main registration process should still succeed
    
    def confirm_email(self, request, email_address):
        """
        Override email confirmation to send welcome email after confirmation.
        """
        # Call the parent method to handle the confirmation
        super().confirm_email(request, email_address)
        
        # Send welcome email after successful confirmation
        try:
            self.send_welcome_email(email_address.user)
        except Exception as e:
            logger.error(f"Welcome email failed for user {email_address.user}: {str(e)}")
            # Don't fail the confirmation process if welcome email fails
    
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Construct the email confirmation URL.
        """
        url = super().get_email_confirmation_url(request, emailconfirmation)
        
        # Ensure we use the correct domain in production
        if hasattr(settings, 'SITE_URL') and settings.SITE_URL:
            # Replace the domain part with our configured site URL
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(url)
            site_parsed = urlparse(settings.SITE_URL)
            
            # Reconstruct URL with correct domain
            url = urlunparse((
                site_parsed.scheme,
                site_parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
        
        return url
    
    def get_login_redirect_url(self, request):
        """
        Return the URL to redirect to after successful login.
        """
        # Check if user has completed their profile
        user = request.user
        if hasattr(user, 'profile'):
            try:
                profile = user.profile
                # If profile is incomplete, redirect to profile page
                if not profile.bio or not profile.date_of_birth:
                    return '/profile/'
            except:
                # If no profile exists, redirect to profile page
                return '/profile/'
        
        # Default redirect to dashboard
        return '/dashboard/'
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user with additional processing.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Add any additional user processing here
        # For example, setting default preferences
        
        if commit:
            user.save()
            
            # Create user profile if it doesn't exist
            try:
                from accounts.models import UserProfile
                UserProfile.objects.get_or_create(user=user)
                logger.info(f"User profile created for {user.email}")
            except Exception as e:
                logger.error(f"Failed to create user profile for {user.email}: {str(e)}")
        
        return user
    
    def get_from_email(self):
        """
        Return the from email address for account-related emails.
        """
        return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    
    def format_email_subject(self, subject):
        """
        Format email subject with site prefix.
        """
        prefix = getattr(settings, 'ACCOUNT_EMAIL_SUBJECT_PREFIX', '')
        if prefix:
            return f"{prefix}{subject}"
        return subject
