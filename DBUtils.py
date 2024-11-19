#import ACMScript as acm
#import IEEEScript as ieee


DB_ACM = 'ACM'
DB_IEEE = 'IEEE'

target_db = DB_IEEE

def get_total_query_results():
    if target_db == DB_ACM:
        return 2#acm.get_total_query_results()
    elif target_db == DB_IEEE:
        return 1#ieee.get_total_query_results()
    else:
        return 0
    

print(get_total_query_results())