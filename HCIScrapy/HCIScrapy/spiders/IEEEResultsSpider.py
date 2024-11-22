import scrapy
from urllib.parse import quote
import time
from bs4 import BeautifulSoup

class IeeeresultsspiderSpider(scrapy.Spider):

    # Spider's name
    name = "ieee_results"

    # Database 
    db = 'IEEE'

    # Spider's type [Results, Page, Issues]
    stype = 'Results'

    allowed_domains = ["ieeexplore.ieee.org"]
    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true"

    # Query 
    # TODO: In orfer to keep coherence between all the spiders, probably better to handle this in a pipeline that take a unformatted query, format it first depending on the data base and then into the url
    query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_timeout = 10


    def encode_boolean_expression(self) -> str:
        return quote(self.query) 

    def start_requests(self):

        search_url = f"{self.base_url}&queryText={self.encode_boolean_expression()}"

        yield scrapy.Request(
                url= search_url,
                meta={'use_selenium': True, 'key_selector' : '.Dashboard-header > span > span'}
            )

    def parse(self, response):
        try:

            #with open("ieee_test.html", 'w' encoding='ISO-8859-1') as file:
            #    print(response.text,file=file)
                
            total_results_elements = response.css('.Dashboard-header > span > span')
            #print(f'---------------------- ELEMENTOS\n\t{total_results_elements.text}')
            total_results_element = (total_results_elements[1]).xpath('.//text()').get()
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
