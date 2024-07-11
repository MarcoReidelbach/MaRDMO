import re
import requests
import os, json
import time

from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import gettext_lazy as _
from django.template import Template, Context

from rdmo.projects.exports import Export
from rdmo.views.utils import ProjectWrapper
from rdmo.views.templatetags import view_tags
from rdmo.domain.models import Attribute

from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes import ExternalID, Item, String, Time, MonolingualText, Quantity
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.models import Qualifiers

from .para import *
from .config import *
from .citation import *
from .id import *
from .sparql import *
from .handlers import *
from .mathmoddb import *

try:
    # Get login credentials if available 
    from config.settings import lgname, lgpassword
except:
    lgname=''
    lgpassword=''

class MaRDIExport(Export):

    def render(self):
        '''Function that renders User answers to MaRDI template
           (adjusted from csv export)'''
        
### Check if MaRDI Questionaire is used ###########################################################################################################################################################

        if str(self.project.catalog)[-6:] != 'MaRDMO':
            return render(self.request,'MaRDMO/workflowError.html', {
                'error': 'Questionnaire \'{}\' not suitable for MaRDI Export!'.format(str(self.project.catalog).split('/')[-1])
                }, status=200)

### Load MaRDMO Options ##########################################################################################################################################################################

        path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')
        with open(path, "r") as json_file:
            mathmoddb = json.load(json_file)

### Gather all User Answers in Dictionary ########################################################################################################################################################
        
        answers ={}
        for label, info in questions.items():
            answers = self.get_answer(answers,**info)
        
       ###################################################################################################################################################
       ###################################################################################################################################################
       ##                                                                                                                                               ##
       ##                                                                                                                                               ##
       ##    ░█──░█ ░█▀▀▀█ ░█▀▀█ ░█─▄▀ ░█▀▀▀ ░█─── ░█▀▀▀█ ░█──░█ 　 ░█▀▀▄ ░█▀▀▀█ ░█▀▀█ ░█─░█ ░█▀▄▀█ ░█▀▀▀ ░█▄─░█ ▀▀█▀▀ ─█▀▀█ ▀▀█▀▀ ▀█▀ ░█▀▀▀█ ░█▄─░█    ##
       ##    ░█░█░█ ░█──░█ ░█▄▄▀ ░█▀▄─ ░█▀▀▀ ░█─── ░█──░█ ░█░█░█ 　 ░█─░█ ░█──░█ ░█─── ░█─░█ ░█░█░█ ░█▀▀▀ ░█░█░█ ─░█── ░█▄▄█ ─░█── ░█─ ░█──░█ ░█░█░█    ##
       ##    ░█▄▀▄█ ░█▄▄▄█ ░█─░█ ░█─░█ ░█─── ░█▄▄█ ░█▄▄▄█ ░█▄▀▄█ 　 ░█▄▄▀ ░█▄▄▄█ ░█▄▄█ ─▀▄▄▀ ░█──░█ ░█▄▄▄ ░█──▀█ ─░█── ░█─░█ ─░█── ▄█▄ ░█▄▄▄█ ░█──▀█    ##
       ##                                                                                                                                               ##
       ##                                                                                                                                               ##
       ###################################################################################################################################################
       ###################################################################################################################################################

              
        # If Workflow Documentation wanted
        if answers['Settings'].get('Documentation') == option['Documentation']:

### Checks for Workflow Documentation #############################################################################################################################################################

            # Login Credentials for MaRDI Portal Export
            if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                if not (lgname and lgpassword):
                    #Stop if no Login Credentials are provided
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'No permission to write to MaRDI Portal. Check Bot Credentials.'
                        }, status=200)

            # Documentation Type
            if answers['Settings'].get('DocumentationType')  == option['Workflow']:
            
                # Workflow Type (THEO/EXP)
                if answers['Settings'].get('WorkflowType')  not in (option['Computation'], option['Analysis']): 
                    # Stop if no Workflow Type is chosen
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Workflow Type!'
                        }, status=200)

                # Research Objective Provided
                if not answers['GeneralInformation'].get('ResearchObjective'):
                    # Stop if no Research Objective is provided
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Research Objective!'
                        }, status=200)

                # Identical Workflow on MaRDI Portal
                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']: 
                    # Evaluate user-defined Workflow Author Name and ID(s)
                    if not answers['Creator'].get('Name'):
                        # Stop if no Workflow Author Name provided
                        return render(self.request,'MaRDMO/workflowError.html', {
                            'error': 'Missing Name of Workflow Documentation Creator'
                            }, status=200)
                    if answers['Creator'].get('IDs'):
                        # If ID(s) provided, check if they match the author ID(s) on MaRDI Portal. If yes, allow edits.
                        creator_orcid_id = []; creator_zbmath_id = []
                        orcid_creator = []; zbmath_creator = []
                        for user_id in answers['Creator']['IDs'].values():
                            user_id = user_id.split(':')
                            if user_id[0] == 'orcid':
                                creator_orcid_id.append(user_id[1])
                                orcid_creator.extend([[answers['Creator']['Name'].split(',')[1]+' '+answers['Creator']['Name'].split(',')[0],user_id[1]]])
                            elif user_id[0] == 'zbmath':
                                creator_zbmath_id.append(user_id[1])
                                zbmath_creator.extend([[answers['Creator']['Name'].split(',')[1]+' '+answers['Creator']['Name'].split(',')[0], user_id[1]]])
                            else:
                                # Stop if wrong ID type provided for Workflow author
                                return render(self.request,'MaRDMO/workflowError.html', {
                                    'error': 'Identifier of Workflow Documentation Creator not supported'
                                    }, status=200)
                    else:
                        # Stop if no ID(s) provided
                        return render(self.request,'MaRDMO/workflowError.html', {
                            'error': 'Missing Identifier of Workflow Documentation Creator'
                            }, status=200)
                
                    # Check if Workflow with same Label and Description on MaRDI Portal, get workflow author credentials
                    req = self.get_results(mardi_endpoint,
                                           mini.format('?qid ?orcid ?zbmath',mbody2.format(self.project.title.replace("'",r"\'"),
                                                                                           answers['GeneralInformation']['ResearchObjective'].replace("'",r"\'"),
                                                                                           P8,P22,P23),'1'))[0]
                    existing_workflow_qid = None
                    if req.get('qid', {}).get('value'):
                        # Store Workflow QID and Workflow Author  credentials
                        existing_workflow_qid = req['qid']['value']
                        workflow_author_orcid = req.get('orcid', {}).get('value')
                        workflow_author_zbmath = req.get('zbmath', {}).get('value')
                        if answers['Creator']['IDs']:
                            # If ID(s) provided, check if they match the author ID(s) on MaRDI Portal. If yes, allow edits.
                            edit_allowed = True
                            for user_id in answers['Creator']['IDs'].values():
                                user_id = user_id.split(':')
                                if user_id[0] == 'orcid': 
                                    if workflow_author_orcid:
                                        if user_id[1] == workflow_author_orcid:
                                            edit_allowed *= True
                                        else:
                                            edit_allowed *= False
                                elif user_id[0] == 'zbmath': 
                                    if workflow_author_zbmath:
                                        if user_id[1] == workflow_author_zbmath:
                                            edit_allowed *= True
                                        else:
                                            edit_allowed *= False
                                else:
                                    edit_allowed *= False
                        if not edit_allowed:
                            # Stop if Workflow with similar Label and Description on MaRDI Portal and edit is not allowed
                            return render(self.request,'MaRDMO/workflowError.html', {
                                'error': 'Workflow already exists on MaRDI Portal'
                                }, status=200)
                else:
                    creator_orcid_id = ''; orcid_creator = ''
                    creator_zbmath_id = ''; zbmath_creator = ''
 
### If Portal Integration desired, check if Paper already exists on MaRDI Portal or Wikidata  #####################################################################################################

                # If Portal integration wanted, get further publication information
                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                    if answers['Publication']['Exists'][0] == option['YesText']:
                        # Extract Paper DOI
                        doi=re.split(':', answers['Publication']['Exists'][1],1)

                        if doi[0] == 'doi':
                            
                            if not doi[-1]:
                                # Stop if no DOI provided
                                return render(self.request,'MaRDMO/workflowError.html', {
                                    'error': 'Missing DOI of related Publication!'
                                    }, status=200)

                            if not answers['Publication']['Info']:
                                # Stop if no Information available via DOI
                                return render(self.request,'MaRDMO/workflowError.html', {
                                    'error': 'DOI for related Publication returns no Information!'
                                    }, status=200)

                            # Get Publication ID, Label and Description
                            answers['Publication']['Info'] = answers['Publication']['Info'].split(' <|> ')
                
                            if re.match(r"mardi:Q[0-9]+", answers['Publication']['Info'][0]):
                                # If Paper with DOI on MaRDI Portal store QID
                                paper_qid= answers['Publication']['Info'][0].split(':')[1]

                            elif re.match(r"wikidata:Q[0-9]+", answers['Publication']['Info'][0]): 
                                # If Paper with DOI on Wikidata, generate dummy entry  store QID
                                paper_qid = self.find_item(answers['Publication']['Info'][1], answers['Publication']['Info'][2])
                                if not paper_qid:
                                    paper_qid= self.entry(answers['Publication']['Info'][1], answers['Publication']['Info'][2], [(ExternalID, answers['Publication']['Info'][0].split(':')[1], P2)])

                            else:
                        
### Create New Publication Entry ##################################################################################################################################################################
### Prepare User edited Authors  ##################################################################################################################################################################
                        
                                orcid_ids = []
                                orcid_authors = []
                                zbmath_ids = []
                                zbmath_authors = []
                                authors_remove = []
                        
                                # Identify Authors with ID added by User
                                other_authors = list(answers['Publication'].get('All Authors',{}).values())[len(list(answers['Publication'].get('Identified Authors',{}).values())):]
                    
                                for author in other_authors:
                                    try:
                                        author_ids = re.search('\((.*)\)',author).group(1)
                                    except:
                                        author_ids = ''
                            
                                    for author_id in author_ids.split('; '):
                                        if author_id.split(':')[0] == 'orcid':
                                            orcid_ids.append(author_id.split(':')[1])
                                            orcid_authors.append([author.split(' (')[0],author_id.split(':')[1]])
                                            authors_remove.append(author)
                                        elif author_id.split(':')[0] == 'zbmath':
                                            zbmath_ids.append(author_id.split(':')[1])
                                            zbmath_authors.append([author.split(' (')[0],author_id.split(':')[1]])
                                            authors_remove.append(author)
                        
                                # Remove Authors with ID added by User from non-ID Author List
                                for author in authors_remove:
                                    try:
                                        other_authors.remove(author)
                                    except ValueError:
                                        pass
                         
                                author_dict_merged = Author_Search(orcid_ids, zbmath_ids, orcid_authors, zbmath_authors)

                                # Store Publication Authors from Citation via ORCID and zbMath
                                answers['Publication'].setdefault('Identified Authors',{})
                                for idx, (author_id, author_data) in enumerate(author_dict_merged.items()):
                                    if author_data['mardiQID']:
                                        answers['Publication']['Identified Authors'].update({f"n{idx}":f"mardi:{author_data['mardiQID']}"})
                                    elif author_data['wikiQID']:
                                        answers['Publication']['Identified Authors'].update({f"n{idx}":f"wikidata:{author_data['wikiQID']} <|> {author_data['wikiLabel']} <|> {author_data['wikiDescription']}"})
                                    else:
                                        if author_data['orcid']:
                                            orcid_info = f"orcid:{author_data['orcid']}"
                                            if author_data['zbmath']:
                                                orcid_info += f"; zbmath:{author_data['zbmath']}"
                                            answers['Publication']['Identified Authors'].update({f"n{idx}":f"{orcid_info} <|> {author_id} <|> researcher (ORCID {author_data['orcid']})"})
                                        elif author_data['zbmath']:
                                            answers['Publication']['Identified Authors'].update({f"n{idx}":f"zbmath:{author_data['zbmath']} <|> {author_id} <|> researcher (zbMath {author_data['zbmath']})"})

### Add Authors, Language and Journal of Paper to MaRDI Portal #####################################################################################################################################
                        
                                author_qids = self.Entry_Generator_Paper_Supplements(answers['Publication']['Identified Authors'],
                                                                                     [(Item, Q7, P4), (Item, Q8, P21)],
                                                                                     True)
                         
                                language_qids = self.Entry_Generator_Paper_Supplements({'Language':answers['Publication'].get('Language')},
                                                                                       [(Item, Q11, P4)],
                                                                                       False)

                                journal_qids = self.Entry_Generator_Paper_Supplements({'Journal':answers['Publication'].get('Journal')},
                                                                                      [(Item, Q9, P4)],
                                                                                      False)

### Add Paper to  MaRDI Portal ####################################################################################################################################################################
                        
                                paper_qid=self.entry(answers['Publication']['Info'][1], answers['Publication']['Info'][2], 
                                                     [(Item, answers['Publication']['Type'].split(' <|> ')[0].split(':')[1], P4)] +
                                                     [(Item, author, P8) for author in author_qids] +
                                                     [(String, author, P9) for author in other_authors] +
                                                     [(Item, language, P10) for language in language_qids] +
                                                     [(Item, journal, P12) for journal in journal_qids] +
                                                     [(MonolingualText, answers['Publication'].get('Title'), P7),
                                                      (Time, answers['Publication'].get('Date')[:10]+'T00:00:00Z', P11),
                                                      (String, answers['Publication'].get('Volume'), P13),
                                                      (String, answers['Publication'].get('Issue'), P14),
                                                      (String, answers['Publication'].get('Pages'), P15),
                                                      (ExternalID,doi[-1].upper(),P16)])
                        
                        elif doi[0] == 'url':
                            paper_qid = doi[1]

                    else:
                        # No DOI provided
                        paper_qid=''

### Get Information of Workflow Creator and add Information to MaRDI Portal  ######################################################################################################################
            
                creator_dict_merged = Author_Search(creator_orcid_id, creator_zbmath_id, orcid_creator, zbmath_creator)
                       
                creators = {}
                for idx, (author_id, author_data) in enumerate(creator_dict_merged.items()):
                    if author_data['mardiQID']:
                        creators.update({f"{idx}":f"mardi:{author_data['mardiQID']}"})
                    elif author_data['wikiQID']:
                        creators.update({f"{idx}":f"wikidata:{author_data['wikiQID']} <|> {author_data['wikiLabel']} <|> {author_data['wikiDescription']}"})
                    else:
                        if author_data['orcid']:
                            orcid_info = f"orcid:{author_data['orcid']}"
                            if author_data['zbmath']:
                                orcid_info += f"; zbmath:{author_data['zbmath']}"
                            creators.update({f"{idx}":f"{orcid_info} <|> {author_id} <|> researcher (ORCID {author_data['orcid']})"})
                        elif author_data['zbmath']:
                            creators.update({f"{idx}":f"zbmath:{author_data['zbmath']} <|> {author_id} <|> researcher (zbMath {author_data['zbmath']})"})

                creator_qids = self.Entry_Generator_Paper_Supplements(creators,
                                                                     [(Item, Q7, P4), (Item, Q8, P21)],
                                                                     True)

### Refine User Answers via External Data Sources #################################################################################################################################################
                
                answers = self.refine(answers)
                answers = ModelRetriever(answers,mathmoddb) 
                
### Integrate related Model in MaRDI KG ###########################################################################################################################################################
                 
                models, answers, error = self.Entry_Generator('Models',              # Entry of Model
                                                              [True,False,False],   # Generation wanted, QID Generation wanted, String Generation not wanted
                                                              [Q3,P17],             # instance of mathematical model (Q3), main subject (P17)
                                                              answers)              # refined user answers 
                if error[0] == 0:
                    # Stop if no Name and Description provided for new model entry
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Name and/or Description of new Mathematical Model!'
                        }, status=200)

                elif error[0] == 1:
                    #Stop if no main subject provided for new model entry
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Main Subject of new Mathematical Model!'
                        }, status=200)

                # Flag Tasks for Workflows
                for key in answers['SpecificTask'].get('MathModID',{}):
                    Id, label = answers['SpecificTask']['MathModID'][key].split(' <|> ')
                    for key2 in answers['Task']:
                        if Id == answers['Task'][key2].get('MathModID'):
                            answers['Task'][key2].update({'Include':True})

                # Add Symbols to Task Quantities
                for tkey in answers['Task']:
                    if answers['Task'][tkey].get('Include'):
                        for tkey2 in answers['Task'][tkey]['Other2']:
                            tvar = answers['Task'][tkey]['Other2'][tkey2].split(' <|> ')[1].rsplit(' ',1)[0]
                            for mkey in answers['MathematicalFormulation']:
                                for mkey2 in answers['MathematicalFormulation'][mkey]['Element']:
                                    if answers['MathematicalFormulation'][mkey]['Element'][mkey2].get('Info',{}).get('Name'):
                                        mvar = answers['MathematicalFormulation'][mkey]['Element'][mkey2].get('Info',{}).get('Name')
                                    else:
                                        mvar = answers['MathematicalFormulation'][mkey]['Element'][mkey2].get('Info',{}).get('QKName')
                                    if tvar == mvar:
                                        answers['Task'][tkey].setdefault('RelationQ',{}).update({tkey2:[answers['Task'][tkey]['Relation2'][tkey2],tvar,answers['MathematicalFormulation'][mkey]['Element'][mkey2]['Symbol']]})
                 
### Integrate related Methods in MaRDI KG #########################################################################################################################################################

                methods, answers, error = self.Entry_Generator('Method',            # Entry of Method with Main Subject
                                                               [True,True,False],   # Generation wanted, QID Generation wanted, String Generation not wanted
                                                               [Q4,P17],            # instance of method (Q4), main subject (P17)
                                                               answers)             # refined user answers

                if error[0] == 0:
                    # Stop if no Name and Description provided for new method entry
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Name and/or Description of new Mathematical Method in Set {}!'.format(error[1])
                        }, status=200)
            
                elif error[0] == 1:
                    #Stop if no main subject provided for new method entry
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Main Subject of new Mathematical Method in Set {}!'.format(error[1])
                        }, status=200)

                for mkey in answers['Method']:
                    i=0
                    for pkey in answers['ProcessStep']:
                        if answers['ProcessStep'][pkey].get('Method'):
                            for pkey2 in answers['ProcessStep'][pkey]['Method']:
                                if answers['Method'][mkey]['Name'] == answers['ProcessStep'][pkey]['Method'][pkey2]:
                                    answers['Method'][mkey].setdefault('ProcessStep',{}).update({i:answers['ProcessStep'][pkey]['Name']})
                                    i=i+1
            
### Integrate related Softwares in MaRDI KG #######################################################################################################################################################
            
                softwares, answers, error = self.Entry_Generator('Software',        # Entry of Software with Programming Languages 
                                                                 [True,True,True],  # Generation wanted, QID Generation wanted, String Generation wanted
                                                                 [Q5,P19],          # instance of software (Q5), programmed in (P19)
                                                                 answers)           # refined user answers

                if error[0] == 0:
                    # Stop if no Name and Description provided for new software entry
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Name and/or Description of new Software in Set {}!'.format(error[1])
                        }, status=200)
            
                elif error[0] == 1:
                    #Stop if no programming language provided for new software entry
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Programming Language(s) of new Software in Set {}!'.format(error[1])
                        }, status=200)
             
                for skey in answers['Software']:
                    for dkey in answers['ExperimentalDevice']:
                        if answers['ExperimentalDevice'][dkey].get('SubProperty2'):
                            for dkey2 in answers['ExperimentalDevice'][dkey]['SubProperty2']:
                                if answers['Software'][skey]['Name'] == answers['ExperimentalDevice'][dkey]['SubProperty2'][dkey2]['Name'] and answers['Software'][skey]['Description'] == answers['ExperimentalDevice'][dkey]['SubProperty2'][dkey2]['Description']:
                                    answers['ExperimentalDevice'][dkey]['SubProperty2'][dkey2]['ID'] = 'mardi:'+answers['Software'][skey]['mardiId']

### Hardware/Devices #############################################################################################################################################################################

                if answers['Settings']['WorkflowType'] == option['Computation']: 
                
                    # Hardware
                    hardwares, answers, error = self.Entry_Generator('Hardware',                     # Entry of Hardware
                                                                     [True,True,False],              # Generation wanted, QID Generation wanted, String Generation not wanted
                                                                     [Q12,P26,P6,P4,P32,P2,P27,P31], # nothing
                                                                     answers)                        # refined user answers  

                    if error[0] == 0:
                        # Stop if no Name and Description provided for new method entry
                        return render(self.request,'MaRDMO/workflowError.html', {
                            'error': 'Missing Name and/or Description of new Hardware in Set {}!'.format(error[1])
                            }, status=200)
            
                elif answers['Settings']['WorkflowType'] == option['Analysis']:
            
                    # Devices
                    devices, answers, error = self.Entry_Generator('ExperimentalDevice',           # Entry of Hardware
                                                                   [True,True,False],              # Generation wanted, QID Generation wanted, String Generation not wanted
                                                                   [Q13,P28,P6,P29,P30],           # nothing
                                                                   answers)                        # refined user answers  

                    if error[0] == 0:
                        # Stop if no Name and Description provided for new method entry
                        return render(self.request,'MaRDMO/workflowError.html', {
                            'error': 'Missing Name and/or Description of new Hardware in Set {}!'.format(error[1])
                            }, status=200)

### Integrate related Data Sets in MaRDI KG #######################################################################################################################################################
            
                datas, answers, error = self.Entry_Generator('DataSet',            # Entry of Data Set
                                                              [True,False,False],   # Generation wanted, QID Generation not wanted, String Generation not wanted
                                                              [Q6,''],              # instance of data set (Q6)
                                                              answers)              # refined user answers

                if error[0] == 0:
                    # Stop if no Name and Description provided for new input data set
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Name of new Input Data in Set {}!'.format(error[1])
                        }, status=200)
       
                for dkey in answers['DataSet']:
                    for pkey in answers['ProcessStep']:
                        if answers['ProcessStep'][pkey].get('Input'):
                            for pkey2 in answers['ProcessStep'][pkey]['Input']:
                                if answers['DataSet'][dkey]['Name'] == answers['ProcessStep'][pkey]['Input'][pkey2]:
                                    answers['DataSet'][dkey].setdefault('Type',{}).update({0:'Input'})
                        if answers['ProcessStep'][pkey].get('Output'):
                            for pkey2 in answers['ProcessStep'][pkey]['Output']:
                                if answers['DataSet'][dkey]['Name'] == answers['ProcessStep'][pkey]['Output'][pkey2]:
                                    answers['DataSet'][dkey].setdefault('Type',{}).update({1:'Output'})
        
### Integrate related non-mathematical Disciplines in MaRDI KG ####################################################################################################################################
            
                if answers['NonMathematicalDiscipline'].get(0,{}).get('ID'):
                    answers.update({'NonMathematicalDiscipline':answers['NonMathematicalDiscipline'][0]['ID']})
                else:
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Non-Mathematical Disciplines of Workflow!'
                        }, status=200)

                disciplines, answers, error = self.Entry_Generator('NonMathematicalDiscipline',     # Entry of non-mathmatical Disciplines
                                                                   [False,False,False],             # Generation not wanted, QID Generation not wanted, String Generation not wanted
                                                                   ['',''],                         # nothing
                                                                   answers)                         # refined user answers

### Mathematical Fields ###########################################################################################################################################################################
            
                if answers['MathematicalArea'].get(0,{}).get('ID'):
                    answers.update({'MathematicalArea':answers['MathematicalArea'][0]['ID']})
                else:
                    # Stop if no Mathematical Field provided by User
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Mathematical Fields of Workflow!'
                        }, status=200)
            
### Integrate Workflow in MaRDI KG ################################################################################################################################################################

                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']: 
                    # Facts for MaRDI KG Integration
                    facts = [(Item,Q2,P4),(Item,paper_qid,P3) if re.match(r"Q[0-9]+",paper_qid) else (ExternalID,paper_qid,P24)] +\
                            [(Item,discipline,P5) for discipline in disciplines] +\
                            [(ExternalID,field,P25) for field in answers['MathematicalArea'].values()] +\
                            [(Item, creator, P8) for creator in creator_qids] +\
                            [(Item,i,P6) for i in methods+models+softwares+datas]        

                    if answers['Settings']['WorkflowType'] == option['Computation']:

                        # Add Hardware Facts for Computational Workflow
                        facts += [(Item,i,P6,answers['Hardware'][idx]['Qualifiers']) for idx,i in enumerate(hardwares)] 

                    elif answers['Settings']['WorkflowType'] == option['Analysis']:

                        # Add Device Facts for Data Analysis Workflow
                        facts += [(Item,i,P6,answers['ExperimentalDevice'][idx]['Qualifiers']) for idx,i in enumerate(devices)]

                    # If MaRDI KG integration is desired
                    if existing_workflow_qid:
                        wbi = self.wikibase_login()
                        item = wbi.item.get(existing_workflow_qid)
                        for claim in item.claims.claims:
                            item.claims.remove(claim)
                        item.write()
                        wbi = self.wikibase_login()
                        item = wbi.item.get(existing_workflow_qid)       
                        d=[]
                        for fact in facts:
                            if fact[1]:
                                if fact[0] == MonolingualText:
                                    d.append(fact[0](text=fact[1],prop_nr=fact[2]))
                                elif fact[0] == Time:
                                    d.append(fact[0](time=fact[1],prop_nr=fact[2]))
                                else:
                                    if len(fact) == 3:
                                        d.append(fact[0](value=fact[1],prop_nr=fact[2]))
                                    elif len(fact) == 4:
                                        d.append(fact[0](value=fact[1],prop_nr=fact[2],qualifiers=fact[3]))
                        item.claims.add(d)
                        item.write()
                        workflow_qid = item.id
                    else:
                        workflow_qid=self.entry(self.project.title, answers['GeneralInformation']['ResearchObjective'], facts)

### Generate and Publish Workflow Page ############################################################################################################################################################
            
                # Download Workflow Doucmentation as Markdown File
                if answers['Settings']['Public'] == option['Local']:
                
                    # Load MaRDI Markdown Workflow Template
                    path = os.path.join(os.path.dirname(__file__), 'templates', 'MaRDMO', 'workflowTemplate.md')
                    with open(path, 'r') as file:
                        markdown_template = file.read()

                    # Create a Django Template object
                    template = Template(markdown_template)
                    
                    # Render the template with the data
                    context = Context({'title':self.project.title}|answers|option|mathmoddb)
                    markdown_workflow = template.render(context)
                
                    # Provide Documentation as Markdown Download
                    response = HttpResponse(os.linesep.join([s.strip() for s in markdown_workflow.splitlines() if s.strip()]), content_type="application/md")
                    response['Content-Disposition'] = 'filename="workflow.md"'
                
                    return response
            
                # Preview Workflow Documentation as HTML File
                elif answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['Yes']:
                    
                    return render(self.request,'MaRDMO/workflowTemplate.html', {
                        'title': self.project.title,
                        'answers': answers,
                        'option': option|mathmoddb
                        }, status=200)
            
                # Export Workflow Documentation to MaRDI Portal as Mediawiki File
                elif answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:

                    # Load MaRDI Markdown Workflow Template
                    path = os.path.join(os.path.dirname(__file__), 'templates', 'MaRDMO', 'workflowTemplate.mediawiki')
                    with open(path, 'r') as file:
                        mediawiki_template = file.read()

                    # Create a Django Template object
                    template = Template(mediawiki_template)

                    # Render the template with the data
                    context = Context(answers|option|mathmoddb)
                    mediawiki_workflow = template.render(context)

                    # Export to MaRDI Portal
                    self.wikipage_export(self.project.title,os.linesep.join([re.sub(r'\$\$\s?(.*?)\$\$',r'<math>\1</math>',s.strip()) for s in mediawiki_workflow.splitlines() if s.strip()]))

                    # Successful Export to Portal
                    return render(self.request,'MaRDMO/workflowExport.html', {
                        'WikiLink': mardi_wiki+self.project.title.replace(' ','_'),
                        'KGLink': mardi_wiki+'Item:'+workflow_qid
                        }, status=200)
            
                else:
                    # Stop if no Export Type is chosen
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Export Type!'
                        }, status=200)

            elif answers['Settings'].get('DocumentationType')  == option['Documentation'] or answers['Settings'].get('DocumentationType')  == option['Model']:
            
                # Mathematical Model documentation soon be integrated
                answers = self.refine(answers)
               
                # Evaluate user-defined Model Author Name
                if answers['Creator'].get('Name'):
                    Surname, GivenName = answers['Creator']['Name'].split(',')
                    answers['Creator'].update({'Surname':Surname,'GivenName':GivenName})
                else:
                    # Stop if no Workflow Author Name provided
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Name of Model Documentation Creator'
                        }, status=200)
                
                # Evaluate user-defined Model Author ID(s)
                if answers['Creator'].get('IDs'):
                    # Check if IDs provided
                    orcidID = []; zbmathID = []
                    for user_id in answers['Creator']['IDs'].values():
                        user_id = user_id.split(':')
                        if user_id[0] == 'orcid':
                            answers['Creator'].setdefault('orcidID',[]).append(user_id[1])
                        elif user_id[0] == 'zbmath':
                            answers['Creator'].setdefault('zbmathID',[]).append(user_id[1])
                        else:
                            # Stop if wrong ID type provided for Workflow author
                            return render(self.request,'MaRDMO/workflowError.html', {
                                'error': 'Identifier of Model Documentation Creator not supported'
                                }, status=200)
                else:
                    # Stop if no ID(s) provided
                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'Missing Identifier of Model Documentation Creator'
                        }, status=200)

        		# Query MathModDB and order Information
                answers = ModelRetriever(answers,mathmoddb)
        
                # Download Model Doucmentation as Markdown File
                if answers['Settings']['Public'] == option['Local']:

                    # Load MaRDI Markdown Workflow Template
                    path = os.path.join(os.path.dirname(__file__), 'templates', 'MaRDMO', 'modelTemplate.md')
                    with open(path, 'r') as file:
                        markdown_template = file.read()

                    # Create a Django Template object
                    template = Template(markdown_template)

                    # Render the template with the data
                    context = Context({'title':self.project.title}|answers|option|mathmoddb)
                    markdown_workflow = template.render(context)

                    # Provide Documentation as Markdown Download
                    response = HttpResponse(os.linesep.join([s.strip() for s in markdown_workflow.splitlines() if s.strip()]), content_type="application/md")
                    response['Content-Disposition'] = 'filename="model.md"'

                    return response

                # Preview Model Documentation as HTML File
                elif answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['Yes']:

                    return render(self.request,'MaRDMO/modelTemplate.html', {
                        'title': self.project.title,
                        'answers': answers,
                        'option': option|mathmoddb
                        }, status=200)

                # Export Model Documentation to MathModDB as Mediawiki File
                elif answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:

                    return render(self.request,'MaRDMO/workflowError.html', {
                        'error': 'The integration of Mathematical Models into MathModDB will be integrated soon!'
                        }, status=200)
            else:
                # Stop if no Documentation Type chosen
                return render(self.request,'MaRDMO/workflowError.html', {
                    'error': 'Missing Documentation Type!'
                    }, status=200)


       ######################################################################################################
       ######################################################################################################
       ##                                                                                                  ##
       ##                                                                                                  ##
       ##    ▒█░░▒█ ▒█▀▀▀█ ▒█▀▀█ ▒█░▄▀ ▒█▀▀▀ ▒█░░░ ▒█▀▀▀█ ▒█░░▒█ 　 ▒█▀▀▀█ ▒█▀▀▀ ░█▀▀█ ▒█▀▀█ ▒█▀▀█ ▒█░▒█   ##
       ##    ▒█▒█▒█ ▒█░░▒█ ▒█▄▄▀ ▒█▀▄░ ▒█▀▀▀ ▒█░░░ ▒█░░▒█ ▒█▒█▒█ 　 ░▀▀▀▄▄ ▒█▀▀▀ ▒█▄▄█ ▒█▄▄▀ ▒█░░░ ▒█▀▀█   ##
       ##    ▒█▄▀▄█ ▒█▄▄▄█ ▒█░▒█ ▒█░▒█ ▒█░░░ ▒█▄▄█ ▒█▄▄▄█ ▒█▄▀▄█ 　 ▒█▄▄▄█ ▒█▄▄▄ ▒█░▒█ ▒█░▒█ ▒█▄▄█ ▒█░▒█   ##
       ##                                                                                                  ##
       ##                                                                                                  ##
       ######################################################################################################
       ######################################################################################################


        # If Workflow Search wanted
        elif answers['Settings']['Documentation'] == option['Search']:
            
### SPARQL via Research Objectives ################################################################################################################################################################
            
            # SPARQL string definitions
            quote_str = ''
            res_obj_strs = ''

            # If SPARQL query via research objective desired
            if answers['Search'].get('Search Objective') == option['Yes']:
                quote_str = quote_sparql
                # Separate key words for SPARQL query vie research objective
                if answers['Search'].get('Objective Keywords'):
                    for res_obj in answers['Search']['Objective Keywords'].values():
                        # Define Filters for SPARQL queries
                        res_obj_strs+=res_obj_sparql.format(res_obj.lower())

### SPARQL via Research Disciplines ###############################################################################################################################################################

            # SPARQL string definitions
            res_disc_str = ''

            # If SPARQL query via research discipline desired
            if answers['Search'].get('Search Discipline') == option['Yes']:
                # Separate disciplines for SPARQL query via research discipline 
                if answers['Search'].get('Discipline Keywords'):
                    for res_disc in answers['Search']['Discipline Keywords'].values():
                        # Define Filters for SPARQL queries
                        res_disc_str += res_disc_sparql.format(P5, res_disc.split('<|>')[0].split(':')[1])

### SPARQL via Mathematical Models, Methods, Softwares, Input or Output Data Sets #################################################################################################################

            # SPARQL string definitions
            mmsios_str = ''

            # If SPARQL query via Mathematical Models, Methods, Softwares, Input or Output Data Sets
            if answers['Search'].get('Search Entities') == option['Yes']:
                # Separate Mathematical Model, Methods, Software, Input or Output Data Sets
                if answers['Search'].get('Entities Keywords'):
                    for mmsio in answers['Search']['Entities Keywords'].values():
                        # Define Filters for SPARQL queries
                        mmsios_str += mmsio_sparql.format(P6, mmsio.split('<|>')[0].split(':')[1])

### Set up Query, query MaRDI Portal and return Results ###########################################################################################################################################

            # Set up entire SPARQL query
            query = query_base.format(P4,Q2,res_disc_str,mmsios_str,quote_str,res_obj_strs)

            # Query MaRDI Portal
            results = self.get_results(mardi_endpoint, query)

            # Number of Results
            no_results = str(len(results))
            
            # Generate Links to Wikipage and Knowledge Graoh Entry of Results
            links=[]
            for result in results:
                links.append([result["label"]["value"],mardi_wiki+result["label"]["value"].replace(' ','_'),mardi_wiki+'Item:'+result["qid"]["value"]])

            return render(self.request,'MaRDMO/workflowSearch.html', {
                    'noResults': no_results,
                    'links': links
                    }, status=200)
        
        else:
            # Stop if Workflow Documentation or Search not chosen
            return render(self.request,'MaRDMO/workflowError.html', {
                    'error': 'Missing Operation Modus!'
                    }, status=200)
       
    def wikipage_export(self,title,content): 
        '''Genereic Mediawiki Example'''

        S = requests.Session()

        URL = mardi_api

        # Step 1: GET request to fetch login token
        PARAMS_0 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }

        R = S.get(url=URL, params=PARAMS_0)
        DATA = R.json()
        
        LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

        # Step 2: POST request to log in.
        PARAMS_1 = {
            "action": "login",
            "lgname": lgname,
            "lgpassword": lgpassword,
            "lgtoken": LOGIN_TOKEN,
            "format": "json"
        }

        R = S.post(URL, data=PARAMS_1)

        # Step 3: GET request to fetch CSRF token
        PARAMS_2 = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }

        R = S.get(url=URL, params=PARAMS_2)
        DATA = R.json()

        CSRF_TOKEN = DATA['query']['tokens']['csrftoken']

        # Step 4: POST request to edit a page

        post_content=re.sub('<math display="block">','<math>',content)

        PARAMS_3 = {
            "action": "edit",
            "title": title,
            "token": CSRF_TOKEN,
            "format": "json",
            "text": post_content
            }

        R = S.post(URL , data=PARAMS_3, files=dict(foo='bar'))
        return

    def wikibase_login(self):
        '''Login stuff for wikibase'''
        wbi_config['MEDIAWIKI_API_URL'] = mardi_api
    
        #login_instance = wbi_login.OAuth1(consumer_token, consumer_secret, access_token, access_secret)
        login_instance = wbi_login.Login(user=lgname, password=lgpassword)

        wbi = WikibaseIntegrator(login=login_instance)

        return wbi

    def entry(self,label,description,facts):
        '''Takes arbitrary information and generates MaRDI portal entry.'''
        wbi = self.wikibase_login()  
        item = wbi.item.new()
        item.labels.set('en', label)
        item.descriptions.set('en', description)

        data=[]
        for fact in facts:
            if fact[1]:
                if fact[0] == MonolingualText:
                    data.append(fact[0](text=fact[1],prop_nr=fact[2]))
                elif fact[0] == Time:
                    data.append(fact[0](time=fact[1],prop_nr=fact[2]))
                elif fact[0] == Quantity:
                    if len(fact) == 3:
                        data.append(fact[0](fact[1],prop_nr=fact[2]))
                    elif len(fact) == 4:
                        data.append(fact[0](fact[1],prop_nr=fact[2],qualifiers=fact[3]))
                else:
                    if len(fact) == 3:
                        data.append(fact[0](value=fact[1],prop_nr=fact[2]))
                    elif len(fact) == 4:
                        data.append(fact[0](value=fact[1],prop_nr=fact[2],qualifiers=fact[3]))
        item.claims.add(data)
            
        item.write()

        return item.id

    def get_results(self,endpoint_url, query):
        '''Perform SPARQL Queries via Get requests'''
        req=requests.get(endpoint_url, params = {'format': 'json', 'query': query}, headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()
        return req["results"]["bindings"]
    
    def portal_wikidata_check(self,answers,public,preview):
        '''Function checks if an entry is on MaRDI portal and returns its QID
           or on Wikidata and copies the entry to the MaRDI portal and returns
           its QID.'''
        # Store Label and Description
        entry = [answers.get('Name'), answers.get('Description')]
        if answers['ID']:
            # IF ID exists, split in prefix and qnumber
            prefix, qnumber = answers['ID'].split(':')
            if prefix == 'mardi':
                # Store MaRDI QID
                qid = qnumber
            elif prefix == 'wikidata':
                # IF Wikidata QID, check Publication Type
                if public == option['Public'] and preview == option['No']:
                    #Create Entry on MaRDI Portal and store MaRDI QID
                    qid = self.entry(entry[0], entry[1] , [(ExternalID, qnumber, P2)])
                else:
                    qid = 'tbd'
            else:
                qid = None
        else:
            qid = answers['ID']

        return qid, entry

    def Entry_Generator_Paper_Supplements(self, props, relations, add_relations):
        '''This function takes a paper supplement (i.e. authors, languages, journal) and creates the corresponding wikibase entries.'''
        qids = []
        for prop in props.values():
            if prop and prop != 'NONE':
                prop = prop.split(' <|> ')
                if re.match(r"mardi:Q[0-9]+", prop[0]):
                    # If supplement  on MaRDI Portal store QID
                    qids.append(prop[0].split(':')[1])
                elif re.match(r"wikidata:Q[0-9]+", prop[0]):
                    # If supplement on Wikidata check if similar entity exist in MarDI KG and use or create dummy Wikidata entry
                    req = {}
                    try:
                        req = requests.get(mardi_api+'?action=wbsearchentities&format=json&language=en&type=item&limit=10&search={0}'.format(prop[1]),
                                           headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}
                                          ).json()['search'][0]
                    except (KeyError,IndexError):
                        # KeyError: search string is empty
                        # IndexError: no result found for string
                        pass
                    if req:
                        #If supplement with Wikidata Label Description on MaRDI Portal, store QID
                        if req['display']['label']['value'] == prop[1] and req['display']['description']['value'] == prop[2]:
                            qids.append(req['id'])
                        else:
                            qids.append(self.entry(prop[1], prop[2], [(ExternalID, prop[0].split(':')[1], P2)]))
                    else:
                        qids.append(self.entry(prop[1], prop[2], [(ExternalID, prop[0].split(':')[1], P2)]))
                else:
                    # If supplement not on MaRDI KG or Wikidata check if Entity with standard label and description exists and use it or create it
                    req = {}
                    try:
                        req = requests.get(mardi_api+'?action=wbsearchentities&format=json&language=en&type=item&limit=10&search={0}'.format(prop[1]),
                                           headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}
                                          ).json()['search'][0]
                    except (KeyError,IndexError):
                        # KeyError: search string is empty
                        # IndexError: no result found for string
                        pass
                    if add_relations:
                        # For Authors additional relations are required
                        relations += [(ExternalID, p.split(':')[1], P22 if p.split(':')[0] == 'orcid' else P23 if p.split(':')[0] == 'zbmath' else '') for p in prop[0].split('; ')] 
                    if req:
                        #If supplement with Wikidata Label Description on MaRDI Portal, store QID
                        if req['display']['label']['value'] == prop[1] and req['display']['description']['value'] == prop[2]:
                            qids.append(req['id'])
                        else:
                            qids.append(self.entry(prop[1], prop[2], relations))
                    else:
                        qids.append(self.entry(prop[1], prop[2], relations))
        return qids

    def refine(self,answers):
        '''This function takes user answers and performs SPARQL queries to MaRDI portal.'''
        
        entities = ['NonMathematicalDiscipline','Models','Software','DataSet','Method','Hardware','ExperimentalDevice','ResearchField',
                    'ResearchProblem','AdditionalModel','MathematicalFormulation','Quantity','Task','PublicationModel']

        for entity in entities:
            for key in answers[entity]:
                # Refining IDs, Names and Descriptions of entities
                if answers[entity][key].get('ID') and answers[entity][key].get('ID') != 'not in MathModDB':
                    if type(answers[entity][key]['ID']) == str:
                        ID, Name, Description = answers[entity][key]['ID'].split(' <|> ')
                        if re.match(r"mardi:Q[0-9]+", ID): 
                            answers[entity][key].update({'ID':ID, 'Name':Name, 'Description':Description})
                        else:
                            mardiID = self.find_item(Name,Description)
                            if mardiID:
                                answers[entity][key].update({'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description})
                            else:
                                answers[entity][key].update({'ID':ID, 'Name':Name, 'Description':Description})
                    else:
                        for ikey in answers[entity][key]['ID']:
                            ID, Name, Description = answers[entity][key]['ID'][ikey].split(' <|> ')
                            if re.match(r"mardi:Q[0-9]+", ID):
                                answers[entity][key]['ID'].update({ikey:{'ID':ID, 'Name':Name, 'Description':Description}})
                            else:
                                mardiID = self.find_item(Name,Description)
                                if mardiID:
                                    answers[entity][key]['ID'].update({ikey:{'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description}})
                                else:
                                    answers[entity][key]['ID'].update({ikey:{'ID':ID, 'Name':Name, 'Description':Description}})
                else:
                    if answers[entity][key].get('Name') and answers[entity][key].get('Description'):
                        mardiID = self.find_item(answers[entity][key]['Name'],answers[entity][key]['Description'])
                        if mardiID:
                            answers[entity][key].update({'ID':f"mardi:{mardiID}"})
                        else:
                            answers[entity][key].update({'ID':None})
                    else:
                        answers[entity][key].update({'ID':None})
                # Refining Subproperties of entities
                if answers[entity][key].get('SubProperty'):
                    for ikey in answers[entity][key]['SubProperty']:
                        ID, Name, Description = answers[entity][key]['SubProperty'][ikey].split(' <|> ')
                        if re.match(r"mardi:Q[0-9]+", ID):
                            answers[entity][key]['SubProperty'].update({ikey:{'ID':ID, 'Name':Name, 'Description':Description}})
                        else:
                            mardiID = self.find_item(Name,Description)
                            if mardiID:
                                answers[entity][key]['SubProperty'].update({ikey:{'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description}})
                            else:
                                answers[entity][key]['SubProperty'].update({ikey:{'ID':ID, 'Name':Name, 'Description':Description}})
                if answers[entity][key].get('SubProperty2'):
                    for ikey in answers[entity][key]['SubProperty2']:
                        ID, Name, Description = answers[entity][key]['SubProperty2'][ikey].split(' <|> ')
                        if re.match(r"mardi:Q[0-9]+", ID):
                            answers[entity][key]['SubProperty2'].update({ikey:{'ID':ID, 'Name':Name, 'Description':Description}})
                        else:
                            mardiID = self.find_item(Name,Description)
                            if mardiID:
                                answers[entity][key]['SubProperty2'].update({ikey:{'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description}})
                            else:
                                answers[entity][key]['SubProperty2'].update({ikey:{'ID':ID, 'Name':Name, 'Description':Description}})
                if answers[entity][key].get('MathModID'):
                    if type(answers[entity][key]['MathModID']) == str:
                        if answers[entity][key]['MathModID'] != 'not in MathModDB':
                            ID, Name = answers[entity][key]['MathModID'].split(' <|> ')
                            answers[entity][key].update({'MathModID':ID,'Name':Name})
                    else:
                        for ikey in answers[entity][key]['MathModID']:
                            ID, Name = answers[entity][key]['MathModID'][ikey].split(' <|> ')
                            answers[entity].setdefault('MathModID',{}).update({ikey:{'MathModID':ID, 'Name':Name}})
        return answers

    def Entry_Generator(self,Type,Generate,Relations,answers):
        '''Function queries Wikidata/MaRDI KG, uses and generates entries in MaRDI Knowledge Graph.'''
        
        qids=[]
        for key in answers[Type].keys():
            # Check if on Portal or in Wikidata, integrate Wikidata entry if desired
            qid, entry = self.portal_wikidata_check(answers[Type][key], answers['Settings']['Public'], answers['Settings']['Preview'])        
            # Update User answers
            if qid: 
                qids.append(qid)
                answers[Type][key].update({'mardiId': qid, 'uri': f"{mardi_wiki}Item:{qid}"})
            
            if Generate[0]:
                # Stop if no label and quote is provided for entry to generate
                if not (qid or entry[0] and entry[1]):
                    return qids, answers, [0,key]
    
                # Get subproperty of 'new' entity
                subqids = []
                subqids2 = []
 
                if Generate[1]:
                    
                    # Define Qualifier for Entries
                    answers[Type][key].update({'Qualifiers':Qualifiers()})

                    if Type == 'ExperimentalDevice' and answers['Settings']['WorkflowType'] == option['Analysis']:

                        if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                            # Add Version as qualifier of 'uses' statement
                            if answers[Type][key].get('Version'):
                                answers[Type][key]['Qualifiers'].add(String(prop_nr=Relations[3], value=answers[Type][key].get('Version')))
                            # Add Serial Number as qualifier of 'uses' statement
                            if answers[Type][key].get('SerialNumber'):
                                answers[Type][key]['Qualifiers'].add(String(prop_nr=Relations[4], value=answers[Type][key].get('SerialNumber')))
                        
                        # Search and add Location as qualifier of 'uses' statement 
                        for subkey in answers[Type][key].get('SubProperty', {}).keys():
                            if answers[Type][key]['SubProperty'][subkey]: 
                                location, _ = self.portal_wikidata_check(answers[Type][key]['SubProperty'][subkey], answers['Settings']['Public'], answers['Settings']['Preview'])
                                answers[Type][key]['SubProperty'][subkey].update({'mardiId': location, 'uri': f"{mardi_wiki}Item:{location}"})
                                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                                    answers[Type][key]['Qualifiers'].add(Item(prop_nr=Relations[1], value=location))
                        
                        # Search and add available Software as qualifier of 'uses' statement
                        for subkey in answers[Type][key].get('SubProperty2', {}).keys():
                            if answers[Type][key]['SubProperty2'][subkey]:
                                availSoftware, _ = self.portal_wikidata_check(answers[Type][key]['SubProperty2'][subkey], answers['Settings']['Public'], answers['Settings']['Preview'])
                                answers[Type][key]['SubProperty2'][subkey].update({'mardiId': availSoftware, 'uri': f"{mardi_wiki}Item:{availSoftware}"})
                                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                                    answers[Type][key]['Qualifiers'].add(Item(prop_nr=Relations[2], value=availSoftware))
                    
                    elif Type == 'Hardware' and answers['Settings']['WorkflowType'] == option['Computation']:
                        
                        # Search and add CPU, with number of cores and ID (wikidata / wikichip)
                        cpuIDs=[]
                        for subkey in answers[Type][key].get('SubProperty', {}).keys():
                            cpuID = self.find_item(answers[Type][key]['SubProperty'][subkey]['Name'],answers[Type][key]['SubProperty'][subkey]['Description'])
                            if not cpuID:
                                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                                    cpuID = self.entry(
                                                answers[Type][key]['SubProperty'][subkey]['Name'],answers[Type][key]['SubProperty'][subkey]['Description'],
                                                [(Item,Relations[0],Relations[3]),(Quantity,answers['Hardware'][key].get('Core') if answers['Hardware'][key].get('Core') else '1',Relations[4])]+
                                                [(ExternalID,answers[Type][key]['SubProperty'][subkey]['ID'].split(':')[-1],Relations[5] if 'wikidata' in answers[Type][key]['SubProperty'][subkey]['ID'] else Relations[6])]
                                                )
                                else:
                                    cpuID = 'tbd'
                            answers[Type][key]['SubProperty'][subkey].update({'mardiId': cpuID, 'uri': f"{mardi_wiki}Item:{cpuID}"})
                            cpuIDs.append(cpuID)

                        # Search and add Compilers as qualifiers of 'uses' statement
                        for subkey in answers[Type][key].get('SubProperty2', {}).keys():
                            if answers[Type][key]['SubProperty2'][subkey]:
                                compiler, _ = self.portal_wikidata_check(answers[Type][key]['SubProperty2'][subkey], answers['Settings']['Public'], answers['Settings']['Preview'])
                                answers[Type][key]['SubProperty2'][subkey].update({'mardiId': compiler, 'uri': f"{mardi_wiki}Item:{compiler}"})
                                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                                    answers[Type][key]['Qualifiers'].add(Item(prop_nr=Relations[2], value=compiler))

                    else:
                        for subkey in answers[Type][key].get('SubProperty', {}).keys():
                            # Check if subproperty on Portal or in Wikidata (store QID and string)
                            if answers[Type][key]['SubProperty'][subkey]: 
                                subqid, subentry = self.portal_wikidata_check(answers[Type][key]['SubProperty'][subkey], answers['Settings']['Public'], answers['Settings']['Preview'])
                                answers[Type][key]['SubProperty'][subkey].update({'mardiId': subqid, 'uri': f"{mardi_wiki}Item:{subqid}"})
                                subqids.append(subqid)
                                if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                                     answers[Type][key]['Qualifiers'].add(Item(prop_nr=Relations[1], value=subqid))

                        for subkey in answers[Type][key].get('SubProperty2', {}).keys():
                            # Check if subproperty2 on Portal or in Wikidata (store QID and string)
                            if answers[Type][key]['SubProperty2'][subkey]:
                                subqid2, subentry = self.portal_wikidata_check(answers[Type][key]['SubProperty2'][subkey], answers['Settings']['Public'], answers['Settings']['Preview'])
                                answers[Type][key]['SubProperty2'][subkey].update({'mardiId': subqid2, 'uri': f"{mardi_wiki}Item:{subqid2}"})
                                subqids2.append(subqid2)

                        # Stop if entry has no QID and its subproperty has no QID    
                        if not (qid or subqids):
                            return qids, answers, [1,key]
    
                # Generate Entry QID
                if not qid:
                    # If desired generate Entry in MaRDI KG and update User answers
                    if answers['Settings']['Public'] == option['Public'] and answers['Settings']['Preview'] == option['No']:
                        if Type == 'Hardware':
                            qids.append(self.entry(
                                entry[0],entry[1],
                                [(Item,Relations[0],Relations[3])] +
                                [(Item,cpuID,Relations[1],Qualifiers().add(Quantity(answers['Hardware'][key].get('Node') if answers['Hardware'][key].get('Node') else '1',prop_nr=Relations[7]))) for cpuID in cpuIDs]))
                        elif Type == 'ExperimentalDevice':
                            qids.append(self.entry(
                                entry[0],entry[1],
                                [(Item,Relations[0],P4)]))
                        else:
                            qids.append(self.entry(entry[0],entry[1], 
                                                   [(Item,Relations[0],P4)]+
                                                   [(ExternalID,answers[Type][key].get('MathModID','') if answers[Type][key].get('MathModID','') != 'not in MathModDB' else '',P24)]+
                                                   [(Item,subqid,Relations[1]) for subqid in subqids]+
                                                   [(Item,subqid2,Relations[2]) for subqid2 in subqids2]+ 
                                                   [(String,re.sub("\$","",form.lstrip()),P18) for form in answers[Type][key].get('Formular',{}).values()]+
                                                   [(ExternalID,answers[Type][key].get('Reference','').split(':')[-1],
                                                     P16 if answers[Type][key].get('Reference','').split(':')[0] == 'doi' else P20 if answers[Type][key].get('Reference','').split(':')[0] == 'sw' else P24 if answers[Type][key].get('Reference','').split(':')[0] == 'url' else '')]))
                        answers[Type][key].update({'mardiId': qids[-1], 'uri': f"{mardi_wiki}Item:{qids[-1]}"})
                    else:
                        answers[Type][key].update({'mardiId': 'tbd', 'uri': f"{mardi_wiki}Item:{qid}"})
            else:
                if not qid:
                    return qids, answers, [2,key]

        return qids, answers, [-1,-1]
            
    def find_item(self, label, description, api=mardi_api, language="en"):
        # Perform label-based search
        response = requests.get(api, params={
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'type': 'item',
            'limit': 10,
            'search': label
        }, headers={'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'})
        data = response.json()
        # Filter results based on description
        matched_items = [item for item in data['search'] if item.get('description') == description] 
        if matched_items:
            # Return the ID of the first matching item
            return matched_items[0]['id']
        else:
            # No matching item found
            return None

    def get_answer(self, val, uName, dName, Id, set_prefix=False, set_index=False, collection_index=False, option_text=False, external_id=False):
        '''Function that retrieves individual User answers'''
        val.setdefault(uName, {})
        try:
            values = self.project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=Id))
        except:
            values = []
        for value in values:
            if value.option:
                if option_text:
                    if set_prefix:
                        if set_index:
                            if collection_index:
                                if external_id:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.text]})
                            else:
                                if external_id:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).update({dName:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).update({dName:[value.option_uri, value.text]})
                        else:
                            if collection_index:
                                if external_id:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.text]})
                            else:
                                if external_id:
                                    val[uName].setdefault(int(value.set_prefix), {}).update({dName:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(int(value.set_prefix), {}).update({dName:[value.option_uri, value.text]})
                    else:
                        if set_index:
                            if collection_index:
                                if external_id:
                                    val[uName].setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.text]})
                            else:
                                if external_id:
                                    val[uName].setdefault(value.set_index, {}).update({dName:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(value.set_index, {}).update({dName:[value.option_uri, value.text]})
                        else:
                            if collection_index:
                                if external_id:
                                    val[uName].setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].setdefault(dName, {}).update({value.collection_index:[value.option_uri, value.text]})
                            else:
                                if external_id:
                                    val[uName].update({dName:[value.option_uri, value.external_id]})
                                else:
                                    val[uName].update({dName:[value.option_uri, value.text]})
                else:
                    if set_prefix:
                        if set_index:
                            if collection_index:
                                if len(value.set_prefix.split('|')) == 1:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.option_uri})
                                elif len(value.set_prefix.split('|')) == 2:
                                    prefix = value.set_prefix.split('|')
                                    val[uName].setdefault(int(prefix[0]), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.option_uri})
                            else:
                                if len(value.set_prefix.split('|')) == 1:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.set_index:value.option_uri})
                                elif len(value.set_prefix.split('|')) == 2:
                                    prefix = value.set_prefix.split('|')
                                    val[uName].setdefault(int(prefix[0]), {}).setdefault(dName, {}).update({value.set_index:value.option_uri})
                        else:
                            if collection_index:
                                val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.collection_index:value.option_uri})
                            else:
                                val[uName].setdefault(int(value.set_prefix), {}).update({dName:value.option_uri})
                    else:
                        if set_index:
                            if collection_index:
                                val[uName].setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.option_uri})
                            else:
                                val[uName].setdefault(value.set_index, {}).update({dName:value.option_uri})
                        else:
                            if collection_index:
                                val[uName].setdefault(dName, {}).update({value.collection_index:value.option_uri})
                            else:
                                val[uName].update({dName:value.option_uri})
            elif value.text and value.text != 'NONE':
                if set_prefix:
                    if set_index:
                        if collection_index:
                            if external_id:
                                val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.external_id})
                            else:
                                val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.text})
                        else:
                            if external_id:
                                if len(value.set_prefix.split('|')) == 1:
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.set_index:value.external_id})
                                elif len(value.set_prefix.split('|')) == 2:
                                    prefix = value.set_prefix.split('|')
                                    if 'Element' in dName:
                                        val[uName].setdefault(int(prefix[0]), {}).setdefault(dName.split(' ')[0], {}).setdefault(value.set_index, {}).update({dName.split(' ')[1]:value.external_id})
                                    else: 
                                        val[uName].setdefault(int(prefix[0]), {}).setdefault(dName, {}).update({value.set_index:value.external_id})
                            else:
                                if len(value.set_prefix.split('|')) == 1: 
                                    val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.set_index:value.text})
                                elif len(value.set_prefix.split('|')) == 2:
                                    prefix = value.set_prefix.split('|')
                                    val[uName].setdefault(int(prefix[0]), {}).setdefault(dName.split(' ')[0], {}).setdefault(value.set_index, {}).update({dName.split(' ')[1]:value.text})
                    else:
                        if collection_index:
                            if external_id:
                                val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.collection_index:value.external_id})
                            else:
                                val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.collection_index:value.text})
                        else:
                            if external_id:
                                val[uName].setdefault(int(value.set_prefix), {}).update({dName:value.external_id})
                            else:
                                val[uName].setdefault(int(value.set_prefix), {}).update({dName:value.text})
                else:
                    if set_index:
                        if collection_index:
                            if external_id:
                                val[uName].setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.external_id})
                            else:
                                val[uName].setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:value.text})
                        else:
                            if external_id:
                                val[uName].setdefault(value.set_index, {}).update({dName:value.external_id})
                            else:
                                val[uName].setdefault(value.set_index, {}).update({dName:value.text})
                    else:
                        if collection_index:
                            if external_id:
                                val[uName].setdefault(dName, {}).update({value.collection_index:value.external_id})
                            else:
                                val[uName].setdefault(dName, {}).update({value.collection_index:value.text})
                        else:
                            if external_id:
                                val[uName].update({dName:value.external_id})
                            else:
                                val[uName].update({dName:value.text})
            elif value.set_index:
                if set_prefix:
                    if set_index:
                        if collection_index:
                            val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:None})
                        else:
                            val[uName].setdefault(int(value.set_prefix), {}).setdefault(value.set_index, {}).update({dName:None})
                    else:
                        if collection_index:
                            val[uName].setdefault(int(value.set_prefix), {}).setdefault(dName, {}).update({value.collection_index:None})
                        else:
                            val[uName].setdefault(int(value.set_prefix), {}).update({dName:None})
                else:
                    if set_index:
                        if collection_index:
                            val[uName].setdefault(value.set_index, {}).setdefault(dName, {}).update({value.collection_index:None})
                        else:
                            val[uName].setdefault(value.set_index, {}).update({dName:None})
                    else:
                        if collection_index:
                            val[uName].setdefault(dName, {}).update({value.collection_index:None})
                        else:
                            val[uName].update({dName:None})
        return val

