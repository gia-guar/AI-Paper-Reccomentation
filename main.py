from S2_tools import refy_reccomend
from agent_tools import *
from dotenv import load_dotenv
load_dotenv()
import requests
import openai
import os
import pinecone

openai.api_key = os.getenv("OPENAI_API_KEY")


# example usage:
if __name__ == "__main__":
    # 1) creates a folder and download the results 
    prompt = "Transformers Architectures in Brain Tumor Segmentation"
    workspace = PaperSearchAndDownload(prompt)

    # 2) expands the folder with reccomendations with Refy 
    # done already in PaperSearchAndDownload, you can use it to recieve new reccomentations
    refy_reccomend(bib_path=os.path.join(workspace,'results','papers.bib'), N=20)

    # 3) summarize the papers in the folder in a .txt file
    # CAUTION: it might consume your credit, 
    # consider setting limits on credit consumtion at your openai account page
    # process_pdf_folder(workspace)
    
    # 4) when you have new reccomendations you can dowload every file suggested like this:
    download_bibtex_library(os.path.join(workspace, 'refy_suggestions','test.csv'))


    # 5) Question your papers
    
    # find API key in console at app.pinecone.io
    YOUR_API_KEY = os.environ['PINECONE_API_KEY']
    # find ENV (cloud region) next to API key in console
    YOUR_ENV = os.environ['PINECONE_API_ENV']

    index_name = 'paperquestioning'

    docs = []
    docs = load_workspace('Transformers_f8385482-0493-11ee-a1ca-000000000002')
    query_engine = llama_query_engine(docs,pinecone_index_name=index_name)

    res = query_engine.query("What is the 3d capsule technique?")

    pinecone.delete_index(index_name)

    print(res)