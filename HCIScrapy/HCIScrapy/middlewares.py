# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time

class SeleniumMiddleware:

    def __init__(self):
        self.drivers = {}

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s


    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
        if getattr(spider, 'use_selenium', False):
            chrome_options = Options()
            #chrome_options.add_argument("--headless") 
            #chrome_options.add_argument("--disable-gpu")   # Improve in wondows
            #chrome_options.add_argument("--no-sandbox")
            #TODO This probably should go in settings
            chrome_options.add_argument(f"user-data-dir=C:\\Users\\jfgon\\AppData\\Local\\Google\\Chrome\\User Data - BU")             
            #chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            #chrome_options.add_experimental_option("useAutomationExtension", False)
            #chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")

            #service = Service(f'C:\\Users\\johannavila\\Documents\\Research\\chromedriver-win64\\chromedriver.exe')  
            service = Service(f'C:\\Users\\jfgon\\Documents\\Postodoc\\chromedriver-win64\\chromedriver.exe')  # Chrome driver path
            self.drivers[spider.name] = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            spider.request = lambda request_data: self.request_selenium(request_data, spider)
        else:
            spider.request = lambda request_data: self.request_html(request_data, spider)
        
    

    def request_html(self, request_data, spider):
        if 'url' in request_data:
            print(f'REQUESTING HTML ', request_data)
            url = request_data['url']
            timeout = 50
            params = {}
            headers = {}
            if 'timeout' in request_data:
                timeout =   request_data['timeout']
            if 'params' in request_data:
                params =   request_data['params']
            if 'headers' in request_data:
                headers =   request_data['headers']

            htmlResponse = requests.get(url, timeout=timeout, params=params, headers=headers)
            response = HtmlResponse(
                url,
                body=htmlResponse,
                encoding='utf-8',
                request=None
            )
            return (response, None)
        
        return (None,None)
    
    # TODO: Adapt IEEE issues to follow thisworkflow
    def request_selenium(self, request_data, spider):


        if spider.name not in self.drivers:
            raise ValueError(f"There is no driver for the spider '{spider.name}'")

        if 'url' not in request_data:
            raise KeyError("Missing 'url' in request_data")
        
        url = request_data['url']
        driver = self.drivers[spider.name]
        
        try:
            driver.get(url)
            
            token_to_wait = request_data.get('token_to_wait')
            if token_to_wait:
                WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, token_to_wait))
                )
            time.sleep(2)
            meta = request_data.get('meta', {})

            if 'js' in request_data:
                js_results = {}
                for js_name, js in request_data['js']:
                    response = driver.execute_script(js)
                    js_results[js_name] = (js, response)
                meta['js'] = js_results

            body = driver.page_source
            response = HtmlResponse(
                driver.current_url,
                body=body,
                encoding='utf-8',
                request=None
            )
            
            return (response, meta)
        except Exception as e:
            spider.logger.error(f"Error in request_selenium: {str(e)}")
            return (None , None)

        

    # TODO If needed the rotative headers must be done in the middleware
    def process_request(self, request, spider):

        if getattr(spider, 'use_selenium', False):

            meta = request.meta
            response, meta = self.request_selenium(meta, spider)

            if 'js' in meta:
                spider.js = meta['js']

           #TODO Adapt IEEE and test
            return response
        elif getattr(spider, 'use_api', False): 
            meta = request.meta
            if 'request_data' in meta:
                request_data = meta['request_data']
                print(f'TRYING THE HTML {request_data}')
                response, meta = self.request_html(request_data, spider)
                print(f'RETURNING THE HTML {response} -- {request_data}')
                return response
            return None
        return None  # Permite que Scrapy maneje la solicitud normalmente

    def spider_closed(self, spider):
        # Limpiar el driver cuando el spider termine
        if spider.name in self.drivers:
            self.drivers[spider.name].quit()
            del self.drivers[spider.name]


class HciscrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class HciscrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

