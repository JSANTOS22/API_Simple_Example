import requests
import sys
import os 
from dotenv import load_dotenv

def get_Odata(amount):

    # calls the API via this link below and authenticates using the API User and API Pass that's protected in the .env file
    url = 'https://odata-huntconsolidated.kminnovations.net/apps/webservices/odata.svc/Incident()?$format=json&$top=' + amount;
    response = requests.get(url, auth=(os.getenv("API_USERNAME"), os.getenv("API_PASSWORD")))

    # if the response is successful, we print the data from the API
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print('Unable to fetch data')


if __name__ == "__main__":

    # initializes the .env file containing the API user and API pass
    load_dotenv()

    try:
        get_Odata(sys.argv[1])

    except:
        print('Error: Have you typed an integer into argv?')
    
    


