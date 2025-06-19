import requests
from requests.auth import HTTPBasicAuth
import os 
from dotenv import load_dotenv
import pandas
import pyodbc as db

''' This file connects to a microsoft sql server database and uses and API to fetch data and insert it into a table via a stored procedure'''

def sendToDatabase(procName, parameter, dataTable):
     # Connect to SQL Server
    connection_string = (
        r"DRIVER=ODBC Driver 18 for SQL Server;"
        r"SERVER=RIV-VS005;"
        f"DATABASE=Integrations;"
        f"TRUSTED_CONNECTION=yes;"
        r"Encrypt=no"
    )
    conn = db.connect(connection_string, autocommit=True)
    cursor = conn.cursor()
    # Execute stored proc
    cursor.execute("EXEC " + procName + " " + parameter, dataTable)
    cursor.close()
    conn.close()

def ConvertToDatatable(data, datatype):
    # Format data as param for stored proc
    listData = [tuple(row) for row in data.values]
    listData.insert(0, datatype)
    listData.insert(1, 'dbo')
    datatable = (listData,)
    return datatable

def formatPD(data):

    headerColumns = ["Location","LocationId","ParentLocationId","LocationStatusId","LocationTreeLevel"]

    tableData = []

    for location in data.get("value", []):
        rowData = []
        for index, value in location.items():

            # Some values are None, to avoid data validation errors, we must set it to a string or integer 0
            if value is None:
                rowData.append('None' if index == 'LocationTreeLevel' else 0)
            elif index in ('ParentLocationId', 'LocationStatusId'):
                rowData.append(int(value))
            else:
                rowData.append(value)
        tableData.append(rowData)

    return pandas.DataFrame(tableData, columns=headerColumns)

def processAPI():
    url = (
        "https://odata-huntconsolidated.kminnovations.net/apps/webservices/odata.svc/"
        "Location()?&$format=json"
        "&$select=LocationId,Location,ParentLocationId,LocationStatusId,LocationTreeLevel"
        #"&$filter=Active eq true"
        #"&$select=IncidentId,IncidentNumber,IncidentStatus/Item"
    )
    
    headers = {
        "Accept": "application/json;odata.metadata=full"
    }
    response = requests.get(url, auth=HTTPBasicAuth(os.getenv("API_USERNAME"), os.getenv("API_PASSWORD")), headers=headers)
    
    response.raise_for_status()
    
    data = formatPD(response.json())
    print(data)
    sendToDatabase('hsp_Upload_Velocity_Locations', '@LocationData=?', ConvertToDatatable(data, 'VelocityLocationType'))

if __name__ == "__main__":
    load_dotenv()

    try:
        processAPI()
    except Exception as e:
        print(e)