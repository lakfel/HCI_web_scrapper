import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time

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
        # chrome_options.add_argument("--headless")  # Descomentar si quieres ejecución sin interfaz gráfica
        service = Service(f'C:\\Users\\johannavila\\Documents\\Research\\chromedriver-win64\\chromedriver.exe')  # Reemplazar con la ruta de tu ChromeDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Consulta de búsqueda
        self.query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'
        #self.query = '("All Metadata":VR) AND ("All Metadata":Virtual reality)'



    def encode_boolean_expression(self) -> str:
        return quote(self.query) 
        #return self.query.replace(' ','%20')

    def start_requests(self):

        # Construir URL con parámetros de búsqueda
        search_url = f"{self.base_url}&queryText={self.encode_boolean_expression()}"
        print(f'URL>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{search_url}')
        # Usar Selenium para cargar la página
        self.driver.get(search_url)

        # Esperar a que se cargue el elemento con los resultados
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.Dashboard-header > span > span'))
        )
        
        # Extraer el número total de resultados
        try:
            total_results_element = self.driver.find_elements(By.CSS_SELECTOR, '.Dashboard-header > span > span')[1]
            total_results = total_results_element.text.replace(',', '')
            total_results = int(total_results)
        except Exception as e:
            self.logger.error(f"Error extrayendo total de resultados: {e}")
            total_results = 0

        # Crear un item con la información
        yield {
            'url': search_url,
            'query': self.query,
            'total_results': total_results
        }

        # Puedes agregar lógica adicional aquí para procesar los resultados
        time.sleep(2)  # Pequeña pausa para estabilidad

    def closed(self, reason):
        # Cerrar el navegador de Selenium al finalizar
        self.driver.quit()
