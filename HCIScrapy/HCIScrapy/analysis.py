from HCIScrapy.database import DatabaseConfig
from collections import Counter

def analyze_terms(entries, terms_list):

    fields = ['doi','title','abstract']
    conditions = [
                    'doi','ID NOT',None
                ]

    # Combinar todas las listas de términos en una sola lista plana
    all_terms = set(term.lower() for terms in terms_list for term in terms)

    results = []
    for entry in entries:
        title = entry.get('title', '').lower()
        abstract = entry.get('abstract', '').lower()
        
        # Combinar título y abstract
        text = f"{title} {abstract}"
        
        # Calcular términos únicos presentes
        unique_terms_in_text = {term for term in all_terms if term in text}
        unique_count = len(unique_terms_in_text)
        
        # Contar repeticiones de todos los términos
        term_frequencies = Counter(word for word in text.split() if word in all_terms)
        total_occurrences = sum(term_frequencies.values())
        
        # Guardar resultados para este entry
        results.append({
            'entry': entry,
            'unique_count': unique_count,
            'total_occurrences': total_occurrences
        })
    
    return results

# Ejemplo de uso
entries = [
    {'title': 'Deep learning applications', 'abstract': 'Deep learning is transforming AI'},
    {'title': 'Natural language processing', 'abstract': 'NLP deals with human language'}
]

terms_list = [['deep', 'learning'], ['natural', 'language', 'ai']]

results = analyze_terms(entries, terms_list)
for result in results:
    print(f"Title: {result['entry']['title']}")
    print(f"Unique Terms: {result['unique_count']}, Total Occurrences: {result['total_occurrences']}")
    print("---")

