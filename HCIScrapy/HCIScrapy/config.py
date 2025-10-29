

# Testing variables
STORAGE_TEST = False
REQUEST_TEST = False 
SCRAPPING_TEST = False  


TRIAL = 5

# Search used in this trial
# This probably should not be in config but pull from the database using the id_trial
 # (_ or _ or_ ...) and (_ or _ or_ ...) and ... TODO probbly stablish how the searches are done, in what fields in each DB



ACRONYMS = ["VR", "AR", "XR", "MR"]
TERMS1 = ["virtual reality", "virtual realities", "augmented reality", "augmented realities", "extended reality", "extended realities", "mixed reality", "mixed realities"]
TERMS2 = ["cross platform", "multi platform"]
TERMS3 = ["multi user", "collaborative", "collaboration"]
TERMS2_REGEX  = ["collaborative environment", "virtual environment"]


'''
SEARCH_QUERY =  [
                    ["VR", "AR", "XR", "MR", "virtual reality", "virtual realities", "augmented reality", "augmented realities", "extended reality", "extended realities", "mixed reality", "mixed realities"] ,
                    ["cross platform", "cross-platform","multi user","multi-user", "collaborative", "collaboration", "collaborative environment", "virtual environment"]  
                ]
'''

'''SEARCH_QUERY =  [
                    [ "virtual reality",  "augmented reality",  "extended reality",  "mixed reality"] ,
                    ["cross-platform","multi-platform"]  
                ]
'''

SEARCH_QUERY =  [
                    [ "virtual reality",  
                     "augmented reality",  
                     "extended reality",  
                     "mixed reality"] ,
                    ["cross-platform",
                     "multi-platform"],
                    ["multi-user","multiuser",
                     "collaborative environment"]  
                ]



CONNECTION_STRING = './data/db.db'
"""
CONNECTION_STRING = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        #'SERVER=pchc3112a-04\\SQLEXPRESS;'
        'SERVER=FELIPE_OMEN\\SQLEXPRESS;'
        'DATABASE=MultiplatformXR;'
        'Trusted_Connection=yes;'
    )
"""
"CONNECTION_STRING = './HCIScrapy/HCIScrapy/data/db.db'"

# Databases
DB_ACM = 'ACM'
DB_IEEE = 'IEEE'
DB_SPRINGER = 'Springer'
DB_SD = 'ScienceDirect'

# Inclusion criterea
# TODO Include this into the scrapping process... eventually
INCLUSION_CRITEREA = {
    DB_ACM : {
                'type' : ['article' , 'research-article', 'short-paper' , 'survey' , ]
            },
    DB_IEEE : {
                'type' : ['book chapter' , 'conference paper', 'short-paper' , 'journal' , ]
            },
    DB_SPRINGER : {
                'type' : ['article' , 'paper', ]
            },
    DB_SD :{
                'type' : ['chp', 	'fla', 	'mic', 	'osp', 	'rev']
            }
}

