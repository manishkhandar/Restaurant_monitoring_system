import csv
import secrets
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponse
from api.services.report import *
from api.models.models import *


@api_view(['POST'])
def trigger_report(request):
    try:
        report_id = secrets.token_urlsafe(16)
        generate_report(report_id)
        return JsonResponse({'report_id': report_id, 'message': 'Success', 'status_code':200})
    except Exception as e:
        return JsonResponse({'message': 'Failed', 'status_code': 500, 'Error': str(e)})


@api_view(['GET'])
def get_report(request):
    try:
        report_id = request.GET.get('report_id')
        print(report_id)
        if not report_id:
            return JsonResponse({'error': 'Missing report ID', "error_code": 400})

        report_status = get_report_status_from_db(report_id)
        if not report_status:
            return JsonResponse({'error': 'Invalid report ID', "error_code": 400})

        if report_status == 'Running':
            return JsonResponse({'status': 'Running', 'message': 'Success', 'error_code': 200})
        elif report_status == 'Complete':
            report_data = get_report_data_from_db(report_id)
            if report_data:
                csv_data = []
                for row in report_data:
                    if not csv_data:
                        csv_data.append(list(row.keys()))
                    csv_data.append(list(row.values()))

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="report.csv"'
                response['status'] = 'Complete'
                writer = csv.writer(response)
                for row in csv_data:
                    writer.writerow(row)
                return response
            else:
                return JsonResponse({'error': 'Failed to retrieve report data', "error_code": 400})
        else:
            return JsonResponse({'error': 'Invalid report status', "error_code": 400})
    except Exception as e:
        return JsonResponse({"error_message": "Something went Wrong", "Error_code": 500, "error": str(e)})


def uploadcsv(request):
    if request.method == 'POST':
        # Process the uploaded files
        for i in range(1, 4):
            myfile = request.FILES[f'myfile{i}']
            if i==1:
                x = 0
                for row in myfile:
                    if x==0:
                        x=1
                        continue
                    store_id, status, timestamp_utc_str = row.decode().strip().split(',')
                    timestamp_utc_str = timestamp_utc_str[:-4]
                    timestamp_utc = datetime.strptime(timestamp_utc_str, '%Y-%m-%d %H:%M:%S.%f')
                    s = Store(store_id=store_id, status=status, timestamp_utc=timestamp_utc)
                    s.save()
            elif i == 2:
                x=0
                for row in myfile:
                    if x == 0:
                        x = 1
                        continue
                    store_id, day, start_time_local, end_time_local = row.decode().strip().split(',')
                    br = BusinessHours(store_id=store_id, day=day, start_time_local=start_time_local,
                                       end_time_local=end_time_local)
                    br.save()
            elif i == 3:
                x=0
                for row in myfile:
                    if x == 0:
                        x=1
                        continue
                    store_id, timezone_str = row.decode().strip().split(',')
                    tz = Timezone(store_id=store_id, timezone_str=timezone_str)
                    print(tz.store_id)
                    tz.save()

        return render(request, 'success.html')
    else:
        return render(request, 'uploadcsv.html')
