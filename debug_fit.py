import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def debug_api():
    # 1. Load your existing token
    TOKEN_PATH = './token.json'
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    service = build('fitness', 'v1', credentials=creds)

    # 2. Define range (last 14 days)
    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(days=14)
    ns_range = f"{int(start_dt.timestamp() * 1e9)}-{int(end_dt.timestamp() * 1e9)}"
    
    print(f"--- Checking API from {start_dt.date()} up to {end_dt.date()} ---")

    # 3. List ALL Heart Rate Sources (to see if yours matches)
    sources = service.users().dataSources().list(userId='me').execute()
    hr_sources = [s for s in sources['dataSource'] if 'heart_rate' in s['dataType']['name'].lower()]
    
    print("\n[Found Heart Rate Sources]")
    for s in hr_sources:
        print(f" - ID: {s['dataStreamId']}")

    # 4. Inspect the specific source used in your pipeline
    target_id = 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm'
    print(f"\n[Inspecting Source: {target_id}]")
    
    try:
        data = service.users().dataSources().datasets().get(
            userId='me', dataSourceId=target_id, datasetId=ns_range
        ).execute()
        
        points = data.get('point', [])
        print(f"Total points found: {len(points)}")
        
        if points:
            print("\nLatest Point structure:")
            print(json.dumps(points[-1], indent=2))
        else:
            print("❌ No data points returned for this range.")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    debug_api()
