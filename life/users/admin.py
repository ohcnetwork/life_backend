import csv

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from life.users.forms import UserChangeForm, UserCreationForm
from life.users.models import District, LocalBody, Ward, State

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        ("User", {"fields": ("local_body", "district", "state", "phone_number", "gender", "age", "verified",)},),
    ) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "is_superuser"]
    search_fields = ["first_name", "last_name"]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    pass


@admin.register(LocalBody)
class LocalBodyAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    autocomplete_fields = ["local_body"]

