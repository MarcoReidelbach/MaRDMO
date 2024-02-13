from django.http import HttpResponse
import requests
import re
from pylatexenc.latex2text import LatexNodes2Text
import bibtexparser
from langdetect import detect
from .para import * 

def BibtexFromDoi(doi):
    url =  "http://dx.doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    r = requests.get(url, headers=headers)
    r.encoding = 'latex'
    return r.text

def GetCitation(doi):
    '''Function gets citation by DOI'''
    
    #Assign Varibles
    citation_dict = {}
    author_with_orcid = []
    author_with_orcid_plain = []
    author_without_orcid = []

    #Get Citation from DOI API as string

    citation=str(BibtexFromDoi(doi))
   
    if 'DOI is incorrect' in citation:
        #Stop if Citation not found via DOI
        return author_with_orcid, author_without_orcid, citation_dict

    #Citation as Dict
    citation_dict = bibtexparser.loads(citation).entries[0]

    #Remove Latex from Citation
    ln2t=LatexNodes2Text()
    for key in citation_dict:
        latex=citation_dict[key]
        no_latex=ln2t.latex_to_text(latex)
        citation_dict[key]=no_latex

    #Refine Citation Entries, if entry not present define dummy (empty)  entry.
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
        citation_dict['author']=authors_refined
    else:
        citation_dict['author']=''
    

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
            #If month already number establish two digit format
            if len(citation_dict['month']) == 1:
                citation_dict['month']='0'+citation_dict['month']
        citation_dict['pub_date']=citation_dict['year']+'-'+citation_dict['month']+'-01'
    else:
        citation_dict['pub_date']=''

    citation_dict['language']=detect(citation_dict['title'])

    #Check DOI in ORCID to get IDs of authors
    orcid_paper = requests.get("https://pub.orcid.org/v3.0/search/?q=doi-self:"+doi, headers={'Accept': 'application/json'}).json()

    if orcid_paper["result"]:
        for entry in orcid_paper["result"]:
            orcid_author = requests.get("https://pub.orcid.org/v3.0/"+entry["orcid-identifier"]["path"]+"/personal-details", headers={'Accept': 'application/json'}).json()
            author_with_orcid.append([orcid_author["name"]["given-names"]["value"]+' '+orcid_author["name"]["family-name"]["value"],entry["orcid-identifier"]["path"]])
            author_with_orcid_plain.append(orcid_author["name"]["given-names"]["value"]+' '+orcid_author["name"]["family-name"]["value"])
    
    #Split authors in authors with and without ORCID
    for name in citation_dict['author']:
        if re.split(' ',name)[-1] not in '\t'.join(author_with_orcid_plain):
            author_without_orcid.append(name)
        
    return author_with_orcid, author_without_orcid, citation_dict


    

