#!/usr/bin/env python3
"""Create per-section headers and assign a global footer in a Google Doc."""
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

def fetch_section_ranges(doc):
    # Find all H1 headings, record start indices and text
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
            ).strip()
            start = el.get('startIndex')
            if isinstance(start, int):
                headings.append((start, text))
    headings.sort(key=lambda x: x[0])
    # Determine document end
    body = doc.get('body', {}).get('content', [])
    doc_end = body[-1].get('endIndex') if body else 1
    # Build section ranges: (start, end, name)
    sections = []
    for i, (start, name) in enumerate(headings):
        end = headings[i+1][0] if i+1 < len(headings) else doc_end
        sections.append({'start': start, 'end': end, 'name': name})
    return sections

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    parser.add_argument('--prefix', default='Advisor Notes - ', help='Header text prefix')
    args = parser.parse_args()
    service = get_service()
    # Fetch doc (include footers for detection)
    # Fetch full document (includes headers, footers, and styles)
    doc = service.documents().get(documentId=args.doc_id).execute()
    # Gather H1 headings to define sections
    headings = []  # list of (startIndex, headingText)
    for el in doc.get('body', {}).get('content', []):
        para = el.get('paragraph')
        if not para:
            continue
        if para.get('paragraphStyle', {}).get('namedStyleType') == 'HEADING_1':
            text = ''.join(
                run.get('textRun', {}).get('content', '')
                for run in para.get('elements', [])
            ).strip()
            idx = el.get('startIndex')
            if isinstance(idx, int):
                headings.append((idx, text))
    if not headings:
        print('No H1 headings found; nothing to do.')
        return
    headings.sort(key=lambda x: x[0])
    # Ensure a default footer exists (applies globally)
    existing_footers = doc.get('footers', {}) or {}
    if existing_footers:
        footer_id = next(iter(existing_footers.keys()))
    else:
        resp = service.documents().batchUpdate(
            documentId=args.doc_id,
            body={'requests': [{'createFooter': {'type': 'DEFAULT'}}]}
        ).execute()
        footer_id = resp.get('replies', [{}])[0].get('createFooter', {}).get('footerId')
    # Check for existing document-level header
    doc_style = doc.get('documentStyle', {}) or {}
    default_header_id = doc_style.get('defaultHeaderId')
    # Create a header for each section
    for i, (idx, name) in enumerate(headings):
        # Determine header creation: global header or section-specific
        if i == 0 and default_header_id:
            header_id = default_header_id
        else:
            create_req = {'type': 'DEFAULT'}
            if i > 0:
                create_req['sectionBreakLocation'] = {'index': idx}
            resp = service.documents().batchUpdate(
                documentId=args.doc_id,
                body={'requests': [{'createHeader': create_req}]}
            ).execute()
            header_id = resp.get('replies', [{}])[0].get('createHeader', {}).get('headerId')
        # Insert the header text if not empty
        header_text = f"{args.prefix}{name}"
        if header_id and header_text:
            service.documents().batchUpdate(
                documentId=args.doc_id,
                body={'requests': [{
                    'insertText': {
                        'location': {'segmentId': header_id, 'index': 0},
                        'text': header_text
                    }
                }]}
            ).execute()
    print(f'Applied headers for {len(headings)} sections and ensured footer.')

if __name__ == '__main__':
    main()