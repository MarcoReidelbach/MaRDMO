import re, os, json
import requests

from django.dispatch import receiver
from django.db.models.signals import post_save

from rdmo.projects.models import Value
from rdmo.domain.models import Attribute
from rdmo.options.models import Option

from .citation import GetCitation
from .mathmoddb import queryMathModDB
from .sparql import queryPublication, queryModelHandler, wini, mini, pl_query, pl_vars, pro_query, pro_vars
from .id import *
from .config import wd, wdt, mardi_api, wikidata_api, mardi_endpoint, wikidata_endpoint, BASE_URI

from difflib import SequenceMatcher

@receiver(post_save, sender=Value)
def PublicationCitationRetriever(sender, **kwargs): 

    instance = kwargs.get("instance", None)

    if instance and instance.attribute.uri == f"{BASE_URI}domain/Published":
    
        # Activate (Yes)  / Deactivate (No or nothin) Publication Information Section
        if instance.option_text == 'Yes':            
            valueEditor(instance,f"{BASE_URI}domain/PublicationInformation",1)
        else: 
            valueEditor(instance,f"{BASE_URI}domain/PublicationInformation",0)

        # Evaluate Information provided for Yes case
        if instance.text.split(':')[0] == 'url': 
            
            # If url provided, deactivate Publication Information section 
            valueEditor(instance,f"{BASE_URI}domain/PublicationInformation",0)
        
        elif re.match(r'doi:10.\d{4,9}/[-._;()/:a-z0-9A-Z]+', instance.text):

            path = os.path.join(os.path.dirname(__file__), 'data', 'options.json')
            with open(path, "r") as json_file:
                option = json.load(json_file)
            
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
            
            object_uris = [f'{BASE_URI}domain/PublicationQID', f'{BASE_URI}domain/PublicationQID_hidden',
                           f'{BASE_URI}domain/PublicationType', f'{BASE_URI}domain/PublicationType_hidden',
                           f'{BASE_URI}domain/PublicationTitle', f'{BASE_URI}domain/PublicationTitle_hidden',
                           f'{BASE_URI}domain/PublicationAuthor', f'{BASE_URI}domain/PublicationAuthor_hidden',
                           f'{BASE_URI}domain/PublicationLanguage', f'{BASE_URI}domain/PublicationLanguage_hidden',
                           f'{BASE_URI}domain/PublicationJournal', f'{BASE_URI}domain/PublicationJournal_hidden',
                           f'{BASE_URI}domain/PublicationVolume', f'{BASE_URI}domain/PublicationVolume_hidden',
                           f'{BASE_URI}domain/PublicationIssue', f'{BASE_URI}domain/PublicationIssue_hidden',
                           f'{BASE_URI}domain/PublicationPage', f'{BASE_URI}domain/PublicationPage_hidden',
                           f'{BASE_URI}domain/PublicationDate', f'{BASE_URI}domain/PublicationDate_hidden']
            
            for paper_info, object_uri in zip(paper_infos, object_uris):
                if object_uri == f'{BASE_URI}domain/PublicationLanguage':
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

    if instance and instance.attribute.uri == f'{BASE_URI}domain/DocumentationType':
    
        path = os.path.join(os.path.dirname(__file__), 'data', 'modus.json')
        with open(path, "r") as json_file:
            OperationModus = json.load(json_file)

        path = os.path.join(os.path.dirname(__file__), 'data', 'options.json')
        with open(path, "r") as json_file:
            option = json.load(json_file)

        if instance.option == Option.objects.get(uri=option['Workflow']):
            # Activate Questions for Workflow Documentation
            val = [0,0,0,0,0]
        elif instance.option == Option.objects.get(uri=option['Model']):
            # Activate Questions for Model Documentation
            val = [1,0,0,0,1]
        else:
            # Deactivate all Documentation Questions
            val = [0,0,0,0,0]

        for idx, key in enumerate(OperationModus['WorkflowOrModel'].keys()):
            for uri in OperationModus['WorkflowOrModel'][key]:
                valueEditor(instance,uri,val[idx])
    return

@receiver(post_save, sender=Value)
def SearchOrDocument(sender, **kwargs):
    
    instance = kwargs.get("instance", None)
    
    if instance and instance.attribute.uri == f'{BASE_URI}domain/OperationType':
        
        path = os.path.join(os.path.dirname(__file__), 'data', 'modus.json')
        with open(path, "r") as json_file:
            OperationModus = json.load(json_file)

        path = os.path.join(os.path.dirname(__file__), 'data', 'options.json')
        with open(path, "r") as json_file:
            option = json.load(json_file)

        if instance.option == Option.objects.get(uri=option['Search']):
            # Activate Questions for Search
            val = [1,0,1,0]
        else:
            # Deactivate all Questionss
            val = [0,0,0,0]

        for idx, key in enumerate(OperationModus['SearchOrDocument'].keys()):
            for uri in OperationModus['SearchOrDocument'][key]:
                valueEditor(instance,uri,val[idx])
    return

@receiver(post_save, sender=Value)
def ComputationalOrExperimental(sender, **kwargs):

    instance = kwargs.get("instance", None)
    
    if instance and instance.attribute.uri == f'{BASE_URI}domain/WorkflowType':

        path = os.path.join(os.path.dirname(__file__), 'data', 'modus.json')
        with open(path, "r") as json_file:
            OperationModus = json.load(json_file)

        path = os.path.join(os.path.dirname(__file__), 'data', 'options.json')
        with open(path, "r") as json_file:
            option = json.load(json_file)

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
    
    if instance and instance.attribute.uri == f'{BASE_URI}domain/MainMathematicalModelMathModDBID':

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
                        valueEditor(instance, f'{BASE_URI}domain/ResearchField', idx, None, None, None, idx)
                        # Add Research Field Values
                        valueEditor(instance, f'{BASE_URI}domain/ResearchFieldMathModDBID', f"{rfLabel}", f"{rfId} <|> {rfLabel}", None, None, idx)
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
                        valueEditor(instance, f'{BASE_URI}domain/ResearchProblem', idx, None, None, None, idx)
                        # Add Research Problem Values
                        valueEditor(instance, f'{BASE_URI}domain/ResearchProblemMathModDBID', f"{rpLabel}", f"{rpId} <|> {rpLabel}", None, None, idx)
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
                    # Set up Qauntity / Quantity Kind Page
                    valueEditor(instance, f'{BASE_URI}domain/QuantityOrQuantityKind', idx, None, None, None, idx)
                    # Add Quantity / Quantity Kind Values
                    valueEditor(instance, f'{BASE_URI}domain/QuantityOrQuantityKindMathModDBID', 
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
                valueEditor(instance, f'{BASE_URI}domain/MathematicalModel', idx, None, None, None, idx)
                # Add Mathematical Model ID and Label
                valueEditor(instance, f'{BASE_URI}domain/MathematicalModelMathModDBID', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx)
                # Add Research Problem related to Mathematical Model
                for idx2, (rpId, rpLabel) in enumerate(zip(rpIds,rpLabels)):
                    valueEditor(instance, f'{BASE_URI}domain/ResearchProblemRelatedToMathematicalModel', f"{rpLabel}", f"{rpId} <|> {rpLabel}", None, idx2, idx)
                
                # Add Model Relations

                modelRelations1 = {'ff': 'containedAsFormulationIn',
                                   'af': 'containedAsAssumptionIn',
                                   'bcf': 'containedAsBoundaryConditionIn',
                                   'ccf': 'containedAsConstraintConditionIn',
                                   'cpcf': 'containedAsCouplingConditionIn',
                                   'icf': 'containedAsInitialConditionIn',
                                   'fcf': 'containedAsFinalConditionIn'}

                modelRelations2 = {'gb': 'generalizedByModel',
                                   'g': 'generalizesModel',
                                   'ab': 'approximatedByModel',
                                   'a': 'approximatesModel',
                                   'db': 'discretizedByModel',
                                   'd': 'discretizesModel',
                                   'lb': 'linearizedByModel',
                                   'l': 'linearizesModel',
                                   'ci': 'containedInModel',
                                   'c': 'containsModel',
                                   's': 'similarToModel'}
                
                formulationRelations1 = {'F': 'containsFormulation',
                                         'FD': 'containedAsFormulationIn',
                                         'A': 'containsAssumption',
                                         'AD': 'containedAsAssumptionIn',
                                         'BC': 'containsBoundaryCondition',
                                         'BCD': 'containedAsBoundaryConditionIn',
                                         'CC': 'containsConstraintCondition',
                                         'CCD': 'containedAsConstraintConditionIn',
                                         'CPC': 'containsCouplingCondition',
                                         'CPCD': 'containedAsCouplingConditionIn',
                                         'IC': 'containsInitialCondition',
                                         'ICD': 'containedAsInitialConditionIn',
                                         'FC': 'containsFinalCondition',
                                         'FCD': 'containedAsFinalConditionIn'}

                formulationRelations2 = {'FGBF': 'generalizedByFormulation',
                                         'FGF': 'generalizesFormulation',
                                         'FABF': 'approximatedByFormulation',
                                         'FAF': 'approximatesFormulation',
                                         'FDBF': 'discretizedByFormulation',
                                         'FDF': 'discretizesFormulation',
                                         'FLBF': 'linearizedByFormulation',
                                         'FLF': 'linearizesFormulation',
                                         'FNBF': 'nondimensionalizedByFormulation',
                                         'FNF': 'nondimensionalizesFormulation',
                                         'FSF': 'similarToFormulation'}
                
                taskRelations = {'TGBT': 'generalizedByTask',
                                 'TGT': 'generalizesTask',
                                 'TABT': 'approximatedByTask',
                                 'TAT': 'approximatesTask',
                                 'TDBT': 'discretizedByTask',
                                 'TDT': 'discretizesTask',
                                 'TICT': 'containedInTask',
                                 'TCT': 'containsTask',
                                 'TLBT': 'linearizedByTask',
                                 'TLT': 'linearizesTask',
                                 'TST': 'similarToTask'}
                
                publicationRelations = {'1': 'documents',
                                        '2': 'invents',
                                        '3': 'studies',
                                        '4': 'surveys',
                                        '5': 'uses'}

                idx2 = 0
                for prefix in modelRelations2.keys():
                    for Id, Label in zip(ModelProperty[f'{prefix}Ids'],ModelProperty[f'{prefix}Labels']):
                        if Id and Label:
                            # Add Property and Model
                            valueEditor(instance, f'{BASE_URI}domain/MathematicalModelToMathematicalModelRelation', None, None, Option.objects.get(uri=mathmoddb[modelRelations2[prefix]]), None, idx2, idx)
                            valueEditor(instance, f'{BASE_URI}domain/MathematicalModelRelatedToMathematicalModel', f"{Label}", f"{Id} <|> {Label}", None, None, idx2, idx)
                            # Increase index
                            idx2 = idx2 + 1
                
                idx2 = 0
                for type in modelRelations1.keys(): #['ff','af','bcf','ccf','cpcf','icf','fcf']:
                    for Id, Label in zip(ModelProperty[f'{type}Ids'],ModelProperty[f'{type}Labels']):
                        if Id and Label:
                            # Set up Page for Mathematical Formulation
                            valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulation', idx2, None, None, None, idx2)
                            # Add Id / Label of Mathematical Formualtion
                            valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulationMathModDBID', f"{Label}", f"{Id} <|> {Label}", None, None, idx2)
                            # Add Contained As Formulation In Property and Model
                            valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulationToMathematicalModelRelation', None, None, Option.objects.get(uri=mathmoddb[modelRelations1[type]]), None, idx, idx2)
                            valueEditor(instance, f'{BASE_URI}domain/MathematicalModelRelatedToMathematicalFormulation', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx, idx2)
                            idx3 = 0
                            idx4 = 0
                            for res2 in results2:
                                if Id == res2.get('mf',{}).get('value'):
                                    for prefix in formulationRelations1.keys():
                                        if res2.get(prefix,{}).get('value'):
                                            its = res2[prefix]['value'].split(' <|> ')
                                            lbs = res2[f'{prefix}L']['value'].split(' <|> ')
                                            for it,lb in zip(its,lbs):
                                                # Add Contains Formulation Property and Formulation
                                                valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulationToMathematicalFormulationRelation1', None, None, Option.objects.get(uri=mathmoddb[formulationRelations1[prefix]]), None, idx3, idx2)
                                                valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulationRelatedToMathematicalFormulation1', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                                # Increase Index
                                                idx3 = idx3 + 1
                                    for prefix in formulationRelations2.keys(): 
                                        if res2.get(prefix,{}).get('value'):
                                            its = res2[prefix]['value'].split(' <|> ')
                                            lbs = res2[f'{prefix}L']['value'].split(' <|> ')
                                            for it,lb in zip(its,lbs):
                                                # Add Generalized By Property and Formulation
                                                valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulationToMathematicalFormulationRelation2', None, None, Option.objects.get(uri=mathmoddb[formulationRelations2[prefix]]), None, idx4, idx2)
                                                valueEditor(instance, f'{BASE_URI}domain/MathematicalFormulationRelatedToMathematicalFormulation2', f"{lb}", f"{it} <|> {lb}", None, None, idx4, idx2)
                                                # Increase Index
                                                idx4 = idx4 + 1
                            idx2 = idx2 + 1
                
                idx2 = 0
                for taId, taLabel in zip(ModelProperty['taIds'], ModelProperty['taLabels']):
                    if taId and taLabel:
                        # Set up Page for Task
                        valueEditor(instance, f'{BASE_URI}domain/Task', idx2, None, None, None, idx2)
                        # Add Task ID / Label
                        valueEditor(instance, f'{BASE_URI}domain/TaskMathModDBID', f"{taLabel}", f"{taId} <|> {taLabel}", None, None, idx2)
                        # Add Model applied by Task
                        valueEditor(instance, f'{BASE_URI}domain/MathematicalModelRelatedToTask', f"{mmLabel}", f"{mmId} <|> {mmLabel}", None, None, idx2)
                        idx3 = 0
                        for res3 in results3:
                            if taId == res3.get('t',{}).get('value'):
                                for prefix in taskRelations.keys(): 
                                    if res3.get(prefix,{}).get('value'):
                                        its = res3[prefix]['value'].split(' <|> ')
                                        lbs = res3[f'{prefix}L']['value'].split(' <|> ')
                                        for it,lb in zip(its,lbs):
                                            # Add Generalized By Property and Task
                                            valueEditor(instance, f'{BASE_URI}domain/TaskToTaskRelation', None, None, Option.objects.get(uri=mathmoddb[taskRelations[prefix]]), None, idx3, idx2)
                                            valueEditor(instance, f'{BASE_URI}domain/TaskRelatedToTask', f"{lb}", f"{it} <|> {lb}", None, None, idx3, idx2)
                                            # Increase Index
                                            idx3 = idx3 + 1
                        idx2 = idx2 + 1

            puIds = []
            puLabels = []
            for res4 in results4:
                for no in range(1,6):
                    if res4.get(f'PU{no}',{}).get('value'):
                        if res4[f'PU{no}']['value'] not in puIds:
                            puIds.append(res4[f'PU{no}']['value'])
                            puLabels.append(res4[f'LABEL{no}']['value'])

            for idx, (puId, puLabel) in enumerate(zip(puIds,puLabels)):
                idx2 = 0
                # Set up Publication Page 
                valueEditor(instance, f'{BASE_URI}domain/Publication', idx, None, None, None, idx)
                # Add Id / Label of Publication
                valueEditor(instance, f'{BASE_URI}domain/PublicationMathModDBID', f"{puLabel}", f"{puId} <|> {puLabel}", None, None, idx)
                # Get Class abbreviation
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
                    for no in publicationRelations.keys():
                        if puId in res4.get(f'PU{no}',{}).get('value',''):                        
                            # Add Documents Property and Entitiy
                            valueEditor(instance, f'{BASE_URI}domain/PublicationToModelEntityRelation', None, None, Option.objects.get(uri=mathmoddb[publicationRelations[no]]), None, idx2, idx)
                            valueEditor(instance, f'{BASE_URI}domain/ModelEntityRelatedToPublication', f"{res4['label']['value']} ({Class})", f"{res4['item']['value']} <|> {res4['label']['value']} <|> {Class} <|> {Abbr}", None, None, idx2, idx)
                            # Increase Index
                            idx2 = idx2 + 1    

    return

@receiver(post_save, sender=Value)
def programmingLanguages(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}domain/SoftwareQID':
       
        software_id = instance.external_id.split(' <|> ')[0]
        
        if software_id.split(':')[0] == 'wikidata':
            
            res = kg_req(wikidata_endpoint,wini.format(pl_vars,pl_query.format(software_id.split(':')[-1],'P277'),'100'))
            for idx, r in enumerate(res):
                if r.get('qid',{}).get('value'): 
                    attribute_object = Attribute.objects.get(uri=f'{BASE_URI}domain/SoftwareProgrammingLanguages')
                    obj, created = Value.objects.update_or_create(
                    project=instance.project,
                    attribute=attribute_object,
                    set_index=instance.set_index,
                    collection_index=idx,
                    defaults={
                              'project': instance.project,
                              'attribute': attribute_object,
                              'external_id': f"wikidata:{res[idx]['qid']['value']} <|> {res[idx]['label']['value']} <|> {res[idx]['quote']['value']}",
                              'text': f"{res[idx]['label']['value']} ({res[idx]['quote']['value']})"
                             }
                    )

        elif software_id.split(':')[0] == 'mardi':
            
            res = kg_req(mardi_endpoint,mini.format(pl_vars,pl_query.format(software_id.split(':')[-1],P19),'100')) 
            for idx, r in enumerate(res):
                if r.get('qid',{}).get('value'):
                    attribute_object = Attribute.objects.get(uri=f'{BASE_URI}domain/SoftwareProgrammingLanguages')
                    obj, created = Value.objects.update_or_create(
                    project=instance.project,
                    attribute=attribute_object,
                    set_index=instance.set_index,
                    collection_index=idx, 
                    defaults={
                              'project': instance.project,
                              'attribute': attribute_object,
                              'external_id': f"mardi:{res[idx]['qid']['value']} <|> {res[idx]['label']['value']} <|> {res[idx]['quote']['value']}",
                              'text': f"{res[idx]['label']['value']} ({res[idx]['quote']['value']})"
                             }
                    )

    return

@receiver(post_save, sender=Value)
def processor(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}domain/HardwareProcessor':
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
            
            attribute_object = Attribute.objects.get(uri=f'{BASE_URI}domain/HardwareProcessor')
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

@receiver(post_save, sender=Value)
def RP2RF(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}domain/ResearchFieldRelatedToResearchProblem':

        path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')
        with open(path, "r") as json_file:
            mathmoddb = json.load(json_file)

        attribute_object = Attribute.objects.get(uri=f'{BASE_URI}domain/ResearchProblemToResearchFieldRelation')
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            set_prefix=instance.set_prefix,
            collection_index=instance.collection_index,
            defaults={
                'project': instance.project,
                'attribute': attribute_object,
                'text': mathmoddb['containedInField']
                }
        )

@receiver(post_save, sender=Value)
def RP2MM(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}domain/ResearchProblemRelatedToMathematicalModel':

        path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')
        with open(path, "r") as json_file:
            mathmoddb = json.load(json_file)

        attribute_object = Attribute.objects.get(uri=f'{BASE_URI}domain/MathematicalModelToResearchProblemRelation')
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            set_prefix=instance.set_prefix,
            collection_index=instance.collection_index,
            defaults={
                'project': instance.project,
                'attribute': attribute_object,
                'text': mathmoddb['models']
                }
        )

@receiver(post_save, sender=Value)
def T2MM(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == f'{BASE_URI}domain/MathematicalModelRelatedToTask':

        path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')
        with open(path, "r") as json_file:
            mathmoddb = json.load(json_file)

        attribute_object = Attribute.objects.get(uri=f'{BASE_URI}domain/TaskToMathematicalModelRelation')
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            set_prefix=instance.set_prefix,
            collection_index=instance.collection_index,
            defaults={
                'project': instance.project,
                'attribute': attribute_object,
                'text': mathmoddb['appliesModel']
                }
        )

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
    
