import scrapy
import time
from HCIScrapy.database import DatabaseConfig
from bs4 import BeautifulSoup
import re
import math
import random 
from urllib.parse import quote

class SdpagesspiderSpider(scrapy.Spider):
    
    name = "sd_pages"

    stype = 'Pages'

    # Database
    db = 'ScienceDirect'

    url_field = 'url'


    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.use_selenium = True
        self.db_param = db_param
        self.query_param = query_param
        self.total_results = 0
        self.max_pages = 50
        self.wait_timeout = 10
        self.base_url = 'https://www.sciencedirect.com/search?qs='
        self.js = {}

    def start_requests(self):

        # Starting in a number but it will be replaced in the first request
        self.max_pages = 40
        self.pages_is_set = False

        if not hasattr(self, 'rows_par_page') or self.rows_par_page == 0:
            self.logger.warning("No max rows_par_page, setting max to 100")
            self.rows_par_page = 100

        base_search_url = f'{self.base_url}{quote(self.query)}'
        total_results = self.get_number_results(base_search_url)
        print(f'Total results found {total_results}')
        DatabaseConfig.insert_query_totals(self.db, base_search_url, self.query, total_results)

        self.max_pages = math.ceil(total_results/self.rows_par_page)
        self.max_pages = 0
        for page_count in range(1, self.max_pages + 1):

            search_url = f'{base_search_url}&page={page_count}'
            query_id = DatabaseConfig.insert_page(self.db, self.query, page_count, search_url)
             #FIXME Currently working by disabling the robot.txt settings. Figure it out
            yield scrapy.Request(
                search_url,
                meta = {
                        'page_count': page_count,
                        'query_id': query_id,
                        'url': search_url
                        },
                dont_filter=True,
                callback=self.parse
            )
            time.sleep(random.uniform(4, 9))

    def parse(self, response):

        print(f'----------------------------- Spider parsing')

        query_id = response.meta['query_id']
        soup = BeautifulSoup(response.text, 'html.parser')
        try:

            li_results = response.css('li[data-test="search-result-item"]')
            
            for li in li_results:
                
                stype = li.css('.c-meta__item').xpath('.//text()').get()
                url = li.css('.app-card-open a::attr(href)').get()
                title = li.css('.app-card-open__link > span').xpath('.//text()').get()
                abstract_truncated_all = li.css('.app-card-open__description').xpath('.//text()').getall()
                abstract_truncated = ''.join(abstract_truncated_all).strip()
                date_str = li.css('span.c-meta__item[data-test="published"]').xpath('.//text()').get()

                item = { 'db' : self.db,  
                        'query_id' : query_id,
                        'url' : url,
                        'unique_id' : 'url'
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
        print(base_search_url)
        request_data = {
                        'url' : base_search_url,
                        'timeout' : 500,
                        'token_to_wait' : 'span.search-body-results-text'
                        }
        
        response = self.request(request_data)

        #response.raise_for_status() 
        soup = BeautifulSoup(response.body, 'html.parser')
        span = soup.find('span', class_ = 'search-body-results-text')
        if not span:
            raise ValueError("Tag not found  -- data-test='results-data-total'.")
        span_text = span.get_text()

        match = re.search(r"([\d,]+) results", span_text)
        if not match:
            raise ValueError(f"Tag format error. {span_text}")
        target_number = int(match.group(1).replace(",", ""))
        return target_number
