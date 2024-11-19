

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

#Global scope so all threads can use them
used_proxies = {}
proxies = []
updating_proxies = False
proxies_updated = Event()
proxies_updating = False

# Query to search
query = "(AllField:(VR) OR AllField:(Virtual reality) OR AllField:(augmented reality) OR AllField:(AR) OR AllField:(Mixed reality) or OR AllField:(XR)) AND (AllField:(Multiuser) OR AllField:(multi-user) OR AllField:(collaborative))"

# URL for the search
url_base = "https://dl.acm.org/action/doSearch?fillQuickSearch=false&target=advanced&expand=dl"


query_encoded = areq.encode_boolean_expression(query, 'ACM')
query_name = "AllField"
url_base = areq.add_parameter_to_url(url_base, query_name, query_encoded)
task_queue = Queue()

def update_proxies_async():
    global proxies, proxies_updating
    proxies_updating = False
    while True:
        
        print("Waiting for a task...")
        task = task_queue.get()
        print("Task Received...")
        if task is None:
            print("Shutting down consumer thread.")
        #break  # Exit if we receive a signal to stop

        print("Refilling proxies")
        if len(proxies) != 0:
            print("There is still proxies! ", len(proxies))
        else:
            prox.create_proxies_file()
            proxies = prox.load_txt_proxies()
        print('update_proxies_async\n\tEvent sent')
        proxies_updated.set()
        task_queue.task_done()
        #proxies_updating = False

        proxies_updated.clear() 

def get_total_resutls() -> int:

    page_prm_str = "pageSize"
    page_size = "1"
    url_base_results = areq.add_parameter_to_url(url_base, page_prm_str, page_size) 

    page_count_str = "startPage"
    page_count = 1
    url_base_results = areq.add_parameter_to_url(url_base_results, page_count_str, str(page_count))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }

    response = requests.get(url_base_results, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve page")
        return 0
    
    soup = BeautifulSoup(response.content, "html.parser")
    result_count_tag = soup.find(class_="result__count") 
    result_count = int(result_count_tag.get_text().replace(" Results", "").replace(",",""))
    return result_count


# Reads a page from results and get all the issues storing them into the database
def get_acm_papers_page(soup: BeautifulSoup, id_query : int, connection):
    for item in soup.select("li.search__item"):
        publication_type = item.select_one("div.issue-heading")
        issue_type = publication_type.getText()
        date = item.find("div", class_="bookPubDate")
        date_str = date['data-title'].replace('Published: ','').strip()
        date_lst = date_str.split(' ')
        date_day = date_lst[0]
        date_month = date_lst[1]
        date_year = date_lst[2]
        title_info = item.select_one(".issue-item__title a")
        title = title_info.get_text(strip=True)
        doi = title_info['href']
        print(date_str + ' - ' + title + ' - ' + doi)
        dbm.insert_data_issue(title, doi, issue_type, date_str, int(date_day), date_month, int(date_year), id_query, 'ACM' ,connection)



def make_request(url) :
    
    global proxies, used_proxies
    
    while True:

        print('Requesting website....', url)
        if len(proxies) == 0:
            print('Make request...\n\tProxies empty!...thread sleeping until the proxies are available')
            #if not proxies_updating:
            task_queue.put('Refill proxies!!!')
            proxies_updated.wait()
            
        proxy = None

        # Re-filled proxies can include some of the already rejected proxies, I select randomly re-rejecting possible previous proxies
        while proxy is None:
            proxy = random.choice(proxies)
            proxy_str =  f"{proxy['ip']}:{proxy['port']}"
            print('Trying page ... ', url , ' ... proxy : ', proxy_str)
            if proxy_str in used_proxies:
                print('Proxy : ', proxy_str, ' already used, removing from ', len(proxies))
                try:
                    proxies.remove(proxy)
                    print('Remaining proxies ', len(proxies))
                except e:
                    print('Not removing proxy, something happened')
                proxy = None

        # If the proxy is exists, I try to reach the website
        if proxy is not None:
            formatted_proxy = prox.format_proxy(proxy)
            try:
                response = requests.get(url, proxies=formatted_proxy, timeout=500)
                response.raise_for_status()  # Check for HTTP errors
                print('Request at:' , url, ' got an answer!')
                
                # Unsatisfactory result
                if response.status_code != 200 or response == None:
                    used_proxies[proxy_str] = f"Failed to retrieve page. Status code {response.status_code}"
                    try:
                        proxies.remove(proxy)
                    except e:
                        print('Something happened removing')
                    print('Request at:' , url, f' WRONG ANSWER {response.status_code}!\nRemoving, remaining ', len(proxies))
                else:
                    print('Request at:' , url, ' GOOD answer!')
                    return response

            except requests.RequestException as e:
                # If an error occurs, remove the proxy and print the error
                print(f"Proxy failed ({proxy['ip']}:{proxy['port']}), trying another. Error: {e}")
                used_proxies[proxy_str] = e
                try:
                    proxies.remove(proxy)
                except e:
                    print('Could not remove the proxie')
                print('REMAINING PROXIES ', len(proxies))
                #response = None
        


def get_acm_papers_request(page_count, page_size, connection):

    page_prm_str = "pageSize"
    url_base_results = areq.add_parameter_to_url(url_base, page_prm_str, page_size) 

    page_count_str = "startPage"
    url_page = areq.add_parameter_to_url(url_base_results, page_count_str, str(page_count)) 

    response = make_request(url_page)

    print('Page ', page_count, ' Ready to be processed')
    soup = BeautifulSoup(response.content, "html.parser")
    current_timestamp = datetime.now()
    id_query = dbm.insert_data_query(query,page_count,url_base_results,current_timestamp, 'ACM' ,connection)
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
    total_results = get_total_resutls()
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
    num_issues = dbm.get_number_issues_uncomplete(connection, 'ACM')
    print(f'Issues : {num_issues}')
    def task_with_error_handling(doi, connection):
        try:
            get_issue_details(doi, connection)
        except Exception as e:
            print(f"Error on doi {doi}: {e}")

    for i in range(10) :
        dois = dbm.get_uncompleted_issues_dois(connection, 'ACM')
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



#print('...getting the proxies')
consumer_thread = threading.Thread(target=update_proxies_async, daemon=True)
consumer_thread.start()
#print('...getting the proxies')
proxies = prox.load_txt_proxies()
#print('...getting the proxies')
#scrape_acm_pages_multithreaded(50, url_base)
scrape_acm_issues_multithread()
#test_no_async()

task_queue.join()
task_queue.put(None)  # Signal the consumer to stop
consumer_thread.join()