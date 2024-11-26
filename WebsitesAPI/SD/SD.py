import requests

from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("SD_API_KEY")
print(API_KEY)
BASE_URL = "http://api.elsevier.com"
HEADERS = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json",  # Cambia a "text/xml, application/atom+xml" si prefieres XML
}

class ElsevierAPI:
    def __init__(self):
        self.auth_token = None

    def get_auth_token(self, platform="SCOPUS", choice_id=None):
        url = f"{BASE_URL}/authenticate?platform={platform}"
        if choice_id:
            url += f"&choice={choice_id}"

        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # Lanza excepción para códigos de error HTTP
            data = response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Mensaje de error detallado
            print(f"Response text: {response.text}")
            return None
        except Exception as err:
            print(f"An error occurred: {err}")
            return None

        if "pathChoices" in data:
            print("Múltiples cuentas detectadas. Opciones disponibles:")
            for choice in data["pathChoices"]["choice"]:
                print(f"ID: {choice['id']}, Nombre: {choice['name']}")
            return None

        self.auth_token = data.get("authtoken")
        if not self.auth_token:
            raise ValueError("No se pudo obtener un authtoken")
        print("Authtoken obtenido correctamente.")
        return self.auth_token


    def make_request(self, endpoint, params=None):
        """
        Realiza una solicitud autenticada a un endpoint de contenido de Elsevier.
        """
        if not self.auth_token:
            raise ValueError("No se ha autenticado aún. Llama a get_auth_token primero.")
        
        headers = HEADERS.copy()
        headers["X-ELS-Authtoken"] = self.auth_token
        url = f"{BASE_URL}{endpoint}"
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

params = {
    "query": '("VR" OR "Virtual reality" OR "augmented reality" OR "AR" OR "mixed reality" OR "XR") AND ("Multiuser" OR "multi-user" OR "collaborative")',

}
response=requests.get(url=f'http://api.elsevier.com/authenticate?platform=sciencedirect', headers=HEADERS)

if response.status_code == 200:
    print(response.json())  # Procesar los resultados
else:
    print(f"Error {response.status_code}: {response.text}")


response=requests.get(url=f'https://api.elsevier.com/content/search/sciencedirect', headers=HEADERS, params=params)

if response.status_code == 200:
    print(response.json())  # Procesar los resultados
else:
    print(f"Error {response.status_code}: {response.text}")




response=requests.get(url=f'http://api.elsevier.com/content/search/sciencedirect?query=heart&apiKey=[{API_KEY}] ')

if response.status_code == 200:
    print(response.json())  # Procesar los resultados
else:
    print(f"Error {response.status_code}: {response.text}")




