import os
import requests
from dotenv import load_dotenv

################################################################################
# Infura API
################################################################################

load_dotenv()

projectId = os.getenv("INFURA_PROJECT_ID")
projectSecret = os.getenv("INFURA_PROJECT_SECRET")

endpoint = "https://ipfs.infura.io:5001"

def send_to_ipfs(file):
    with open(file, "rb") as a_file:
        file_dict = {"file_to_upload.txt": a_file}
        response1 = requests.post(endpoint + '/api/v0/add', files=file_dict, auth=(projectId, projectSecret))
        print(response1)
        hash = response1.text.split(",")[1].split(":")[1].replace('"','')
        return hash
        #print(hash)