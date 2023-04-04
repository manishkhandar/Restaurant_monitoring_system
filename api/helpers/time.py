from api.models.models import *
from datetime import datetime, timedelta, timezone, time
import pytz
from pytz import timezone


def get_current_time(timezone_name):
    tz = pytz.timezone(timezone_name)
    return datetime.now(tz)


def compute_uptime_downtime(store_id):
    store_timezone = get_store_timezone(store_id)
    business_hours = get_store_business_hours(store_id)
    active_status = get_active_status(store_id)
    active_status_local = []
    for row in active_status:
        local = row.timestamp_utc.astimezone(pytz.timezone(store_timezone))
        active_status_local.append({
            'store_id': row.store_id,
            'status': row.status,
            'timestamp_local': local
        })
    current_time = get_current_time(store_timezone)

    hour_range = (current_time - timedelta(hours=1), current_time)
    day_range = (current_time - timedelta(days=1), current_time)
    week_range = (current_time - timedelta(weeks=1), current_time)

    uptime_last_hour, downtime_last_hour = \
        calculate_uptime_downtime_hours(active_status_local, hour_range, business_hours, store_timezone)
    uptime_last_day, downtime_last_day = \
        calculate_uptime_downtime_day(active_status_local, day_range, business_hours, store_timezone)
    uptime_last_week, downtime_last_week = \
        calculate_uptime_downtime_week(active_status_local, week_range, business_hours, store_timezone)

    return uptime_last_hour, uptime_last_day, uptime_last_week,\
        downtime_last_hour, downtime_last_day, downtime_last_week


def get_active_status(store_id):
    active_status = Store.objects.filter(store_id=store_id).order_by('timestamp_utc')
    return active_status


def get_store_timezone(store_id):
    tz = Timezone.objects.filter(store_id=store_id)
    if timezone:
        return tz[0].timezone_str
    return "UTC"


def get_store_business_hours(store_id):
    business_hours = BusinessHours.objects.filter(store_id=store_id).all()
    if business_hours.exists():
        return business_hours
    else:
        start = time(hour=00, minute=00, second=00, microsecond=000000)
        end = time(hour=23, minute=59, second=59, microsecond=990000)
        business_hours = [
            BusinessHours(store_id=store_id, day=0, start_time_local=start, end_time_local=end),
            BusinessHours(store_id=store_id, day=1, start_time_local=start, end_time_local=end),
            BusinessHours(store_id=store_id, day=2, start_time_local=start, end_time_local=end),
            BusinessHours(store_id=store_id, day=3, start_time_local=start, end_time_local=end),
            BusinessHours(store_id=store_id, day=4, start_time_local=start, end_time_local=end),
            BusinessHours(store_id=store_id, day=5, start_time_local=start, end_time_local=end),
            BusinessHours(store_id=store_id, day=6, start_time_local=start, end_time_local=end),
        ]
        BusinessHours.objects.bulk_create(business_hours)
    return business_hours


def get_business_hours_local(start_time_local, end_time_local, current_time, store_timezone):
    local_tz = pytz.timezone(store_timezone)
    start_of_day = \
        datetime(current_time.year, current_time.month, current_time.day, 00, 00, 00, 000000)
    start = datetime.combine(start_of_day ,start_time_local)
    start = local_tz.localize(start)
    end = datetime.combine(start_of_day,end_time_local)
    end = local_tz.localize(end)
    return start, end


def compare_dates(date1, date2):
    date1 = date1.date()
    date2 = date2.date()
    return date1 == date2


def convert_to_hours_and_mins(time):
    total_secs = time.total_seconds()
    total_days = time.days
    hours, remainder = divmod(total_secs - (total_days * 24 * 3600), 3600)
    mins, seconds = divmod(remainder, 60)
    mins += hours * 60
    return hours, mins


def calculate_uptime_downtime_hours(activity_status, time_range, business_hours, store_timezone):
    print(store_timezone)
    uptime = timedelta()
    downtime = timedelta()
    total_duration = timedelta(0)
    last_status = None

    for bh in business_hours:
        start_time_local, end_time_local = \
            get_business_hours_local(bh.start_time_local, bh.end_time_local, time_range[0], store_timezone)

        if bh.day == time_range[0].weekday():
            total_duration += max(timedelta(0),
                                  min(time_range[1], end_time_local) - max(time_range[0], start_time_local))
        for item in activity_status:
            if bh.day != time_range[0].weekday():
                continue

            if time_range[0] <= item['timestamp_local'] <= time_range[1]:
                if item['status'] == 'active':
                    if last_status != 'active':
                        uptime += max(timedelta(0),
                                      min(end_time_local,item['timestamp_local']) - max(time_range[0], start_time_local))
                    last_status = 'active'
                else:
                    if last_status == 'active':
                        downtime += item['timestamp_local'] - max(time_range[0], start_time_local)
                    last_status = 'inactive'

    uptime_hours, uptime_mins = convert_to_hours_and_mins(uptime)
    downtime_hours, downtime_mins = convert_to_hours_and_mins(downtime)
    duration_hours, duration_mins = convert_to_hours_and_mins(total_duration)

    return uptime_mins, downtime_mins

def calculate_uptime_downtime_day(activity_status, time_range, business_hours, store_timezone):
    uptime = timedelta()
    downtime = timedelta()
    last_status = None
    total_duration = timedelta(0)

    first_half = [time_range[0], time_range[1]]
    second_half = [time_range[1], time_range[1]]
    local_tz = pytz.timezone(store_timezone)
    two_partitions = False

    if time_range[0].weekday() != time_range[1].weekday():
        first_half[1] = local_tz.localize(
            datetime(time_range[0].year, time_range[0].month, time_range[0].day, 23, 59, 59, 999999))
        second_half[0] = local_tz.localize(
            datetime(time_range[1].year, time_range[1].month, time_range[1].day, 00, 00, 00, 000000))
        two_partitions = True

    for bh in business_hours:
        if bh.day == first_half[0].weekday():
            start_time_local, end_time_local = \
                get_business_hours_local(bh.start_time_local, bh.end_time_local, first_half[0], store_timezone)
            total_duration += max(timedelta(0),
                                  min(first_half[1], end_time_local) - max(first_half[0], start_time_local))

            pre_date = -1
            for item in activity_status:
                if bh.day == first_half[0].weekday():
                    if first_half[0] <= item['timestamp_local'] <= first_half[1]:
                        if item['status'] == 'active':
                            if last_status != 'active':
                                if pre_date!=-1 and compare_dates(item['timestamp_local'], pre_date):
                                    uptime += min(end_time_local, item['timestamp_local']) - max(pre_date, start_time_local)
                                else:
                                    uptime += min(end_time_local,item['timestamp_local']) - max(first_half[0], start_time_local)
                                    pre_date = item['timestamp_local']
                                last_status = 'active'
                            else:
                                if last_status == 'active':
                                    downtime += item['timestamp_local'] - max(first_half[0], start_time_local)
                                last_status = 'inactive'

        if two_partitions==True and bh.day == second_half[0].weekday():
            start_time_local, end_time_local = \
                get_business_hours_local(bh.start_time_local, bh.end_time_local, second_half[0], store_timezone)

            total_duration += max(timedelta(0),
                                  min(second_half[1], end_time_local) - max(second_half[0], start_time_local))
            pre_date = -1
            for item in activity_status:
                if second_half[0] <= item['timestamp_local'] <= second_half[1]:
                    if item['status'] == 'active':
                        if last_status != 'active':
                            if pre_date != -1 and compare_dates(item['timestamp_local'], pre_date):
                                uptime += min(end_time_local,item['timestamp_local']) - max(pre_date, start_time_local)
                            else:
                                uptime += min(end_time_local,item['timestamp_local']) - max(second_half[0], start_time_local)
                            pre_date = item['timestamp_local']
                            last_status = 'active'
                    else:
                        if last_status == 'active':
                            downtime += item['timestamp_local'] - max(second_half[0], start_time_local)
                        last_status = 'inactive'

    uptime_hours, uptime_mins = convert_to_hours_and_mins(uptime)
    downtime_hours, downtime_mins = convert_to_hours_and_mins(downtime)
    duration_hours, duration_mins = convert_to_hours_and_mins(total_duration)
    return uptime_hours, downtime_hours


def calculate_uptime_downtime_week(activity_status, time_range, business_hours, store_timezone):
    uptime = 0
    downtime = 0
    start = time_range[0]
    end = time_range[0] + timedelta(days=1)
    current_range = (start ,end)
    while current_range[1] <= time_range[1]:
        upt, downt = calculate_uptime_downtime_day(activity_status, current_range, business_hours, store_timezone)
        uptime += upt
        downtime += downt
        current_range = (current_range[0] + timedelta(days=1), current_range[1] + timedelta(days=1))

    return uptime, downtime

