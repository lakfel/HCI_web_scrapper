import scrapy
from urllib.parse import quote, urlencode
import time
import random
from HCIScrapy.database import DatabaseManager

class IeeepagesspiderSpider(scrapy.Spider):

    # Spider's name
    name = "ieee_pages"

    # Database 
    db = 'IEEE'

    # Spider's type [Results, Page, Issues]
    stype = 'Pages'


    allowed_domains = ["ieeexplore.ieee.org"]
    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
    
        # Query 
    # TODO: In orfer to keep coherence between all the spiders, probably better to handle this in a pipeline that take a unformatted query, format it first depending on the data base and then into the url
    #query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'

    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.db_param = db_param
        self.query_param = query_param
        # TODO This must come from the pipeline 
        self.total_results = 0
        self.max_pages = 0
        #self.query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'
        self.wait_timeout = 10


    def start_requests(self):

        # Verify parameters
        if not hasattr(self, 'max_pages') or self.max_pages == 0:
            self.logger.warning("No max pages, setting max to 45")
            self.max_pages = 45
        if not hasattr(self, 'rows_par_page') or self.rows_par_page == 0:
            self.logger.warning("No max rows_par_page, setting max to 100")
            self.rows_par_page = 100

        encoded_query = quote(self.query)

        # make it fo all pages
        #for page in range(self.max_pages):
        """search_params = {
            'queryText': encoded_query,
            #'pageNumber' : str(page + 1),
            'pageNumber' : '1',
            'rowsPerPage' :  self.rows_par_page
        }
"""
       # search_url = f"{self.base_url}?{urlencode(search_params)}"
        print('---------------------------------------------------------------------------------------------')
      

        print(f' TOTAL PAGES {self.max_pages}')
        for page_number in range(1, self.max_pages + 1):
    

            search_url = f"{self.base_url}?queryText={encoded_query}&pageNumber={page_number}&rowsPerPage={self.rows_par_page}"
            
            print(f'STORING -- {self.db}, {self.query},{page_number}, {search_url}')
            id_query = DatabaseManager.insert_page(self.db, self.query,page_number, search_url)

            yield scrapy.Request(
                search_url, 
                #callback=self.parse_page,
                #meta={'page': page + 1}
                meta={'use_selenium': True, 
                    'key_selector' : 'div.result-item-align',
                    'page_count': page_number,
                    'id_query': id_query},
                dont_filter=True
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):
        try:
            self.use_selenium = True
            page_count = response.meta['page_count']
            id_query = response.meta['id_query']
            #with open("ieee_test.html", 'w') as file:
            #    print(response.text,file=file)
            results = response.css('div.result-item-align')

            for result in results:
                title_all = result.css('h3').xpath('.//text()').getall()
                title = ''.join(title_all).strip()
                url =  result.css('h3 a::attr(href)').get()
                descrption = result.css('div.description')
                venue_all = descrption.css('a').xpath('.//text()').getall()
                venue = ''.join(venue_all).strip()
                publi_info = descrption.css('div.publisher-info-container').xpath('.//text()').getall()
                type_issue = ''.join(publi_info).strip()
                        
                yield {
                    'title': title,
                    'type' : type_issue,
                    'venue' : venue,
                    'url' : url,
                    'id_query' : id_query,
                    'unique_id' : 'url'
                    # Añade más campos según necesites
                }
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")
