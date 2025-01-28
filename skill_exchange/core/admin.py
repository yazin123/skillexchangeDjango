# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Skill, UserSkill

admin.site.register(User, UserAdmin)
admin.site.register(Skill)
admin.site.register(UserSkill)