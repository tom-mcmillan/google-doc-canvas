#!/usr/bin/env python3
"""Fetch a Google Doc and convert it to Markdown, then optionally commit and push."""
import os
import argparse
import subprocess

from google.oauth2 import service_account
from googleapiclient.discovery import build

# OAuth2 scopes for Google Docs
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def get_service():
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.isfile(creds_path):
        raise FileNotFoundError(
            'Service account credentials not found. '
            'Set GOOGLE_APPLICATION_CREDENTIALS to a valid JSON file.'
        )
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES)
    service = build('docs', 'v1', credentials=creds)
    return service

def fetch_doc(doc_id):
    service = get_service()
    doc = service.documents().get(documentId=doc_id).execute()
    return doc

def parse_doc_to_markdown(doc):
    md = ''
    body = doc.get('body', {}).get('content', [])
    for element in body:
        paragraph = element.get('paragraph')
        if not paragraph:
            continue
        style = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')
        text_runs = paragraph.get('elements', [])
        text = ''.join(
            run.get('textRun', {}).get('content', '')
            for run in text_runs
        )
        text = text.rstrip('\n')
        if style == 'HEADING_1':
            md += f'# {text}\n\n'
        elif style == 'HEADING_2':
            md += f'## {text}\n\n'
        else:
            md += f'{text}\n'
    return md

def write_markdown(md, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)

def git_commit_and_push(path, message):
    subprocess.run(['git', 'add', path], check=True)
    subprocess.run(['git', 'commit', '-m', message], check=True)
    subprocess.run(['git', 'push'], check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--doc-id', required=True, help='Google Doc ID')
    parser.add_argument(
        '--output', default='docs/doc.md',
        help='Path to output Markdown file'
    )
    parser.add_argument(
        '--commit', action='store_true',
        help='Commit changes to git'
    )
    parser.add_argument(
        '--push', action='store_true',
        help='Push changes after commit'
    )
    args = parser.parse_args()

    doc = fetch_doc(args.doc_id)
    md = parse_doc_to_markdown(doc)
    write_markdown(md, args.output)

    if args.commit:
        git_commit_and_push(args.output, f'Update doc {args.doc_id}')
        if args.push:
            print('Changes pushed.')

if __name__ == '__main__':
    main()