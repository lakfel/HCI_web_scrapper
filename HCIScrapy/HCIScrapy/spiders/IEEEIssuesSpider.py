import scrapy
from urllib.parse import quote, urlencode
import time
import random

class IeeeissuesspiderSpider(scrapy.Spider):

    # Spider's name
    name = "ieee_issues"

    # Database 
    db = 'IEEE'

    # Spider's type [Results, Page, Issues]
    stype = 'Issues'

    allowed_domains = ["ieeexplore.ieee.org"]

    base_url = "https://ieeexplore.ieee.org"
    
    url_field = 'url'

    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_selenium = True
        self.db_param = db_param
        self.query_param = query_param
        self.total_results = 0
        self.max_pages = 0
        self.wait_timeout = 10
        self.js = {}

    def start_requests(self):


        print(f' TOTAL Documents {len(self.documents)}')
        if not hasattr(self, 'documents'):
            self.documents = []
            self.logger.error('NO DOCUMENTS TO DOWNLOAD ')
        
        #docs = [self.documents[0]]

        for url in self.documents :


            search_url = f"{self.base_url}{url}"
            print(f'SEARCHING-- {self.db}, {search_url}')
            
            
            yield scrapy.Request(
                search_url, 
                meta={
                    'js' : [('metadata', 'return window.xplGlobal.document.metadata')],
                    'token_to_wait' : 'meta[name="parsely-type"]',
                    'url': search_url},
                dont_filter=True
            )

            #time.sleep(random.uniform(1, 2))



    def parse(self, response):
        try:
            #with open("ieee_test.html", 'w') as file:
            #    print(response.text.encode("utf-8"),file=file)
            #with open("ieee_test_meta.js", 'w') as file:
            #    print(self.metadata,file=file)                
            
            url = response.meta['url']
            js_parse = self.js[url]
            item = {'db' : self.db, 'url' : url.replace(self.base_url,'')}

            js_instruction, metadata = js_parse['metadata']
            
            #metadata.json.loads(metadata)
            #print(f'JS RESULTS = {metadata}')
            #return

            if 'title' in metadata:
                item['title'] = metadata['title']
            if 'doi' in metadata:
                item['doi'] = metadata['doi']
            if 'contentType' in metadata:
                item['type'] = metadata['contentType']

            # Not sure what the best way to get the content type is, I will append all the possibilities       

            if 'isChapter' in metadata and metadata['isChapter']:
                item['type'] = 'book chapter'
            elif 'isBook' in metadata and metadata['isBook']:
                item['type'] = 'book'
            elif 'isConference' in metadata and metadata['isConference']:
                item['type'] = 'conference paper'
            elif 'isEarlyAccess' in metadata and metadata['isEarlyAccess']:
                item['type'] = 'early access'
            elif 'isJournal' in metadata and metadata['isJournal']:
                item['type'] = 'journal'
            elif 'isStandard' in metadata and metadata['isStandard']:
                item['type'] = 'standard'
            
                
            if 'displayPublicationDate' in metadata:
                item['date'] = metadata['displayPublicationDate'].strip()
              
            if 'abstract' in metadata:
                item['abstract'] = metadata['abstract']

            item['status'] = 'OK'

            if 'publicationTitle' in metadata:
                item['venue'] = metadata['publicationTitle']

            if 'metrics'in metadata:
                metrics = metadata['metrics']
                if 'citationCountPaper' in metrics:
                    item['Citations'] = metrics['citationCountPaper']
                if 'totalDownloads' in metrics:
                    item['Downloads'] = metrics['totalDownloads']

            keywords = []
            if 'keywords' in metadata:
                for k_dic in metadata['keywords']:
                    keywords.extend(k_dic['kwd'])

            item['keywords'] = ' , '.join(keywords)

            del self.js[url]
            #print(f'PARSE SERUSL \n\t\t{item}')
            yield item
        
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")

    
