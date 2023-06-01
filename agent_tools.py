import uuid
import os
import tiktoken

import summarize

import csv
import sys
import requests

from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import S2_tools as scholar
 

def PaperSearchAndDownload(query):
    # make new workspace 
    workspace_dir_name = query.split()[0] + '_'+ str(uuid.uuid1(2))
    os.mkdir(workspace_dir_name)
    os.mkdir(os.path.join(workspace_dir_name,'results'))
    os.mkdir(os.path.join(workspace_dir_name,'refy_suggestions'))
    os.environ['workspace'] = workspace_dir_name

    # search papers
    print('searching base papers') 
    papers = scholar.find_paper_from_query(query)

    scholar.update_dataframe(incomplete=papers, dest=os.path.join(workspace_dir_name, 'results','papers.csv'))

    # get recommendations
    print('\nexpanding with reccomendations') 
    reccomends = []
    for paper in papers:
        guesses = scholar.find_recommendations(paper)
        for guess in guesses:
            if guess['isOpenAccess']: reccomends.append(guess)

    # save them into a csv
    scholar.update_dataframe(incomplete= reccomends, dest=os.path.join(workspace_dir_name, 'results','papers.csv'))

    # download 
    with open(os.path.join(workspace_dir_name,'results','papers.csv'), 'r',encoding='utf-8') as fp:
        csvfile = csv.DictReader(fp)  
        scholar.download_pdf_from_id(" ".join( row['paperId'] for row in csvfile))
    
    scholar.write_bib_file(csv_file=os.path.join(workspace_dir_name,'results','papers.csv'), bib_file=os.path.join(workspace_dir_name,'results','papers.bib'))

    # expand further with refy reccomendendation system
    scholar.refy_reccomend(bib_path=os.path.join(workspace_dir_name,'results','papers.bib'))

    # download 'em as well
    download_bibtex_library(os.path.join(workspace_dir_name,'refy_suggestions','test.csv'))

    return f'papers downloaded to {os.path.join(os.getcwd(), workspace_dir_name)}'


def update_csv_file():
    # work in progress: detect new papers in a folder add add them to the csv to 
    # get new reccomendations
    pass

def download_bibtex_library(csv_path):
    with open(csv_path, 'r',encoding='utf-8') as fp:
        csvfile = csv.DictReader(fp) 
        for row in csvfile:
            title = scholar.replace_non_alphanumeric(row['title'])
            title = title.replace(" ","-")

            save_path = os.path.join(os.path.join(csv_path, '..', title+'.pdf'))

            try:
                download_paper(url=row['url']+'.pdf', save_path=save_path)
            except:
                try:
                    download_paper(url=row['url']+'.pdf', save_path=save_path)
                except:
                    try:
                        download_paper(url=row['url'], save_path=save_path)
                    except: 
                        print(f'couldn t download {row}')

def generate_chunks(text):
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens = enc.encode(text)
    token_chunks = [tokens[i:i + 4000] for i in range(0, len(tokens), 4000)]

    word_chunks = [enc.decode(chunk) for chunk in token_chunks]
    return word_chunks


from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings

import langid
import time

def process_pdf_folder(folder_path):
    if not os.path.exists(folder_path):
        return 'the folder does not exist, check your spelling'
    
    

    for item in os.listdir(folder_path):
        if not item.endswith('.pdf'):continue
        pdf_path = os.path.join(folder_path, item)
        loader = OnlinePDFLoader(pdf_path)
        data  = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=100)
        
        texts = text_splitter.split_documents(data)
        
        with open(os.path.join(folder_path,'SUMMARY.txt'), 'a', encoding='UTF-8') as write_file:
            write_file.write(item)
            write_file.write("\n\n\n")
            for text in texts:
                text_string = text.page_content
                
                # split in 2 if too long
                encoder = tiktoken.get_encoding('gpt-4')
                if len(encoder.encode(text_string))>4050:
                    tokens = encoder.encode(text_string)

                    win1 = text_string(encoder.decode(tokens[:4050]))
                    win2 = text_string(encoder.decode(tokens[4050:]))
                    piece1 = summarize.tldr(win1, to_language=langid.classify(text_string)[0].strip())
                    piece2 = summarize.tldr(win2, to_language=langid.classify(text_string)[0].strip())
                    piece = summarize.tldr(piece1+piece2, to_language=langid.classify(text_string)[0].strip())
                    write_file.write(piece)
                    continue
                    
                try:
                    piece = summarize.tldr(text_string, to_language=langid.classify(text_string)[0].strip())
                except:
                    print('sleeping a minute')
                    time.sleep(60)
                
                try:
                    write_file.write(piece)
                except:
                    print(piece)
    
    with open(os.path.join(folder_path,'SUMMARY.txt'), 'r', encoding='UTF-8') as read_file:
        return read_file.read()

from langchain.document_loaders import OnlinePDFLoader


def readPDF(pdf_path):
    loader = OnlinePDFLoader(pdf_path)
    data  = loader.load()
    text_content = ''
    for page in data:
        text_content+=page.page_content
    
    return text_content


import urllib
def download_paper(url, save_path):
    if 'doi' in url:
        doi = paper_id = "/".join(url.split("/")[-2:])
        # Construct the Crossref API URL
        print(doi)
        doi_url = f"https://doi.org/{doi}"

        # Send a GET request to the doi.org URL
        response = requests.get(doi_url, allow_redirects=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the final URL after redirection
            url = response.url

    if 'arxiv' in url:
        # URL del paper su arXiv

        # Ottieni l'ID del paper dall'URL
        paper_id = url.split("/")[-1]

        # Costruisci l'URL di download del paper
        pdf_url = f"http://arxiv.org/pdf/{paper_id}.pdf"

        # Scarica il paper in formato PDF
        urllib.request.urlretrieve(pdf_url, save_path)
        return


    if 'doi' in url:
        doi = paper_id = "/".join(url.split("/")[-2:])
        # Construct the Crossref API URL
        print(doi)
        doi_url = f"https://doi.org/{doi}"

        # Send a GET request to the doi.org URL
        response = requests.get(doi_url, allow_redirects=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the final URL after redirection
            final_url = response.url

            # Download the paper in PDF format
            urllib.request.urlretrieve(final_url, save_path)