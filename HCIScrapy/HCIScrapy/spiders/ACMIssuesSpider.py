import scrapy
import time
from HCIScrapy.config import DB_ACM

class AcmissuesspiderSpider(scrapy.Spider):
    
    # Spider's name
    name = "acm_issues"

    # Database
    db = DB_ACM

    # Spider's type
    stype = 'Issues'

    # Where to get the info to create the URL in the database
    url_field = 'doi'

    # Use selenium ?
    use_selenium = False

    # Use API ?
    use_api = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.total_results = 0
        self.rows_par_page = 200
        self.max_results = 2000
        self.max_pages = self.max_results / self.rows_par_page
        self.wait_timeout = 10
        self.base_url = 'https://dl.acm.org'
        self.use_selenium = False
        self.use_api = False

    def start_requests(self):

        if not hasattr(self, 'documents'):
                    self.documents = []
                    self.logger.error('NO DOCUMENTS TO DOWNLOAD ')
                    print('NO DOCUMENTS TO DOWNLOAD ')
        print(f' Starting ISSUES ACM -- TOTAL Documents {len(self.documents)}')
    
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        }

        for url in self.documents:
            search_url = f"{self.base_url}{url}"
            print(f'SEARCHING-- {search_url}')
            time.sleep(1.5)
            
            yield scrapy.Request (
                url=search_url,
                meta={'doi': url},
                headers=headers,
                callback=self.parse
            )
              

    def parse(self, response):

        doi = response.meta['doi']
        print(f'Parsing --- {self.base_url}{doi}')
        abstract = response.css('section#abstract div[role="paragraph"]::text').get().strip()
        keywords = response.css('section[property="keywords"] li a::text').getall()
        keywords_string = ", ".join(keywords)
        yield {
                'doi': doi,
                'abstract': abstract,
                'DB': self.db,
                'keywords' : keywords_string,
                'status':'OK'
            }
        
