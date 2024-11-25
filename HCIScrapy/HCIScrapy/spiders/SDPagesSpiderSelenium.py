import scrapy
import time
from HCIScrapy.database import DatabaseConfig
from bs4 import BeautifulSoup
import re
import math
import random 
from urllib.parse import quote

class SdpagesspiderSpider(scrapy.Spider):
    
    # I do not use this anymore, SD bans every try and it has a very good API so I choose to integrate the api here
    name = "sd_pages_selenium"

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
        self.rows_par_page = 50 
        self.wait_timeout = 10
        self.base_url = 'https://www.sciencedirect.com/search?qs='
        self.js = {} # Dict key:name value: tuple ( statement, result)
        #TODO adapt IEEE to this 
        self.ids_query = {} # Temproraryy measure to pass the query to the parser. With selenium is not possbile.

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
        self.max_pages = 1
        for page_count in range(1, self.max_pages + 1):

            search_url = f'{base_search_url}&show={self.rows_par_page}&offset={((page_count-1)*self.rows_par_page)}'

            #TODO This can be better generalized in order to add any type of storage
            id_query = DatabaseConfig.insert_page(self.db, self.query, page_count, search_url)
            self.ids_query[search_url] = id_query
             #FIXME Currently working by disabling the robot.txt settings. Figure it out
             #TODO IEEE works differently with the excecution of Js information. Adapt it to the current version
            token_to_wait = 'li.ResultItem'
            yield scrapy.Request(
                search_url,
                meta = {
                        'page_count': page_count,
                        'id_query': id_query,
                        'url': search_url,
                        'token_to_wait' : token_to_wait
                        },
                dont_filter=True,
                callback=self.parse
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):


        id_query = self.ids_query[response.url]


        with open("ieee_test.html", 'w') as file:
            print(response.body,file=file)


        try:
            print(f'----------------------------- Spider parsing')

            li_results = response.css('li.ResultItem')
            
            for li in li_results:
                
                stype = li.css('.article-type').xpath('.//text()').get()
                title_info = li.css('h2')
                url = title_info.css('a.result-list-title-link::attr(href)').get()
                title = title_info.css('.anchor-text > span').xpath('.//text()').get()
                pub_info = li.css('.srctitle-date-fields')
                venue = pub_info.css('.subtype-srctitle-link .anchor-text > span').xpath('.//text()').get()

                item = { 'db' : self.db,  
                        'id_query' : id_query,
                        'url' : url,
                        'unique_id' : 'url'
                        }
                if title:
                    item['title'] = title
                if stype:
                    item['type'] = stype
                if  venue:
                    item['venue'] = venue

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
        
        response, meta = self.request(request_data)

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
