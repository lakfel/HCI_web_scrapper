import scrapy
import time
from HCIScrapy.database import DatabaseManager
import requests
from bs4 import BeautifulSoup
import re
import math
import random 
from urllib.parse import quote
from HCIScrapy.config import DB_SPRINGER

class SpringerpagesSpider(scrapy.Spider):

    # Spider's name
    name = "springer_pages"

    stype = 'Pages'

    # Database
    db = DB_SPRINGER

    url_field = 'url'


    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.total_results = 0
        self.rows_par_page = 20
        self.max_pages = 50
        self.max_results = 1000
        self.wait_timeout = 10
        self.base_url = 'https://link.springer.com/search?new-search=true&query='

    def start_requests(self):

        # Starting in a number but it will be replaced in the first request
        

        base_search_url = f'{self.base_url}{quote(self.query)}'
        total_results = self.get_number_results(base_search_url)
        DatabaseManager.insert_query_totals(self.db, base_search_url, self.query, total_results)

        self.max_pages = min(math.ceil(total_results/self.rows_par_page), self.max_pages)
        #self.max_pages = 1
        print(f'{self.name} -- TOTAL PAGES = {self.max_pages}')
        for page_count in range(1, self.max_pages + 1):

            search_url = f'{base_search_url}&page={page_count}'
            id_query = DatabaseManager.insert_page(self.db, self.query, page_count, search_url)
             #FIXME Currently working by disabling the robot.txt settings. Figure it out
            yield scrapy.Request(
                search_url,
                meta = {
                        'page_count': page_count,
                        'id_query': id_query,
                        'url': search_url
                        },
                dont_filter=True,
                callback=self.parse
            )
            time.sleep(random.uniform(6, 15))

    def parse(self, response):

        print(f'----------------------------- Spider parsing')

        id_query = response.meta['id_query']
        soup = BeautifulSoup(response.text, 'html.parser')
        try:

            li_results = response.css('li[data-test="search-result-item"]')
            
            for li in li_results:
                
                stype = li.css('.c-meta__item').xpath('.//text()').get() # This is not working
                url = li.css('.app-card-open a::attr(href)').get()
                title = li.css('.app-card-open__link > span').xpath('.//text()').get()
                abstract_truncated_all = li.css('.app-card-open__description').xpath('.//text()').getall()
                abstract_truncated = ''.join(abstract_truncated_all).strip()
                date_str = li.css('span.c-meta__item[data-test="published"]').xpath('.//text()').get()

                item = { 'db' : self.db,  
                        'id_query' : id_query,
                        'url' : url,
                        #'unique_id' : 'url'
                        }
                if title:
                    item['title'] = title
                if stype:
                    item['type'] = stype
                if  abstract_truncated:
                    item['abstract_truncated'] = abstract_truncated
                if date_str:
                    item['date'] = date_str

                yield item
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")
        


    def get_number_results(self, base_search_url):
        # I first check there is no initial query in the db 
        response = requests.get(base_search_url, timeout=500)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        span = soup.find('span', {'data-test': 'results-data-total'})
        if not span:
            raise ValueError("Tag not found  -- data-test='results-data-total'.")
        span_text = span.get_text()
        match = re.search(r"of ([\d,]+) results", span_text)
        if not match:
            raise ValueError(f"Tag format error. {span_text}")
        target_number = int(match.group(1).replace(",", ""))
        return target_number
