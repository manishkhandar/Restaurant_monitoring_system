# Restaurant_monitoring_system

# Installation
To install the required packages, run the following command in the project directory:

    pip install -r requirements.txt
    
# Usage
To start the server, run the following command in the project directory:

    python manage.py runserver

# API details
* uploacsv/
  * open 'ulr'/uploadcsv/ in browser. upload three require csv file and submit
  
* api/trigger_report/?report_id={report_id}
  * No input 
  * Output - report_id (random string) 
  * report_id will be used for polling the status of report completion
  
* api/get_report/
  * Input params - report_id
  * Output
    - if report generation is not complete, return “Running” as the output
    - if report generation is complete, return “Complete” along with the CSV file with the schema described above.
    
    
# File Structure

        api/
        
          ├── templates/
        
          ├── routes/
          
          ├── controller/
          
          ├── models/
          
          └── services/
        ```
* created director for each and everything. can add more file according to need.


