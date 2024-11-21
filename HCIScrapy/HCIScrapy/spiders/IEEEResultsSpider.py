import scrapy
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
from bs4 import BeautifulSoup

class IeeeresultsspiderSpider(scrapy.Spider):
    name = "ieee_results"
    db = 'IEEE'
    stype = 'Results'
    allowed_domains = ["ieeexplore.ieee.org"]
    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true"

    query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'
    
    #query = '("All Metadata":VR)'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuración de Selenium WebDriver
        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        #service = Service(f'C:\\Users\\johannavila\\Documents\\Research\\chromedriver-win64\\chromedriver.exe')  # Reemplazar con la ruta de tu ChromeDriver
        service = Service(f'C:\\Users\\jfgon\\Documents\\Postodoc\\chromedriver-win64\\chromedriver.exe')  # Reemplazar con la ruta de tu ChromeDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Consulta de búsqueda
        self.query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'
        #self.query = '("All Metadata":VR) AND ("All Metadata":Virtual reality)'
        self.wait_timeout = 10


    def encode_boolean_expression(self) -> str:
        return quote(self.query) 
        #return self.query.replace(' ','%20')

    def start_requests(self):

        # Construir URL con parámetros de búsqueda
        search_url = f"{self.base_url}&queryText={self.encode_boolean_expression()}"
        print(f'URL>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{search_url}')
        # Usar Selenium para cargar la página
        #self.driver.get(search_url)
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://ieeexplore.ieee.org/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        # Esperar a que se cargue el elemento con los resultados
        #WebDriverWait(self.driver, 20).until(
        #    EC.presence_of_element_located((By.CSS_SELECTOR, '.Dashboard-header > span > span'))
        #)
        
        # Extraer el número total de resultados
        

        # Crear un item con la información
        yield SeleniumRequest(
            url =search_url,
            headers = headers,
            #'query': self.query,
            callback = self.parse,
            wait_time= self.wait_timeout, 
            wait_until = EC.presence_of_element_located((By.CSS_SELECTOR, '.Dashboard-header > span > span'))
        )

        # Puedes agregar lógica adicional aquí para procesar los resultados
        time.sleep(10)  # Pequeña pausa para estabilidad

    def parse(self, response):
        try:
            #soup = BeautifulSoup(response.content, "html.parser")
            with open("ieee_test.html", 'w') as file:
                print(response.text,file=file)
                #print(str(soup),file=file)
            total_results_elements = response.css('.Dashboard-header > span > span')
            print(f'---------------------- ELEMENTOS\n\t{len(total_results_elements)}')
            total_results_element = total_results_elements[1].get()
            total_results = int(total_results_element.replace(',', ''))
        except Exception as e:
            self.logger.error(f"Error extrayendo total de resultados: {e}")
            total_results = 0
        yield {
            'url':response.request.url,
            'query': self.query,
            'total_results': total_results
        }
        

    def closed(self, reason):
        # Cerrar el navegador de Selenium al finalizar
        self.driver.quit()
