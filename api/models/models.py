import django
from django.db import models


class Store(models.Model):
    store_id = models.IntegerField(null=False)
    status = models.CharField(max_length=50)
    timestamp_utc = models.DateTimeField()


class BusinessHours(models.Model):
    store_id = models.IntegerField(null=False)
    day = models.IntegerField(null=True)
    start_time_local = models.TimeField(null=True)
    end_time_local = models.TimeField(null=True)


class Timezone(models.Model):
    store_id = models.IntegerField(primary_key=True)
    timezone_str = models.TextField(default='America/Chicago')


class Report(models.Model):
    report_id = models.CharField(primary_key=True, max_length=16)
    status = models.CharField(max_length=50)
    data = models.TextField(null=False)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    completed_at = models.DateTimeField(null=True)

