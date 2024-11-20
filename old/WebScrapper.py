import requests
from bs4 import BeautifulSoup
import random
import Proxies as prox
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import DBManager as dbm
from datetime import datetime
import math
import time
import random
from queue import Queue
import threading
import ACMScript as acm
import IEEEScript as ieee


#Global scope so all threads can use them
used_proxies = {}
proxies = []
proxies_updated = Event()

# Query to search
query = ""

# URL for the search
url_base = ""

# Queue to communicate with the thread to erfill proxies
task_queue = Queue()



# It updates proxies
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
        




   

def scrape_issues_multithread(db:str, get_issue_details):
    print("Starting scarping Issues...")
    connection = dbm.connect_to_db()
    num_issues = dbm.get_number_issues_uncomplete(connection, db)
    print(f'Issues : {num_issues}')
    def task_with_error_handling(doi, connection):
        try:
            get_issue_details(doi, connection)
        except Exception as e:
            print(f"Error on doi {doi}: {e}")

    for i in range(10) :
        dois = dbm.get_uncompleted_issues_dois(connection, db)
        thread_number = 1
        with ThreadPoolExecutor(max_workers=15) as executor:
            
            for doi in dois:
                thread_number += 1
                print("Launching a new thread for a doi ", doi , ' ID ',thread_number)
                executor.submit(task_with_error_handling, doi, connection)
                time.sleep(random.uniform(5, 10))





def scrape_pages(dbst):
    

    # First we retreive the info from the main website
    get_total_query_results = dbst.get('get_total_query_results')
    total_results = get_total_query_results()
    print(total_results)

'''
    #total_results = 100
    print('Total results:' ,total_results)
    connection = dbm.connect_to_db()
    total_pages = math.ceil(total_results / page_size)
    print('Total pages:' ,total_pages)


    def task_with_error_handling(page_count, page_size, connection):
        try:
            get_papers_request(url_base, str(page_count), str(page_size), connection)
        except Exception as e:
            print(f"Error on page {page_count}: {e}")

    with ThreadPoolExecutor(max_workers=5) as executor:
            
        for page_count in range(1, total_pages + 1):

            print("Launching a new thread... page ", page_count)
            executor.submit(task_with_error_handling, str(page_count), str(page_size), connection)
            time.sleep(random.uniform(10, 45))

'''



DB_ACM = 'ACM'
DB_IEEE = 'IEEE'

target_db = DB_IEEE

strategies = {
    DB_ACM : {
        'get_total_query_results' : acm.get_total_query_results
    },
    DB_IEEE : {
        'get_total_query_results' : ieee.get_total_query_results
    }
}

strategy = strategies.get(target_db)
scrape_pages(strategy)


#consumer_thread = threading.Thread(target=update_proxies_async, daemon=True)
#consumer_thread.start()

#proxies = prox.load_txt_proxies()


#scrape_acm_pages_multithreaded(50, url_base)
#scrape_acm_issues_multithread()
#test_no_async()

#task_queue.join()
#task_queue.put(None)  # Signal the consumer to stop
#consumer_thread.join()