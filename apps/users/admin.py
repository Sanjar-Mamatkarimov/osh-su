from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Group

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Роль и Учебная группа', {'fields': ('role', 'group', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Роль и Учебная группа', {'fields': ('role', 'group', 'first_name', 'last_name')}),
    )
    list_display = ['username', 'first_name', 'last_name', 'role', 'group', 'is_staff']
    list_filter = ['role', 'group']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']