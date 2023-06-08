import csv
import re
from time import time
import requests
import dotenv
dotenv.load_dotenv()
import aspose.pdf as ap

import os
from requests import Session
import subprocess
import urllib3
urllib3.disable_warnings()

import refy


result_limit = 10
S2_API_KEY = os.environ['S2_API_KEY']

PAPER_FIELDS = 'paperId,externalIds,title,authors,year,abstract,openAccessPdf,influentialCitationCount,citationStyles,tldr,venue,journal'

def get_paper(session: Session, paper_id: str, fields: str = 'paperId,title', **kwargs) -> dict:
    params = {
        'fields': fields,
        **kwargs,
    }
    headers = {
        'x-api-key': S2_API_KEY,
    }

    with session.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}', params=params, headers=headers) as response:
        response.raise_for_status()
        return response.json()



def find_paper_from_query(query):
    papers = None
    begin = time()
    while papers is None:
        try:
            rsp = requests.get('https://api.semanticscholar.org/graph/v1/paper/search',
                                    params={'query': query, 'limit': result_limit, 'fields': PAPER_FIELDS})
            
            rsp.raise_for_status()
            results = rsp.json()
            total = results["total"]
            if not total:
                print('No matches found. Please try another query.')
                return 'No matches found. Please try another query.'

            print(f'Found {total} results. Showing up to {result_limit}.')

            papers = results['data']
        except Exception as e:
            print(e)
            print(rsp)
            if input('continue?')=='yes':
                end = time()
                if end-begin>60:
                    return 'a failure occured'
            else: quit()

    return papers

# Finds papers which are similar to an exisiting one
def find_recommendations(paper):
    print(f"Up to {result_limit} recommendations based on: {paper['title']}")
    rsp = requests.get(f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper['paperId']}",
                       params={'fields': 'title,url,isOpenAccess', 'limit': result_limit*2})
    
    rsp.raise_for_status()
    results = rsp.json()
    print_papers(results['recommendedPapers'])
    return results['recommendedPapers']



def print_papers(papers):
    results = ''
    for idx, paper in enumerate(papers):
        results+= f"{idx}  {paper['title']} {paper['url']}"
    return results


def chunks(items, chunk_size):
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def fetch_paper_batch(paperid: list):
    req = {'ids': [f'{id}' for id in paperid]}
    # https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers
    
    rsp = requests.post('https://api.semanticscholar.org/graph/v1/paper/batch',
                        params={'fields': PAPER_FIELDS},
                        json=req)
    
    if rsp.status_code != 200:
        return f'Problem fetching {req}: ' + rsp.text
    return rsp.json()


def download_pdf_from_id(paperid):
    os.system(f'python simple.py -d papers {paperid}')


def update_dataframe(incomplete, dest):
    results = fetch_paper_batch(paperid= [item['paperId'] for item in incomplete])
    pdf_des= dest
    pdf_des = pdf_des[:-4] + '.pdf'
    text = ''

    with open(pdf_des, 'a+',encoding='utf-8') as f:
        for paper in results:
            try:
                text += paper['title'].upper()+'\n'
                text += paper['tldr']['text']
                text += '\n\n'
            except:
                pass

    write_to_pdf(text, pdf_des)

    count = 0

    # Read existing entries from the CSV file
    existing_entries = set()

    isFile =  os.path.isfile(dest)
    if not isFile:
        with open(dest, 'w',encoding='utf-8') as fp:
            csvfile = csv.DictWriter(fp, ['paperId', 'title', 'first_author', 'year', 'abstract','tldr','bibtex','influentialCitationCount','venue','journal','pages'])
            csvfile.writeheader()
    if isFile:
        with open(dest, 'r',encoding='utf-8') as fp:
            csvfile = csv.DictReader(fp)
            for row in csvfile:
                existing_entries.add(row['paperId'])

    # Append new entries to the CSV file
    with open(dest, 'a', newline='', encoding='utf-8') as fp:
        csvfile = csv.DictWriter(fp, ['paperId', 'title', 'first_author', 'year', 'abstract','tldr','bibtex','influentialCitationCount','venue','journal','pages'])

        for paper in results:
            if not paper:
                break
            
            print(paper)
            paperId = paper['paperId']
            if paperId in existing_entries:
                continue  # Skip if the entry already exists

            paper_authors = paper.get('authors', [])
            try:
                csvfile.writerow({
                    'title': paper['title'],
                    'first_author': paper_authors[0]['name'] if paper_authors else '<no_author_data>',
                    'year': paper['year'],
                    'abstract': paper['abstract'],
                    'paperId': paperId,
                    'tldr':paper['tldr'] if paper['citationStyles']['bibtex'] else paper['abstract'],
                    'bibtex':paper['citationStyles']['bibtex'] if paper['citationStyles']['bibtex'] else '',
                    'influentialCitationCount':paper['influentialCitationCount'],
                    'venue':paper['venue'],
                    'journal':paper['journal']['name'] if paper['journal']['name'] else '<no_journal_data>',
                    'pages':paper['journal']['pages'] if paper['journal'] else '<no_pages_data>',
                })
            except:
                print(paper)
            count += 1

    print(f'Added {count} new results to {dest}')
    return f'Added {count} new results to {dest}'




def write_bib_file(csv_file, bib_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with open(bib_file, 'w', encoding='utf-8') as output:
            for row in reader:
                bib_entry = create_bib_entry(row)
                output.write(bib_entry + '\n\n')

def create_bib_entry(row):
    paper_id = row['paperId']
    title = row['title']
    author = row['first_author']
    year = row['year']

    journal_match = re.search(r"journal\s*=\s*{([^}]*)}", row['bibtex'])
    if journal_match:
        journal = journal_match.group(1)
    else: journal = ''
    pages_match = re.search(r"pages\s*=\s*{([^}]*)}", row['bibtex'])
    if pages_match:
        pages = pages_match.group(1)
    else: pages = ''

    abstract = replace_non_alphanumeric(row['abstract'])

    # Generate the BibTeX entry
    bib_entry = f"@ARTICLE{{{paper_id},\n"
    bib_entry += f"  title     = \"{title}\",\n"
    bib_entry += f"  author    = \"{author}\",\n"
    bib_entry += f"  abstract  = \"{abstract}\",\n"
    bib_entry += f"  year      = {year},\n"
    bib_entry += f"  journal   = \"{journal}\",\n"
    bib_entry += f"  pages     = \"{pages}\"\n"
    bib_entry += "}"

    return bib_entry


def replace_non_alphanumeric(string, replacement=''):
    pattern = r'[^a-zA-Z0-9]'
    replaced_string = re.sub(pattern, replacement, string)
    return replaced_string


def refy_reccomend(bib_path, N=10):
    d = refy.Recomender(
        bib_path,            # path to your .bib file
        n_days=30,           # fetch preprints from the last N days
        html_path=os.path.join(
            os.path.join(bib_path.replace('\\results\\papers.bib',''),'refy_suggestions'),"test.html"
            ),               # save results to a .html (Optional)
        N=N                 # number of recomended papers
        )
    d.results.to_csv(
        os.path.join(os.path.join(bib_path.replace('\\results\\papers.bib',''),'refy_suggestions'),"test.csv"),
        )                    # save results to a .csv
    
    

def write_to_pdf(text, dest):
    # Initialize document object
    document = ap.Document()

    # Add page
    page = document.pages.add()

    # Initialize textfragment object
    text_fragment = ap.text.TextFragment(text)

    # Add text fragment to new page
    page.paragraphs.add(text_fragment)

    # Save updated PDF
    document.save(dest)
 



