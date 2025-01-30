import scrapy
from urllib.parse import quote, urlencode
import time
import random
from HCIScrapy.database import DatabaseManager
import math
from datetime import datetime
from HCIScrapy.config import DB_IEEE

class IeeepagesspiderSpider(scrapy.Spider):

    # Spider's name
    name = "ieee_pages"

    # Database 
    db = DB_IEEE

    # Spider's type [Results, Page, Issues]
    stype = 'Pages'

    allowed_domains = ["ieeexplore.ieee.org"]

    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
    
    url_field = 'url'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.id_query_totals = -1
        self.total_results = 0
        self.rows_par_page = 100 # Even trying with 200 the website only provides 100 rows
        self.use_selenium = True
        self.use_api = False
        self.wait_timeout = 10
        self.ids_query = {}

    def start_requests(self):

        encoded_query = quote(self.query)
        request_data = {
            "url" : f"{self.base_url}?queryText={encoded_query}",
            'key_selector' : 'h1..result-item-align',
        }

        if self.id_query_totals == -1 :
            print('No totals registered... retreiving totals') 
            req_data =  request_data.copy()
            req_data['url'] = f'{req_data["url"]}&rowsPerPage={1}'
            self.total_results = self.get_number_results(request_data)
            self.id_query_totals = DatabaseManager.insert_query_totals(self.db, request_data['url'], self.query, self.total_results)
            print(f'Totals : {self.total_results} -- id_totals {self.id_query_totals}')
        
        
        # make it fo all pages
        #for page in range(self.max_pages):
        """search_params = {
            'queryText': encoded_query,
            #'pageNumber' : str(page + 1),
            'pageNumber' : '1',
            'rowsPerPage' :  self.rows_par_page
        }
"""
        self.max_pages = math.ceil(self.total_results/self.rows_par_page)
        #self.max_pages = 1
        return
        for page_number in range(1, self.max_pages + 1):
    
            
            req_data = {
                "url" : f"{self.base_url}?queryText={encoded_query}&pageNumber={page_number}&rowsPerPage={self.rows_par_page}",
            }

            search_url = f"{self.base_url}?queryText={encoded_query}&pageNumber={page_number}&rowsPerPage={self.rows_par_page}"
            
            print(f'Trying IEEE pages -- {page_number} --> {search_url}')
            id_query = DatabaseManager.insert_page(self.db, page_number, search_url, self.id_query_totals )
            self.ids_query[search_url] = id_query

            yield scrapy.Request(
                search_url, 
                #callback=self.parse_page,
                #meta={'page': page + 1}
                meta={
                    'token_to_wait' : 'div.result-item-align',
                    'url' : search_url
                    },
                dont_filter=True
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):
        
        url = response.url
        id_query = self.ids_query[url]
        try:
            
            
            results = response.css('div.result-item-align')
          
            for result in results:

                title_all = result.css('h3 a')
                title = title_all.css("::text, span::text").getall()
                title = "".join(title).strip()
                url =  title_all.attrib['href']
                #descrption = result.css('div.description')
                #venue_all = descrption.css('a').xpath('.//text()').getall()
                #venue = ''.join(venue_all).strip()
                #publi_info = descrption.css('div.publisher-info-container').xpath('.//text()').getall()
                #type_issue = ''.join(publi_info).strip()
                        
                item =  {
                    'title': title,
                    #'type' : type_issue,
                    #'venue' : venue,
                    'url' : url,
                    'id_query' : id_query,
                    'db' : self.db,
                    'id_issues' : url
                    # Añade más campos según necesites
                }
                #print(f'YIELD ---  {item}')
                yield item
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")


    def get_number_results(self, request_data):

        try:
            response, meta = self.request(request_data)
            total_results_elements = response.css('.Dashboard-header > span > span')
            total_results_element = (total_results_elements[1]).xpath('.//text()').get()
            total_results = int(total_results_element.replace(',', ''))
        except Exception as e:
            self.logger.error(f"Error extrayendo total de resultados: {e}")
            total_results = 0

        return total_results
        