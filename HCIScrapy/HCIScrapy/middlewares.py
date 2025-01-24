# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.http import TextResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
from dotenv import load_dotenv
import os 

class SeleniumMiddleware:

    def __init__(self):
        self.drivers = {}

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s


    def spider_opened(self, spider):
        if getattr(spider, 'use_selenium', False):
            #chrome_options.add_argument("--headless") 
            #chrome_options.add_argument("--disable-gpu")   # Improve in wondows
            #chrome_options.add_argument("--no-sandbox")
            #TODO This probably should go in settings
            

                
            load_dotenv()
            
                
            
            #lab['options'].add_argument(f"user-data-dir=C:\\Users\\johannavila\\AppData\\Local\\Google\\Chrome\\User Data - BU")   
            #lab['service'] = Service(f'C:\\Users\\johannavila\\Documents\\Research\\chromedriver-win64\\chromedriver.exe')     

            
            options_sel = Options()
            user_data_path = os.getenv('CHROME_USER_DATA_PATH')
            print(f'user_data_path - {user_data_path}')
            options_sel.add_argument(f"user-data-dir={user_data_path}")
            service_path = os.getenv("SELENIUM_PATH_SERVICE")
            print(f'service_path - {service_path}')
            service_sel = Service(service_path)  

            #options_sel.add_argument("--headless")
            options_sel.add_argument("--disable-dev-shm-usage")
            options_sel.add_argument("--remote-debugging-port=0")  # Use random debugging port
            options_sel.add_argument('--log-level=3')  # Only show fatal errors
            options_sel.add_experimental_option('excludeSwitches', ['enable-logging'])
            options_sel.add_argument('--disable-logging')
            options_sel.add_argument('--silent')
            
            #chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            #chrome_options.add_experimental_option("useAutomationExtension", False)
            #chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")

            
            #conf = lab

            self.drivers[spider.name] = webdriver.Chrome(
                service=service_sel,
                options=options_sel
            )

            try:
                # Kill any existing Chrome processes using the user data directory
                import psutil
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == 'chrome.exe':
                        try:
                            proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                self.drivers[spider.name] = webdriver.Chrome(
                    service=service_sel,
                    options=options_sel
                )
                spider.request = lambda request_data: self.request_selenium(request_data, spider)
            except Exception as e:
                spider.logger.error(f"Failed to initialize Chrome driver: {str(e)}")
                raise
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

            api_response = requests.get(url, timeout=timeout, params=params, headers=headers)
            response = TextResponse(
                url,
                body= api_response.text,
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
            
            
            if 'token_to_wait' in request_data:
                token_to_wait = request_data.get('token_to_wait')
                WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, token_to_wait))
                )
            time.sleep(1)
            meta = request_data.get('meta', {})

            if 'js' in request_data:
                js_results = {}
                for js_name, js in request_data['js']:
                    response = driver.execute_script(js)
                    js_results[js_name] = (js, response)
                meta['js'] = js_results

            body = driver.page_source
            response = HtmlResponse(
                url=url,
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
        print(f'MIDDLEWARES ----- processing requests...')
        if getattr(spider, 'use_selenium', False):

            meta = request.meta
            response, meta = self.request_selenium(meta, spider)

            if 'js' in meta:
                spider.js = meta['js']

           #TODO Adapt IEEE and test
            return response
        elif getattr(spider, 'use_api', False): 
            print('Requesting API')
            meta = request.meta
            if 'request_data' in meta:
                request_data = meta['request_data']
                response, meta = self.request_html(request_data, spider)
                response = TextResponse(
                    request_data['url'],
                    body=response.text,
                    encoding='utf-8',
                    request=None
                )
                return response
            return None
        return None  

    def spider_closed(self, spider):
        """Cleanup method to ensure all Selenium resources are properly released"""
        if spider.name in self.drivers:
            try:
                # Quit the driver
                self.drivers[spider.name].quit()
                
                # Kill any remaining chrome processes
                import psutil
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.name() == 'chrome.exe' or proc.name() == 'chromedriver.exe':
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                del self.drivers[spider.name]
                print(f"Successfully closed Selenium driver for spider: {spider.name}")
            except Exception as e:
                print(f"Error closing Selenium driver: {e}")


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

