from S2_tools import refy_reccomend
from agent_tools import *
from dotenv import load_dotenv
load_dotenv()
import requests
import openai
import os

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
    download_bibtex_library(os.path.join('Transformers_74527296-0081-11ee-b648-000000000002', 'refy_suggestions','test.csv'))