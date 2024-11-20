import scrapy
from urllib.parse import quote, urlencode
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

class IeeepagesspiderSpider(scrapy.Spider):
    name = "ieee_pages"
    db = 'IEEE'
    stype = 'Pages'
    allowed_domains = ["ieeexplore.ieee.org"]
    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"


    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Parámetros que pueden ser pasados al iniciar el spider
        self.db_param = db_param
        self.query_param = query_param
        
        # Estos serán establecidos por el pipeline
        self.total_results = 0
        self.max_pages = 0
        self.query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'

        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Modo sin interfaz gráfica
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(f'C:\\Users\\johannavila\\Documents\\Research\\chromedriver-win64\\chromedriver.exe')  # Reemplazar con la ruta de tu ChromeDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.wait_timeout = 10

    def start_requests(self):
        # Verificar que el pipeline haya establecido los valores
        if not hasattr(self, 'max_pages') or self.max_pages == 0:
            self.logger.warning("No max pages, setting max to 45")
            self.max_pages = 45

        encoded_query = quote(self.query)


        # make it fo all pages
        #for page in range(self.max_pages):
        search_params = {
            'queryText': encoded_query,
            #'pageNumber' : str(page + 1),
            'pageNumber' : '1',
            'rowsPerPage' :  self.rows_par_page
        }
        #search_url = f"{self.base_url}?{urlencode(search_params)}"
        search_url = f"{self.base_url}?queryText={encoded_query}"


        yield scrapy.Request(
            search_url, 
            callback=self.parse_page,
            #meta={'page': page + 1}
            meta={'page': 1}
        )

        time.sleep(random.uniform(1, 3))


    def parse_page(self, response):

        page = response.meta['page']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://ieeexplore.ieee.org/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }

        self.driver.get(response.search_url, headers = headers)
        wait = WebDriverWait(self.driver, self.wait_timeout)
        results = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div.result-item-align')
            )
        )
        # Extraer resultados usando selectores de Scrapy
        #results = response.css('div.result-item-align')
        print('----------------------------- TESTING PARSE ---------------------------------------------')
        for result in results:
            title = result.css('h3::text').get()
            print(f'\t\t title: \t{title}')
            url =  result.css('h3 a::attr(href)')
            print(f'\t\t url: \t{url}')
            descrption = result.css('div.description')
            venue = descrption.css('a::text').get()
            publi_info = descrption.css('div.publisher-info-container div')
            type_issue = publi_info[2].get()
            print(f'\t\t type_issue: \t{type_issue}')
                    
            yield {
                'page': page,
                'title': title,
                'link': link,
                # Añade más campos según necesites
            }
