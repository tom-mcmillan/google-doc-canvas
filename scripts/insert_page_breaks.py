#!/usr/bin/env python3
"""Insert a page break before each H1 heading in a Google Doc."""
import os, argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build

# write scope for Google Docs
SCOPES = ['https://www.googleapis.com/auth/documents']

def get_service():
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.isfile(creds_path):
        raise FileNotFoundError('Set GOOGLE_APPLICATION_CREDENTIALS to your key JSON.')
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES)
    return build('docs', 'v1', credentials=creds)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    args = parser.parse_args()
    service = get_service()
    doc = service.documents().get(documentId=args.doc_id).execute()
    positions = []
    for el in doc.get('body', {}).get('content', []):
        para = el.get('paragraph')
        if para and para.get('paragraphStyle', {}).get('namedStyleType') == 'HEADING_1':
            idx = el.get('startIndex')
            if isinstance(idx, int):
                positions.append(idx)
    if not positions:
        print('No H1 headings found; nothing to do.')
        return
    # Build requests in reverse order to avoid index shifts
    requests = []
    for idx in sorted(positions, reverse=True):
        requests.append({'insertPageBreak': {'location': {'index': idx}}})
    service.documents().batchUpdate(
        documentId=args.doc_id,
        body={'requests': requests}
    ).execute()
    print(f'Inserted {len(positions)} page break(s).')

if __name__ == '__main__':
    main()