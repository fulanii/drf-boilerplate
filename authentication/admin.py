from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, EmailVerificationModel, PasswordResetCodeModel

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username') 

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'is_verified')}), 
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2') 
        }),
    )

    list_display = ('id', 'email', 'username', 'is_verified', 'date_joined', 'is_superuser', 'is_staff')

    search_fields = ('email', 'username')

    list_filter = ('is_staff', 'is_active', 'is_verified')

    ordering = ('email',)

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EmailVerificationModel)
admin.site.register(PasswordResetCodeModel)