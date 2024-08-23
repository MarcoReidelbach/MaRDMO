import re, os, json
import requests

from django.dispatch import receiver
from django.db.models.signals import post_save

from rdmo.projects.models import Value
from rdmo.domain.models import Attribute
from rdmo.options.models import Option

from .citation import GetCitation
from .mathmoddb import queryMathModDB
from .para import BASE_URI, option, OperationModus
from .sparql import queryPublication, queryModelHandler, wini, mini, pl_query, pl_vars, pro_query, pro_vars
from .id import *
from .config import wd, wdt, mardi_api, wikidata_api, mardi_endpoint, wikidata_endpoint

from difflib import SequenceMatcher

@receiver(post_save, sender=Value)
def PublicationCitationRetriever(sender, **kwargs): 

    instance = kwargs.get("instance", None)

    if instance and instance.attribute.uri == f"{BASE_URI}Section_2/Set_1/Question_02":
    
        # Activate (Yes)  / Deactivate (No or nothin) Publication Information Section
        if instance.option_text == 'Yes':            
            valueEditor(instance,f"{BASE_URI}Section_2/Set_2",1)
        else: 
            valueEditor(instance,f"{BASE_URI}Section_2/Set_2",0)

        # Evaluate Information provided for Yes case
        if instance.text.split(':')[0] == 'url': 
            
            # If url provided, deactivate Publication Information section 
            valueEditor(instance,f"{BASE_URI}Section_2/Set_2",0)
        
        elif re.match(r'doi:10.\d{4,9}/[-._;()/:a-z0-9A-Z]+', instance.text):
            
            # Extract DOI and Initialize different dictionaries
            doi = instance.text.split(':')[1]   
            
            dict_merged = {}
            author_dict_merged = {}
            
            # Define Prefix & Parameter for MaRDI KG search, Search Paper in MaRDI KG via DOI and merge results
            mardi_prefix = f"PREFIX wdt:{wdt} PREFIX wd:{wd}"
            mardi_query_parameter = [P16, doi.upper(), P8, P22, P4, P12, P10, P7, P9, P11, P13, P14, P15, P2, P23]
            mardi_dicts = kg_req(mardi_endpoint, mardi_prefix + queryPublication['All'].format(*mardi_query_parameter))
            
            # Combine dictionaries from MaRDI Query
            for mardi_dict in mardi_dicts:
                for key in mardi_dict.keys():
                    if key == 'authorInfo':
                        if mardi_dict.get(key, {}).get('value'):
                            authorQid, authorLabel, authorDescription, authorOrcid, authorWikidataQid, authorZBmathID = mardi_dict[key]['value'].split(' <|> ')
                            if authorQid not in dict_merged.get('mardi_authorQid', []):
                                dict_merged.setdefault('mardi_authorQid', []).append(authorQid)
                                dict_merged.setdefault('mardi_authorLabel', []).append(authorLabel)
                                dict_merged.setdefault('mardi_authorDescription', []).append(authorDescription)
                                dict_merged.setdefault('mardi_authorOrcid', []).append(authorOrcid)
                                dict_merged.setdefault('mardi_authorWikidataQid', []).append(authorWikidataQid)
                                dict_merged.setdefault('mardi_authorZBmathID', []).append(authorZBmathID)
                    elif key == 'otherAuthor':
                        if mardi_dict.get(key, {}).get('value'):
                            if mardi_dict[key]['value'] not in dict_merged.get('mardi_'+key, []):
                                dict_merged.setdefault('mardi_'+key, []).append(mardi_dict[key]['value'])
                    elif key == 'publicationLabel':
                        dict_merged['publication'] = mardi_dict.get(key, {}).get('value')
                        dict_merged['mardi_'+key] = mardi_dict.get(key, {}).get('value')
                    else:
                        dict_merged['mardi_'+key] = mardi_dict.get(key, {}).get('value')
            
            if not dict_merged:
            
                # If results not found for Paper in MaRDI KG via DOI, define Parameters for Wikidata search, search paper via DOI and merge results
                wikidata_parameter = ['356', doi.upper(), '50', '496', '31', '1433', '407', '1476', '2093', '577', '478', '433', '304', '', '1556']
                wikidata_dicts = kg_req(wikidata_endpoint, queryPublication['All'].format(*wikidata_parameter))
            
                # Combine dictionaries from Wikidata Query
                for wikidata_dict in wikidata_dicts:
                    for key in wikidata_dict.keys():
                        if key == 'authorInfo':
                            if wikidata_dict.get(key, {}).get('value'):
                                authorQid, authorLabel, authorDescription, authorOrcid, authorWikidataQid, authorZBmathID = wikidata_dict[key]['value'].split(' <|> ')
                                if authorQid not in dict_merged.get('wikidata_authorQid', []):
                                    dict_merged.setdefault('wikidata_authorQid', []).append(authorQid)
                                    dict_merged.setdefault('wikidata_authorLabel', []).append(authorLabel)
                                    dict_merged.setdefault('wikidata_authorDescription', []).append(authorDescription)
                                    dict_merged.setdefault('wikidata_authorOrcid', []).append(authorOrcid)
                                    dict_merged.setdefault('wikidata_authorWikidataQid', []).append(authorWikidataQid)
                                    dict_merged.setdefault('wikidata_authorZBmathID', []).append(authorZBmathID)
                        elif key == 'otherAuthor':
                            if wikidata_dict.get(key, {}).get('value'):
                                if wikidata_dict[key]['value'] not in dict_merged.get('wikidata_'+key, []):
                                    dict_merged.setdefault('wikidata_'+key, []).append(wikidata_dict[key]['value'])
                        elif key == 'publicationLabel':
                            dict_merged['publication'] = wikidata_dict.get(key, {}).get('value')
                            dict_merged['wikidata_'+key] = wikidata_dict.get(key, {}).get('value')
                        else:
                            dict_merged['wikidata_'+key] = wikidata_dict.get(key, {}).get('value')
                 
                if dict_merged:
            
                    # If results found for Paper in Wikidata use Wikidata QID to search MaRDI KG again
                    mardi_parameter = [P2, dict_merged.get('wikidata_publicationQid', '')]
                    mardi_dict = kg_req(mardi_endpoint, mardi_prefix+queryPublication['WikiCheck'].format(*mardi_parameter))
            
                    if mardi_dict:
                        # If results found for Paper in MaRDI KG via Wikidata QID update results 
                        dict_merged['mardi_publicationQid'] = mardi_dict[0].get('publicationQid', {}).get('value')
                        dict_merged['mardi_publicationLabel'] = mardi_dict[0].get('publicationLabel', {}).get('value')
                        dict_merged['mardi_publicationDescription1'] = mardi_dict[0].get('publicationDescription1', []).get('value')
                else: 
            
                    # If no results found in MaRDI KG or Wikidata use DOI to get complete citation
                    orcid_authors, zbmath_authors, other_authors, citation_dictionary = GetCitation(doi)
            
                    if citation_dictionary:
            
                        # If citation found, extract ORCID and zbMath IDs
                        orcid_ids = [orcid_author[1] for orcid_author in orcid_authors]
                        zbmath_ids = [zbmath_author[1] for zbmath_author in zbmath_authors]
            
                        # Search Authors related to publication 
                        author_dict_merged = Author_Search(orcid_ids, zbmath_ids, orcid_authors, zbmath_authors)
            
                        # Define search objects, journal, for Wikidata API and MaRDI requests and store results 
                        search_objects_wikidata = [[citation_dictionary.get('journal', '')]]
                        make_api_requests(wikidata_api, search_objects_wikidata, dict_merged, 'cit_wikidata')
                        search_objects_mardi = [[citation_dictionary.get('journal', ''), dict_merged.get('cit_wikidata_journalLabel', '')]]
                        make_api_requests(mardi_api, search_objects_mardi, dict_merged, 'cit_mardi')
            
                        # Store Entrytype Data
                        entry_type_data = {'article': {'wikidata_qid': 'Q13442814', 
                                                       'mardi_qid': Q1, 
                                                       'label': 'scholarly article', 
                                                       'description': 'article in an academic publication, usually peer reviewed'},
                                           
                                           'publication': {'wikidata_qid': 'Q732577', 
                                                           'mardi_qid': Q10, 
                                                           'label': 'publication', 
                                                           'description': 'content made available to the general public'}}
            
                        # Update dictionary with citation information
                        dict_merged.update({
                            'cit_wikidata_entrytypeQid': entry_type_data[citation_dictionary['ENTRYTYPE']]['wikidata_qid'],
                            'cit_wikidata_entrytypeLabel': entry_type_data[citation_dictionary['ENTRYTYPE']]['label'],
                            'cit_wikidata_entrytypeDescription1': entry_type_data[citation_dictionary['ENTRYTYPE']]['description'],
                            'cit_mardi_entrytypeQid': entry_type_data[citation_dictionary['ENTRYTYPE']]['mardi_qid'],
                            'cit_mardi_entrytypeLabel': entry_type_data[citation_dictionary['ENTRYTYPE']]['label'],
                            'cit_mardi_entrytypeDescription1': entry_type_data[citation_dictionary['ENTRYTYPE']]['description'],
                            'cit_wikidata_languageQid': citation_dictionary.get('language',['','',''])[0], 
                            'cit_wikidata_languageLabel': citation_dictionary.get('language',['','',''])[1],
                            'cit_wikidata_languageDescription1': citation_dictionary.get('language',['','',''])[2],
                            'publication': citation_dictionary.get('title',''),
                            'volume': citation_dictionary.get('volume',''),
                            'issue': citation_dictionary.get('number',''),
                            'page': citation_dictionary.get('pages',''),
                            'publicationDate': citation_dictionary.get('pub_date',''),
                            'otherAuthor': other_authors,
                            'journal': citation_dictionary.get('journal',''),
                            'entrytypeQid': citation_dictionary.get('ENTRYTYPE','')})
            
            # Gather Data for fill out and storage for later export
            paper_information = {}
            
            # Store publication, entrytype, language and journal information
            citation_properties = [['publicationQid', 'publicationLabel', 'publicationDescription1'],
                                   ['entrytypeQid', 'entrytypeLabel', 'entrytypeDescription1'],
                                   ['languageQid', 'languageLabel', 'languageDescription1'],
                                   ['journalQid', 'journalLabel', 'journalDescription1']]
            
            for citation_property in citation_properties:
                prefix = 'mardi_' if dict_merged.get('mardi_' + citation_property[0]) else \
                         'wikidata_' if dict_merged.get('wikidata_' + citation_property[0]) else \
                         'cit_mardi_' if dict_merged.get('cit_mardi_' + citation_property[0]) else \
                         'cit_wikidata_'
                if dict_merged.get(prefix + citation_property[0]):
                    qid = prefix[:-1].removeprefix('cit_') + ':' + dict_merged[prefix + citation_property[0]]
                    if citation_property[0] == 'publicationQid':
                        paper_information[citation_property[0]] = [qid]
                    else:
                        paper_information[citation_property[0]] = [dict_merged[prefix + citation_property[1]]]
                    paper_information[citation_property[0] + '_back'] = [qid + ' <|> ' + dict_merged[prefix + citation_property[1]] + ' <|> ' + dict_merged[prefix + citation_property[2]]]
                else:
                    default_value = 'no information available'
                    if dict_merged.get(citation_property[0][:-3]):
                        if citation_property[0].startswith('publication'):
                            paper_information[citation_property[0]] = [default_value]
                            paper_information[citation_property[0] + '_back'] = ['no id <|> ' + dict_merged[citation_property[0][:-3]] + ' <|> ' + citation_property[0][:-3]]
                        else:
                            paper_information[citation_property[0]] = [dict_merged[citation_property[0][:-3]]]
                            paper_information[citation_property[0] + '_back'] = ['no id <|> ' + dict_merged[citation_property[0][:-3]] + ' <|> ' + citation_property[0][:-3]]
                    else:
                        paper_information[citation_property[0]] = [default_value]
                        paper_information[citation_property[0] + '_back'] = ['NONE']        
            
            # Store Author Information
            paper_information['author_label'] = []
            paper_information['author_label_back'] = []
            
            if 'mardi_authorQid' in dict_merged or 'mardi_otherAuthor' in dict_merged:
            
                # Store MaRDI Author QID /Label
                try:
                    for qid, label in zip(dict_merged['mardi_authorQid'], dict_merged['mardi_authorLabel']):
                    
                        if qid:
                            paper_information['author_label'].append(label+' (mardi:'+qid+')')
                        else:
                            paper_information['author_label'].append(label)
                    
                        paper_information['author_label_back'].append(['mardi:'+qid])
                except KeyError:
                    pass
                if dict_merged.get('mardi_otherAuthor', ''): 
                    paper_information['author_label'].extend(dict_merged['mardi_otherAuthor'])
            
            elif 'wikidata_authorQid' in dict_merged or 'wikidata_otherAuthor' in dict_merged:
            
                # Store Wikidata Author QID / Label
                try:
                    for qid, label in zip(dict_merged['wikidata_authorQid'], dict_merged['wikidata_authorLabel']):
                        
                        if qid:
                            paper_information['author_label'].append(label+' (wikidata:'+qid+')')
                        else:
                            paper_information['author_label'].append(label)

                        paper_information['author_label_back'].append(['wikidata:'+qid])
                except KeyError:
                    pass
                if dict_merged.get('wikidata_otherAuthor', ''):
                    paper_information['author_label'].extend(dict_merged['wikidata_otherAuthor'])
            
            elif author_dict_merged:
            
                # Store Publication Authors from Citation via ORCID and zbMath
                for author in author_dict_merged.keys():
                    if author_dict_merged[author]['mardiQID']:
                        paper_information['author_label'].append(author_dict_merged[author]['mardiLabel'] + ' (mardi:' + author_dict_merged[author]['mardiQID'] + ')')
                        paper_information['author_label_back'].append('mardi:' + author_dict_merged[author]['mardiQID'])
                    elif author_dict_merged[author]['wikiQID']:
                        paper_information['author_label'].append(author_dict_merged[author]['wikiLabel'] + ' (wikidata:' + author_dict_merged[author]['wikiQID'] + ')')
                        paper_information['author_label_back'].append('wikidata:' + author_dict_merged[author]['wikiQID'] +
                                                                          ' <|> ' + author_dict_merged[author]['wikiLabel'] +
                                                                          ' <|> ' + author_dict_merged[author]['wikiDescription'])
                    elif author_dict_merged[author]['orcid']:
                        if author_dict_merged[author]['zbmath']:
                            paper_information['author_label'].append(author+' (orcid:'+author_dict_merged[author]['orcid']+', zbmath:'+author_dict_merged[author]['zbmath']+')')
                            paper_information['author_label_back'].append('orcid:'+author_dict_merged[author]['orcid']+'; zbmath:'+author_dict_merged[author]['zbmath']+' <|> '+author+' <|> researcher (ORCID '+author_dict_merged[author]['orcid']+')')
                        else:
                            paper_information['author_label'].append(author+' (orcid:'+author_dict_merged[author]['orcid']+')')
                            paper_information['author_label_back'].append('orcid:'+author_dict_merged[author]['orcid']+' <|> '+author+' <|> researcher (ORCID '+author_dict_merged[author]['orcid']+')')
                    elif author_dict_merged[author]['zbmath']:
                        paper_information['author_label'].append(author+' (zbmath:'+author_dict_merged[author]['zbmath']+')')
                        paper_information['author_label_back'].append('zbmath:'+author_dict_merged[author]['zbmath']+' <|> '+author+' <|> researcher (zbMath '+author_dict_merged[author]['zbmath']+')')
                
                if dict_merged.get('otherAuthor', ''):
                    paper_information['author_label'].extend(dict_merged['otherAuthor'])
            
            else:
            
                if dict_merged.get('otherAuthor', ''):
                    paper_information['author_label'].extend(dict_merged['otherAuthor'])
                    paper_information['author_label_back'].append('')
                else:
                    paper_information['author_label'].append('no information available')
                    paper_information['author_label_back'].append('')
            
            # Store publication volume, issue, page and publication date
            citation_properties = ['volume', 'issue', 'page', 'publicationDate', 'publication']
            for citation_property in citation_properties:
                if dict_merged.get('mardi_'+citation_property):
                    # Store MaRDI Property
                    paper_information[citation_property] = [dict_merged['mardi_'+citation_property]]
                    paper_information[citation_property+'_back'] = [dict_merged['mardi_'+citation_property]]
                elif dict_merged.get('wikidata_'+citation_property):
                    # Store Wikidata Property
                    paper_information[citation_property] = [dict_merged['wikidata_'+citation_property]]
                    paper_information[citation_property+'_back'] = [dict_merged['wikidata_'+citation_property]]
                elif dict_merged.get(citation_property):
                    # Store Citation Property
                    paper_information[citation_property] = [dict_merged[citation_property]]
                    paper_information[citation_property+'_back'] = [dict_merged[citation_property]]
                else:
                    # No Publication Volume available
                    paper_information[citation_property] = ['no information available']
                    paper_information[citation_property+'_back'] = ['NONE']
            
            # Append paper information to question ids 
            paper_infos = [paper_information['publicationQid'], paper_information['publicationQid_back'],
                           paper_information['entrytypeQid'], paper_information['entrytypeQid_back'],
                           paper_information['publication'], paper_information['publication_back'],
                           paper_information['author_label'], paper_information['author_label_back'],
                           paper_information['languageQid'], paper_information['languageQid_back'],
                           paper_information['journalQid'], paper_information['journalQid_back'],
                           paper_information['volume'], paper_information['volume_back'],
                           paper_information['issue'], paper_information['issue_back'],
                           paper_information['page'], paper_information['page_back'],
                           paper_information['publicationDate'], paper_information['publicationDate_back']]
            
            object_uris = [f'{BASE_URI}Section_2/Set_2/Question_00', f'{BASE_URI}Section_2/Set_2/Question_00_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_01', f'{BASE_URI}Section_2/Set_2/Question_01_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_02', f'{BASE_URI}Section_2/Set_2/Question_02_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_03', f'{BASE_URI}Section_2/Set_2/Question_03_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_04', f'{BASE_URI}Section_2/Set_2/Question_04_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_05', f'{BASE_URI}Section_2/Set_2/Question_05_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_06', f'{BASE_URI}Section_2/Set_2/Question_06_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_07', f'{BASE_URI}Section_2/Set_2/Question_07_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_08', f'{BASE_URI}Section_2/Set_2/Question_08_hidden',
                           f'{BASE_URI}Section_2/Set_2/Question_09', f'{BASE_URI}Section_2/Set_2/Question_09_hidden']
            
            for paper_info, object_uri in zip(paper_infos, object_uris):
                if object_uri == f'{BASE_URI}Section_2/Set_2/Question_04':
                    for idx,val in enumerate(paper_info):
                        if option.get(val) is not None:
                            valueEditor(instance, object_uri, None, None, Option.objects.get(uri=option.get(val)))
                else:
                    for idx,val in enumerate(paper_info):
                        valueEditor(instance, object_uri, val, None, None, idx)

            return

@receiver(post_save, sender=Value)
def WorkflowOrModel(sender, **kwargs):

    instance = kwargs.get("instance", None)

    if instance and instance.attribute.uri == f'{BASE_URI}Section_0/Set_1/Question_02':
        
        if instance.option == Option.objects.get(uri=option['Workflow']):
            # Activate Questions for Workflow Documentation
            val = [1,1,1,0,1]
        elif instance.option == Option.objects.get(uri=option['Model']):
            # Activate Questions for Model Documentation
            val = [1,0,1,0,1]
        else:
            # Deactivate all Documentation Questions
            val = [0,0,1,0,0]

        for idx, key in enumerate(OperationModus['WorkflowOrModel'].keys()):
            for uri in OperationModus['WorkflowOrModel'][key]:
                valueEditor(instance,uri,val[idx])
    return

@receiver(post_save, sender=Value)
def SearchOrDocument(sender, **kwargs):
    
    instance = kwargs.get("instance", None)
    
    if instance and instance.attribute.uri == f'{BASE_URI}Section_0/Set_1/Question_01':
        
        if instance.option == Option.objects.get(uri=option['Documentation']):
            # Activate Questions for Documentation
            val = [0,1,1,0]
        elif instance.option == Option.objects.get(uri=option['Search']):
            # Activate Questions for Search
            val = [1,0,0,0]
        else:
            # Deactivate all Questionss
            val = [0,0,1,0]

        for idx, key in enumerate(OperationModus['SearchOrDocument'].keys()):
            for uri in OperationModus['SearchOrDocument'][key]:
                valueEditor(instance,uri,val[idx])
    return

@receiver(post_save, sender=Value)
def ComputationalOrExperimental(sender, **kwargs):

    instance = kwargs.get("instance", None)
    
    if instance and instance.attribute.uri == f'{BASE_URI}Section_2/Set_1/Question_03':

        if instance.option == Option.objects.get(uri=option['Analysis']):
            # Activate Questions for Experimental Workflow
            val = [1,0,1]
        elif instance.option == Option.objects.get(uri=option['Computation']):
            # Activate Questions for Computational Workflow
            val = [1,1,0]
        else:
            # Deactivate all Questions
            val = [0,0,0]

        for idx, key in enumerate(OperationModus['ComputationalOrExperimental'].keys()):
            for uri in OperationModus['ComputationalOrExperimental'][key]:
                valueEditor(instance,uri,val[idx])
    return

@receiver(post_save, sender=Value)
def ModelHandler(sender, **kwargs):
    
    instance = kwargs.get("instance", None)
    
    if instance and instance.attribute.uri == f'{BASE_URI}Section_3/Set_0/Wiki_01':

        if instance.external_id and instance.external_id != 'not in MathModDB':        
            IdMM, _ = instance.external_id.split(' <|> ')
        else:
            return

        path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')
        with open(path, "r") as json_file:
            mathmoddb = json.load(json_file)

        # Get Model, Research Field, Research Problem, Quantity, Mathematical Formulation and Task Information        
        results = queryMathModDB(queryModelHandler['All'].format(f":{IdMM.split('#')[1]}"))

        if results:

            # Add Research Field Information to Questionnaire
            rfIds = []
            idx = 0
            for res in results:                
                rfId = res.get('rf',{}).get('value')
                rfLabel = res.get('rfl',{}).get('value')
                if rfId and rfLabel:
                    if rfId not in rfIds:
                        rfIds.append(rfId) 
                        # Set up Research Field Page 
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_0', idx, None, None, None, idx)
                        # Add Research Field Values
                        valueEditor(instance, f'{BASE_URI}Section_3/Set_0/Set_0/Question_04', f"{rfLabel}", f"{rfId} <|> {rfLabel}", None, None, idx)
                        idx = idx + 1
            
            # Add Research Problem Information to Questionnaire
            rpIds = []
            rpLabels =[]
            idx = 0
            for res in results:
                rpId = res.get('rp',{}).get('value')
                rpLabel = res.get('rpl',{}).get('value')
                if rpId and rpLabel:
                    if rpId not in rpIds:
                        rpIds.append(rpId)
                        rpLabels.append(rpLabel)
                        # Setup Research Problem Page
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_1', idx, None, None, None, idx)
                        # Add Research Problem Values
                        valueEditor(instance, f'{BASE_URI}Section_3/Set_0/Set_0/Question_05', f"{rpLabel}", f"{rpId} <|> {rpLabel}", None, None, idx)
                        idx = idx +1

            # Add Quantity Information to Questionnaire
            qIds =[]
            qLabels = []
            qClasss = []
            for res in results:
                for key in ['fmfq','amfq','bcmfq','ccmfq','cpcmfq','icmfq','fcmfq']:
                    qId = res.get(key,{}).get('value')
                    qLabel = res.get(f'{key}l',{}).get('value')
                    qClass = res.get(f'{key}c',{}).get('value')
                    if qId and qLabel and qClass:
                        if qId not in qIds:
                            qIds.append(qId)
                            qLabels.append(qLabel)
                            qClasss.append(qClass)

            
            for idx, (qId, qLabel, qClass) in enumerate(zip(qIds,qLabels,qClasss)):
                    # Set upt Qauntity / Quantity Kind Page
                    valueEditor(instance, f'{BASE_URI}Section_3a/Set_3', idx, None, None, None, idx)
                    # Add Quantity / Quantity Kind Values
                    valueEditor(instance, f'{BASE_URI}Section_3/Set_0/Set_0/Question_07', 
                                f"{qLabel} (Quantity)" if qClass.split('#')[1] == 'Quantity' else f"{qLabel} (Quantity Kind)", 
                                f"{qId} <|> {qLabel} <|> {qClass.split('#')[1]}", None, None, idx)

            # Restructure Results from initial Query
            ModelPropertyKeys = ['mm','ta','gb','g','ab','a','db','d','lb','l','ci','c','s','ff','af','bcf','ccf','cpcf','icf','fcf']
            ModelProperty = {f'{ModelPropertyKey}{kind}': [] for ModelPropertyKey in ModelPropertyKeys for kind in ['Ids', 'Labels']}
            for res in results:
                for idx, key in enumerate(['mm','ta','gbmm','gmm','abmm','amm','dbmm','dmm','lbmm','lmm','cimm','cmm','smm','fmf','amf','bcmf','ccmf','cpcmf','icmf','fcmf']):
                    if res.get(key,{}).get('value') and res.get(f'{key}l',{}).get('value'): 
                        if res[key]['value'] not in ModelProperty[list(ModelProperty.keys())[2*idx]] and res[f'{key}l']['value'] not in ModelProperty[list(ModelProperty.keys())[2*idx+1]]:
                            ModelProperty[list(ModelProperty.keys())[2*idx]].append(res[key]['value'])
                            ModelProperty[list(ModelProperty.keys())[2*idx+1]].append(res[f'{key}l']['value'])

            # Group results from initial query for further queries (IdsMF - Ids of all related Formulation, IdsT - Ids of all related Tasks, Ids - Ids for all related Entities)
            IdsMF = ModelProperty['ffIds'] + ModelProperty['afIds'] + ModelProperty['bcfIds'] + ModelProperty['ccfIds'] + ModelProperty['cpcfIds'] + ModelProperty['icfIds'] + ModelProperty['fcfIds']
            IdsT = ModelProperty['taIds']
            Ids = [IdMM] + rfIds + rpIds + qIds + IdsMF + IdsT

            # Further Queries of Knowledge Graph to get further Formualtion, Task and Publication Information
            search_string2 = ''
            search_string3 = ''
            search_string4 = ''

            for Id in IdsMF:
                search_string2 = search_string2 + f" :{Id.split('#')[1]}"

            for Id in IdsT:
                search_string3 = search_string3 + f" :{Id.split('#')[1]}"
            
            for Id in Ids:
                search_string4 = search_string4 + f" :{Id.split('#')[1]}"

            results2 = queryMathModDB(queryModelHandler['MFRelations'].format(search_string2))
            results3 = queryMathModDB(queryModelHandler['TRelation'].format(search_string3))
            results4 = queryMathModDB(queryModelHandler['PRelation'].format(search_string4))


            for idx, (mmId, mmLabel) in enumerate(zip(ModelProperty['mmIds'],ModelProperty['mmLabels'])):

                # Set up Mathematical Model Page
                valueEditor(instance, f'{BASE_URI}Section_3a/Set_2', idx, None, None, None, idx)
               
                # Add Mathematical Model ID and Label
                valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx)
               
                # Add Research Problem related to Mathematical Model
                for idx2, (rpId, rpLabel) in enumerate(zip(rpIds,rpLabels)):
                    valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Question_4', f"{rpLabel}", f"{rpId} <|> {rpLabel}", None, idx2, idx)
                
                # Add Model Relations

                idx2 = 0

                for gbId, gbLabel in zip(ModelProperty['gbIds'],ModelProperty['gbLabels']):
                    if gbId and gbLabel:
                        
                        # Add Generalized By Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{gbLabel}", f"{gbId} <|> {gbLabel}", None, None, idx2, idx)

                        idx2 = idx2 + 1
                
                for gId, gLabel in zip(ModelProperty['gIds'],ModelProperty['gLabels']):
                    if gId and gLabel:
                        
                        # Add Generalizes Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{gLabel}", f"{gId} <|> {gLabel}", None, None, idx2, idx)
                        
                        idx2 = idx2 + 1

                for abId, abLabel in zip(ModelProperty['abIds'],ModelProperty['abLabels']):
                    if abId and abLabel:
                        
                        # Add Approximated By Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{abLabel}", f"{abId} <|> {abLabel}", None, None, idx2, idx)

                        idx2 = idx2 + 1

                for aId, aLabel in zip(ModelProperty['aIds'],ModelProperty['aLabels']):
                    if aId and aLabel:

                        # Add Approximates Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{aLabel}", f"{aId} <|> {aLabel}", None, None, idx2, idx)
                    
                        idx2 = idx2 + 1

                for dbId, dbLabel in zip(ModelProperty['dbIds'],ModelProperty['dbLabels']):
                    if dbId and dbLabel:

                        # Add Discretized By Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{dbLabel}", f"{dbId} <|> {dbLabel}", None, None, idx2, idx)
                                            
                        idx2 = idx2 + 1

                for dId, dLabel in zip(ModelProperty['dIds'],ModelProperty['dLabels']):
                    if dId and dLabel:

                        # Add Discretizes Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{dLabel}", f"{dId} <|> {dLabel}", None, None, idx2, idx)

                        idx2 = idx2 + 1
                
                for lbId, lbLabel in zip(ModelProperty['lbIds'],ModelProperty['lbLabels']):
                    if lbId and lbLabel:

                        # Add Linearized By Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{lbLabel}", f"{lbId} <|> {lbLabel}", None, None, idx2, idx)
                    
                        idx2 = idx2 + 1

                for lId, lLabel in zip(ModelProperty['lIds'],ModelProperty['lLabels']):
                    if lId and lLabel:
                    
                        # Add Linearizes Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{lLabel}", f"{lId} <|> {lLabel}", None, None, idx2, idx)
                    
                        idx2 = idx2 + 1

                for ciId, ciLabel in zip(ModelProperty['ciIds'],ModelProperty['ciLabels']):
                    if ciId and ciLabel:

                        # Add Contained In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedIn']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{ciLabel}", f"{ciId} <|> {ciLabel}", None, None, idx2, idx)
                        
                        idx2 = idx2 + 1

                for cId, cLabel in zip(ModelProperty['cIds'],ModelProperty['cLabels']):
                    if cId and cLabel:

                        # Add Contains Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Contains']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{cLabel}", f"{cId} <|> {cLabel}", None, None, idx2, idx)
                    
                        idx2 = idx2 + 1

                for sId, sLabel in zip(ModelProperty['sIds'],ModelProperty['sLabels']):
                    if sId and sLabel:

                        # Add Similar To Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_2/Set_0/Question_0', f"{sLabel}", f"{sId} <|> {sLabel}", None, None, idx2, idx)

                        idx2 = idx2 + 1
            
                idx2 = 0

                for ffId, ffLabel in zip(ModelProperty['ffIds'],ModelProperty['ffLabels']):
                    if ffId and ffLabel:
                        
                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{ffLabel}", f"{ffId} <|> {ffLabel}", None, None, idx2)
                        
                        # Add Contained As Formulation In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)
                        
                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if ffId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                for afId, afLabel in zip(ModelProperty['afIds'],ModelProperty['afLabels']):
                    if afId and afLabel:

                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{afLabel}", f"{afId} <|> {afLabel}", None, None, idx2)
                        
                        # Add Contained As Assumption In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)

                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if afId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                for bcfId, bcfLabel in zip(ModelProperty['bcfIds'],ModelProperty['bcfLabels']):
                    if bcfId and bcfLabel:

                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{bcfLabel}", f"{bcfId} <|> {bcfLabel}", None, None, idx2)
                        
                        # Add Contained As Boundary Condition In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)

                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if bcfId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                for ccfId, ccfLabel in zip(ModelProperty['ccfIds'],ModelProperty['ccfLabels']):
                    if ccfId and ccfLabel:

                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{ccfLabel}", f"{ccfId} <|> {ccfLabel}", None, None, idx2)
                        
                        # Add Contained As Constraint Condition In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)
                    
                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if ccfId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                for cpcfId, cpcfLabel in zip(ModelProperty['cpcfIds'],ModelProperty['cpcfLabels']):
                    if cpcfId and cpcfLabel:

                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{cpcfLabel}", f"{cpcfId} <|> {cpcfLabel}", None, None, idx2)
                        
                        # Add Contained As Coupling Condition In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)

                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if cpcfId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                for icfId, icfLabel in zip(ModelProperty['icfIds'],ModelProperty['icfLabels']):
                    if icfId and icfLabel:

                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{icfLabel}", f"{icfId} <|> {icfLabel}", None, None, idx2)
                        
                        # Add Contained As Initial Condition In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)

                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if icfId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                for fcfId, fcfLabel in zip(ModelProperty['fcfIds'],ModelProperty['fcfLabels']):
                    if fcfId and fcfLabel:

                        # Set up Page for Mathematical Formulation
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5', idx2, None, None, None, idx2)
                        
                        # Add Id / Label of Mathematical Formualtion
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Question_0', f"{fcfLabel}", f"{fcfId} <|> {fcfLabel}", None, None, idx2)
                        
                        # Add Contained As Final Condition In Property and Model
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx, idx2)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_2/Question_0', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)

                        idx3 = 0
                        idx4 = 0

                        for res2 in results2:
                            
                            if fcfId == res2.get('mf',{}).get('value'):
                                if res2.get('F',{}).get('value'):
                                    its = res2['F']['value'].split(' <|> ')
                                    lbs = res2['FL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):
                                        
                                        # Add Contains Formulation Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFormulation']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                        
                                        idx3 = idx3 + 1 

                                if res2.get('FD',{}).get('value'):
                                    its = res2['FD']['value'].split(' <|> ')
                                    lbs = res2['FDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Formulation In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFormulationIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('A',{}).get('value'):
                                    its = res2['A']['value'].split(' <|> ')
                                    lbs = res2['AL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Assumption Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsAssumption']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('AD',{}).get('value'):
                                    its = res2['AD']['value'].split(' <|> ')
                                    lbs = res2['ADL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Assumption In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsAssumptionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('BC',{}).get('value'):
                                    its = res2['BC']['value'].split(' <|> ')
                                    lbs = res2['BCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Boundary Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsBoundaryCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('BCD',{}).get('value'):
                                    its = res2['BCD']['value'].split(' <|> ')
                                    lbs = res2['BCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Boundary Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsBoundaryConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CC',{}).get('value'):
                                    its = res2['CC']['value'].split(' <|> ')
                                    lbs = res2['CCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Constraint Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsConstraintCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CCD',{}).get('value'):
                                    its = res2['CCD']['value'].split(' <|> ')
                                    lbs = res2['CCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Constraint Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsConstraintConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('CPC',{}).get('value'):
                                    its = res2['CPC']['value'].split(' <|> ')
                                    lbs = res2['CPCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Coupling Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsCouplingCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('CPCD',{}).get('value'):
                                    its = res2['CPCD']['value'].split(' <|> ')
                                    lbs = res2['CPCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Coupling Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsCouplingConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('IC',{}).get('value'):
                                    its = res2['IC']['value'].split(' <|> ')
                                    lbs = res2['ICL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Initial Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsInitialCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('ICD',{}).get('value'):
                                    its = res2['ICD']['value'].split(' <|> ')
                                    lbs = res2['ICDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Initial Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsInitialConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FC',{}).get('value'):
                                    its = res2['FC']['value'].split(' <|> ')
                                    lbs = res2['FCL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Final Condition Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainsFinalCondition']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1 

                                if res2.get('FCD',{}).get('value'):
                                    its = res2['FCD']['value'].split(' <|> ')
                                    lbs = res2['FCDL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained As Final Condition In Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_1', None, None, Option.objects.get(uri=mathmoddb['ContainedAsFinalConditionIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_1/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res2.get('FGBF',{}).get('value'):
                                    its = res2['FGBF']['value'].split(' <|> ')
                                    lbs = res2['FGBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FGF',{}).get('value'):
                                    its = res2['FGF']['value'].split(' <|> ')
                                    lbs = res2['FGFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FABF',{}).get('value'):
                                    its = res2['FABF']['value'].split(' <|> ')
                                    lbs = res2['FABFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FAF',{}).get('value'):
                                    its = res2['FAF']['value'].split(' <|> ')
                                    lbs = res2['FAFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FDBF',{}).get('value'):
                                    its = res2['FDBF']['value'].split(' <|> ')
                                    lbs = res2['FDBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FDF',{}).get('value'):
                                    its = res2['FDF']['value'].split(' <|> ')
                                    lbs = res2['FDFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FLBF',{}).get('value'):
                                    its = res2['FLBF']['value'].split(' <|> ')
                                    lbs = res2['FLBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FLF',{}).get('value'):
                                    its = res2['FLF']['value'].split(' <|> ')
                                    lbs = res2['FLFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FNBF',{}).get('value'):
                                    its = res2['FNBF']['value'].split(' <|> ')
                                    lbs = res2['FNBFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalized By Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['NondimensionalizedBy']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1
                                
                                if res2.get('FNF',{}).get('value'):
                                    its = res2['FNF']['value'].split(' <|> ')
                                    lbs = res2['FNFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Nondimensionalizes Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['Nondimensionalizes']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                                if res2.get('FSF',{}).get('value'):
                                    its = res2['FSF']['value'].split(' <|> ')
                                    lbs = res2['FSFL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Formulation
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_1', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx4, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_5/Set_3/Question_0', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)

                                        idx4 = idx4 + 1

                        idx2 = idx2 + 1

                idx2 = 0
                
                for taId, taLabel in zip(ModelProperty['taIds'], ModelProperty['taLabels']):
                    if taId and taLabel:
                        
                        # Set up Page for Task
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6', idx2, None, None, None, idx2)
                        
                        # Add Task ID / Label
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Question_0', f"{taLabel}", f"{taId} <|> {taLabel}", None, None, idx2)
                        
                        # Add Model applied by Task
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Question_1', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx2)

                        idx3 = 0

                        for res3 in results3:
                            
                            if taId == res3.get('t',{}).get('value'):
                                if res3.get('TGBT',{}).get('value'):
                                    its = res3['TGBT']['value'].split(' <|> ')
                                    lbs = res3['TGBTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalized By Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['GeneralizedBy']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TGT',{}).get('value'):
                                    its = res3['TGT']['value'].split(' <|> ')
                                    lbs = res3['TGTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Generalizes Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['Generalizes']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TABT',{}).get('value'):
                                    its = res3['TABT']['value'].split(' <|> ')
                                    lbs = res3['TABTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximated By Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['ApproximatedBy']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TAT',{}).get('value'):
                                    its = res3['TAT']['value'].split(' <|> ')
                                    lbs = res3['TATL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Approximates Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['Approximates']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                    idx3 = idx3 + 1

                                if res3.get('TDBT',{}).get('value'):
                                    its = res3['TDBT']['value'].split(' <|> ')
                                    lbs = res3['TDBTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretized By Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['DiscretizedBy']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TDT',{}).get('value'):
                                    its = res3['TDT']['value'].split(' <|> ')
                                    lbs = res3['TDTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Discretizes Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['Discretizes']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TICT',{}).get('value'):
                                    its = res3['TICT']['value'].split(' <|> ')
                                    lbs = res3['TICTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contained In Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['ContainedIn']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TCT',{}).get('value'):
                                    its = res3['TCT']['value'].split(' <|> ')
                                    lbs = res3['TCTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Contains Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['Contains']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                    
                                        idx3 = idx3 + 1

                                if res3.get('TLBT',{}).get('value'):
                                    its = res3['TLBT']['value'].split(' <|> ')
                                    lbs = res3['TLBTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearized By Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['LinearizedBy']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TLT',{}).get('value'):
                                    its = res3['TLT']['value'].split(' <|> ')
                                    lbs = res3['TLTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Linearizes Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['Linearizes']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                                if res3.get('TST',{}).get('value'):
                                    its = res3['TST']['value'].split(' <|> ')
                                    lbs = res3['TSTL']['value'].split(' <|> ')
                                    for it,lb in zip(its,lbs):

                                        # Add Similar To Property and Task
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_0', None, None, Option.objects.get(uri=mathmoddb['SimilarTo']), None, idx3, idx2)
                                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_6/Set_1/Question_1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)

                                        idx3 = idx3 + 1

                        idx2 = idx2 + 1

            puIds = []
            puLabels = []

            for res4 in results4:

                if res4.get('PU1',{}).get('value'):
                    if res4['PU1']['value'] not in puIds:
                        puIds.append(res4['PU1']['value'])
                        puLabels.append(res4['LABEL1']['value'])

                if res4.get('PU2',{}).get('value'):
                    if res4['PU2']['value'] not in puIds:
                        puIds.append(res4['PU2']['value'])
                        puLabels.append(res4['LABEL2']['value'])

                if res4.get('PU3',{}).get('value'):
                    if res4['PU3']['value'] not in puIds:
                        puIds.append(res4['PU3']['value'])
                        puLabels.append(res4['LABEL3']['value'])

                if res4.get('PU4',{}).get('value'):
                    if res4['PU4']['value'] not in puIds:
                        puIds.append(res4['PU4']['value'])
                        puLabels.append(res4['LABEL4']['value'])

                if res4.get('PU5',{}).get('value'):
                    if res4['PU5']['value'] not in puIds:
                        puIds.append(res4['PU5']['value'])
                        puLabels.append(res4['LABEL5']['value'])

            for idx, (puId, puLabel) in enumerate(zip(puIds,puLabels)):

                idx2 = 0

                # Set up Publication Page 
                valueEditor(instance, f'{BASE_URI}Section_3a/Set_7', idx, None, None, None, idx)
                
                # Add Id / Label of Publication
                valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Question_0', f"{puLabel}", f"{puId} <|> {puLabel}", None, None, idx)
                
                for res4 in results4:

                    Class = res4.get('class',{}).get('value','').split('#')[-1]

                    if Class == 'ResearchField':
                        Abbr = 'RF'
                    elif Class == 'ResearchProblem':
                        Abbr = 'RP'
                    elif Class == 'MathematicalModel':
                        Abbr = 'MM'
                    elif Class == 'MathematicalFormulation':
                        Abbr = 'MF'
                    elif Class == 'Quantity':
                        Abbr = 'QQK'
                    elif Class == 'QuantityKind':
                        Abbr = 'QQK'
                    elif 'Task' in Class:
                        Class = 'Task'
                        Abbr = 'T'

                    if puId in res4.get('PU1',{}).get('value',''):
                        
                        # Add Documents Property and Entitiy
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Documents']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_0', f"{res4['label']['value']} ({Class})", f"{res4['item']['value']} <|> {res4['label']['value']} <|> {Class} <|> {Abbr}", None, None, idx2, idx)
                        
                        idx2 = idx2 + 1

                    if puId in res4.get('PU2',{}).get('value',''):

                        # Add Invents Property and Entitiy
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Invents']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_0', f"{res4['label']['value']} ({Class})", f"{res4['item']['value']} <|> {res4['label']['value']} <|> {Class} <|> {Abbr}", None, None, idx2, idx)

                        idx2 = idx2 + 1

                    if puId in res4.get('PU3',{}).get('value',''):

                        # Add Studies Property and Entitiy
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Studies']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_0', f"{res4['label']['value']} ({Class})", f"{res4['item']['value']} <|> {res4['label']['value']} <|> {Class} <|> {Abbr}", None, None, idx2, idx)
    
                        idx2 = idx2 + 1

                    if puId in res4.get('PU4',{}).get('value',''):

                        # Add Surveys Property and Entitiy
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Surveys']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_0', f"{res4['label']['value']} ({Class})", f"{res4['item']['value']} <|> {res4['label']['value']} <|> {Class} <|> {Abbr}", None, None, idx2, idx)
    

                    if puId in res4.get('PU5',{}).get('value',''):

                        # Add Uses Property and Entitiy
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_1', None, None, Option.objects.get(uri=mathmoddb['Uses']), None, idx2, idx)
                        valueEditor(instance, f'{BASE_URI}Section_3a/Set_7/Set_0/Question_0', f"{res4['label']['value']} ({Class})", f"{res4['item']['value']} <|> {res4['label']['value']} <|> {Class} <|> {Abbr}", None, None, idx2, idx)
    
                        idx2 = idx2 + 1

    return

@receiver(post_save, sender=Value)
def programmingLanguages(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}Section_4/Set_3/Question_01':
       
        software_id = instance.text.split(' <|> ')[0]
        
        if software_id.split(':')[0] == 'wikidata':
            
            res = kg_req(wikidata_endpoint,wini.format(pl_vars,pl_query.format(software_id.split(':')[-1],'P277'),'100'))
            for idx, r in enumerate(res):
                if r.get('qid',{}).get('value'): 
                    attribute_object = Attribute.objects.get(uri=f'{BASE_URI}Section_4/Set_3/Question_05')
                    obj, created = Value.objects.update_or_create(
                    project=instance.project,
                    attribute=attribute_object,
                    set_index=instance.set_index,
                    collection_index=idx,
                    defaults={
                              'project': instance.project,
                              'attribute': attribute_object,
                              'text': 'wikidata:' + res[idx]['qid']['value'] + ' <|> ' + res[idx]['label']['value'] + ' <|> ' + res[idx]['quote']['value']
                             }
                    )

        elif software_id.split(':')[0] == 'mardi':
            
            res = kg_req(mardi_endpoint,mini.format(pl_vars,pl_query.format(software_id.split(':')[-1],P19),'100')) 
            for idx, r in enumerate(res):
                if r.get('qid',{}).get('value'):
                    attribute_object = Attribute.objects.get(uri=f'{BASE_URI}Section_4/Set_3/Question_05')
                    obj, created = Value.objects.update_or_create(
                    project=instance.project,
                    attribute=attribute_object,
                    set_index=instance.set_index,
                    collection_index=idx, 
                    defaults={
                              'project': instance.project,
                              'attribute': attribute_object,
                              'text': 'mardi:' + res[idx]['qid']['value'] + ' <|> ' + res[idx]['label']['value'] + ' <|> ' + res[idx]['quote']['value']
                             }
                    )

    return

@receiver(post_save, sender=Value)
def processor(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}Section_4/Set_4/Question_03':
        try:
            url, label, quote = instance.external_id.split(' <|> ')
            
            # Get "real" URL
            r = requests.get(url)
            tmp = r.text.replace('<link rel="canonical" href="', 'r@ndom}-=||').split('r@ndom}-=||')[-1]
            idx = tmp.find('"/>')
            
            if 'https://en.wikichip.org/wiki/' in tmp[:idx]:
                real_link = tmp[:idx].replace('https://en.wikichip.org/wiki/','')
            else:
                real_link = url.replace('https://en.wikichip.org/wiki/','')
            
            res = kg_req(wikidata_endpoint,wini.format(pro_vars,pro_query.format('P12029',real_link),'1'))
            
            if res[0]:
                info = 'wikidata:'+res[0]['qid']['value'] + ' <|> ' + res[0]['label']['value'] + ' <|> ' + res[0]['quote']['value']
            else:
                info = real_link + ' <|> ' + label + ' <|> ' + quote
            
            attribute_object = Attribute.objects.get(uri=f'{BASE_URI}Section_4/Set_4/Question_03')
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                set_index=instance.set_index,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'external_id': info
                    }
            )
        except:
            pass

def kg_req(sparql_endpoint, query):
    '''Function performing SPARQL query at specific endpoint'''
    req = requests.get(sparql_endpoint,
                       params = {'format': 'json', 'query': query},
                       headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}
                       ).json()["results"]["bindings"]
    return req
    
def Author_Search(orcid_ids, zbmath_ids, orcid_authors, zbmath_authors):
    '''Function that takes orcid and zbmath ids and queries wikidata and MaRDI Portal to get
       further Information and map orcid and zbmath authors.'''
    
    # Initialize orcid and zbmath dicts   
    author_merged_orcid = {}
    author_merged_zbmath = {}
    
    # Define parameters for author queries
    query_parameters = [(orcid_ids, '496', author_merged_orcid, P22), (zbmath_ids, '1556', author_merged_zbmath, P23)]
    
    # Loop through each set of IDs
    for ids, property_id, author_merged_dict, mardi_property_id in query_parameters:
        if ids:
            
            # Define parameters for author queries to Wikidata and query data
            wikidata_parameter = ["'{}'".format(id_) for id_ in ids]
            wikidata_author_dicts = kg_req(wikidata_endpoint, queryPublication['AuthorViaOrcid'].format(' '.join(wikidata_parameter), property_id))

            # Sort author data according to the IDs
            for dic in wikidata_author_dicts:
                author_id = dic['authorId']['value']
                author_merged_dict[author_id] = {
                    'wikidata_authorLabel': dic.get('authorLabel', {}).get('value'),
                    'wikidata_authorDescription': dic.get('authorDescription', {}).get('value'),
                    'wikidata_authorQid': dic.get('authorQid', {}).get('value')}
        
            # Define parameters for author queries to MaRDI KG and query data
            mardi_parameter = [["'{}'".format(id_) for id_ in ids], 
                               ["'{}'".format(author_merged_dict[k]['wikidata_authorQid']) for k in author_merged_dict if author_merged_dict[k]['wikidata_authorQid']]]
            
            # Query MaRDI KG for Authors by IDs and Wikidata QID
            mardi_author_dicts_1 = kg_req(mardi_endpoint, queryPublication['AuthorViaOrcid'].format(' '.join(mardi_parameter[0]), mardi_property_id))
            mardi_author_dicts_2 = kg_req(mardi_endpoint, queryPublication['AuthorViaWikidataQID'].format(' '.join(mardi_parameter[1]), P2))
        
            # Add QIDs from MaRDI KG to sorted authors 
            for dic in mardi_author_dicts_1:
                author_id = dic['authorId']['value']
                if author_id in author_merged_dict:
                    author_merged_dict[author_id].update({
                        'mardi_authorLabel': dic.get('authorLabel', {}).get('value'),
                        'mardi_authorDescription': dic.get('authorDescription', {}).get('value'),
                        'mardi_authorQid': dic.get('authorQid', {}).get('value')})
        
            for dic in mardi_author_dicts_2:
                wikidata_qid = dic['wikidataQid']['value']
                for author_id, author_data in author_merged_dict.items():
                    if author_data['wikidata_authorQid'] == wikidata_qid:
                        try:
                            author_data.update({
                                'mardi_authorQid': dic['mardiQid']['value'],
                                'mardi_authorLabel': dic['authorLabel']['value'],
                                'mardi_authorDescription': dic['authorDescription']['value']})
                        except KeyError:
                            pass
                            
    # Combine orcid and zbmath Authors, defined by User 
    
    author_dict_merged = {}
    
    for author_id, orcid_id in orcid_authors:
        author_data = {
            'orcid': orcid_id,
            'zbmath': None,
            'wikiQID': author_merged_orcid[orcid_id]['wikidata_authorQid'],
            'wikiLabel': author_merged_orcid[orcid_id]['wikidata_authorLabel'],
            'wikiDescription': author_merged_orcid[orcid_id]['wikidata_authorDescription'],
            'mardiQID': author_merged_orcid[orcid_id]['mardi_authorQid'],
            'mardiLabel': author_merged_orcid[orcid_id]['mardi_authorLabel'],
            'mardiDescription': author_merged_orcid[orcid_id]['mardi_authorDescription']}
        
        author_dict_merged[author_id] = author_data
    
    for author_id, zbmath_id in zbmath_authors:
        score = [0.0, '']
        for author in author_dict_merged:
            s = SequenceMatcher(None, re.sub('[^a-zA-Z ]',' ',author_id), re.sub('[^a-zA-Z ]',' ',author)).ratio()
            if s > score[0]:
                score = [s, author]
        if round(score[0]):
            author_dict_merged[score[1]].update({
                'zbmath': zbmath_id,
                'wikiQID': author_dict_merged[score[1]]['wikiQID'] or author_merged_zbmath[zbmath_id]['wikidata_authorQid'],
                'wikiLabel': author_dict_merged[score[1]]['wikiLabel'] or author_merged_zbmath[zbmath_id]['wikidata_authorLabel'],
                'wikiDescription': author_dict_merged[score[1]]['wikiDescription'] or author_merged_zbmath[zbmath_id]['wikidata_authorDescription'],
                'mardiQID': author_dict_merged[score[1]]['mardiQID'] or author_merged_zbmath[zbmath_id]['mardi_authorQid'],
                'mardiLabel': author_dict_merged[score[1]]['mardiLabel'] or author_merged_zbmath[zbmath_id]['mardi_authorLabel'],
                'mardiDescription': author_dict_merged[score[1]]['mardiDescription'] or author_merged_zbmath[zbmath_id]['mardi_authorDescription']})
        else:
            author_data = {
                'orcid': None,
                'zbmath': zbmath_id,
                'wikiQID': author_merged_zbmath[zbmath_id]['wikidata_authorQid'],
                'wikiLabel': author_merged_zbmath[zbmath_id]['wikidata_authorLabel'],
                'wikiDescription': author_merged_zbmath[zbmath_id]['wikidata_authorDescription'],
                'mardiQID': author_merged_zbmath[zbmath_id]['mardi_authorQid'],
                'mardiLabel': author_merged_zbmath[zbmath_id]['mardi_authorLabel'],
                'mardiDescription': author_merged_zbmath[zbmath_id]['mardi_authorDescription']}
    
            author_dict_merged[author_id] = author_data
    return author_dict_merged
    
def make_api_requests(api, search_objects, dict_merged, prefix):
    req = {}
    for index, search_object in enumerate(search_objects):
        for item in search_object:
            try:
                req.update({index: requests.get(api + '?action=wbsearchentities&format=json&language=en&type=item&limit=10&search={0}'.format(item), 
                                                headers={'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['search'][0]})
            except (KeyError, IndexError):
                pass
    
    properties = ['journal']
    for index, prop in enumerate(properties):
        if index in req:
            display_label = req[index]['display']['label']['value'] if 'display' in req[index] and 'label' in req[index]['display'] else ''
            display_desc = req[index]['display']['description']['value'] if 'display' in req[index] and 'description' in req[index]['display'] else ''
            dict_merged.update({
                '{0}_{1}Qid'.format(prefix, prop): req[index]['id'],
                '{0}_{1}Label'.format(prefix, prop): display_label,
                '{0}_{1}Description1'.format(prefix, prop): display_desc
            })

def valueEditor(instance, uri, text=None, external_id=None, option=None, collection_index=None, set_index=None, set_prefix=None):
    
    attribute_object = Attribute.objects.get(uri=uri)

    # Prepare the defaults dictionary
    defaults = {
        'project': instance.project,
        'attribute': attribute_object,
    }

    if text is not None:
        defaults['text'] = text

    if external_id is not None:
        defaults['external_id'] = external_id

    if option is not None:
        defaults['option'] = Option.objects.get(uri=option)

    # Handle collection_index if provided
    if collection_index is not None and set_index is not None and set_prefix is None:
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            collection_index=collection_index,
            set_index=set_index,
            defaults=defaults
        )
    elif collection_index is not None and set_index is None and set_prefix is None:
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            collection_index=collection_index,
            defaults=defaults
        )
    elif set_index is not None and collection_index is None and set_prefix is None:
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            set_index=set_index,
            defaults=defaults
        )
    elif set_index is not None and collection_index is None and set_prefix is not None:
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            set_prefix=set_prefix,
            set_index=set_index,
            defaults=defaults
        )
    else:
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            defaults=defaults
        )

    return
    
