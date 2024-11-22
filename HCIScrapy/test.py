from scrapy.http import HtmlResponse



def get_variable_name(variable):
    # Search for the variable name in the global scope
    for name, value in globals().items():
        if value is variable:
            return name
    return None

def printV(variable):
    name = get_variable_name(variable)
    print(f'{name} : {variable}')

# Cargar el archivo HTML local
with open('C:\\Users\\johannavila\\Documents\\Research\\Multiuser CVE Survey paper\\Scripts\\HCIScrapy\\ieee_test.html', 'r', encoding='ISO-8859-1') as f:
    html_content = f.read()

# Crear un objeto de respuesta tipo Scrapy
response = HtmlResponse(url='http://example.com', body=html_content, encoding='ISO-8859-1')
title = response.css('.document-title span').xpath('.//text()').get()
printV(title)
doi = response.css('.stats-document-abstract-doi a').xpath('.//text()').get()
printV(doi)
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
