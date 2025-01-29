from database import DatabaseManager
from collections import Counter
from config import *
import json 
import pandas as pd
import re
from itertools import tee
from bs4 import BeautifulSoup


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

    

    for url, title, abstract  in documents:

    
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
    
        df = DatabaseManager.get_random_issue_queries(TRIAL, 15000)
        df.to_csv(f'random_issues_trial_{TRIAL}_2.csv', index=False, encoding='utf-8')
        #print(f"Datos exportados exitosamente a {output_file}")

    except Exception as e:
        print(f"Error: {e}")
    
def define_paper_nature():


    df = DatabaseManager.get_random_issue_queries(TRIAL, 15000)
    print(df.head())
    def classify_paper(row):
        content = (str(row['title']) + " " + str(row['abstract'])).lower()
        # Determine if VR/AR/XR/MR is used

        vr_terms = {"vr", "virtual reality", "ar", "augmented reality", "mr", "mixed reality", "xr", "extended reality"}
        uses_vr_ar_xr = "Yes" if any(term in content for term in vr_terms) else "No"

         # Coincidences in text
        coincidences = ", ".join([term for term in vr_terms if term in content]) if uses_vr_ar_xr == "Yes" else "None"

        # Determine category and subcategory
        if uses_vr_ar_xr == "Yes":
            if "collaborative" in content or "multi-user" in content or "multi-user" in content:
                if "cross" in content or "platform" in content:
                    category = "Human-Centric Studies"
                    subcategory = "Collaboration, Crossed Platforms"
                else:
                    category = "Human-Centric Studies"
                    subcategory = "Collaboration"
            elif any(term in content for term in {"rendering", "tracking", "latency"}):
                category = "Technological Focus"
                subcategory = "Rendering, Tracking"
            elif any(term in content for term in {"education", "healthcare", "art", "industrial"}):
                category = "Application Domains"
                subcategory = "Education" if "education" in content else "Healthcare" if "healthcare" in content else "Industrial Applications"
            else:
                category = "Human-Centric Studies"
                subcategory = "General"
        else:
            category = "Erratum or Unclassifiable"
            subcategory = "Irrelevant Focus"

        return uses_vr_ar_xr, coincidences, category, subcategory
   

def classify_rows():

    print('Quqerying issues')
    df = DatabaseManager.get_issues_queries(TRIAL, 19000)
    # Apply classification
    df["Terms category 1"], df["Terms category  2"], df["Terms 1"], df["Terms 2"] = zip(*df.apply(classify_record, axis=1))

    # Save the results to a new file
    output_path = "output_file_it2.csv"
    #df.to_csv(output_path, index=False)

    print(f"Classification complete. Results saved to {output_path}")

# Helper function to find two consecutive words
def find_consecutive_words(text, acronym):

    letters = list(acronym.lower())

    pattern = r'\b({})\w*\s+({})\w*\b'.format(letters[0], letters[1]) if len(letters) > 1 else r'\b({})\w*\b'.format(letters[0])

    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    # Formatear y devolver las palabras encontradas
    found_pairs = [' '.join(match).lower() for match in matches]
    return found_pairs


# Classification function
def classify_record(row):
    #print(f'CLASSIFIYING ROW... {row}')
    text = f"{row['Title']} {row['Abstract']} {row['keywords']}".lower()
    text_case= f"{row['Title']} {row['Abstract']} {row['keywords']}"

    complete_terms = TERMS1 + [t.replace(' ','-') for t in TERMS1] + [t.replace(' ','') for t in TERMS1]
    matching_terms1 = [t for t in complete_terms if t in text]

    terms2 = TERMS2 + [t.replace(' ','-') for t in TERMS2 if t.replace(' ','-') not in TERMS2] + [t.replace(' ','') for t in TERMS2 if t.replace(' ','') not in TERMS2] 
    print(f'TERMS 2 {terms2}')
    print(f'text {text}')
    matching_terms2 = [t for t in terms2 if t in text]
    print(f'matching_terms2 2 {matching_terms2}')
    
    terms3 = TERMS3 + [t.replace(' ','-') for t in TERMS3 if t.replace(' ','-') not in TERMS3] + [t.replace(' ','') for t in TERMS3 if t.replace(' ','') not in TERMS3] + TERMS2_REGEX 
    matching_terms3 = [t for t in terms3 if t in text]

    regex_matching_terms = []
    for ex in TERMS2_REGEX:
        terms = ex.split()
        pattern = rf'{terms[0]}\b[ -]?\w+[ -]?\b{terms[1]}[s]?\b'
        matches = re.findall(pattern, text)
        unique_matches = list(set(matches))
        regex_matching_terms.extend([match for match in unique_matches if match not in regex_matching_terms])

    
    acrs = ACRONYMS
    acrs_complete_matching = []
    acrs_modified_matching = []
    for acr in acrs:
        pattern_complete = fr'\b{acr}\b'
        pattern_modified = fr'\b[a-z]*[A-Z]*{acr[0]}[a-z]*[A-Z]*{acr[1]}[a-z]*[A-Z]*\b'
        if re.search(pattern_complete, text_case):
            acrs_complete_matching.append(ex)

        matches = re.findall(pattern_modified, text_case)
        unique_matches = list(set(matches))
        acrs_modified_matching.extend([match for match in unique_matches if match not in acrs_modified_matching])


    group1 = '900 - No match'
    group2 = '900 - No match'

    group1_terms = matching_terms1+ acrs_complete_matching
    group1_terms.extend([t for t in acrs_modified_matching if t not in group1_terms])

    group2_terms = matching_terms2 + matching_terms3
    group2_terms.extend([t for t in regex_matching_terms if t not in group2_terms])

    if len(matching_terms1) > 0:
        group1 = '1 - Complete terms'
    elif len(acrs_complete_matching) > 0:
        group1 = '2 - Complete acrs'
    elif len(acrs_modified_matching) > 0:
        group1 = '3 - Modified acrs'
    
    if len(matching_terms2) > 0:
        group2 = '1 - Complete terms cross'
    elif len(matching_terms3) > 0 :
        group2 = '2 - Complete terms'
    elif len(regex_matching_terms) > 0 :
        group2 = '3 - Regex terms'

    return group1,  group2,  group1_terms, group2_terms 


#get_random_issues()
#define_paper_nature()
#define_categories_ZERO()
#print(classify_record({'title':'A collaborative optimization strategy for computing offloading and resource allocation based on multi-agent deep reinforcement learning', 'abstract': 'This paper demonstrates the connection between organisation, collaboration and learning in virtual learning environments (VLEs). Our main focus is the investigation of the extent to which course developers and course instructors need to consider organisational measures and design in order to trigger (self-guided) learning and collaboration of participants within online learning environments. The design of these virtual learning environments involves an intricate balance between the following elements: the organisation of the content; how the instructional activities are sequenced; how the interactions between students, tasks, and materials are structured; and how the learning process is evaluated. Mentorship must be present throughout this process. Aspects of mentorship can manifest themselves in a variety of ways including: asking an expert, true mentoring, tutoring, and peer to peer support.'}))
classify_rows()