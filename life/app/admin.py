from django.contrib import admin

from life.app.models import Job
from django_celery_beat.models import SolarSchedule, PeriodicTask, IntervalSchedule, CrontabSchedule, ClockedSchedule
from allauth.account.models import EmailAddress
from django_rest_passwordreset.models import ResetPasswordToken

admin.site.site_header = "Life Administration"
admin.site.site_title = "Coronasafe Network"
admin.site.index_title = "Life"

for model in [
    SolarSchedule,
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    ClockedSchedule,
    EmailAddress,
    ResetPasswordToken,
]:
    admin.site.unregister(model)


class JobAdmin(admin.ModelAdmin):
    actions = ["silent_delete"]

    def silent_delete(self, request, queryset):
        queryset.delete()


admin.site.register(Job, JobAdmin)
