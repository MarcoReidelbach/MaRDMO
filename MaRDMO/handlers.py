import logging
import requests

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from rdmo.projects.models import Value
from rdmo.domain.models import Attribute
from rdmo.options.models import Option

from .citation import *
from .para import *
from .sparql import *
from .id import *

from difflib import SequenceMatcher

@receiver(post_save, sender=Value)
def publication(sender, **kwargs): 
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_2/Set_1/Question_02':
        # Activate (Yes)  / Deactivate (No or nothin) Publication Information Section
        if instance.option_text == 'Yes':
            uri = 'http://example.com/terms/domain/MaRDI/Section_2/Set_2'
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': 1
                    }
                )
        else: 
            uri = 'http://example.com/terms/domain/MaRDI/Section_2/Set_2'
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': 0
                    }
                )
        # Evaluate Information provided for Yes case
        if instance.text.split(':')[0] == 'url':
            # If url provided, deactivate Publication Information section 
            # the URL will only be integrated into Workflow documentation as link
            uri = 'http://example.com/terms/domain/MaRDI/Section_2/Set_2'
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': 0
                    }
                )
        elif re.match(r'doi:10.\d{4,9}/[-._;()/:a-z0-9A-Z]+', instance.text):
            # Extract DOI and Initialize different dictionaries
            doi = instance.text.split(':')[1]   
            dict_merged = {}
            author_merged_orcid = {}
            author_merged_zbmath = {}
            author_merged_dict = {}
            author_dict_merged = {}
            # Define Prefix & Parameter for MaRDI KG search, Search Paper in MaRDI KG via DOI and merge results
            mardi_prefix = '''PREFIX wdt:{0} PREFIX wd:{1}'''.format(wdt,wd)
            mardi_query_parameter = [P16, doi.upper(), P8, P22, P4, P12, P10, P7, P9, P11, P13, P14, P15, P2, P23]
            mardi_dicts = kg_req(mardi_endpoint, mardi_prefix + query_1.format(*mardi_query_parameter))
            # Combine dictionaries from MaRDI Query
            for mardi_dict in mardi_dicts:
                for key in keys:
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
                wikidata_dicts = kg_req(wikidata_endpoint, query_1.format(*wikidata_parameter))
                # Combine dictionaries from Wikidata Query
                for wikidata_dict in wikidata_dicts:
                    for key in keys:
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
                    mardi_dict = kg_req(mardi_endpoint, mardi_prefix+query_2.format(*mardi_parameter))
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
            object_uris = ['http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_00',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_00_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_01',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_01_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_02',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_02_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_03',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_03_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_04',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_04_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_05',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_05_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_06',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_06_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_07',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_07_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_08',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_08_hidden',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_09',
                           'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_09_hidden']
            for paper_info, object_uri in zip(paper_infos, object_uris):
                if object_uri == 'http://example.com/terms/domain/MaRDI/Section_2/Set_2/Question_04':
                    for idx,val in enumerate(paper_info):
                        language_option = 'english' if val == 'English' else 1 if val == 'german' else None
                        if language_option is not None:
                            attribute_object = Attribute.objects.get(uri=object_uri)
                            obj, created = Value.objects.update_or_create(
                                project=instance.project,
                                attribute=attribute_object,
                                defaults={
                                    'project': instance.project,
                                    'attribute': attribute_object,
                                    'option': Option.objects.get(uri=f'http://example.com/terms/options/MaRDI/languages/{language_option}')
                                }
                            )
                else:
                    for idx,val in enumerate(paper_info):
                        attribute_object = Attribute.objects.get(uri=object_uri)
                        obj, created = Value.objects.update_or_create(
                            project=instance.project,
                            attribute=attribute_object,
                            collection_index = idx,
                            defaults={
                                'project': instance.project,
                                'attribute': attribute_object,
                                'text': val,
                            }
                        )
 
            return

@receiver(post_save, sender=Value)
def doctype(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_0/Set_1/Question_02':
        mod = ['http://example.com/terms/domain/MaRDI/Section_3/Set_0']
        moddetail = ['http://example.com/terms/domain/MaRDI/Section_3a/Set_0_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_1_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_2_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_3_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_5_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_6_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_7_hidden']
        doc = ['http://example.com/terms/domain/MaRDI/Section_2/Set_1',
               'http://example.com/terms/domain/MaRDI/Section_2/Set_3',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_3_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_4_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_5_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_6_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_2_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_1_hidden',
               'http://example.com/terms/domain/MaRDI/Section_5/Set_1']
        ident = ['http://example.com/terms/domain/MaRDI/Section_0a/Set_1',
                'http://example.com/terms/domain/MaRDI/Section_6/Set_1']
        pub = ['http://example.com/terms/domain/MaRDI/Section_2/Set_2']
        if instance.option_text == 'Workflow' or instance.option_text == 'Workflow':
            val = [1,1,1,0,0]
        elif instance.option_text == 'Mathematical Model' or instance.option_text == 'Mathematisches Modell':
            val = [1,0,1,0,0]
        else:
            val = [0,0,1,0,0]
        
        for uri in mod:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[0]
                    }
                )

        for uri in doc:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[1]
                    }
                )

        for uri in ident:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[2]
                    }
                )

        for uri in pub:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[3]
                    }
                )

        for uri in moddetail:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[4]
                    }
                )

    return

@receiver(post_save, sender=Value)
def types(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_0/Set_1/Question_01':
        search = ['http://example.com/terms/domain/MaRDI/Section_1/Set_1']
        pub = ['http://example.com/terms/domain/MaRDI/Section_2/Set_2']
        doc = ['http://example.com/terms/domain/MaRDI/Section_2/Set_1',
               'http://example.com/terms/domain/MaRDI/Section_2/Set_3',
               'http://example.com/terms/domain/MaRDI/Section_3/Set_0',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_3_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_4_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_5_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_6_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_2_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_1_hidden',
               'http://example.com/terms/domain/MaRDI/Section_5/Set_1']
        ident = ['http://example.com/terms/domain/MaRDI/Section_0a/Set_1',
                 'http://example.com/terms/domain/MaRDI/Section_6/Set_1']
        moddetail = ['http://example.com/terms/domain/MaRDI/Section_3a/Set_0_hidden',
                     'http://example.com/terms/domain/MaRDI/Section_3a/Set_1_hidden',
                     'http://example.com/terms/domain/MaRDI/Section_3a/Set_2_hidden',
                     'http://example.com/terms/domain/MaRDI/Section_3a/Set_3_hidden',
                     'http://example.com/terms/domain/MaRDI/Section_3a/Set_5_hidden',
                     'http://example.com/terms/domain/MaRDI/Section_3a/Set_6_hidden',
                     'http://example.com/terms/domain/MaRDI/Section_3a/Set_7_hidden']

        if instance.option_text == 'Document' or instance.option_text == 'Dokumentieren':
            val = [0,1,1,0,0]
        elif instance.option_text == 'Search' or instance.option_text == 'Suchen':
            val = [1,0,0,0,1]
        else:
            val = [0,0,1,0,1]
        print(val)
        for uri in search:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[0]
                    }
                )

        for uri in doc:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[1]
                    }
                )

        for uri in ident:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[2]
                    }
                )

        for uri in pub:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[3]
                    }
                )

        for uri in moddetail:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[4]
                    }
                )

    return

@receiver(post_save, sender=Value)
def workflowtype(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_2/Set_1/Question_03':
        pub = ['http://example.com/terms/domain/MaRDI/Section_2/Set_2']
        doc = ['http://example.com/terms/domain/MaRDI/Section_2/Set_1',
               'http://example.com/terms/domain/MaRDI/Section_3/Set_0',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_0_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_1_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_2_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_3_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_5_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_6_hidden',
               'http://example.com/terms/domain/MaRDI/Section_3a/Set_7_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_3_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_6_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_2_hidden',
               'http://example.com/terms/domain/MaRDI/Section_4/Set_1_hidden',
               'http://example.com/terms/domain/MaRDI/Section_5/Set_1',
               'http://example.com/terms/domain/MaRDI/Section_6/Set_1']
        comp = ['http://example.com/terms/domain/MaRDI/Section_4/Set_4_hidden']
        exp = ['http://example.com/terms/domain/MaRDI/Section_4/Set_5_hidden']

        if instance.option_text == '(Measurement) Data Analysis Workflow' or instance.option_text == '(Mess-)datenanalyse Workflow':
            val = [1,0,1]
        elif instance.option_text == 'Computational Workflow' or instance.option_text == 'Komputationaler Workflow':
            val = [1,1,0]
        else:
            val = [0,0,0,0]
        
        for uri in doc:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[0]
                    }
                )

        for uri in comp:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[1]
                    }
                )

        for uri in exp:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val[2]
                    }
                )
        if len(val) == 4:
            for uri in pub:
                attribute_object = Attribute.objects.get(uri=uri)
                obj, created = Value.objects.update_or_create(
                    project=instance.project,
                    attribute=attribute_object,
                    defaults={
                        'project': instance.project,
                        'attribute': attribute_object,
                        'text': val[3]
                        }
                    )

    return

@receiver(post_save, sender=Value)
def model(sender, **kwargs):
    
    instance = kwargs.get("instance", None)
    
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_3/Set_0/Wiki_01':
        
        if instance.text:
            val = 1
        else:
            val = 0

        uris = ['http://example.com/terms/domain/MaRDI/Section_3a/Set_0_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_1_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_2_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_3_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_5_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_6_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_7_hidden']

        for uri in uris:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val
                    }
                )
    return

@receiver(post_save, sender=Value)
def model2(sender, **kwargs):

    instance = kwargs.get("instance", None)

    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_3/Set_0/Set_1/Question_1':

        if instance.option == Option.objects.get(uri='http://example.com/terms/options/MaRDI/yes_no/yes'):
            val = 0
        else:
            val = 1

        uris = ['http://example.com/terms/domain/MaRDI/Section_3a/Set_3_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_5_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_6_hidden',
                'http://example.com/terms/domain/MaRDI/Section_3a/Set_7_hidden']

        for uri in uris:
            attribute_object = Attribute.objects.get(uri=uri)
            obj, created = Value.objects.update_or_create(
                project=instance.project,
                attribute=attribute_object,
                defaults={
                    'project': instance.project,
                    'attribute': attribute_object,
                    'text': val
                    }
                )
    return

@receiver(post_save, sender=Value)
def researchField(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_3/Set_0/Set_0/Question_04':
        if instance.text:
            val = 1
        else:
            val = 0
        attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_3a/Set_0_hidden')
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            defaults={
                'project': instance.project,
                'attribute': attribute_object,
                'text': val
                }
            )
    return

@receiver(post_save, sender=Value)
def researchProblem(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_3/Set_0/Set_0/Question_05':
        if instance.text:
            val = 1
        else:
            val = 0
        attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_3a/Set_1_hidden')
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            defaults={
                'project': instance.project,
                'attribute': attribute_object,
                'text': val
                }
            )
    return

@receiver(post_save, sender=Value)
def model3(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_3/Set_0/Set_0/Question_06':
        if instance.option == Option.objects.get(uri=option['Yes']):
            val = 0
        else:
            val = 1
        attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_3a/Set_2_hidden')
        obj, created = Value.objects.update_or_create(
            project=instance.project,
            attribute=attribute_object,
            defaults={
                'project': instance.project,
                'attribute': attribute_object,
                'text': val
                }
            )
    return

#@receiver(post_save, sender=Value)
#def quantity(sender, **kwargs):
#    instance = kwargs.get("instance", None)
#    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_3/Set_0/Set_0/Question_08':
#        if instance.option == Option.objects.get(uri=option['Yes']):
#            val = 0
#        else:
#            val = 1
#        attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_3a/Set_3_hidden')
#        obj, created = Value.objects.update_or_create(
#            project=instance.project,
#            attribute=attribute_object,
#            defaults={
#                'project': instance.project,
#                'attribute': attribute_object,
#                'text': val
#                }
#            )
#    return

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
            wikidata_author_dicts = kg_req(wikidata_endpoint, query_3.format(' '.join(wikidata_parameter), property_id))

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
            mardi_author_dicts_1 = kg_req(mardi_endpoint, query_3.format(' '.join(mardi_parameter[0]), mardi_property_id))
            mardi_author_dicts_2 = kg_req(mardi_endpoint, query_4.format(' '.join(mardi_parameter[1]), P2))
        
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

@receiver(post_save, sender=Value)
def programmingLanguages(sender, **kwargs):
    instance = kwargs.get("instance", None)
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_4/Set_3/Question_01':
       
        software_id = instance.text.split(' <|> ')[0]
        
        if software_id.split(':')[0] == 'wikidata':
            
            res = kg_req(wikidata_endpoint,wini.format(pl_vars,pl_query.format(software_id.split(':')[-1],'P277'),'100'))
            for idx, r in enumerate(res):
                if r.get('qid',{}).get('value'): 
                    attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_4/Set_3/Question_05')
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
                    attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_4/Set_3/Question_05')
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
    if instance and instance.attribute.uri == 'http://example.com/terms/domain/MaRDI/Section_4/Set_4/Question_03':
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
            
            attribute_object = Attribute.objects.get(uri='http://example.com/terms/domain/MaRDI/Section_4/Set_4/Question_03')
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
    
