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

            debug = 0
            debug+=1
            print(f' --- Debugging -- {debug}') #1
            js_instruction, metadata = js_parse['metadata']
            
            debug+=1
            print(f' --- Debugging -- {debug}') #2

            #metadata.json.loads(metadata)
            #print(f'JS RESULTS = {metadata}')
            #return

            if 'title' in metadata:
                item['title'] = metadata['title']
            debug+=1
            print(f' --- Debugging -- {debug}')#3
            if 'doi' in metadata:
                item['doi'] = metadata['doi']
            debug+=1
            print(f' --- Debugging -- {debug}')#4
            if 'contentType' in metadata:
                item['type'] = metadata['contentType']
            debug+=1
            print(f' --- Debugging -- {debug}')#5

            # Not sure what the best way to get the content type is, I will append all the possibilities       
            type_checkers = ['isBook', 'isBookWithoutChapters' ,'isChapter', 'isConference', 'isEarlyAccess', 'isJournal', 'isStandard']
            comments = [t for t in type_checkers if t in metadata and metadata[t]]
            debug+=1
            print(f' --- Debugging -- {debug}')#6
            if 'xploreDocumentType' in metadata:
                comments.append(metadata['xploreDocumentType'])
            debug+=1
            print(f' --- Debugging -- {debug}')#7
            if 'contentTypeDisplay' in metadata:
                comments.append(metadata['contentTypeDisplay'])
            item['Comments'] = ' , '.join(comments)
            debug+=1
            print(f' --- Debugging -- {debug}')#8
            
            if 'displayPublicationDate' in metadata:
                item['date'] = metadata['displayPublicationDate'].strip()
                #date_day = int(date.split()[0].split('-')[0])
                #date_month = date.split()[1]
                #item['date_day'] = date_day
                #item['date_month'] = date_month
                #item['date'] = date
                #date_year = int(date.split()[2])
            #if 'publicationYear' in metadata:
            #    item['date_year'] = metadata['publicationYear']
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

    
