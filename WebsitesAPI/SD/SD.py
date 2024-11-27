import requests
import json
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
    "view" : 'COMPLETE',
    'start' : 300,
    'count' : 100
}

params2 = {
    "query": 'doi(10.1016/j.jss.2024.112287) OR doi(10.1016/j.inffus.2023.102004) OR doi(10.1016/j.comcom.2024.04.003) OR doi(10.1016/j.energy.2022.125047) OR doi(10.1016/S0378-4274(23)00421-6) OR doi(10.1016/j.autrev.2022.103034) OR doi(10.1016/j.patcog.2022.108991) OR doi(10.1016/j.soildyn.2022.107673) OR doi(10.1016/j.jnca.2024.103989) OR doi(10.1016/j.sasc.2024.200094) OR doi(10.1016/j.eiar.2023.107097) OR doi(10.1016/j.jbiomech.2023.111488) OR doi(10.1016/j.compind.2023.104006) OR doi(10.1016/S2214-109X(22)00523-X) OR doi(10.1016/j.amjmed.2022.06.016) OR doi(10.1016/j.scs.2022.104120) OR doi(10.1016/j.hspr.2024.05.002) OR doi(10.1016/j.respol.2022.104649) OR doi(10.1016/j.rcim.2022.102384) OR doi(10.1016/j.xjtc.2024.01.004) OR doi(10.1016/j.jbc.2024.105937) OR doi(10.1016/j.edurev.2022.100437) OR doi(10.1016/j.mri.2023.02.004) OR doi(10.1016/j.measen.2023.100740) OR doi(10.1016/j.knosys.2024.112693) OR doi(10.1016/j.eswa.2024.125423) OR doi(10.1016/j.teln.2024.03.006) OR doi(10.1016/j.rcim.2023.102638) OR doi(10.1016/j.ejso.2023.107948) OR doi(10.1016/j.tate.2023.104189) OR doi(10.1016/j.epsr.2024.110710) OR doi(10.1016/j.procs.2024.03.164) OR doi(10.1016/j.ress.2024.109988) OR doi(10.1016/j.phoj.2023.10.007) OR doi(10.1016/j.eswa.2023.121976) OR doi(10.1016/j.jmir.2024.02.020) OR doi(10.1016/j.comnet.2024.110862) OR doi(10.1016/j.chb.2023.107650) OR doi(10.1016/S0016-5085(24)03114-7) OR doi(10.1016/j.rcim.2024.102761) OR doi(10.1016/j.emj.2022.08.001) OR doi(10.1016/j.eng.2024.11.006) OR doi(10.1016/j.focat.2022.07.020) OR doi(10.1016/j.envsci.2024.103713) OR doi(10.1016/j.jmsy.2023.05.019) OR doi(10.1016/j.prime.2024.100571) OR doi(10.1016/j.eswa.2023.122684) OR doi(10.1016/j.ijrobp.2024.07.1274) OR doi(10.1016/j.phycom.2023.102257) OR doi(10.1016/j.ipm.2023.103470) OR doi(10.1016/j.jmathb.2024.101200) OR doi(10.1016/j.engappai.2024.109630) OR doi(10.1016/j.jece.2024.114658) OR doi(10.1016/j.future.2024.107562) OR doi(10.1016/j.nedt.2024.106136) OR doi(10.1016/j.dib.2023.109702) OR doi(10.1016/j.engappai.2023.107000) OR doi(10.1016/j.giq.2024.101964) OR doi(10.1016/j.shaw.2021.12.1008) OR doi(10.1016/j.jclepro.2022.135821) OR doi(10.1016/S0090-8258(22)01754-1) OR doi(10.1016/B978-0-443-13701-3.00201-2) OR doi(10.1016/j.semperi.2022.151637) OR doi(10.1016/j.respol.2024.105110) OR doi(10.1016/j.jisa.2023.103518) OR doi(10.1016/j.ast.2023.108384) OR doi(10.1016/j.drugalcdep.2022.109648) OR doi(10.1016/j.jclepro.2024.143528) OR doi(10.1016/j.orgdyn.2024.101077) OR doi(10.1016/j.scs.2023.104905) ',
    "view" : 'COMPLETE'


}

params3 = {
    "doi": '10.1016/j.jss.2024.112287',
    "view" : 'COMPLETE'


}


#response=requests.get(url=f'https://api.elsevier.com/content/search/sciencedirect', headers=HEADERS, params=params)
#response=requests.get(url=f'https://api.elsevier.com/content/metadata/article', headers=HEADERS, params=params2)
#response=requests.get(url=f'https://api.elsevier.com/content/article/doi/10.1016/j.ress.2024.109988', headers=HEADERS)
response=requests.get(url=f'https://api.elsevier.com/content/abstract/citation-count', headers=HEADERS, params=params3)

if response.status_code == 200:
    print(response.json())  # Procesar los resultados
    data = json.loads(response.text)
    search_results = data['search-results']
    for entry in search_results['entry']:
        print(entry['prism:doi'])
        
else:
    print(f"Error {response.status_code}: {response.text}")



