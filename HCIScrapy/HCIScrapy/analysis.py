from database import DatabaseManager
from collections import Counter
from config import SEARCH_QUERY
from config import TRIAL # Probably I would need only the trial and manage the 
import json 
import pandas as pd
def analyze_terms():

    fields = ['doi','title','abstract']
    conditions = [
                    ('doi','IS NOT',None),
                    #('doi','=','/doi/10.1145/3609395.3610596'),
                    ('title','IS NOT',None),
                    ('abstract','IS NOT',None)
                ]

    search_terms_str = DatabaseManager.get_query_terms(TRIAL)
    print(search_terms_str)
    search_terms_json= json.loads(search_terms_str)
    search_terms = search_terms_json['query']
    documents = DatabaseManager.get_issues(fields,conditions)
   
    all_terms = [term.lower() for terms in search_terms for term in terms]
    results = []
    docs = [documents[0]]

    print(f'QUERY TERMS = {type(search_terms)} -- {search_terms}\n\t all_terms : {all_terms} \n\t{docs}')

    

    for doi, title, abstract  in documents:

    
        text = f"{title.lower()} {abstract.lower()}"
        
        # Unique terms
        unique_terms_in_text = {term for term in all_terms if term in text}
        unique_count = len(unique_terms_in_text)
        
        # Repetitions
        term_frequencies = Counter(word for word in all_terms if word in text)
        total_occurrences = term_frequencies.total()
        
        matching_groups = 0
        for term_group in search_terms:
            if any(term.lower() in text for term in term_group):
                matching_groups += 1

        print(f'Results for {doi} \n\tunique_terms_in_text : {unique_terms_in_text} \n\tterm_frequencies{dict(term_frequencies)} \n\tmatching_groups{matching_groups}')

        values = [
                    ('keyword_count', unique_count),
                    ('unique_terms', str(unique_terms_in_text)),
                    ('key_group_count', matching_groups),
                    ('keyword_repetition' , total_occurrences),
                    ('term_frecuency', str(dict(term_frequencies)))
                ]
        DatabaseManager.upsert_issue_query(values,doi,TRIAL)

def get_random_issues():
    try:
    
        df = DatabaseManager.get_random_issue_queries(TRIAL, 500)
        df.to_csv(f'random_issues_trial_{TRIAL}.csv', index=False, encoding='utf-8')
        #print(f"Datos exportados exitosamente a {output_file}")

    except Exception as e:
        print(f"Error: {e}")
    

get_random_issues()
#analyze_terms()
    