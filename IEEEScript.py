

import requests
from bs4 import BeautifulSoup
import random
import Proxies as prox
import ACMRequest as areq
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import DBManager as dbm
from datetime import datetime
import math
import time
import random
from queue import Queue
import threading
import DBUtils as utils

# Query to search
query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'


# URL for the search
url_base = "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true"


query_encoded = areq.encode_boolean_expression(query)
query_name = "queryText"
url_base = areq.add_parameter_to_url(url_base, query_name, query_encoded)
task_queue = Queue()


def get_total_query_results() -> int:

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }

    response = requests.get(url_base, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve page")
        return 0
    
    soup = BeautifulSoup(response.content, "html.parser")
    result_count_tag = soup.select('.Dashboard-header > span > span')[1]
    result_count = int(result_count_tag.get_text().replace(" ,", ""))
    return result_count


# Reads a page from results and get all the issues storing them into the database
def get_acm_papers_page(soup: BeautifulSoup, id_query : int, connection):
    for item in soup.select("div.result-item-align"):
        title_info = item.select_one("h3")
        title = title_info.get_text(strip=True)
        description = item.select_one('div.description')
        venue = description.select_one('a').get_text()
        
        publication_type = item.select_one("div.issue-heading")
        issue_type = publication_type.getText()
        date = item.find("div", class_="bookPubDate")
        date_str = date['data-title'].replace('Published: ','').strip()
        date_lst = date_str.split(' ')
        date_day = date_lst[0]
        date_month = date_lst[1]
        date_year = date_lst[2]
        doi = title_info['href']
        print(date_str + ' - ' + title + ' - ' + doi)
        dbm.insert_data_issue(title, doi, issue_type, date_str, int(date_day), date_month, int(date_year), id_query, connection)


def build_url(page_count, page_size) :  
    page_prm_str = "pageSize"
    url_base_results = areq.add_parameter_to_url(url_base, page_prm_str, page_size) 

    page_count_str = "startPage"
    url_page = areq.add_parameter_to_url(url_base_results, page_count_str, str(page_count))      

    return url_page

def get_acm_papers_request(page_count, page_size, connection):

    page_prm_str = "pageSize"
    url_base_results = areq.add_parameter_to_url(url_base, page_prm_str, page_size) 

    page_count_str = "startPage"
    url_page = areq.add_parameter_to_url(url_base_results, page_count_str, str(page_count)) 

    response = make_request(url_page)

    print('Page ', page_count, ' Ready to be processed')
    soup = BeautifulSoup(response.content, "html.parser")
    current_timestamp = datetime.now()
    id_query = dbm.insert_data_query(query,page_count,url_base_results,current_timestamp,connection)
    get_acm_papers_page(soup, id_query, connection)
    print("\t Finishing thread... page ", page_count)


def get_issue_details(doi, connection):

    url = 'https://dl.acm.org/' + doi
    print("\t Reaching  ", url)
    response = make_request(url)
    print("\t Answered  ", url)
    soup = BeautifulSoup(response.content, "html.parser")
    abstract_tag = soup.select_one('section#abstract div[role="paragraph"]')
    abstract = abstract_tag.get_text()
    dbm.update_data_issue([
        ('Abstract',abstract),
        ('Status', 'OK')],
        doi,
        connection
    )
    print("\t Stored  ", url)


def scrape_acm_pages_multithreaded(page_size, url_base):
    # First I will get the 
    print("Let's  GO!!!")
    total_results = get_total_query_results()
    #total_results = 100
    print('Total results:' ,total_results)
    connection = dbm.connect_to_db()
    total_pages = math.ceil(total_results / page_size)
    print('Total pages:' ,total_pages)


    def task_with_error_handling(page_count, page_size, connection):
        try:
            get_acm_papers_request(str(page_count), str(page_size), connection)
        except Exception as e:
            print(f"Error on page {page_count}: {e}")

    with ThreadPoolExecutor(max_workers=5) as executor:
            
        for page_count in range(1, total_pages + 1):

            print("Launching a new thread... page ", page_count)
            executor.submit(task_with_error_handling, str(page_count), str(page_size), connection)
            time.sleep(random.uniform(10, 45))
   

def scrape_acm_issues_multithread():
    print("Starting scarping Issues...")
    connection = dbm.connect_to_db()
    num_issues = dbm.get_number_issues_uncomplete(connection)
    print(f'Issues : {num_issues}')
    def task_with_error_handling(doi, connection):
        try:
            get_issue_details(doi, connection)
        except Exception as e:
            print(f"Error on doi {doi}: {e}")

    for i in range(10) :
        dois = dbm.get_uncompleted_issues_dois(connection)
        thread_number = 1
        with ThreadPoolExecutor(max_workers=15) as executor:
            
            for doi in dois:
                thread_number += 1
                print("Launching a new thread for a doi ", doi , ' ID ',thread_number)
                executor.submit(task_with_error_handling, doi, connection)
                time.sleep(random.uniform(5, 10))

#proxies_manager = new ThreadPoolExecutor 

def test_no_async():
    global proxies
    connection = dbm.connect_to_db()
    prox.create_proxies_file()
    proxies = prox.load_txt_proxies()
    get_acm_papers_request(str(1),str(10), connection)

consumer_thread = threading.Thread(target=update_proxies_async, daemon=True)
consumer_thread.start()
#proxies = prox.load_txt_proxies()
#scrape_acm_pages_multithreaded(50, url_base)
scrape_acm_issues_multithread()
#test_no_async()

task_queue.join()
task_queue.put(None)  # Signal the consumer to stop
consumer_thread.join()