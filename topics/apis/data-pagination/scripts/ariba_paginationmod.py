import os
import argparse
from os import getenv
import requests
import json
import urllib.parse
from dotenv import load_dotenv
load_dotenv()

# Cargando variables de entorno
REALM = getenv('REALM')
API_KEY = getenv('API_KEY')
API_URL = getenv('API_URL')

def get_access_token():
    credential_path = f'{REALM}-token.json'
    if os.path.exists(credential_path):
        with open(credential_path) as json_file:
            data = json.load(json_file)
            return data['access_token']
    raise ValueError(f"Authentication file {credential_path} does not exist. "
                     "Run the ariba_authentication.py script before this script.")

def call_ar_sync_api(api_name, mode, save, user, passwordAdapter, apiUrl, contractId, page_token=None):
    headers = {
        'Authorization': f"Bearer {get_access_token()}",
        'apiKey': API_KEY
    }

    params = {
        'realm': REALM,
        'user': user,
        'passwordAdapter': passwordAdapter
    }

    request_url = f"{API_URL}/{api_name}/v1/prod/{apiUrl}/"
    if page_token:
        params['pageToken'] = page_token

    # Impresión de depuración
    print(f"Realizando solicitud a: {request_url}")
    print(f"Con parámetros: {params}")
    print(f"Y headers: {headers}")
    print (f"Contrato: {contractId}")

    response = requests.get(request_url + contractId, headers=headers, params=params)



    if not response.ok:
        raise Exception(f"API Request failed: {response.text}")

    result = response.json()
    if save:
        output_file_name = f"{REALM}_{api_name}_{mode}.json"
        with open(output_file_name, 'w') as output_file:
            json.dump(result, output_file)

        print(f"==========================")
        print(f"👉 Request URL: {request_url} -> Output file: {output_file_name}")
        print(f"==========================")

    return result

def analytical_reporting_sync_api(api_name, mode, save, user, passwordAdapter, apiUrl, contractId):
    page_token = ""
    while page_token != "STOP":
        parsed_json = call_ar_sync_api(api_name, mode, save, user, passwordAdapter, apiUrl, contractId, page_token=page_token)
        print(f"Total number of records in response: {len(parsed_json.get('Records', []))}")
        page_token = parsed_json.get("PageToken", "STOP")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SAP Ariba API pagination')
    parser.add_argument('--mode', type=str, default='paginate', choices=['count', 'paginate'])
    parser.add_argument('--api_name', type=str, default='retrieve-contract-workspaces')
    parser.add_argument('--apiUrl', type=str, default='contractWorkspaces')
    parser.add_argument('--contractId', type=str, default='CW2228821')
    parser.add_argument('--user', type=str, default='eperez')
    parser.add_argument('--passwordAdapter', type=str, default='PasswordAdapter1')
    save_parser = parser.add_mutually_exclusive_group(required=False)
    save_parser.add_argument('--save', dest='save', action='store_true')
    parser.set_defaults(save=False)

    args = parser.parse_args()
    analytical_reporting_sync_api(args.api_name, args.mode, args.save, args.user, args.passwordAdapter, args.apiUrl, args.contractId)
