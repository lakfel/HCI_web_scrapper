import scrapy
from HCIScrapy.config import DB_ACM
from urllib.parse import quote
import time
from HCIScrapy.database import DatabaseManager
import math 

class AcmpagesspiderSpider(scrapy.Spider):

    name = "acm_pages"

    stype = 'Pages'

    db = DB_ACM

    url_field = 'doi'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.id_query_totals = -1
        self.total_results = 0
        
        self.use_selenium = True  # Enable Selenium to handle Cloudflare challenges
        self.use_api = False
        self.rows_par_page = 100
        self.max_results = 2000
        self.max_pages = self.max_results / self.rows_par_page
        self.wait_timeout = 10
        self.base_url = 'https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl&AllField='
        self.ids_query = {}

    def start_requests(self):

        
        base_search_url = f"{self.base_url}{quote(self.query.replace(' ','+'),safe='+')}"
        
        request_data = {
            "url" : base_search_url
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }

        print(f'id querys { self.id_query_totals} --- String : {base_search_url}')
        if self.id_query_totals == -1 :
            self.total_results = self.get_number_results(request_data)
            self.id_query_totals = DatabaseManager.insert_query_totals(self.db, base_search_url, self.query, self.total_results)


        
        print(f'Starting the scrapping of ACM .... totals {self.total_results}')    
        print(f'Info ... rows per page {self.rows_par_page}, Max pages {self.max_pages}')    
        print(f'Testin the totals id: {self.id_query_totals}')
      
        pages = int(min(math.ceil(self.total_results/self.rows_par_page),self.max_pages)) 
        print(f'Info ... pages {pages}')    

        #self.rows_par_page = 1
        #page_count = 1
        #pages=1
        
        for page_count in range(0, pages):

            print(f'----- requesting page count {page_count}')
            url = f'{base_search_url}&pageSize={self.rows_par_page}&startPage={page_count}'
            print(url)
            # TODO This must be updated with the trial and so no.
            id_query = DatabaseManager.insert_page(self.db, page_count, url, self.id_query_totals)
            self.ids_query[url] = id_query

            time.sleep(1)
            
            yield scrapy.Request (
                url,
                headers=headers,
                meta = {
                    'id_query' : id_query,
                    'wait_for': 'span.result__count',  # Wait for results count element
                    'wait_timeout': 15  # Increase timeout for Cloudflare challenge
                    },
                callback=self.parse
            )

    def parse(self, response):
        
        print('PARSING ACM')
        id_query = response.meta['id_query']
        
        # Check if we're getting a Cloudflare challenge page
        if "Just a moment" in response.text or "cf_chl_opt" in response.text:
            self.logger.error("Encountered Cloudflare challenge. Selenium should handle this automatically.")
            with open("acm_cloudflare_debug.html", 'w', encoding='utf-8') as file:
                file.write(response.text)
            return
        
        # Try to extract total results if not yet set
        if self.total_results <= 1000:  # Our default placeholder value
            result_count_element = response.css('span.result__count::text').get()
            if result_count_element:
                try:
                    self.total_results = int(result_count_element.replace(" Results", "").replace(",", ""))
                    self.logger.info(f"Updated total results to: {self.total_results}")
                except ValueError:
                    self.logger.warning(f"Could not parse result count: {result_count_element}")
        
        items = response.css("li.search__item")
        print(f'QUERIES PAGE {id_query} ---- {len(items)}')
        
        for item in items:
            publication_type = item.css("div.issue-heading::text").get()
            venue = item.css("span.epub-section__title::text").get()
            citations_info = item.css(".citation")
            citations = citations_info.css("::text").get().strip()
            downloads_info = item.css(".citation")
            downloads = downloads_info.css("::text").get().strip()
            date_str = item.css("div.bookPubDate::attr(data-title)").get().replace('Published: ', '').strip()
            #date_lst = date_str.split(' ')
            #date_day = int(date_lst[0])
            #date_month = date_lst[1]
            #date_year = int(date_lst[2])
            title_info = item.css(".issue-item__title a")
            title = title_info.css("::text, span::text").getall()
            title = "".join(title).strip()
            doi = title_info.attrib['href']
            venue 
            yield {
                'title': title,
                'doi': doi,
                'type': publication_type,
                'date': date_str,
                'id_issues': doi,
                'venue' : venue,
                #'date_day' : date_day,
                #'date_month' : date_month,
                #'date_year' : date_year,
                'id_query': id_query,
                'DB': self.db,
                'citations' : citations,
                'downloads' : downloads
            }

    def get_number_results(self, request_data):
        try:
            # When using Selenium, we need to trigger a proper request through the middleware
            # For now, let's set a default value and handle this in the main parse method
            self.logger.warning("get_number_results called with Selenium enabled. Will extract count from first page.")
            return 1000  # Default value, will be updated when first page is parsed
        except Exception as e:
            self.logger.error(f"Error extracting total results: {str(e)}")
            return 0