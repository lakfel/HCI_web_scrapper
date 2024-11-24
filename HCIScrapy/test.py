from scrapy.http import HtmlResponse
import os
from bs4 import BeautifulSoup



        
def open_spider(search_terms, db):
    
    if db == 'ACM':
        or_groups = []
        for group in search_terms:
            or_groups.append(" OR ".join([f'("AllField:(":{term})' for term in group]))
        return " AND ".join([f'({term})' for term in or_groups])
    elif db == 'IEEE':
        or_groups = []
        for group in search_terms:
            or_groups.append(" OR ".join([f'("All Metadata":{term})' for term in group]))
        return " AND ".join([f'({term})' for term in or_groups])
    elif db == 'Springer':
        or_groups = []
        for group in search_terms:
            or_groups.append(" OR ".join([f'"{term}"' for term in group]))
        return " AND ".join([f'({term})' for term in or_groups])
    return ''

def search_css_in_folder(folder_path, css_selector):
    # Verificar que la ruta es válida
    if not os.path.isdir(folder_path):
        print(f"La ruta '{folder_path}' no es una carpeta válida.")
        return

    # Recorrer los archivos en la carpeta
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Verificar que sea un archivo HTML
        if not filename.endswith(".html"):
            continue
        
        print(f"\nProcesando archivo: {filename}")

        try:
            # Leer el archivo
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Analizar el HTML con BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Buscar elementos que coincidan con el selector CSS
            elements = soup.select(css_selector)

            # Verificar si encontró algo
            if elements:
                for i, element in enumerate(elements, start=1):
                    print(f"\tElemento {i}: {element.get_text(strip=True)}")
            else:
                print("No lo encontré.")
        
        except Exception as e:
            print(f"Error procesando el archivo {filename}: {e}")

def get_variable_name(variable):
    # Search for the variable name in the global scope
    for name, value in globals().items():
        if value is variable:
            return name
    return None

def printV(variable):
    name = get_variable_name(variable)
    print(f'{name} : {variable}')


    
search_terms = [
                ["VR", "Virtual reality", "augmented reality", "AR", "mixed reality", "XR"],  
                ["Multiuser", "multi-user", "collaborative"]  
            ]
        
print(open_spider(search_terms=search_terms, db='ACM'))
print(open_spider(search_terms=search_terms, db='IEEE'))
print(open_spider(search_terms=search_terms, db='Springer'))



#search_css_in_folder(f'C:\\Users\\johannavila\\Documents\\Research\\Multiuser CVE Survey paper\\Scripts\\HCIScrapy\\ieee_types','.stats-document-abstract-doi')
"""
# Cargar el archivo HTML local
with open('C:\\Users\\johannavila\\Documents\\Research\\Multiuser CVE Survey paper\\Scripts\\HCIScrapy\\ieee_test.html', 'r', encoding='ISO-8859-1') as f:
    html_content = f.read()

# Crear un objeto de respuesta tipo Scrapy
response = HtmlResponse(url='http://example.com', body=html_content, encoding='ISO-8859-1')
#title = response.css('.document-title span').xpath('.//text()').get()
#printV(title)
#doi = response.css('meta.stats-document-abstract-doi a').xpath('.//text()').get()
doi = response.css('meta[scheme="doi"]::attr(content)').get()
print(doi)
date_str = response.css('.doc-abstract-pubdate').xpath('normalize-space(text())').get().strip()
printV(date_str)
date_info = date_str.split()
date_day = date_info[0]
printV(date_day)
date_month = date_info[1]
printV(date_month)
date_year = date_info[2]
printV(date_year)
abstract_t = response.css('.abstract-text').xpath('.//text()').getall()
abstract = ''.join(abstract_t).strip()
printV(abstract)
metrics = response.css('div.document-banner-metric-count')
citations = metrics[0].xpath('.//text()').get()
printV(citations)
downloads = metrics[1].xpath('.//text()').get()
printV(downloads)
comments = 'Downloads refer to full text views'
printV(comments)
"""





""" 
            stype = response.xpath('//meta[@name="parsely-type"]/@content').get()
            title = response.xpath('//meta[@name="parsely-type"]/@content').get().split('|')[0].strip()



            #title = response.css('.document-title span').xpath('.//text()').get()
            doi = response.css('.stats-document-abstract-doi a').xpath('.//text()').get()

            date_str = response.css('.doc-abstract-pubdate').xpath('normalize-space(text())').get().strip()
            date_info = date_str.split()
            date_day = date_info[0]
            date_month = date_info[1]
            date_year = date_info[2]
            abstract_t = response.css('.abstract-text').xpath('.//text()').getall()
            abstract = ''.join(abstract_t).strip()
            metrics = response.css('div.document-banner-metric-count')
            citations = metrics[0].xpath('.//text()').get()
            downloads = metrics[1].xpath('.//text()').get()
            comments = 'Downloads refer to full text views'
            url = response.meta['url']

                    
            yield {
                'db' : self.db,
                'title': title,
                'doi' : doi,
                'date' : date_str,
                'date_day' : int(date_day),
                'date_month' : date_month,
                'date_year' : int(date_year),
                'abstract' : abstract,
                'status' : 'OK',
                'comments' : comments,
                'citations' : int(citations),
                'downloads' : int(downloads),
                'url' : url,
                # Añade más campos según necesites
            }
            """