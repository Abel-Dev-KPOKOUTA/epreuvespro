from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'classe', 'date_inscription', 'is_staff']
    list_filter = ['classe', 'is_staff', 'is_active', 'date_inscription']
    search_fields = ['email', 'first_name', 'last_name', 'telephone']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('telephone', 'classe', 'photo')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('email', 'telephone', 'classe')}),
    )