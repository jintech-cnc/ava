from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'telephone', 'langue_preferee')
    list_filter = ('role', 'langue_preferee')
    search_fields = ('user__username', 'user__email')
