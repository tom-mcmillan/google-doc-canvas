#!/usr/bin/env python3
"""Assign a unique named range ID to each H1 section heading in a Google Doc."""
import os
import re
import json
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build

# OAuth2 scopes for Google Docs write access
SCOPES = ['https://www.googleapis.com/auth/documents']

def slugify(text):
    # Lowercase, replace non-alphanum with dashes
    s = text.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

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

def tag_sections(doc_id, section_names):
    service = get_service()
    doc = service.documents().get(documentId=doc_id).execute()
    # Map heading text to its start/end indices
    heading_positions = {}
    for el in doc.get('body', {}).get('content', []):
        para = el.get('paragraph')
        if not para:
            continue
        if para.get('paragraphStyle', {}).get('namedStyleType') == 'HEADING_1':
            text = ''.join(
                run.get('textRun', {}).get('content', '')
                for run in para.get('elements', [])
            ).strip()
            start = el.get('startIndex')
            end = el.get('endIndex')
            heading_positions[text] = (start, end)
    requests = []
    mapping = {}
    slug_set = set()
    # Tag only the specified sections
    for name in section_names:
        pos = heading_positions.get(name)
        if not pos:
            print(f'Warning: heading "{name}" not found; skipping.')
            continue
        start, end = pos
        # Generate unique slug
        base = slugify(name) or 'section'
        slug = base
        suffix = 1
        while slug in slug_set:
            slug = f"{base}-{suffix}"
            suffix += 1
        slug_set.add(slug)
        # Create named range for this heading
        requests.append({
            'createNamedRange': {
                'name': slug,
                'range': {'startIndex': start, 'endIndex': end}
            }
        })
        mapping[slug] = {'name': name, 'startIndex': start, 'endIndex': end}
    if not requests:
        print('No valid headings to tag; nothing to do.')
        return
    service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()
    # Write mapping locally
    os.makedirs('sections', exist_ok=True)
    with open('sections/sections.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    print(f'Tagged {len(mapping)} sections; mapping in sections/sections.json')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    parser.add_argument(
        '--sections', required=True, nargs='+',
        help='List of exact H1 section names to tag'
    )
    args = parser.parse_args()
    tag_sections(args.doc_id, args.sections)

if __name__ == '__main__':
    main()