#!/usr/bin/env python3
"""Fetch Drive activity for a Google Doc and output author, timestamp, and action."""
import os
import argparse
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build

# OAuth2 scopes for Drive Activity API
SCOPES = ['https://www.googleapis.com/auth/drive.activity.readonly']

def get_activity_service():
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.isfile(creds_path):
        raise FileNotFoundError(
            'Service account credentials not found. '
            'Set GOOGLE_APPLICATION_CREDENTIALS to a valid JSON file.'
        )
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES)
    service = build('driveactivity', 'v2', credentials=creds)
    return service

def fetch_activity(doc_id):
    service = get_activity_service()
    body = {'itemName': f'items/{doc_id}'}
    response = service.activity().query(body=body).execute()
    return response.get('activities', [])

def parse_activities(activities):
    records = []
    for act in activities:
        timestamp = act.get('timestamp') or act.get('timeRange', {}).get('endTime')
        actors = act.get('actors', [])
        user = None
        for a in actors:
            user_known = a.get('user', {}).get('knownUser')
            if user_known:
                user = user_known.get('personName')
                break
        actions = act.get('actions', [])
        action_desc = ','.join([next(iter(a)) for a in actions])
        records.append({
            'timestamp': timestamp,
            'user': user,
            'action': action_desc,
        })
    return records

def write_output(records, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    parser.add_argument(
        '--output', default='activity/activity.json',
        help='Path to output JSON file'
    )
    args = parser.parse_args()
    activities = fetch_activity(args.doc_id)
    records = parse_activities(activities)
    write_output(records, args.output)
    print(f'Wrote {len(records)} activity records to {args.output}')

if __name__ == '__main__':
    main()