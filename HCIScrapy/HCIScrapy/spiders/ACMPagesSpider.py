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
        
        self.use_selenium = False
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        }

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

        for page_count in range(1, pages+1):

            print(f'----- requesting page count {page_count}')
            url = f'{base_search_url}&pageSize={self.rows_par_page}&startPage={page_count}'
            # TODO This must be updated with the trial and so no.
            id_query = DatabaseManager.insert_page(self.db, page_count, url, self.id_query_totals)
            self.ids_query[url] = id_query

            time.sleep(1.5)
            
            yield scrapy.Request (
                url,
                headers=headers,
                meta = {
                    'id_query' : id_query
                    },
                callback=self.parse
            )

    def parse(self, response):
        
        print('PARSING ACM')
        id_query = response.meta['id_query']
        for item in response.css("li.search__item"):
            publication_type = item.css("div.issue-heading::text").get()
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
            
            yield {
                'title': title,
                'doi': doi,
                'type': publication_type,
                'date': date_str,
                'id_issues': doi,
                #'date_day' : date_day,
                #'date_month' : date_month,
                #'date_year' : date_year,
                'id_query': id_query,
                'DB': self.db,
                'citations' : citations,
                'downloads' : downloads
            }

    def get_number_results(self, request_data):

        # I first check there is no initial query in the db 

        response, meta = self.request(request_data)
        soup = BeautifulSoup(response.text, 'html.parser')
        result_count_tag = soup.find(class_="result__count") 
        span = soup.find('span', class_ = 'result__count')
        if not result_count_tag:
            raise ValueError("Tag not found  -- data-test='results-data-total'.")
        span_text = span.get_text()
        result_count = int(span_text.replace(" Results", "").replace(",",""))
       
        return result_count