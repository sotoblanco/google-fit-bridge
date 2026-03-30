"""@bruin

name: ingestion.fitness_data
type: python
image: python:3.11
connection: gcp-default

materialization:
  type: table
  strategy: append

columns:
  - name: data_type
    type: string
    description: "Type of fitness metric (e.g. steps, heart_rate, sleep)"
  - name: value
    type: float
    description: "Value of the fitness metric"
  - name: start_time  
    type: timestamp
    description: "Start time of the fitness metric"
  - name: end_time
    type: timestamp
    description: "End time of the fitness metric"
  - name: extracted_at
    type: timestamp
    description: "Timestamp of extraction"

@bruin"""

def materialize():
    # return final_dataframe
    import os
    from datetime import datetime
    import pandas as pd
    start_date = os.getenv("BRUIN_START_DATE")
    end_date = os.getenv("BRUIN_END_DATE")
    extracted_at = datetime.utcnow()

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    ns_start = int(start_dt.timestamp() * 1e9)
    ns_end = int(end_dt.timestamp() * 1e9)

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'token.json')
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    from googleapiclient.discovery import build

    service = build('fitness', 'v1', credentials=creds)

    response_steps = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId='derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
        datasetId=f'{ns_start}-{ns_end}'
    ).execute()

    response_heart_rate = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId='derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm',
        datasetId=f'{ns_start}-{ns_end}'
    ).execute()
    
    response_sleep = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId='derived:com.google.sleep.segment:com.google.android.gms:merged',
        datasetId=f'{ns_start}-{ns_end}'
    ).execute()

    rows = []
    for point in response_steps['point']:
        start = datetime.utcfromtimestamp(int(point['startTimeNanos']) / 1e9)  # nanoseconds → seconds
        end = datetime.utcfromtimestamp(int(point['endTimeNanos']) / 1e9)
        value = point['value'][0].get('intVal', 0)  # steps use intVal
        rows.append({'data_type': 'steps', 'extracted_at': extracted_at, 'start_time': start, 'end_time': end, 'value': value})
    
    for point in response_heart_rate['point']:
        start = datetime.utcfromtimestamp(int(point['startTimeNanos']) / 1e9)  # nanoseconds → seconds
        end = datetime.utcfromtimestamp(int(point['endTimeNanos']) / 1e9)
        value = point['value'][0].get('fpVal', 0)  # heart rate uses fpVal
        rows.append({'data_type': 'heart_rate', 'extracted_at': extracted_at, 'start_time': start, 'end_time': end, 'value': value})
    
    for point in response_sleep['point']:
        start = datetime.utcfromtimestamp(int(point['startTimeNanos']) / 1e9)  # nanoseconds → seconds
        end = datetime.utcfromtimestamp(int(point['endTimeNanos']) / 1e9)
        value = point['value'][0].get('intVal', 0)  # sleep uses intVal
        rows.append({'data_type': 'sleep', 'extracted_at': extracted_at, 'start_time': start, 'end_time': end, 'value': value})

    return pd.DataFrame(rows)


