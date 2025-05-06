#!/usr/bin/env python3
"""Ensure H1 section headings exist in a Google Doc."""
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

def fetch_existing_headings(service, doc_id):
    doc = service.documents().get(documentId=doc_id).execute()
    headings = []
    for el in doc.get('body', {}).get('content', []):
        para = el.get('paragraph')
        if not para:
            continue
        style = para.get('paragraphStyle', {}).get('namedStyleType')
        if style == 'HEADING_1':
            text = ''.join(
                run.get('textRun', {}).get('content', '')
                for run in para.get('elements', [])
            )
            headings.append(text.strip())
    return headings, doc

def create_sections(service, doc_id, sections):
    existing, doc = fetch_existing_headings(service, doc_id)
    requests = []
    # Determine insertion index: one index before the document’s last endIndex
    body_content = doc.get('body', {}).get('content', [])
    if body_content:
        raw_end = body_content[-1].get('endIndex', 1)
        # insertText index must be less than segment endIndex
        end_index = max(raw_end - 1, 1)
    else:
        end_index = 1
    for section in sections:
        if section in existing:
            continue
        # Insert a newline, the section text, and another newline
        text = f"\n{section}\n"
        requests.append({
            'insertText': {
                'location': {'index': end_index},
                'text': text
            }
        })
        # Apply HEADING_1 style to the inserted line (exclude the first newline)
        start = end_index + 1
        end = start + len(section)
        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {'namedStyleType': 'HEADING_1'},
                'fields': 'namedStyleType'
            }
        })
        end_index += len(text)
    if not requests:
        return None
    return service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    parser.add_argument(
        '--sections', required=True, nargs='+',
        help='List of H1 section names to ensure in the Doc'
    )
    args = parser.parse_args()
    service = get_service()
    result = create_sections(service, args.doc_id, args.sections)
    if result:
        print(f'Added {len(args.sections)} new section(s).')
    else:
        print('All sections already exist; no changes made.')

if __name__ == '__main__':
    main()