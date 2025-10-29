# Scraper

Notes related to the process of building the scrapper for **ACM, IEEE, ScrpingerLink** and **Elsevier ScienceDirect**.

## ACM

ACM does not have API. Data retreival must be done with REST requests. In Scrapy ot gets banned easily. It is easier playing with normal requests, rotating headers and proxies.

The search string can include what fields are taken into account. An example of it with our first trial

`(AllField:(VR) OR AllField:(Virtual reality) OR AllField:(augmented reality) OR AllField:(AR) OR AllField:(Mixed reality) or OR AllField:(XR)) AND (AllField:(Multiuser) OR AllField:(multi-user) OR AllField:(collaborative))`

The limit of rows you can retreive is 2K.

### Type of issues

After the first trial the found type of articles are

***Included***
- Article*
- Chapter
- research-article
- short-paper
- survey* // Survey papers

***NOT Included***

- column
- course
- demonstration
- editorial
- extended-abstract
- invited-talk
- keynote
- news
- opinion
- other
- panel
- poster
- proceeding
- tutorial


## IEEE

IEEE does have an API but I started first with the webscrapping, using selenium since the website uses javascript, and it is through a global js variable I am getting all the metadata

TODO: Migrate to the API

I did not find any limitations in the number of issues. This first trial coveef +4000.

The search also allow to define in what field we want the search to be done on. An example on the search string

`(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))`

### Type of issues

***Included***
- Book Chapter
- Conference Paper
- Journal

***NOT Included***
- conferences
- Early Access Article
- Standard

## SpringerLink

Springer also has API. I did the search with normal requests. 
Search is limited to 1K. 
Search string sample 

``("VR" OR "Virtual reality" OR "augmented reality" OR "AR" OR "mixed reality" OR "XR") AND ("Multiuser" OR "multi-user" OR "collaborative")``


### Type of issues

***Included***
- article
- Paper

***NOT Included***
- book


## Elsevier ScienceDirect

I used the API since doing it with requests or selenium normally results in banning. Api ispretty good

Results limited to 6k

Search string sample 

``("VR" OR "Virtual reality" OR "augmented reality" OR "AR" OR "mixed reality" OR "XR") AND ("Multiuser" OR "multi-user" OR "collaborative")``



### Type of issues


***Included***

- chp , Chapter
- fla , Full-length article
- mic , Micro article
- osp , Original software publication
- rev , Review article


***NOT Included***
- abs , Abstract
- brv , Book review
- cnf , About a conference
- cor , Correspondence
- crp , Case Report
- dat , Data article
- dis , Discussion
- edi , Editorial
- err , Erratum
- ins , Insights
- mis , Miscellaneous
- mis , Miscellaneous
- nws , News
- pgl , Practice Guidelines
- pro , Protocol
- prv , Product review
- pub , Publisher&#39;s note
- sco , Short communication
- ssu , Short review
- vid , Video Article


# Categorizing

In the first iteration I revise papers in order explore possible fields of study. We start by analyzing possible scnearios of the papers finding 4 cases.
Based in the paper 10.48550/arXiv.2010.05988
- The paper does research in aspects related to VR/AR/XR/MR
- The paper uses VR/AR/XR/MR in reserach with other fields
- The papers was included by mistake due to the misunderstood use of the keywords
- The title and abstract are not enough to determine

# Next meeting questions

Discuss inclusion criteria that are not clear

## ACM

I am not sure what 'Article' means, seems to be way more informal, not peer reviewed ubt the I saw examples such as an article from ISMAR ehich I did not have access to to verify. As it is smaller in number, I keep it.

Probably better go with full words cuz there are several coincidences with words such as XR X-Ray. VR- Voice rated .... etc

# Others

Estoy realizando un estudio para un survey paper sobre Virtual Reallity, Augmented reality, Mixed reality, o Extended reality en multiusuarios multiplataforma. Es un proyecto que se hace en iteraciones. Estamos en la primera iteración que tiene el ánimo de explorar que hay en investigación sobre el tema actualmente, antes de especializarnos en un campo específico.
Hemos realizado la descarga de papers en las bases de datos ACM, IEEE, SpringerLink, ScienceDirect basados en una consulta que anida terminos. Los terminos estan en grupos. Dentro de cada grupo, los terminos se anidan con OR. Los grupos se anidan con AND entre ellos
`("VR" OR "Virtual reality" OR "augmented reality" OR "AR" OR "mixed reality" OR "XR") AND ("Multiuser" OR "multi-user" OR "collaborative")`
doi
title
abstract
keyword_count: Cantidad de keywords que aparecen en el titulo y abstract
key_group_count: Cantidad de grupos que aparecen con almenos un termino en el titulo y abstrac
keyword_repetition:  Repeticiones de los keywords en el titulo y abstract
unique_terms: String de keywords que aparecen en titulo y abstract
term_frecuency: Frecuencia en la que cada keyword aparece en titulo y abstract.
Quiero empezar un análisis con el archivo CSV que tiene 500 registros aleatorios de los resultados que hemos encontrado
Quiero que generes un archivo con la mismoa información del archivo de entrada pero agregando nuevas columnas como sigue
Fits the field: Acá quiero que pongas 'Y' si el paper busca realizar investigación sobre VR, AR, XR, MR. Pongas 'N' si el paper usa VR, AR, XR, MR para investigar otros campos como por ejemplo (pero no limitado) educacion, entrenamiento, psicologia, educacion, u otros. Pongas 'ER' si el paper no investiga ni utiliza VR,AR,XR,MR sino que peude ser un error de los resultados como por ejemplo usando los acronimos con otro significados. Pongas 'NA' si con el título y el abstract no es posible definir este campo.
Field. Si en el campo anterior es 'Y', quiero que pongas que esta investigando, por ejemplo immersion, performance, user experience, u potros que identifiques. Puede ser más de uno. Si el campo anterior es 'N', quiero que pongas en que otro campo se esta usando la tecnología. Si en el campo anterior en 'ER' quier que calsifiques el error
Contrubution. Unicamente sin en 'Fits the field' es 'Y', quiero que digas que tipo de contribución es. Por ejemplo, empirical study, methodology, system, prototype, u otro que encuentres. Si en 'Fits the field' es diferente a 'Y', déjalo en blanco.
Keywords. Quiero que identifiques keywords relevantes que vayan siendo repetitivos y los pngas en una lista separados por comas

# Notes

It seemes that the acronyms are problematic since, I think, the databases engines not always look for info in words but in the whole text. So there are A LOT of  coincidences, specially with AR
In the pipeline, we will need to process immediately the tet and define if it is a clear hit or not
It seems some of the engines are very broad. Like for instance in the different group of terms, sometimes papers only match one. Althoguth in the references I checked some of the terms. I will need to  refine the search as much as possible. Including not ALL meta data but only the ones that matters Title, Keywords *useing these to improve the search possbily*, and text when possible
Not all multi user specify early in the document if they are cross-platform. Thus I am gonna include them
I will use the venues to also filter. 
Acronyms can be also check by not ignoring case 

Problems with current search

- Serch fields: I started by including (when possible) all metadata fields in the search trying to avoid missing fields. However, this makes verifications based on title, abstract, and kewords difficult. Probably at this stage, it is better to limit the search fields to those.
- Search engines accuracy. Even when we have conjunction condition of grups of disjunctions G1(OR) AND G2(OR), the engines are not assuring the AND conditions.
- Acronyms. Acronyms present some problems
    - Some engines are looking for the acronyms not as words but part of words. This gives a LOT of false positive hits with very generic acronims such as AR.
    - Acronyms are not taking into account cases so this is even worse
    - In some cases, Acronyms are embeeded in other acronyms, like more complex
- Other words must be included
- Some results are not dilligently separating words by space.

Actions
- Modifying scapping
    - Assure that the scrapping is retrieving the information correctly, like for instance when complex HTML is found, it respects the spaces between words.
    - Modify (for now) when possible the search to look for info only in the desired metadata

- Pre-filter.
    - Classify results according to the terms I found
        - Group 1. It has the terms of the first group (NOT ACRONYMS) and terms of the second group
        - Group 2. It does not have complete terms of the first groups, but it has full complete ACRONMYS and terms in the second group
        - Group 3. It has modified versions of the acronyms and terms of the second group
        - Group 4. It has either compelte terms, completer ACRONYMS, or modified acronyms of the first group but no elements of the second group
        - Group 5. it does not have any coincidente with the first group but it has coincidences of the second group
        - Group 6. It has no coincidences in any group
        


--> I am not sure about the terms to include in a third group to assure CROSSPLATFORM
    - I will run a second iteration to get this


# Reading protocols

First I take a look and fill the basic statistic information (e.g., venue, publication year, first author affilation coutntry and institution).

Then I jump to introduction, skip RW, and the rest of the paper to extrat the information we need



# Inclusion critireon

- It needs to be a papers related to VR/XR/MR/AR
- It needs to be related to cross-platform research. Cross-platform means systems accessible from different platforms. The paper can be about research on cross-platforms, or can be about research in other fields using cross-platforms.
- It needs to be related to collaborative environments. It means, systems where more than one person interacts. Even if the stury or the case of study involves only one person in the scene, the design/objectives must be related to collaborative environments.