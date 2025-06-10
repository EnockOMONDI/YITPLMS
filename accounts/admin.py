from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, UserSkill, UserGoal


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom user admin interface
    """
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'profile_picture', 'bio', 'date_of_birth', 'location', 'timezone')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User profile admin interface
    """
    list_display = ('user', 'role', 'organization', 'experience_level', 'created_at')
    list_filter = ('role', 'experience_level', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'organization')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """
    User skill admin interface
    """
    list_display = ('user', 'skill_name', 'proficiency_level', 'verified', 'created_at')
    list_filter = ('proficiency_level', 'verified', 'created_at')
    search_fields = ('user__email', 'skill_name')
    readonly_fields = ('created_at',)


@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    """
    User goal admin interface
    """
    list_display = ('user', 'title', 'status', 'progress_percentage', 'target_date', 'created_at')
    list_filter = ('status', 'created_at', 'target_date')
    search_fields = ('user__email', 'title')
    readonly_fields = ('created_at', 'updated_at')

