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
        Override the default send_mail method to add better error handling.
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
        # Use the parent class method to send confirmation email
        # This ensures compatibility with Django Allauth's expected behavior
        try:
            # Call the parent method which handles all the complexity
            super().send_confirmation_mail(request, emailconfirmation, signup)

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
            # Get the site URL safely
            site_url = getattr(settings, 'SITE_URL', 'https://yitplms.onrender.com')

            # Prepare context for welcome email
            ctx = {
                'user': user,
                'site_name': 'Youth Impact Training Programme',
                'dashboard_url': f"{site_url}/dashboard/",
                'courses_url': f"{site_url}/courses/",
                'support_url': f"{site_url}/admin-support/",
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
            pass
    
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
            pass
    
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Construct the email confirmation URL.
        """
        # Use the parent class method to get the URL
        url = super().get_email_confirmation_url(request, emailconfirmation)

        # In production, the URL should already be correct
        # No need to modify it unless there are specific domain issues
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
        user = super().save_user(request, user, form, commit=commit)

        # Create user profile if it doesn't exist and user is saved
        if commit:
            try:
                from accounts.models import UserProfile
                UserProfile.objects.get_or_create(user=user)
                logger.info(f"User profile created for {user.email}")
            except Exception as e:
                logger.error(f"Failed to create user profile for {user.email}: {str(e)}")
                # Don't fail the user creation process if profile creation fails
                pass

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
