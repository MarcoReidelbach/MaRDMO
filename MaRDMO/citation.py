from django.http import HttpResponse
import requests, re, os, json
from pylatexenc.latex2text import LatexNodes2Text
import bibtexparser
from langdetect import detect
from .para import * 

def GetCitation(doi):
    '''Function gets citation by DOI'''  
    
    #Get Language codes
    path = os.path.join(os.path.dirname(__file__), 'data', 'lang.json')
    with open(path, "r") as json_file:
        lang_dict = json.load(json_file)

    #Assign Varibles
    citation_dict = {}
    author_with_orcid = []
    author_with_zbmath = []
    author_with_orcid_plain = []
    author_without_id = []

    search = True

    if search:
        # Get Citation from Crossref
        response = requests.get('https://api.crossref.org/works/{}'.format(doi))
        # Check if request was successful
        if response.status_code == 200:
            # If succesfull stop further requests
            search = False
            # Get Data
            data = response.json()['message']
            # Extracting title
            citation_dict['title'] = data.get('title', [''])[0]
            citation_dict['ENTRYTYPE'] = 'article' if data.get('type', '') == 'journal-article' else 'publication' if data.get('type', '') else '' 
            # Extracting authors with ORCID IDs (if present)
            author_without_id = []
            author_with_orcid = []
            for author in data.get('author', []):
                name = author.get('given', '') + ' ' + author.get('family', '')
                orcid = author.get('ORCID', '')
                if orcid:
                    author_with_orcid.append([name, orcid.split('/')[-1]])
                else:
                    author_without_id.append(name)
            # Extracting language
            if data.get('language', ''):
                if len(data.get('language')) == 2:
                    citation_dict['language'] = lang_dict[data.get('language')]
                else:
                    citation_dict['language'] = data.get('language')
            else:
                citation_dict['language']= lang_dict[detect(citation_dict['title'])]
            # Extracting journal information
            citation_dict['journal'] = data.get('container-title', [''])[0]
            citation_dict['volume'] = data.get('volume', '')
            citation_dict['pages'] = data.get('page', '')
            citation_dict['number'] = data.get('issue', '')
            published = data.get('published',{}).get('date-parts',[''])[0]
            if published:
                if len(published) == 3:
                    citation_dict['pub_date'] = '{0[0]}-{0[1]:02d}-{0[2]:02d}'.format(published)
                elif len(published) == 2:
                    citation_dict['pub_date'] = '{0[0]}-{0[1]:02d}-{0[2]:02d}'.format(published+[1])
                elif len(published) == 1:
                    citation_dict['pub_date'] = '{0[0]}-{0[1]:02d}-{0[2]:02d}'.format(published+[1,1])
                else:
                    citation_dict['pub_date'] = ''
            else:
                citation_dict['pub_date'] = ''

    if search:
        # Make a GET request to the DataCite API /doi endpoint
        response = requests.get('https://api.datacite.org/dois/{}'.format(doi))
        # Check if request was successful
        if response.status_code == 200:
            # If succesfull stop further requests
            search = False
            # Parse the JSON response and extract metadata attributes
            data = response.json().get('data', {})
            attributes = data.get('attributes', {})
            # Extract the title
            citation_dict['title'] = attributes.get('titles', [''])[0].get('title', '')
            # Extracting language
            if attributes.get('language', ''):
                if len(attributes.get('language')) == 2:
                    citation_dict['language'] = lang_dict[attributes.get('language')]
                else:
                    citation_dict['language'] = attributes.get('language')
            else:
                citation_dict['language']= lang_dict[detect(citation_dict['title'])]
            # Extract the resource type
            citation_dict['ENTRYTYPE'] = 'article' if attributes.get('types', {}).get('bibtex', '') == 'article' else 'publication' if attributes.get('types', {}).get('bibtex', '') else ''
            # Extract authors with ORCID IDs (if present)
            authors = attributes.get('creators', [])
            author_without_id = []
            author_with_orcid = []
            for author in authors:
                name = author.get('givenName', '') + ' ' + author.get('familyName', '')
                orcid = author.get('nameIdentifiers', [])
                orcid_id = [id_info.get('nameIdentifier', '') for id_info in orcid if id_info.get('nameIdentifierScheme') == 'ORCID']
                if orcid_id:
                    author_with_orcid.append([name, orcid_id[0].split('/')[-1]])
                else:
                    author_without_id.append(name)
            # Extract publication date
            pub_date_parts = attributes.get('dates', [])
            for date_part in pub_date_parts:
                if date_part.get('dateType') == 'Issued':
                    if len(date_part.get('date')) == 4:
                        citation_dict['pub_date'] = date_part.get('date')+'-01-01'
                    elif len(date_part.get('date')) == 7:
                        citation_dict['pub_date'] = date_part.get('date')+'-01'
                    else:
                        citation_dict['pub_date'] = date_part.get('date')
                else:
                    citation_dict['pub_date'] = ''

    if search:
        # Get Citation from DOI API as string
        response = requests.get("http://dx.doi.org/{}".format(doi), headers = {"accept": "application/x-bibtex"})
        # Check if request was successfull
        if response.status_code == 200:
            # If successfull stop further requests
            search = False
            # Get Data
            response.encoding = 'latex'
            citation=str(response.text)
            #Citation as Dict
            citation_dict = bibtexparser.loads(citation).entries[0]
            #Remove Latex from Citation
            ln2t=LatexNodes2Text()
            for key in citation_dict:
                latex=citation_dict[key]
                no_latex=ln2t.latex_to_text(latex)
                citation_dict[key]=no_latex
            #Refine Citation Entries, if entry not present define dummy (empty) entry.
            if 'author' in citation_dict:
                #Authors to list
                citation_dict['author']=re.split(' and ', citation_dict['author'])
                #Author Names to First Name Last Name
                authors_refined=[]
                for author in citation_dict['author']:
                    if len(author.split(', ')) > 1:
                        authors_refined.append(author.split(', ')[1]+' '+author.split(', ')[0])
                    else:
                        authors_refined.append(author)
                author_without_id = authors_refined
            else:
                author_without_id = ''
            if 'title' not in citation_dict:
                citation_dict['title']=''
            if 'journal' not in citation_dict:
                citation_dict['journal']=''
            if 'number' not in citation_dict:
                citation_dict['number']=''
            if 'volume' not in citation_dict:
                citation_dict['volume']=''
            if 'pages' not in citation_dict:
                citation_dict['pages']=''
            if 'doi' not in citation_dict:
                citation_dict['doi']=''
            if 'ENTRYTYPE' not in citation_dict:
                citation_dict['ENTRY_TYPE']=''
            if 'month' not in citation_dict:
                citation_dict['month']='jan'
            if 'year' not in citation_dict:
                citation_dict['year']=''
            if citation_dict['year']:
                #Convert three letter month to number
                months = {'jan': '01','feb': '02','mar': '03','apr': '04','may': '05','jun': '06',
                          'jul': '07','aug': '08','sep': '09','oct': '10','nov': '11','dec': '12'}
                try:
                    citation_dict['month']=months[citation_dict['month'].lower()[:3]]
                except:
                    pass
                citation_dict['pub_date'] = '{0[0]}-{0[1]:02d}-{0[2]:02d}'.format([int(citation_dict['year']),int(citation_dict['month']),1])
            else:
                citation_dict['pub_date']=''
            citation_dict['language']=lang_dict[detect(citation_dict['title'])]

    #Check DOI in ORCID to get IDs of authors
    response = requests.get("https://pub.orcid.org/v3.0/search/?q=doi-self:{0}".format(doi), headers={'Accept': 'application/json'})
    # Check if request was successfull
    if response.status_code == 200:
        orcid_paper = response.json().get('result', '')
        if orcid_paper:
            for entry in orcid_paper:
                orcid_id = entry.get('orcid-identifier', {}).get('path', '')
                response = requests.get("https://pub.orcid.org/v3.0/"+orcid_id+"/personal-details", headers={'Accept': 'application/json'})
                if response.status_code == 200:
                    orcid_author = response.json()
                    if not any(orcid_id in author for author in author_with_orcid):
                        if orcid_author.get('name', ''):
                            author_with_orcid.append([orcid_author.get('name', {}).get('given-names', {}).get('value', '').capitalize() + ' ' + 
                                                      orcid_author.get('name', {}).get('family-name', {}).get('value', '').capitalize(),
                                                      orcid_id])
        # Remove Authors with ORCID ID from non-ID Author List
        for author in author_with_orcid:
            name_parts = author[0].lower().split(' ')
            similar = [index for index, name in enumerate(author_without_id) if name_parts[-1].lower() in name.lower()]
            if similar:
                del author_without_id[similar[0]]

    #Check DOI in zbmath to get IDs of authors
    response = requests.get('https://api.zbmath.org/v1/document/_structured_search?page=0&results_per_page=100&external%20id={0}'.format(doi))
    # Check if request was successfull
    if response.status_code == 200:
        zbmath_paper = response.json().get('result', [''])[0]
        if zbmath_paper:
            authors = zbmath_paper.get('contributors', {}).get('authors', '')
            # Extract zbMath IDs
            for author in authors:
                author_name = author.get('name', '')
                author_codes = author.get('codes', [])
                if author.get('codes', []):
                    if author_name == 'zbMATH Open Web Interface contents unavailable due to conflicting licenses.':
                        author_name = [author_codes[0].split('.')[0].capitalize(),author_codes[0].split('.')[1].capitalize()]
                    else:
                        author_name = author_name.split(', ') 
                    author_with_zbmath.append([author_name[-1].capitalize() + ' ' + 
                                               author_name[0].capitalize(),
                                               author_codes[0]])
        # Remove Authors with zbmath ID from non-ID Author List
        for author in author_with_zbmath:
            name_parts = author[0].lower().split(' ')
            similar = [index for index, name in enumerate(author_without_id) if name_parts[-1].lower() in name.lower()]
            if similar:
                del author_without_id[similar[0]]
                
    return author_with_orcid, author_with_zbmath, author_without_id, citation_dict


    

