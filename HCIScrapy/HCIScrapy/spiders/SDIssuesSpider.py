import scrapy
import time
import random
from dotenv import load_dotenv
import os
import json
from HCIScrapy.config import DB_SD


class SdissuesspiderSpider(scrapy.Spider):
    # Spider's name
    name = "sd_issues"

    # Database 
    db = DB_SD

    # Spider's type [Results, Page, Issues]
    stype = 'Issues'
    
    url_field = 'doi'

    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.use_api = True
        load_dotenv()
        self.API_KEY = os.getenv("SD_API_KEY")
        self.wait_timeout = 10
        self.metadata = {}
        self.base_search_url = 'https://api.elsevier.com/content/metadata/article'


    def start_requests(self):


        # Initial search
        HEADERS = {
            "X-ELS-APIKey": self.API_KEY,
            "Accept": "application/json",  # Cambia a "text/xml, application/atom+xml" si prefieres XML
        }


        request_data = {
            "url" : self.base_search_url, 
            "headers" : HEADERS,
            
        }

        
        while len(self.documents) > 0:
            dois = []
            for i in range(min(70, len(self.documents))):
                dois.append(self.documents.pop(0))

            query = ' OR '.join([f'doi({doi})' for doi in dois])
            #print(query)
            params = {
                'query' : query,
                'view' : 'COMPLETE'
            }   
            request_data_tempo = request_data.copy()
            request_data_tempo['params'] = params
            #search_url = f"{self.base_url}{url}"
            #print(f'SEARCHING-- {self.db}, {doi}')
        
            yield scrapy.Request(
                self.base_search_url,
                meta = {
                        'request_data': request_data_tempo 
                        },
                dont_filter=True,
                callback=self.parse
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):
        data = json.loads(response.text)
        #print(f'Got article {data}')
        search_results = data['search-results']
        
        results = int(search_results['opensearch:totalResults'])
        doit = search_results['opensearch:Query']['@searchTerms']
        if results == 0:
            print(f'DOI NOT FOUND {doit[2:-1]}')
            yield {
                'db' : self.db,  
                'doi' :doit[2:-1],
                'comments' : 'DOI NOT FOUND',
                'status' :'Not Found'
            }
        else:
            # TODO maybe is better to send alld the entries at once, not one by one.
            for entry in search_results['entry']:
                #print(entry)
                doi = entry['prism:doi']
                if doi:
                    item = {
                        'db' : self.db,
                        'doi' : doi,
                        'status' : 'OK', 
                        }
                    
                    if 'dc:description' in entry:
                        item['abstract'] = entry['dc:description']
                    elif 'prism:teaser' in entry:
                        item['abstract'] = entry['prism:teaser']
                    
                    if 'prism:aggregationType' in entry:
                        item['comments'] = entry['prism:aggregationType']

                    if 'pubType' in entry:
                        item['type'] = entry['pubType']

                    yield item
                else:
                    print(f'NOT RESULTS WITH {doit} --- {data}')

