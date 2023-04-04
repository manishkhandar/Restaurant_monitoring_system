import json
from api.models.models import Store, Report
from api.helpers.time import compute_uptime_downtime
from datetime import datetime


def generate_report(report_id):
    # Create new report object and add it to the database
    report = Report(report_id=report_id, status='Running', data='')

    # Generate report data
    report_data = []
    stores = Store.objects.all()
    unique_stores = stores.values('store_id').distinct()
    for store in unique_stores:
        uptime_last_hour, uptime_last_day, update_last_week, downtime_last_hour,\
            downtime_last_day, downtime_last_week = compute_uptime_downtime(store['store_id'])
        report_data.append({
            'store_id': store['store_id'],
            'uptime_last_hour': uptime_last_hour,
            'uptime_last_day': uptime_last_day,
            'uptime_last_week': update_last_week,
            'downtime_last_hour': downtime_last_hour,
            'downtime_last_day': downtime_last_day,
            'downtime_last_week': downtime_last_week
        })

    report.status = 'Complete'
    report.completed_at = datetime.utcnow()

    # Update report data object with generated report data
    report.data = json.dumps(report_data)
    report.save()
    return report


def get_report_status_from_db(report_id):
    report = Report.objects.filter(report_id=report_id).first()
    if report is None:
        return None
    else:
        return report.status


def get_report_data_from_db(report_id):
    """
    Retrieves the report data from the database for a given report_id.
    """
    report = Report.objects.filter(report_id=report_id).first()

    if report is None:
        raise ValueError(f"No report found for report_id: {report_id}")

    return json.loads(report.data)