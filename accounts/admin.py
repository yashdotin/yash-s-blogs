from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_editor', 'is_author')
	fieldsets = DjangoUserAdmin.fieldsets + (
		('Roles', {'fields': ('is_editor', 'is_author')}),
	)