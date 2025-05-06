#!/usr/bin/env python3
"""Insert section breaks (NEXT_PAGE) before each H1 heading in a Google Doc."""
import os
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build

# OAuth2 scopes for Google Docs write access
SCOPES = ['https://www.googleapis.com/auth/documents']

def get_service():
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.isfile(creds_path):
        raise FileNotFoundError(
            'Service account credentials not found. '
            'Set GOOGLE_APPLICATION_CREDENTIALS to your key JSON.'
        )
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)

def fetch_h1_positions(doc):
    positions = []
    for el in doc.get('body', {}).get('content', []):
        para = el.get('paragraph')
        if not para:
            continue
        if para.get('paragraphStyle', {}).get('namedStyleType') == 'HEADING_1':
            idx = el.get('startIndex')
            if isinstance(idx, int):
                positions.append(idx)
    return positions

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    args = parser.parse_args()
    service = get_service()
    # Fetch full doc content
    doc = service.documents().get(documentId=args.doc_id).execute()
    positions = fetch_h1_positions(doc)
    if not positions:
        print('No H1 headings found; nothing to do.')
        return
    # Build section break requests in reverse order
    requests = []
    for idx in sorted(positions, reverse=True):
        requests.append({
            'insertSectionBreak': {
                'location': {'index': idx},
                'sectionType': 'NEXT_PAGE'
            }
        })
    service.documents().batchUpdate(
        documentId=args.doc_id,
        body={'requests': requests}
    ).execute()
    print(f'Inserted {len(positions)} section break(s).')

if __name__ == '__main__':
    main()