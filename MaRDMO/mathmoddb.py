import requests

from django.shortcuts import render

from .sparql import *
from .para import *

def ModelRetriever(answers,mathmoddb):
    '''Function queries MathModDB to gather further Model Information
       and connects them with Information provided by the User'''
    print(answers['Models'])
    # Add Research Problem to Model
    for idx,key in enumerate(answers['ResearchProblem']):
        if answers['ResearchProblem'][key].get('MathModID') and answers['ResearchProblem'][key].get('MathModID') != 'not in MathModDB':
            answers['Models'][0].setdefault('RelationRP1',{}).update({idx:'RP'+str(idx+1)})
        elif answers['ResearchProblem'][key].get('Models') == option['Yes']:
            answers['Models'][0].setdefault('RelationRP1',{}).update({idx:'RP'+str(idx+1)})

    # Combine Model and additional Models
    if answers.get('AdditionalModel'):
        answers['Models'][max(answers['AdditionalModel'].keys())+1] = answers['Models'].pop(list(answers['Models'].keys())[0])
        answers.update({'AllModels':answers['Models']|answers['AdditionalModel']})
    else:
        answers.update({'AllModels':answers['Models']})
    print(answers['Models'])
    # Flag Tasks wanted by User in Workflow Documentation
    for key in answers['Task']:
        answers['Task'][key].update({'Include':True})

    # Get additional Model Information (additional Models)
    
    keys = list(answers['AllModels'])
    
    for key in keys:
        if answers['AllModels'][key].get('MathModID') and answers['AllModels'][key]['MathModID'] != 'not in MathModDB':
    
            req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_mm.format(answers['AllModels'][key]['MathModID'].split('#')[1])},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
         
            req2=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_mm2.format(answers['AllModels'][key]['MathModID'].split('#')[1])},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']

            for r in req:

                # Evaluate Comment of Mathematical Model
                if r.get('quote', {}).get('value'):
                    answers['AllModels'][key].update({'Description':r['quote']['value']})
                
                # Evaluate Data Properties of Mathematical Model
                for prop, mapping in dataProp_mapping.items():
                    if r.get(prop, {}):
                        if r[prop]['value'] == 'true':
                            answers['AllModels'][key].setdefault('Properties',{}).update({mapping[0]:mathmoddb[mapping[1]]})
                        else:
                            answers['AllModels'][key].setdefault('Properties',{}).update({mapping[2]:mathmoddb[mapping[3]]})
                    elif len(mapping) == 6:
                        answers['AllModels'][key].setdefault('Properties',{}).update({mapping[4]:mathmoddb[mapping[5]]})
                
                # Evaluate Research Problem(s) of Mathematical Model 
                if r.get('P', {}).get('value') and r.get('PL', {}).get('value'):
                    for idx, (Id, label) in enumerate(zip(r['P']['value'].split(' <|> '),r['PL']['value'].split(' <|> '))):
                        if f"{Id} <|> {label}" not in answers['AllModels'][key].setdefault('ResearchProblem',{}).values():
                            answers['AllModels'][key].setdefault('ResearchProblem',{}).update({f"pp{idx}":f"{Id} <|> {label}"})
                        for key2 in answers['ResearchProblem']:
                            if Id == answers['ResearchProblem'][key2].get('MathModID'):
                                break
                        else:
                            if answers['ResearchProblem'].keys():
                                new_key = max(answers['ResearchProblem'].keys())+1
                            else:
                                new_key = 0
                        answers['ResearchProblem'].setdefault(new_key,{})['MathModID'] = Id

                # Evaluate Task(s) of Mathematical Model
                if r.get('TA', {}).get('value') and r.get('TAL', {}).get('value'):
                    for idx, (Id, label, quote) in enumerate(zip(r['TA']['value'].split(' <|> '),r['TAL']['value'].split(' <|> '),r['TAQ']['value'].split(' <|> '))):
                        for key2 in answers['Task']:
                            if Id == answers['Task'][key2].get('MathModID'):
                                if f"{answers['AllModels'][key]['MathModID']} <|> {answers['AllModels'][key]['Name']}" not in answers['Task'][key2].setdefault('Model',{}).values():
                                    if answers['Task'][key2]['Model'].keys():
                                        new_key2 = max(answers['Task'][key2]['Model'].keys())+1
                                    else:
                                        new_key2 = 0
                                    answers['Task'][key2]['Model'].update({new_key2:f"{answers['AllModels'][key]['MathModID']} <|> {answers['AllModels'][key]['Name']}"}) 
                                break
                        else:
                            if answers['Task'].keys():
                                new_key = max(answers['Task'].keys())+1
                            else:
                                new_key = 0
                            answers['Task'].setdefault(new_key,{}).update({'MathModID':Id,'Name':label,'Description':quote})
                            answers['Task'][new_key].setdefault('Model',{}).update({idx:f"{answers['AllModels'][key]['MathModID']} <|> {answers['AllModels'][key]['Name']}"})
                 
                # Evaluate Mathematical Model(s) contained in Mathematical Model
                if r.get('CMM', {}).get('value') and r.get('CMML', {}).get('value'):
                    for idx, (Id, label) in enumerate(zip(r['CMM']['value'].split(' <|> '),r['CMML']['value'].split(' <|> '))):
                        answers['AllModels'][key].setdefault('Relation1', {}).update({f'mm{idx}': mathmoddb['ContainsModel']})
                        answers['AllModels'][key].setdefault('Other1', {}).update({f'mm{idx}': f'{Id} <|> {label}'})
                        answers['AllModels'].setdefault(max(answers['AllModels'].keys())+1, {}).update({'MathModID': Id, 'Name': label})
                        keys.append(max(answers['AllModels'].keys()))
                   
                # Evaluate Object Properties of Mathematical Model
                for prop, mapping in objectProp_mapping.items():
                    if r.get(mapping[0], {}).get('value') and r.get(mapping[1], {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r[mapping[0]]['value'].split(' <|> '),r[mapping[1]]['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation1', {}).update({f'{mapping[0]}{idx}': mathmoddb[prop]})
                                    math_form.setdefault('Other1', {}).update({f'{mapping[0]}{idx}': f"{answers['AllModels'][key]['MathModID']} <|> {answers['AllModels'][key]['Name']}"})
                                    break
                            else:
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation1', {}).update({f'{mapping[0]}{idx}': mathmoddb[prop]})
                                new_form.setdefault('Other1', {}).update({f'{mapping[0]}{idx}': f"{answers['AllModels'][key]['MathModID']} <|> {answers['AllModels'][key]['Name']}"})

            objectProp_mapping2 = {
                                   'GeneralizedBy': ('gb', 'GBMODEL', 'GBMLabel'),
                                   'Generalizes': ('g', 'GMODEL', 'GMLabel'),
                                   'ApproximatedBy': ('ab', 'ABMODEL', 'ABMLabel'),
                                   'Approximates': ('a', 'AMODEL', 'AMLabel'),
                                   'DiscretizedBy': ('db', 'DBMODEL', 'DBMLabel'),
                                   'Discretizes': ('d', 'DMODEL', 'DMLabel'),
                                   'LinearizedBy': ('lb', 'LBMODEL', 'LBMLabel'),
                                   'Linearizes': ('l', 'LMODEL', 'LMLabel'),
                                   'SimilarTo': ('s', 'SMODEL', 'SMLabel')
                                  }

            for r in req2:
    
                # Evaluate Object Properties of Mathematical Model
                for prop, mapping in objectProp_mapping2.items():
                    if r.get(mapping[1], {}).get('value') and r.get(mapping[2], {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r[mapping[1]]['value'].split(' <|> '),r[mapping[2]]['value'].split(' <|> '))):
                            answers['AllModels'][key].setdefault('Relation1',{}).update({f'{mapping[0]}{idx}':mathmoddb[prop]})
                            answers['AllModels'][key].setdefault('Other1',{}).update({f'{mapping[0]}{idx}':f'{Id} <|> {label}'})
                         
    # Get additional Task Information
    
    search_string = ''
    
    for key in answers['Task']:
        if answers['Task'][key].get('MathModID') and answers['Task'][key]['MathModID'] != 'not in MathModDB':
    
            search_string = search_string + f' :{answers["Task"][key]["MathModID"].split("#")[1]}'
    
    req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                    params = {'format': 'json', 'query': query_ta.format(search_string)},
                    headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']

    req2=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                    params = {'format': 'json', 'query': query_ta2.format(search_string)},
                    headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
    
    if req:
        for r in req:
            for key in answers['Task']:
                if r.get('t', {}).get('value') == answers['Task'][key].get('MathModID'):
    
                    if r.get('quote', {}).get('value'):
                        answers['Task'][key].update({'Description':r['quote']['value']})
                    
                    if r.get('linear', {}):
                        if r['linear']['value'] == 'true':
                            answers['Task'][key].setdefault('Properties', {}).update({0:mathmoddb['IsLinear']})
                        else:
                            answers['Task'][key].setdefault('Properties', {}).update({1:mathmoddb['IsNotLinear']})
                    
                    if r.get('P', {}).get('value') and r.get('PL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['P']['value'].split(' <|> '),r['PL']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('ResearchProblem',{}).update({'p'+str(idx):Id + ' <|> ' + label})
                    if r.get('subclass', {}).get('value'):
                        answers['Task'][key].setdefault('TaskClass',{}).update({0:mathmoddb[r['subclass']['value'].split('#')[-1]]})
                    
                    if r.get('F', {}).get('value') and r.get('FL', {}).get('value'):
                
                        for idx, (Id, label) in enumerate(zip(r['F']['value'].split(' <|> '),r['FL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'f{idx}': mathmoddb['ContainedAsFormulationIn']})
                                    math_form.setdefault('Other4', {}).update({f'f{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1 
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'f{idx}': mathmoddb['ContainedAsFormulationIn']})
                                new_form.setdefault('Other4', {}).update({f'f{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                
                    if r.get('A', {}).get('value') and r.get('AL', {}).get('value'):
                    
                        for idx, (Id, label) in enumerate(zip(r['A']['value'].split(' <|> '),r['AL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'a{idx}': mathmoddb['ContainedAsAssumptionIn']})
                                    math_form.setdefault('Other4', {}).update({f'a{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1 
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'a{idx}': mathmoddb['ContainedAsAssumptionIn']})
                                new_form.setdefault('Other4', {}).update({f'a{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                    if r.get('BC', {}).get('value') and r.get('BCL', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['BC']['value'].split(' <|> '),r['BCL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'bc{idx}': mathmoddb['ContainedBoundaryConditionIn']})
                                    math_form.setdefault('Other4', {}).update({f'bc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1 
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'bc{idx}': mathmoddb['ContainedAsBoundaryConditionIn']})
                                new_form.setdefault('Other4', {}).update({f'bc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                    if r.get('CC', {}).get('value') and r.get('CCL', {}).get('value'):
                
                        for idx, (Id, label) in enumerate(zip(r['CC']['value'].split(' <|> '),r['CCL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'cc{idx}': mathmoddb['ContainedAsConstraintConditionIn']})
                                    math_form.setdefault('Other4', {}).update({f'cc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1 
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'cc{idx}': mathmoddb['ContainedAsConstraintConditionIn']})
                                new_form.setdefault('Other4', {}).update({f'cc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                    
                    if r.get('CPC', {}).get('value') and r.get('CPCL', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['CPC']['value'].split(' <|> '),r['CPCL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'cpc{idx}': mathmoddb['ContainedAsCouplingConditionIn']})
                                    math_form.setdefault('Other4', {}).update({f'cpc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'cpc{idx}': mathmoddb['ContainedAsCouplingConditionIn']})
                                new_form.setdefault('Other4', {}).update({f'cpc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                    if r.get('IC', {}).get('value') and r.get('ICL', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['IC']['value'].split(' <|> '),r['ICL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'ic{idx}': mathmoddb['ContainedAsInitialConditionIn']})
                                    math_form.setdefault('Other4', {}).update({f'ic{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1 
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'ic{idx}': mathmoddb['ContainedAsInitialConditionIn']})
                                new_form.setdefault('Other4', {}).update({f'ic{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                    if r.get('FC', {}).get('value') and r.get('FCL', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['FC']['value'].split(' <|> '),r['FCL']['value'].split(' <|> '))):
                            for k, math_form in answers['MathematicalFormulation'].items():
                                if math_form.get('MathModID') == Id:
                                    math_form.setdefault('Relation4', {}).update({f'fc{idx}': mathmoddb['ContainedAsFinalConditionIn']})
                                    math_form.setdefault('Other4', {}).update({f'fc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                    break
                            else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                if answers['MathematicalFormulation'].keys():
                                    new_key = max(answers['MathematicalFormulation'].keys())+1 
                                else:
                                    new_key = 0
                                answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                new_form = answers['MathematicalFormulation'][new_key]
                                new_form.setdefault('Relation4', {}).update({f'fc{idx}': mathmoddb['ContainedAsFinalConditionIn']})
                                new_form.setdefault('Other4', {}).update({f'fc{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                    if r.get('IN', {}).get('value') and r.get('INL', {}).get('value') and r.get('INC', {}).get('value'):
                        
                        seen = set()
                        
                        for idx, (Id, label, Class) in enumerate(zip(r['IN']['value'].split(' <|> '),r['INL']['value'].split(' <|> '),r['INC']['value'].split(' <|> '))):
                            
                            if (Id, label, Class) not in seen:

                                if Class.split('#')[-1] == 'MathematicalFormulation': 
                                                 
                                    for k, math_form in answers['MathematicalFormulation'].items():
                                        if math_form.get('MathModID') == Id:
                                            math_form.setdefault('Relation4', {}).update({f'in{idx}': mathmoddb['ContainedAsInputIn']})
                                            math_form.setdefault('Other4', {}).update({f'in{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                            break
                                    else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                        if answers['MathematicalFormulation'].keys():
                                            new_key = max(answers['MathematicalFormulation'].keys())+1 
                                        else:
                                            new_key = 0
                                        answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                        new_form = answers['MathematicalFormulation'][new_key]
                                        new_form.setdefault('Relation4', {}).update({f'in{idx}': mathmoddb['ContainedAsInputIn']})
                                        new_form.setdefault('Other4', {}).update({f'in{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                        
                                elif Class.split('#')[-1] == 'Quantity' or Class.split('#')[-1] == 'QuantityKind':
                                    answers['Task'][key].setdefault('Relation2',{}).update({'in'+str(idx):mathmoddb['ContainsInput']})
                                    if Class.split('#')[-1] == 'Quantity':
                                        answers['Task'][key].setdefault('Other2',{}).update({'in'+str(idx):Id + ' <|> ' + label + ' (Quantity)'})
                                    else:
                                        answers['Task'][key].setdefault('Other2',{}).update({'in'+str(idx):Id + ' <|> ' + label + ' (QuantityKind)'})

                                seen.add((Id, label, Class))
                
                    if r.get('O', {}).get('value') and r.get('OL', {}).get('value') and r.get('OC', {}).get('value'):
                        
                        seen = set()

                        for idx, (Id, label, Class) in enumerate(zip(r['O']['value'].split(' <|> '),r['OL']['value'].split(' <|> '),r['OC']['value'].split(' <|> '))):
                            
                            if (Id, label, Class) not in seen:
                            
                                if Class.split('#')[-1] == 'MathematicalFormulation':
                            
                                    for k, math_form in answers['MathematicalFormulation'].items():
                                        if math_form.get('MathModID') == Id:
                                            math_form.setdefault('Relation4', {}).update({f'out{idx}': mathmoddb['ContainedAsOutputIn']})
                                            math_form.setdefault('Other4', {}).update({f'out{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                            break
                                    else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                        if answers['MathematicalFormulation'].keys():
                                            new_key = max(answers['MathematicalFormulation'].keys())+1 
                                        else:
                                            new_key = 0
                                        answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                        new_form = answers['MathematicalFormulation'][new_key]
                                        new_form.setdefault('Relation4', {}).update({f'out{idx}': mathmoddb['ContainedAsOutputIn']})
                                        new_form.setdefault('Other4', {}).update({f'out{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                        
                                elif Class.split('#')[-1] == 'Quantity' or Class.split('#')[-1] == 'QuantityKind':
                                    answers['Task'][key].setdefault('Relation2',{}).update({'out'+str(idx):mathmoddb['ContainsOutput']})
                                    if Class.split('#')[-1] == 'Quantity':
                                        answers['Task'][key].setdefault('Other2',{}).update({'out'+str(idx):Id + ' <|> ' + label + ' (Quantity)'})
                                    else:
                                        answers['Task'][key].setdefault('Other2',{}).update({'out'+str(idx):Id + ' <|> ' + label + ' (QuantityKind)'})

                                seen.add((Id, label, Class))
                
                    if r.get('OB', {}).get('value') and r.get('OBL', {}).get('value') and r.get('OBCl', {}).get('value'):
                   
                        seen = set()

                        for idx, (Id, label, Class) in enumerate(zip(r['OB']['value'].split(' <|> '),r['OBL']['value'].split(' <|> '),r['OBC']['value'].split(' <|> '))):
                            
                            if (Id, label, Class) not in seen:

                                if Class.split('#')[-1] == 'MathematicalFormulation':
                            
                                    for k, math_form in answers['MathematicalFormulation'].items():
                                        if math_form.get('MathModID') == Id:
                                            math_form.setdefault('Relation4', {}).update({f'obj{idx}': mathmoddb['ContainedAsObjectiveIn']})
                                            math_form.setdefault('Other4', {}).update({f'obj{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                            break
                                    else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                        if answers['MathematicalFormulation'].keys():
                                            new_key = max(answers['MathematicalFormulation'].keys())+1 
                                        else:
                                            new_key = 0
                                        answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                        new_form = answers['MathematicalFormulation'][new_key]
                                        new_form.setdefault('Relation4', {}).update({f'obj{idx}': mathmoddb['ContainedAsObjectiveIn']})
                                        new_form.setdefault('Other4', {}).update({f'obj{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                                elif Class.split('#')[-1] == 'Quantity' or Class.split('#')[-1] == 'QuantityKind':
                                    answers['Task'][key].setdefault('Relation2',{}).update({'obj'+str(idx):mathmoddb['ContainsObjective']})
                                    if Class.split('#')[-1] == 'Quantity':
                                        answers['Task'][key].setdefault('Other2',{}).update({'obj'+str(idx):Id + ' <|> ' + label + ' (Quantity)'})
                                    else:
                                        answers['Task'][key].setdefault('Other2',{}).update({'obj'+str(idx):Id + ' <|> ' + label + ' (QuantityKind)'})

                                seen.add((Id, label, Class))
    
                    if r.get('PA', {}).get('value') and r.get('PAL', {}).get('value') and r.get('PAC', {}).get('value'):
                    
                        seen = set()

                        for idx, (Id, label, Class) in enumerate(zip(r['PA']['value'].split(' <|> '),r['PAL']['value'].split(' <|> '),r['PAC']['value'].split(' <|> '))):
                            
                            if (Id, label, Class) not in seen:

                                if Class.split('#')[-1] == 'MathematicalFormulation':
        
                                    for k, math_form in answers['MathematicalFormulation'].items():
                                        if math_form.get('MathModID') == Id:
                                            math_form.setdefault('Relation4', {}).update({f'pa{idx}': mathmoddb['ContainedAsParameterIn']})
                                            math_form.setdefault('Other4', {}).update({f'pa{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
                                            break
                                    else:  # This else corresponds to the for loop, it runs if the loop is not broken
                                        if answers['MathematicalFormulation'].keys():
                                            new_key = max(answers['MathematicalFormulation'].keys())+1 
                                        else:
                                            new_key = 0
                                        answers['MathematicalFormulation'].setdefault(new_key, {}).update({'MathModID': Id, 'Name': label})
                                        new_form = answers['MathematicalFormulation'][new_key]
                                        new_form.setdefault('Relation4', {}).update({f'pa{idx}': mathmoddb['ContainedAsParameterIn']})
                                        new_form.setdefault('Other4', {}).update({f'pa{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"})
    
                                elif Class.split('#')[-1] == 'Quantity' or Class.split('#')[-1] == 'QuantityKind':
                                    answers['Task'][key].setdefault('Relation2',{}).update({'pa'+str(idx):mathmoddb['ContainsParameter']})
                                    if Class.split('#')[-1] == 'Quantity':
                                        answers['Task'][key].setdefault('Other2',{}).update({'pa'+str(idx):Id + ' <|> ' + label + ' (Quantity)'})
                                    else:
                                        answers['Task'][key].setdefault('Other2',{}).update({'pa'+str(idx):Id + ' <|> ' + label + ' (QuantityKind)'})

                                seen.add((Id, label, Class))
    
    if req2:
    
        for r in req2:
            for key in answers['Task']:
                if r.get('t', {}).get('value') == answers['Task'][key].get('MathModID'):
                
                    if r.get('GBTASK', {}).get('value') and r.get('GBTLabel', {}).get('value'):
                    
                        for idx, (Id, label) in enumerate(zip(r['GBTASK']['value'].split(' <|> '),r['GBTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'gb'+str(idx):mathmoddb['GeneralizedBy']})
                            answers['Task'][key].setdefault('Other3',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('GTASK', {}).get('value') and r.get('GTLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['GTASK']['value'].split(' <|> '),r['GTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'g'+str(idx):mathmoddb['Generalizes']})
                            answers['Task'][key].setdefault('Other3',{}).update({'g'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('ABTASK', {}).get('value') and r.get('ABTLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['ABTASK']['value'].split(' <|> '),r['ABTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'gb'+str(idx):mathmoddb['ApproximatedBy']})
                            answers['Task'][key].setdefault('Other3',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('ATASK', {}).get('value') and r.get('ATLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['ATASK']['value'].split(' <|> '),r['ATLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'a'+str(idx):mathmoddb['Approximates']})
                            answers['Task'][key].setdefault('Other3',{}).update({'a'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('DBTASK', {}).get('value') and r.get('DBTLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['DBTASK']['value'].split(' <|> '),r['DBTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'db'+str(idx):mathmoddb['DiscretizedBy']})
                            answers['Task'][key].setdefault('Other3',{}).update({'db'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('DTASK', {}).get('value') and r.get('DTLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['DTASK']['value'].split(' <|> '),r['DTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'d'+str(idx):mathmoddb['Discretizes']})
                            answers['Task'][key].setdefault('Other3',{}).update({'d'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('LBTASK', {}).get('value') and r.get('LBTLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['LBTASK']['value'].split(' <|> '),r['LBTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'lb'+str(idx):mathmoddb['LinearizedBy']})
                            answers['Task'][key].setdefault('Other3',{}).update({'lb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('LTASK', {}).get('value') and r.get('LTLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['LTASK']['value'].split(' <|> '),r['LTLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'l'+str(idx):mathmoddb['Linearizes']})
                            answers['Task'][key].setdefault('Other3',{}).update({'l'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('STASK', {}).get('value') and r.get('STLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['STASK']['value'].split(' <|> '),r['STLabel']['value'].split(' <|> '))):
                            answers['Task'][key].setdefault('Relation3',{}).update({'s'+str(idx):mathmoddb['SimilarTo']})
                            answers['Task'][key].setdefault('Other3',{}).update({'s'+str(idx):Id + ' <|> ' + label})
    
    # Get additional Mathematical Formulation Information
    if 'ID' in answers['Quantity'].get('MathModID',{}).keys():
        del answers['Quantity']['MathModID']['ID']
    
    # Add Mathematical Formulation from Task to Formulation List
    for idx, key in enumerate(answers['Task']):
        for key2 in answers['Task'][key].get('Relation1',{}):
            
            if answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsAssumption']:
                relation = mathmoddb['ContainedAsAssumptionIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsBoundaryCondition']:
                relation = mathmoddb['ContainedAsBoundaryConditionIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsConstraintCondition']:
                relation = mathmoddb['ContainedAsConstraintConditionIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsCouplingCondition']:
                relation = mathmoddb['ContainedAsCouplingConditionIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsFormulation']:
                relation = mathmoddb['ContainedAsFormulationIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsInitialCondition']:
                relation = mathmoddb['ContainedAsInitialConditionIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsFinalCondition']:
                relation = mathmoddb['ContainedAsFinalConditionIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsInput']:
                relation = mathmoddb['ContainedAsInputIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsOutput']:
                relation = mathmoddb['ContainedAsOutputIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsObjective']:
                relation = mathmoddb['ContainedAsObjectiveIn']
            elif answers['Task'][key]['Relation1'][key2] == mathmoddb['ContainsParameter']:
                relation = mathmoddb['ContainedAsParameterIn']
    
            Id,label = answers['Task'][key]['Other1'][key2].split(' <|> ')[:2]
            for k in answers['MathematicalFormulation']:
                if label == answers['MathematicalFormulation'][k]['Name']:
                    answers['MathematicalFormulation'][k].setdefault('Relation4',{}).update({'abc'+str(key)+str(idx):relation})
                    answers['MathematicalFormulation'][k].setdefault('Other4',{}).update({'abc'+str(key)+str(idx):f"{answers['Task'][key].get('MathModID',idx)} <|> {answers['Task'][key]['Name']}"})
                    break
            else:
                if answers['MathematicalFormulation'].keys():
                    key3 = max(answers['MathematicalFormulation'].keys()) + 1
                else:
                    key3 = 0
                answers['MathematicalFormulation'].update({key3:{'MathModID':Id,'Name':label,
                                                                'Relation4':{'abc'+str(key)+str(idx):relation},
                                                                'Other4':{'abc'+str(key)+str(idx):f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"}}})
    
    search_string = ''
    
    for key in answers['MathematicalFormulation']:
    
        if answers['MathematicalFormulation'][key].get('MathModID') and answers['MathematicalFormulation'][key]['MathModID'] != 'not in MathModDB':
    
            search_string = search_string + f' :{answers["MathematicalFormulation"][key]["MathModID"].split("#")[1]}'
    
    req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                    params = {'format': 'json', 'query': query_mf.format(search_string)},
                    headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
    
    req2=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                    params = {'format': 'json', 'query': query_mf2.format(search_string)},
                    headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
 
    if req:
    
        for r in req:
            for key in answers['MathematicalFormulation']:
                
                if r.get('mf', {}).get('value') == answers['MathematicalFormulation'][key].get('MathModID'):
    
                    if r.get('quote', {}).get('value'):
                        answers['MathematicalFormulation'][key].update({'Description':r['quote']['value']})
    
                    if r.get('convex',{}):
                        if r['convex']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({0:mathmoddb['IsConvex']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({1:mathmoddb['IsNotConvex']})
    
                    if r.get('deterministic',{}):
                        if r['deterministic']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({2:mathmoddb['IsDeterministic']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({3:mathmoddb['IsStochastic']})
                
                    if r.get('dimensionless',{}):
                        if r['dimensionless']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({4:mathmoddb['IsDimensionless']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({5:mathmoddb['IsDimensional']})
                
                    if r.get('dynamic',{}):
                        if r['dynamic']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({6:mathmoddb['IsDynamic']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({7:mathmoddb['IsStatic']})
                
                    if r.get('linear',{}):
                        if r['linear']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({8:mathmoddb['IsLinear']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({9:mathmoddb['IsNotLinear']})
                
                    if r.get('spacecont',{}):
                        if r['spacecont']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({10:mathmoddb['IsSpaceContinuous']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({11:mathmoddb['IsSpaceDiscrete']})
                    else:
                        answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({12:mathmoddb['IsSpaceIndependent']})
                
                    if r.get('timecont',{}):
                        if r['timecont']['value'] == 'true':
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({13:mathmoddb['IsTimeContinuous']})
                        else:
                            answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({14:mathmoddb['IsTimeDiscrete']})
                    else:
                        answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({15:mathmoddb['IsTimeIndependent']})
    
                    if r.get('F', {}).get('value') and r.get('FL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['F']['value'].split(' <|> '),r['FL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'fff{idx}': mathmoddb['ContainsFormulation']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'fff{idx}': f'{Id} <|> {label}'})
                
                    if r.get('A', {}).get('value') and r.get('AL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['A']['value'].split(' <|> '),r['AL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'aaa{idx}': mathmoddb['ContainsAssumption']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'aaa{idx}': f'{Id} <|> {label}'})
    
                    if r.get('BC', {}).get('value') and r.get('BCL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['BC']['value'].split(' <|> '),r['BCL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'bcbcbc{idx}': mathmoddb['ContainsBoundaryCondition']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'bcbcbc{idx}': f'{Id} <|> {label}'})
    
                    if r.get('CC', {}).get('value') and r.get('CCL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['CC']['value'].split(' <|> '),r['CCL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'cccccc{idx}': mathmoddb['ContainsConstraintCondition']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'cccccc{idx}': f'{Id} <|> {label}'})
    
                    if r.get('CPC', {}).get('value') and r.get('CPCL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['CPC']['value'].split(' <|> '),r['CPCL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'cpccpccpc{idx}': mathmoddb['ContainsCouplingCondition']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'cpccpccpc{idx}': f'{Id} <|> {label}'})
    
                    if r.get('IC', {}).get('value') and r.get('ICL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['IC']['value'].split(' <|> '),r['ICL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'icicic{idx}': mathmoddb['ContainsInitialCondition']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'icicic{idx}': f'{Id} <|> {label}'})
    
                    if r.get('FC', {}).get('value') and r.get('FCL', {}).get('value'):
                        for idx, (Id, label) in enumerate(zip(r['FC']['value'].split(' <|> '),r['FCL']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'fcfcfc{idx}': mathmoddb['ContainsFinalCondition']})
                            answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'fcfcfc{idx}': f'{Id} <|> {label}'})
    
                    if r.get('formula',{}).get('value'):
                        for idx,formula in enumerate(r['formula']['value'].split(' <|> ')):
                            answers['MathematicalFormulation'][key].setdefault('Formula',{}).update({idx:'$'+formula+'$'})
                
                    if r.get('formula_elements',{}).get('value'):
                        for idx,element in enumerate(r['formula_elements']['value'].split(' <|> ')):
                            answers['MathematicalFormulation'][key].setdefault('Element',{}).update({idx:{'Symbol':'$'+element.split(',')[0]+'$','Quantity':element.split(',')[-1].lstrip()}})
                
                    if r.get('quantity', {}).get('value') and r.get('quantityLabel', {}).get('value') and r.get('QC', {}).get('value'):
                        for idx, (Id, label, Class) in enumerate(zip(r['quantity']['value'].split(' <|> '), r['quantityLabel']['value'].split(' <|> '),r['QC']['value'].split(' <|> '))):
                            for k in answers['Quantity'].get('MathModID',{}):
                                if answers['Quantity']['MathModID'][k] == f'{Id} <|> {label} ({Class.split("#")[1]})':
                                    break
                            else:
                                if answers['Quantity'].get('MathModID',{}).keys():
                                    val = max(answers['Quantity']['MathModID'].keys())+1
                                else:
                                    val = 0
                                answers['Quantity'].setdefault('MathModID',{}).update({val:f'{Id} <|> {label} ({Class.split("#")[1]})'})
    
    if req2:
    
        for r in req2:
            for key in answers['MathematicalFormulation']:
                if r.get('mf', {}).get('value') == answers['MathematicalFormulation'][key].get('MathModID'):
    
                    if r.get('GBFORMULA', {}).get('value') and r.get('GBFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['GBFORMULA']['value'].split(' <|> '),r['GBFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'gb'+str(idx):mathmoddb['GeneralizedBy']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('GFORMULA', {}).get('value') and r.get('GFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['GFORMULA']['value'].split(' <|> '),r['GFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'g'+str(idx):mathmoddb['Generalizes']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'g'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('ABFORMULA', {}).get('value') and r.get('ABFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['ABFORMULA']['value'].split(' <|> '),r['ABFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'ab'+str(idx):mathmoddb['ApproximatedBy']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'ab'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('AFORMULA', {}).get('value') and r.get('AFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['AFORMULA']['value'].split(' <|> '),r['AFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'a'+str(idx):mathmoddb['Approximates']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'a'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('DBFORMULA', {}).get('value') and r.get('DBFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['DBFORMULA']['value'].split(' <|> '),r['DBFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'db'+str(idx):mathmoddb['DiscretizedBy']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'db'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('DFORMULA', {}).get('value') and r.get('DFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['DFORMULA']['value'].split(' <|> '),r['DFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'d'+str(idx):mathmoddb['Discretizes']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'d'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('LBFORMULA', {}).get('value') and r.get('LBFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['LBFORMULA']['value'].split(' <|> '),r['LBFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'lb'+str(idx):mathmoddb['LinearizedBy']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'lb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('LFORMULA', {}).get('value') and r.get('LFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['LFORMULA']['value'].split(' <|> '),r['LFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'l'+str(idx):mathmoddb['Linearizes']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'l'+str(idx):Id + ' <|> ' + label})
                    
                    if r.get('NBFORMULA', {}).get('value') and r.get('NBFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['NBFORMULA']['value'].split(' <|> '),r['NBFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'nb'+str(idx):mathmoddb['NondimensionalizedBy']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'nb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('NFORMULA', {}).get('value') and r.get('NFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['NFORMULA']['value'].split(' <|> '),r['NFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'n'+str(idx):mathmoddb['Nondimensionalizes']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'n'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('SFORMULA', {}).get('value') and r.get('SFLabel', {}).get('value'):
    
                        for idx, (Id, label) in enumerate(zip(r['SFORMULA']['value'].split(' <|> '),r['SFLabel']['value'].split(' <|> '))):
                            answers['MathematicalFormulation'][key].setdefault('Relation3',{}).update({'s'+str(idx):mathmoddb['SimilarTo']})
                            answers['MathematicalFormulation'][key].setdefault('Other3',{}).update({'s'+str(idx):Id + ' <|> ' + label})
    
    # Get additional Quantity Information
    
    search_string_q = ''
    search_string_qk = ''
    
    for key in answers['Quantity'].get('MathModID',{}):
        
        Id,label_qqk = answers['Quantity']['MathModID'][key].split(' <|> ')
        label,qqk = label_qqk.rsplit(' ',1)
        
        if qqk == '(Quantity)':
            search_string_q = search_string_q + f' :{Id.split("#")[1]}'
        elif qqk == '(QuantityKind)':
            search_string_qk = search_string_qk + f' :{Id.split("#")[1]}'
    
    req_q  = requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                        params = {'format': 'json', 'query': query_q.format(search_string_q)},
                        headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
    
    req_q2  = requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_q2.format(search_string_q)},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
    
    req_q3  = requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_q3.format(search_string_q)},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
    
    req_qk = requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                        params = {'format': 'json', 'query': query_qk.format(search_string_qk)},
                        headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
 
    req_qk2 = requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                        params = {'format': 'json', 'query': query_qk2.format(search_string_qk)},
                        headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
    
    if req_q:
        for r in req_q:
            for key in answers['Quantity']['MathModID']:
                if r.get('q', {}).get('value') == answers['Quantity']['MathModID'][key].split(' <|> ')[0]:
                
                    answers.setdefault('Quantity_refined',{}).update({key:{'MathModID':r.get('q',{}).get('value'),'QName':r.get('qlabel',{}).get('value')}})
                
                    if r.get('qquote', {}).get('value'):
                        answers['Quantity_refined'][key].update({'QDescription':r['qquote']['value']})
                
                    if r.get('qdimensionless', {}):
                        if r['qdimensionless']['value'] == 'true':
                            answers['Quantity_refined'][key].setdefault('QProperties', {}).update({0:mathmoddb['IsDimensionless']})
                        else:
                            answers['Quantity_refined'][key].setdefault('QProperties', {}).update({1:mathmoddb['IsDimensional']})
                    if r.get('qlinear', {}):
                        if r['qlinear']['value'] == 'ture':
                            answers['Quantity_refined'][key].setdefault('QProperties', {}).update({2:mathmoddb['IsLinear']})
                        else:
                            answers['Quantity_refined'][key].setdefault('QProperties', {}).update({3:mathmoddb['IsNotLinear']})
                
                    if r.get('answer', {}).get('value'):
                        answers['Quantity_refined'][key].update({'QKID':r['answer']['value']})
                
                    if r.get('qklabel', {}).get('value'):
                        answers['Quantity_refined'][key].update({'QKName':r['qklabel']['value']})
                
                    if r.get('qkquote', {}).get('value'):
                        answers['Quantity_refined'][key].update({'QKDescription':r['qkquote']['value']})
                
                    if r.get('qkdimensionless', {}):
                        if r['qkdimensionless']['value'] == 'true':
                            answers['Quantity_refined'][key].setdefault('QKProperties', {}).update({0:mathmoddb['IsDimensionless']})
                        else:
                            answers['Quantity_refined'][key].setdefault('QKProperties', {}).update({0:mathmoddb['IsDimensional']})
    
    if req_qk:
        for r in req_qk:
            for key in answers['Quantity']['MathModID']:
                if r.get('qk', {}).get('value') == answers['Quantity']['MathModID'][key].split(' <|> ')[0]:
    
                    answers.setdefault('QuantityKind_refined',{}).update({key:{'MathModID':r.get('qk',{}).get('value'),'QKName':r.get('qklabel',{}).get('value')}})
        
                    if r.get('qkquote', {}).get('value'):
                        answers['QuantityKind_refined'][key].update({'QKDescription':r['qkquote']['value']})
        
                    if r.get('qkdimensionless', {}):
                        if r['qkdimensionless']['value'] == 'true':
                            answers['QuantityKind_refined'][key].setdefault('QKProperties', {}).update({0:mathmoddb['IsDimensional']})
                        else:
                            answers['QuantityKind_refined'][key].setdefault('QKProperties', {}).update({0:mathmoddb['IsNotDimensional']})
    
    if req_q2:
        for r in req_q2:
            
            if answers['MathematicalFormulation'].keys():
                key = max(answers['MathematicalFormulation'].keys()) + 1
            else:
                key = 0
            
            answers['MathematicalFormulation'].setdefault(key,{}).update({'MathModID':r.get('mf', {}).get('value')})
            answers['MathematicalFormulation'][key].update({'Name':r.get('label', {}).get('value')})
            answers['MathematicalFormulation'][key].update({'DefinedQuantity':f'{r.get("q", {}).get("value")} <|> {r.get("qlabel", {}).get("value")}'}) 
    
            if r.get('quote', {}).get('value'):
                answers['MathematicalFormulation'][key].update({'Description':r['quote']['value']})
            
            if r.get('convex',{}):
                if r['convex']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({0:mathmoddb['IsConvex']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({1:mathmoddb['IsNotConvex']})
    
            if r.get('deterministic',{}):
                if r['deterministic']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({2:mathmoddb['IsDeterministic']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({3:mathmoddb['IsStochastic']})
    
            if r.get('dimensionless',{}):
                if r['dimensionless']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({4:mathmoddb['IsDimensionless']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({5:mathmoddb['IsDimensional']})
    
            if r.get('dynamic',{}):
                if r['dynamic']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({6:mathmoddb['IsDynamic']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({7:mathmoddb['IsStatic']})
    
            if r.get('linear',{}):
                if r['linear']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({8:mathmoddb['IsLinear']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({9:mathmoddb['IsNotLinear']})
    
            if r.get('spacecont',{}):
                if r['spacecont']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({10:mathmoddb['IsSpaceContinuous']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({11:mathmoddb['IsSpaceDiscrete']})
            else:
                answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({12:mathmoddb['IsSpaceIndependent']})
    
            if r.get('timecont',{}):
                if r['timecont']['value'] == 'true':
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({13:mathmoddb['IsTimeContinuous']})
                else:
                    answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({14:mathmoddb['IsTimeDiscrete']})
            else:
                answers['MathematicalFormulation'][key].setdefault('Properties',{}).update({15:mathmoddb['IsTimeIndependent']})
    
            if r.get('formula_elements',{}).get('value'):
                for idx,element in enumerate(r['formula_elements']['value'].split(' <|> ')):
                    answers['MathematicalFormulation'][key].setdefault('Element',{}).update({idx:{'Symbol':'$'+element.split(',')[0]+'$','Quantity':element.split(',')[-1].lstrip()}})
    
            if r.get('quantity', {}).get('value') and r.get('quantityLabel', {}).get('value') and r.get('QC', {}).get('value'):
                for idx, (Id, label, Class) in enumerate(zip(r['quantity']['value'].split(' <|> '), r['quantityLabel']['value'].split(' <|> '),r['QC']['value'].split(' <|> '))):
                    if Class.split('#')[1] == 'Quantity':
                        for k in answers['Quantity_refined']:
                            if answers['Quantity_refined'][k]['MathModID'] == Id:
                                break
                        else:
                            answers['Quantity_refined'].update({max(answers['Quantity_refined'].keys())+1:{'MathModID':Id,'QName':label}})
                    elif Class.split('#')[1] == 'QuantityKind':
                        for k in answers['QuantityKind_refined']:
                            if answers['QuantityKind_refined'][k]['MathModID'] == Id:
                                break
                        else:
                            answers['QuantityKind_refined'].update({max(answers['QuantityKind_refined'].keys())+1:{'MathModID':Id,'QName':label}})
    
    if req_q3:
    
        for r in req_q3:
            for key in answers['Quantity_refined']:
                if r.get('q', {}).get('value') == answers['Quantity_refined'][key]['MathModID']:
                    
                    if r.get('GBQUANTITY', {}).get('value') and r.get('GBQLabel', {}).get('value') and r.get('GBCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['GBQUANTITY']['value'].split(' <|> '),r['GBQLabel']['value'].split(' <|> '),r['GBCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'gb'+str(idx):mathmoddb['GeneralizedBy']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'gb'+str(idx):mathmoddb['GeneralizedBy']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('GQUANTITY', {}).get('value') and r.get('GQLabel', {}).get('value') and r.get('GCLASS', {}).get('value'):
                        
                        for idx, (Id, label, Class) in enumerate(zip(r['GQUANTITY']['value'].split(' <|> '),r['GQLabel']['value'].split(' <|> '),r['GCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'g'+str(idx):mathmoddb['Generalizes']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'g'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'g'+str(idx):mathmoddb['Generalizes']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'g'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('ABQUANTITY', {}).get('value') and r.get('ABQLabel', {}).get('value') and r.get('ABCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['ABQUANTITY']['value'].split(' <|> '),r['ABQLabel']['value'].split(' <|> '),r['ABCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'ab'+str(idx):mathmoddb['ApproximatedBy']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'ab'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'ab'+str(idx):mathmoddb['ApproximatedBy']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'ab'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('AQUANTITY', {}).get('value') and r.get('AQLabel', {}).get('value') and r.get('ACLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['AQUANTITY']['value'].split(' <|> '),r['AQLabel']['value'].split(' <|> '),r['ACLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'a'+str(idx):mathmoddb['Approximates']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'a'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'a'+str(idx):mathmoddb['Approximates']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'a'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('LBQUANTITY', {}).get('value') and r.get('LBQLabel', {}).get('value') and r.get('LBCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['LBQUANTITY']['value'].split(' <|> '),r['LBQLabel']['value'].split(' <|> '),r['LBCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'lb'+str(idx):mathmoddb['LinearizedBy']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'lb'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'lb'+str(idx):mathmoddb['LinearizedBy']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'lb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('LQUANTITY', {}).get('value') and r.get('LQLabel', {}).get('value') and r.get('LCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['LQUANTITY']['value'].split(' <|> '),r['LQLabel']['value'].split(' <|> '),r['LCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'l'+str(idx):mathmoddb['Linearizes']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'l'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'l'+str(idx):mathmoddb['Linearizes']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'l'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('NBQUANTITY', {}).get('value') and r.get('NBQLabel', {}).get('value') and r.get('NBCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['NBQUANTITY']['value'].split(' <|> '),r['NBQLabel']['value'].split(' <|> '),r['NBCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'nb'+str(idx):mathmoddb['NondimensionalizedBy']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'nb'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'nb'+str(idx):mathmoddb['NondimensionalizedBy']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'nb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('NQUANTITY', {}).get('value') and r.get('NQLabel', {}).get('value') and r.get('NCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['NQUANTITY']['value'].split(' <|> '),r['NQLabel']['value'].split(' <|> '),r['NCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'n'+str(idx):mathmoddb['Nondimensionalizes']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'n'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'n'+str(idx):mathmoddb['Nondimensionalizes']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'n'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('SQUANTITY', {}).get('value') and r.get('SQLabel', {}).get('value') and r.get('SCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['SQUANTITY']['value'].split(' <|> '),r['SQLabel']['value'].split(' <|> '),r['SCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['Quantity_refined'][key].setdefault('Relation1',{}).update({'s'+str(idx):mathmoddb['SimilarTo']})
                                answers['Quantity_refined'][key].setdefault('Other1',{}).update({'s'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['Quantity_refined'][key].setdefault('Relation2',{}).update({'s'+str(idx):mathmoddb['SimilarTo']})
                                answers['Quantity_refined'][key].setdefault('Other2',{}).update({'s'+str(idx):Id + ' <|> ' + label})
    
    if req_qk2:
    
        for r in req_qk2:
            for key in answers.get('QuantityKind_refined',[]):
                if r.get('q', {}).get('value') == answers['QuantityKind_refined'][key]['MathModID']:
    
                    if r.get('GBQUANTITY', {}).get('value') and r.get('GBQLabel', {}).get('value') and r.get('GBCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['GBQUANTITY']['value'].split(' <|> '),r['GBQLabel']['value'].split(' <|> '),r['GBCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['QuantityKind_refined'][key].setdefault('Relation2',{}).update({'gb'+str(idx):mathmoddb['GeneralizedBy']})
                                answers['QuantityKind_refined'][key].setdefault('Other2',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['QuantityKind_refined'][key].setdefault('Relation1',{}).update({'gb'+str(idx):mathmoddb['GeneralizedBy']})
                                answers['QuantityKind_refined'][key].setdefault('Other1',{}).update({'gb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('GQUANTITY', {}).get('value') and r.get('GQLabel', {}).get('value') and r.get('GCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['GQUANTITY']['value'].split(' <|> '),r['GQLabel']['value'].split(' <|> '),r['GCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['QuantityKind_refined'][key].setdefault('Relation2',{}).update({'g'+str(idx):mathmoddb['Generalizes']})
                                answers['QuantityKind_refined'][key].setdefault('Other2',{}).update({'g'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['QuantityKind_refined'][key].setdefault('Relation1',{}).update({'g'+str(idx):mathmoddb['Generalizes']})
                                answers['QuantityKind_refined'][key].setdefault('Other1',{}).update({'g'+str(idx):Id + ' <|> ' + label})
                    
                    if r.get('NBQUANTITY', {}).get('value') and r.get('NBQLabel', {}).get('value') and r.get('NBCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['NBQUANTITY']['value'].split(' <|> '),r['NBQLabel']['value'].split(' <|> '),r['NBCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['QuantityKind_refined'][key].setdefault('Relation2',{}).update({'nb'+str(idx):mathmoddb['NondimensionalizedBy']})
                                answers['QuantityKind_refined'][key].setdefault('Other2',{}).update({'nb'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['QuantityKind_refined'][key].setdefault('Relation1',{}).update({'nb'+str(idx):mathmoddb['NondimensionalizedBy']})
                                answers['QuantityKind_refined'][key].setdefault('Other1',{}).update({'nb'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('NQUANTITY', {}).get('value') and r.get('NQLabel', {}).get('value') and r.get('NCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['NQUANTITY']['value'].split(' <|> '),r['NQLabel']['value'].split(' <|> '),r['NCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['QuantityKind_refined'][key].setdefault('Relation2',{}).update({'n'+str(idx):mathmoddb['Nondimensionalizes']})
                                answers['QuantityKind_refined'][key].setdefault('Other2',{}).update({'n'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['QuantityKind_refined'][key].setdefault('Relation1',{}).update({'n'+str(idx):mathmoddb['Nondimensionalizes']})
                                answers['QuantityKind_refined'][key].setdefault('Other1',{}).update({'n'+str(idx):Id + ' <|> ' + label})
    
                    if r.get('SQUANTITY', {}).get('value') and r.get('SQLabel', {}).get('value') and r.get('SCLASS', {}).get('value'):
    
                        for idx, (Id, label, Class) in enumerate(zip(r['SQUANTITY']['value'].split(' <|> '),r['SQLabel']['value'].split(' <|> '),r['SCLASS']['value'].split(' <|> '))):
                            if Class.split('#')[1] == 'Quantity':
                                answers['QuantityKind_refined'][key].setdefault('Relation2',{}).update({'s'+str(idx):mathmoddb['SimilarTo']})
                                answers['QuantityKind_refined'][key].setdefault('Other2',{}).update({'s'+str(idx):Id + ' <|> ' + label})
                            elif Class.split('#')[1] == 'QuantityKind':
                                answers['QuantityKind_refined'][key].setdefault('Relation1',{}).update({'s'+str(idx):mathmoddb['SimilarTo']})
                                answers['QuantityKind_refined'][key].setdefault('Other1',{}).update({'s'+str(idx):Id + ' <|> ' + label})

    # Get additional Publication Information

    search_string = ''

    for key in answers.get('ResearchField',{}):
        if answers['ResearchField'][key].get('MathModID') and answers['ResearchField'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["ResearchField"][key]["MathModID"].split("#")[1]}'
    
    for key in answers.get('ResearchProblem',{}):
        if answers['ResearchProblem'][key].get('MathModID') and answers['ResearchProblem'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["ResearchProblem"][key]["MathModID"].split("#")[1]}'

    for key in answers.get('AllModels',{}):
        if answers['AllModels'][key].get('MathModID') and answers['AllModels'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["AllModels"][key]["MathModID"].split("#")[1]}'

    for key in answers.get('Quantity_refined',{}):
        if answers['Quantity_refined'][key].get('MathModID') and answers['Quantity_refined'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["Quantity_refined"][key]["MathModID"].split("#")[1]}'

    for key in answers.get('QuantityKind_refined',{}):
        if answers['QuantityKind_refined'][key].get('MathModID') and answers['QuantityKind_refined'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["QuantityKind_refined"][key]["MathModID"].split("#")[1]}'

    for key in answers.get('MathematicalFormulation',{}):
        if answers['MathematicalFormulation'][key].get('MathModID') and answers['MathematicalFormulation'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["MathematicalFormulation"][key]["MathModID"].split("#")[1]}'

    for key in answers.get('Task',{}):
        if answers['Task'][key].get('MathModID') and answers['Task'][key]['MathModID'] != 'not in MathModDB':
            search_string = search_string + f' :{answers["Task"][key]["MathModID"].split("#")[1]}'

    req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                    params = {'format': 'json', 'query': query_pu.format(search_string)},
                    headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings'] 

    for r in req:
        if r.get('PU1',{}).get('value'):
            for key in answers['PublicationModel']:
                if answers['PublicationModel'][key]['MathModID'] == r['PU1']['value']:
                    if answers['PublicationModel'][key]['Relation1'].keys():
                        new_key = max(answers['PublicationModel'][key]['Relation1'].keys())+1
                    else:
                        new_key = 0
                    answers['PublicationModel'][key].setdefault('Relation1',{}).update({new_key:mathmoddb['Documents']})
                    answers['PublicationModel'][key].setdefault('Other1',{}).update({new_key:f"{r['item']['value']} <|> {r['label']['value']}"})
                    break
            else:
                if answers['PublicationModel'].keys():
                    new_key = max(answers['PublicationModel'].keys())+1
                else:
                    new_key = 0
                answers['PublicationModel'].setdefault(new_key,{}).update({'MathModID':r['PU1']['value'],
                                                                           'Name':r['LABEL1']['value'],
                                                                           'Relation1': {0:mathmoddb['Documents']},
                                                                           'Other1': {0:f"{r['item']['value']} <|> {r['label']['value']} ({class_mapping[r['class']['value'].split('#')[1]]})"}})

        if r.get('PU2',{}).get('value'):
            for key in answers['PublicationModel']:
                if answers['PublicationModel'][key]['MathModID'] == r['PU2']['value']:
                    if answers['PublicationModel'][key]['Relation1'].keys():
                        new_key = max(answers['PublicationModel'][key]['Relation1'].keys())+1
                    else:
                        new_key = 0
                    answers['PublicationModel'][key].setdefault('Relation1',{}).update({new_key:mathmoddb['Invents']})
                    answers['PublicationModel'][key].setdefault('Other1',{}).update({new_key:f"{r['item']['value']} <|> {r['label']['value']}"})
                    break
            else:
                if answers['PublicationModel'].keys():
                    new_key = max(answers['PublicationModel'].keys())+1
                else:
                    new_key = 0
                answers['PublicationModel'].setdefault(new_key,{}).update({'MathModID':r['PU2']['value'],
                                                                           'Name':r['LABEL2']['value'],
                                                                           'Relation1': {0:mathmoddb['Invents']},
                                                                           'Other1': {0:f"{r['item']['value']} <|> {r['label']['value']} ({class_mapping[r['class']['value'].split('#')[1]]})"}})

        if r.get('PU3',{}).get('value'):
            for key in answers['PublicationModel']:
                if answers['PublicationModel'][key]['MathModID'] == r['PU3']['value']:
                    if answers['PublicationModel'][key]['Relation1'].keys():
                        new_key = max(answers['PublicationModel'][key]['Relation1'].keys())+1
                    else:
                        new_key = 0
                    answers['PublicationModel'][key].setdefault('Relation1',{}).update({new_key:mathmoddb['Studies']})
                    answers['PublicationModel'][key].setdefault('Other1',{}).update({new_key:f"{r['item']['value']} <|> {r['label']['value']}"})
                    break
            else:
                if answers['PublicationModel'].keys():
                    new_key = max(answers['PublicationModel'].keys())+1
                else:
                    new_key = 0
                answers['PublicationModel'].setdefault(new_key,{}).update({'MathModID':r['PU3']['value'],
                                                                           'Name':r['LABEL3']['value'],
                                                                           'Relation1': {0:mathmoddb['Studies']},
                                                                           'Other1': {0:f"{r['item']['value']} <|> {r['label']['value']} ({class_mapping[r['class']['value'].split('#')[1]]})"}})

        if r.get('PU4',{}).get('value'):
            for key in answers['PublicationModel']:
                if answers['PublicationModel'][key]['MathModID'] == r['PU4']['value']:
                    if answers['PublicationModel'][key]['Relation1'].keys():
                        new_key = max(answers['PublicationModel'][key]['Relation1'].keys())+1
                    else:
                        new_key = 0
                    answers['PublicationModel'][key].setdefault('Relation1',{}).update({new_key:mathmoddb['Surveys']})
                    answers['PublicationModel'][key].setdefault('Other1',{}).update({new_key:f"{r['item']['value']} <|> {r['label']['value']}"})
                    break
            else:
                if answers['PublicationModel'].keys():
                    new_key = max(answers['PublicationModel'].keys())+1
                else:
                    new_key = 0
                answers['PublicationModel'].setdefault(new_key,{}).update({'MathModID':r['PU4']['value'],
                                                                           'Name':r['LABEL4']['value'],
                                                                           'Relation1': {0:mathmoddb['Surveys']},
                                                                           'Other1': {0:f"{r['item']['value']} <|> {r['label']['value']} ({class_mapping[r['class']['value'].split('#')[1]]})"}})

        if r.get('PU5',{}).get('value'):
            for key in answers['PublicationModel']:
                if answers['PublicationModel'][key]['MathModID'] == r['PU5']['value']:
                    if answers['PublicationModel'][key]['Relation1'].keys():
                        new_key = max(answers['PublicationModel'][key]['Relation1'].keys())+1
                    else:
                        new_key = 0
                    answers['PublicationModel'][key].setdefault('Relation1',{}).update({new_key:mathmoddb['Uses']})
                    answers['PublicationModel'][key].setdefault('Other1',{}).update({new_key:f"{r['item']['value']} <|> {r['label']['value']}"})
                    break
            else:
                if answers['PublicationModel'].keys():
                    new_key = max(answers['PublicationModel'].keys())+1
                else:
                    new_key = 0
                answers['PublicationModel'].setdefault(new_key,{}).update({'MathModID':r['PU5']['value'],
                                                                           'Name':r['LABEL5']['value'],
                                                                           'Relation1': {0:mathmoddb['Uses']},
                                                                           'Other1': {0:f"{r['item']['value']} <|> {r['label']['value']} ({class_mapping[r['class']['value'].split('#')[1]]})"}})
    
    # Research Field to Research Field Relations
    for key in answers['ResearchField']:
        if answers['ResearchField'][key].get('MathModID') and answers['ResearchField'][key]['MathModID'] != 'not in MathModDB':
            # If RF from MathModDB get Description
            req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_rfs.format(answers['ResearchField'][key].get('MathModID'))},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
            for idx,r in enumerate(req):
                answers['ResearchField'][key].update({'Description':r['quote']['value']})
        for key2 in answers['ResearchField'][key].get('Relation1',{}):
            Id,label = answers['ResearchField'][key]['Other1'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['ResearchField']):
                if label == answers['ResearchField'][k]['Name']:
                    answers['ResearchField'][key].setdefault('RelationRF1',{}).update({key2:[answers['ResearchField'][key]['Relation1'][key2],'RF'+str(idx+1)]})    
            if not answers['ResearchField'][key].get('RelationRF1',{}).get(key2):
                answers['ResearchField'][key].setdefault('RelationRF1',{}).update({key2:[answers['ResearchField'][key]['Relation1'][key2],Id]})
    
    # Research Problem to Research Field Relations
    for key in answers['ResearchProblem']:
        if answers['ResearchProblem'][key].get('MathModID') and answers['ResearchProblem'][key]['MathModID'] != 'not in MathModDB':
            # If RP from MathModDB get Description
            req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_rps.format(answers['ResearchProblem'][key].get('MathModID'))},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
            
            for idx,r in enumerate(req):
                answers['ResearchProblem'][key].update({'Name':r['label']['value']})
                if r.get('quote'):
                    answers['ResearchProblem'][key].update({'Description':r['quote']['value']})
                if r.get('FIELD'):
                    for idx2, (field, fieldLabel) in enumerate(zip(r['FIELD']['value'].split(' <|> '),r['FIELDLabel']['value'].split(' <|> '))):
                        answers['ResearchProblem'][key].setdefault('ResearchField',{}).update({idx2:f"{field} <|> {fieldLabel}"})
                        for key2 in answers['ResearchField']:
                            if field == answers['ResearchField'][key2].get('MathModID'):
                                break
                        else:
                            if answers['ResearchField'].keys():
                                new_key = max(answers['ResearchField'].keys())+1
                            else:
                                new_key = 0
                            if r.get('FIELDQuote',{}):
                                answers['ResearchField'].setdefault(new_key,{}).update({'MathModID':field,'Name':fieldLabel,'Description':r['FIELDQuote']['value'].split(' <|> ')[idx2]})
                            else:
                                answers['ResearchField'].setdefault(new_key,{}).update({'MathModID':field,'Name':fieldLabel})

        if answers['ResearchProblem'][key].get('ResearchField',{}).get(0):
            Id,label = answers['ResearchProblem'][key]['ResearchField'][0].split(' <|> ')[:2]
        elif len(answers['ResearchField'].keys()) == 1:
            Id = answers['ResearchField'][0]['MathModID'] if answers['ResearchField'][0]['MathModID'] and answers['ResearchField'][0]['MathModID'] != 'not in MathModDB' else answers['ResearchField'][0]['ID'] if answers['ResearchField'][0]['ID'] else '' 
            label = answers['ResearchField'][0]['Name']
        else:
            # Stop if more than one Research Field present and no Field selected for Problem
            return render(self.request,'MaRDMO/workflowError.html', {
                'error': 'If more than one Research Field is defined the Research Problem(s) has/ve be assigned to them'
                }, status=200)
        for idx, key2 in enumerate(answers['ResearchField']):
            if label == answers['ResearchField'][key2]['Name']:
                answers['ResearchProblem'][key].setdefault('RelationRF1',{}).update({0:'RF'+str(idx+1)})
    
    # Research Problem to Research Problem Relations
    for key in answers['ResearchProblem']:
        for key2 in answers['ResearchProblem'][key].get('Relation1',{}):
            Id,label = answers['ResearchProblem'][key]['Other1'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['ResearchProblem']):
                if label == answers['ResearchProblem'][k]['Name']:
                    answers['ResearchProblem'][key].setdefault('RelationRP1',{}).update({key2:[answers['ResearchProblem'][key]['Relation1'][key2],'RP'+str(idx+1)]})
            if not answers['ResearchProblem'][key].get('RelationRP1',{}).get(key2):
                answers['ResearchProblem'][key].setdefault('RelationRP1',{}).update({key2:[answers['ResearchProblem'][key]['Relation1'][key2],Id]})
    
    # Convert Research Problems in additional Models
    for key in answers['AllModels']:
        if answers['AllModels'][key].get('ResearchProblem'):
            for key2 in answers['AllModels'][key]['ResearchProblem']:
                Id,label = answers['AllModels'][key]['ResearchProblem'][key2].split(' <|> ')[:2]
                for idx, k in enumerate(answers['ResearchProblem']):
                    if label == answers['ResearchProblem'][k]['Name']:
                        answers['AllModels'][key].setdefault('RelationRP1',{}).update({key2:'RP'+str(idx+1)})
                if not answers['AllModels'][key].get('RelationRP1',{}).get(key2):
                    answers['AllModels'][key].setdefault('RelationRP1',{}).update({key2:Id})
        else:
            req=requests.get('https://sparql.ta4.m1.mardi.ovh/mathalgodb/query',
                            params = {'format': 'json', 'query': query_models.format(answers['AllModels'][key].get('MathModID'))},
                            headers = {'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()['results']['bindings']
            for idx,r in enumerate(req):
                answers['AllModels'][key].setdefault('RelationRP1',{}).update({idx:r['answer']['value']})
    
    # Add Information to main Mathematical Model
    for key2 in answers['Models']:
        if answers['Models'][key2].get('MathModID'):
            for key in answers['AllModels']:
                if answers['Models'][key2]['MathModID'] == answers['AllModels'][key].get('MathModID'):
                    Name = answers['AllModels'][key]['Name']
                    Description = answers['AllModels'][key]['Description']
                    mardiID = find_item(Name,Description)
                    if mardiID:
                        answers['Models'][key2].update({'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description})
                    else:
                        answers['Models'][key2].update({'ID':None, 'Name':Name, 'Description':Description})

    # Add Mathematical Model to Mathematical Model Relations
    for key in answers['AllModels']:
        for key2 in answers['AllModels'][key].get('Relation1',{}):
            Id,label = answers['AllModels'][key]['Other1'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['AllModels']):
                if label == answers['AllModels'][k]['Name']:
                    answers['AllModels'][key].setdefault('RelationMM1',{}).update({key2:[answers['AllModels'][key]['Relation1'][key2],'MM'+str(idx+1)]})
            if not answers['AllModels'][key].get('RelationMM1',{}).get(key2):
                answers['AllModels'][key].setdefault('RelationMM1',{}).update({key2:[answers['AllModels'][key]['Relation1'][key2],Id]})
    
    # Add Mathematical Formulation to Mathematical Formulation Relations 1
    for key in answers['MathematicalFormulation']:
        for key2 in answers['MathematicalFormulation'][key].get('Relation2',{}):
            Id,label = answers['MathematicalFormulation'][key]['Other2'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['MathematicalFormulation']):
                if label == answers['MathematicalFormulation'][k]['Name']:
                    answers['MathematicalFormulation'][key].setdefault('RelationMF1',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation2'][key2],'MF'+str(idx+1)]})
            if not answers['MathematicalFormulation'][key].get('RelationMF1',{}).get(key2):
                answers['MathematicalFormulation'][key].setdefault('RelationMF1',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation2'][key2],Id]})
    
    # Add Mathematical Formulation to Mathematical Formulation Relations 2
    for key in answers['MathematicalFormulation']:
        for key2 in answers['MathematicalFormulation'][key].get('Relation3',{}):
            Id,label = answers['MathematicalFormulation'][key]['Other3'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['MathematicalFormulation']):
                if label == answers['MathematicalFormulation'][k]['Name']:
                    answers['MathematicalFormulation'][key].setdefault('RelationMF2',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation3'][key2],'MF'+str(idx+1)]})
            if not answers['MathematicalFormulation'][key].get('RelationMF2',{}).get(key2):
                answers['MathematicalFormulation'][key].setdefault('RelationMF2',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation3'][key2],Id]})
    
    # Add Mathematical Model to Mathematical Formulation Relations 1
    for key in answers['MathematicalFormulation']:
        for key2 in answers['MathematicalFormulation'][key].get('Relation1',{}):
            Id,label = answers['MathematicalFormulation'][key]['Other1'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['AllModels']):
                if label == answers['AllModels'][k]['Name']:
                    answers['MathematicalFormulation'][key].setdefault('RelationMM1',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation1'][key2],idx+1,'MM'+str(idx+1)]})
            if not answers['MathematicalFormulation'][key].get('RelationMM1',{}).get(key2):
                answers['MathematicalFormulation'][key].setdefault('RelationMM1',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation1'][key2],Id,Id]})
    
    # Add Task to Mathematical Formulation Relations 1
    for key in answers['MathematicalFormulation']:
        for key2 in answers['MathematicalFormulation'][key].get('Relation4',{}):
            Id,label = answers['MathematicalFormulation'][key]['Other4'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['Task']):
                if label == answers['Task'][k]['Name']:
                    answers['MathematicalFormulation'][key].setdefault('RelationT1',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation4'][key2],idx+1,'T'+str(idx+1)]})
            if not answers['MathematicalFormulation'][key].get('RelationT1',{}).get(key2):
                answers['MathematicalFormulation'][key].setdefault('RelationT1',{}).update({key2:[answers['MathematicalFormulation'][key]['Relation4'][key2],Id,Id]})
    
    # Sort user defined Quantities / Quantitiy Kinds in respective Dictionaries
    for key in answers['Quantity']:
        if key != 'MathModID':
            if answers['Quantity'][key]['QorQK'] == mathmoddb['Quantity']:
                
                if answers.get('Quantity_refined', {}).keys():
                    idx = max(answers['Quantity_refined'].keys())+1
                else:
                    idx = 0
                
                answers.setdefault('Quantity_refined',{}).update({idx:{'QName':answers['Quantity'][key].get('Name',''),
                                                                        'QDescription':answers['Quantity'][key].get('Description',''),
                                                                        'ID':answers['Quantity'][key].get('ID') if answers['Quantity'][key].get('ID') else answers['Quantity'][key].get('Reference') if answers['Quantity'][key].get('Reference') else '',
                                                                        'QProperties':answers['Quantity'][key].get('PropertiesQ'),
                                                                        'Relation1':answers['Quantity'][key].get('RelationQ1',{}),
                                                                        'Other1':answers['Quantity'][key].get('OtherQ1',{}),
                                                                        'Relation2':answers['Quantity'][key].get('RelationQ2',{}),
                                                                        'Other2':answers['Quantity'][key].get('OtherQ2',{}),
                                                                        'QKName':answers['Quantity'][key].get('OtherQ2',{}).get(0,'').split(' <|> ')[-1],
                                                                        'QKID':answers['Quantity'][key].get('OtherQ2',{}).get(0,'').split(' <|> ')[0]}})
    
            elif answers['Quantity'][key]['QorQK'] == mathmoddb['QuantityKind']:
                
                if answers.get('QuantityKind_refined', {}).keys():
                    idx = max(answers['QuantityKind_refined'].keys())+1
                else:
                    idx = 0
    
                answers.setdefault('QuantityKind_refined',{}).update({idx:{'QKName':answers['Quantity'][key].get('Name',''),
                                                                            'QKDescription':answers['Quantity'][key].get('Description',''),
                                                                            'ID':answers['Quantity'][key].get('ID',''),
                                                                            'QKProperties':answers['Quantity'][key].get('PropertiesQK'),
                                                                            'Relation1':answers['Quantity'][key].get('RelationQK1',{}),
                                                                            'Other1':answers['Quantity'][key].get('OtherQK1',{}),
                                                                            'Relation2':answers['Quantity'][key].get('RelationQK2',{}),
                                                                            'Other2':answers['Quantity'][key].get('OtherQK2',{})}})

    # Add Quantity to Quantity Relations
    # for key in answers.get('Quantity_refined', []):
    #     for key2 in answers['Quantity_refined'][key].get('Relation1',{}):
    #         Id,label = answers['Quantity_refined'][key]['Other1'][key2].split(' <|> ')[:2]
    #         for idx, k in enumerate(answers['Quantity_refined']):
    #             if label == answers['Quantity_refined'][k]['QName']:
    #                 answers['Quantity_refined'][key].setdefault('RelationQQ1',{}).update({key2:[answers['Quantity_refined'][key]['Relation1'][key2],'Q'+str(idx+1)]})
    #         if not answers['Quantity_refined'][key].get('RelationQQ1',{}).get(key2):
    #             answers['Quantity_refined'][key].setdefault('RelationQQ1',{}).update({key2:[answers['Quantity_refined'][key]['Relation1'][key2],Id]})
    
    label_to_index = {answers['Quantity_refined'][k]['QName']: idx for idx, k in enumerate(answers.get('Quantity_refined',{}))}
    for key in answers.get('Quantity_refined', []):
        for key2 in answers['Quantity_refined'][key].get('Relation1', {}):
            Id, label = answers['Quantity_refined'][key]['Other1'][key2].split(' <|> ')[:2]
            if label in label_to_index:
                idx = label_to_index[label]
                answers['Quantity_refined'][key].setdefault('RelationQQ', {}).update({key2: [answers['Quantity_refined'][key]['Relation1'][key2], 'Q' + str(idx + 1)]})
            else:
                answers['Quantity_refined'][key].setdefault('RelationQQ', {}).update({key2: [answers['Quantity_refined'][key]['Relation1'][key2], Id]})
    
    # Add QuantityKind to QuantityKind Relations
    for key in answers.get('QuantityKind_refined', []):
        for key2 in answers['QuantityKind_refined'][key].get('Relation1',{}):
            Id,label = answers['QuantityKind_refined'][key]['Other1'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['QuantityKind_refined']):
                if label == answers['QuantityKind_refined'][k]['QKName']:
                    answers['QuantityKind_refined'][key].setdefault('RelationQKQK',{}).update({key2:[answers['QuantityKind_refined'][key]['Relation1'][key2],'QK'+str(idx+1)]})
            if not answers['QuantityKind_refined'][key].get('RelationQKQK',{}).get(key2):
                answers['QuantityKind_refined'][key].setdefault('RelationQKQK',{}).update({key2:[answers['QuantityKind_refined'][key]['Relation1'][key2],Id]})
    
    # Add Quantity to QuantityKind Relations
    for key in answers.get('Quantity_refined', []):
        for key2 in answers['Quantity_refined'][key].get('Relation2',{}):
            Id,label = answers['Quantity_refined'][key]['Other2'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers.get('QuantityKind_refined',[])):
                if label == answers['QuantityKind_refined'][k].get('QKName'):
                    answers['Quantity_refined'][key].setdefault('RelationQQK',{}).update({key2:[answers['Quantity_refined'][key]['Relation2'][key2],'QK'+str(idx+1)]})
            if not answers['Quantity_refined'][key].get('RelationQQK',{}).get(key2):
                answers['Quantity_refined'][key].setdefault('RelationQQK',{}).update({key2:[answers['Quantity_refined'][key]['Relation2'][key2],Id]})
    
    # Add QuantityKind to Quantity Relations
    for key in answers.get('QuantityKind_refined', []):
        for key2 in answers['QuantityKind_refined'][key].get('Relation2',{}):
            Id,label = answers['QuantityKind_refined'][key]['Other2'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['Quantity_refined']):
                if label == answers['Quantity_refined'][k]['QName']:
                    answers['QuantityKind_refined'][key].setdefault('RelationQKQ',{}).update({key2:[answers['QuantityKind_refined'][key]['Relation2'][key2],'Q'+str(idx+1)]})
            if not answers['QuantityKind_refined'][key].get('RelationQKQ',{}).get(key2):
                answers['QuantityKind_refined'][key].setdefault('RelationQKQ',{}).update({key2:[answers['QuantityKind_refined'][key]['Relation2'][key2],Id]})
                                
    # Add Quantity to Elements
    for key in answers['MathematicalFormulation']:
        for key2 in answers['MathematicalFormulation'][key].get('Element',{}):
            if len(answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].split(' <|> ')) == 1:
                
                for k in answers.get('Quantity_refined', []):
                    if answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].lower() == answers['Quantity_refined'][k]['QName'].lower():
                        answers['MathematicalFormulation'][key]['Element'][key2].update(
                            {'Info': 
                                {'Name':answers['Quantity_refined'][k].get('QName',''),
                                'Description':answers['Quantity_refined'][k].get('QDescription',''),
                                'QID':answers['Quantity_refined'][k].get('MathModID') if answers['Quantity_refined'][k].get('MathModID') else answers['Quantity_refined'][k].get('ID',''),
                                'QKName':answers['Quantity_refined'][k].get('QKName',''),
                                'QKID':answers['Quantity_refined'][k].get('QKID','')}
                            })
                
                for k in answers.get('QuantityKind_refined',[]):
                    if answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].lower() == answers['QuantityKind_refined'][k].get('QKName','').lower():
                        answers['MathematicalFormulation'][key]['Element'][key2].update(
                            {'Info':
                                {'Description':answers['QuantityKind_refined'][k].get('QKDescription',''),
                                'QKID':answers['QuantityKind_refined'][k].get('MathModID') if answers['QuantityKind_refined'][k].get('MathModID') else answers['QuantityKind_refined'][k].get('QKID',''),
                                'QKName':answers['QuantityKind_refined'][k].get('QKName','')}
                            })
    
            elif len(answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].split(' <|> ')) >= 2:
                
                Id,label_qqk = answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].split(' <|> ')[:2]
                label,qqk = label_qqk.rsplit(' ',1)

                if qqk == '(Quantity)':
                    for k in answers['Quantity_refined']:
                        if label.lower() == answers['Quantity_refined'][k]['QName'].lower():
                            answers['MathematicalFormulation'][key]['Element'][key2].update(
                                {'Info':
                                    {'Name':answers['Quantity_refined'][k].get('QName',''),
                                    'Description':answers['Quantity_refined'][k].get('QDescription',''),
                                    'QID':answers['Quantity_refined'][k].get('MathModID') if answers['Quantity_refined'][k].get('MathModID') else answers['Quantity_refined'][k].get('ID',''),
                                    'QKName':answers['Quantity_refined'][k].get('QKName',''),
                                    'QKID':answers['Quantity_refined'][k].get('QKID','')}
                                })
                
                if qqk == '(QuantityKind)':
                    for k in answers['QuantityKind_refined']:
                        if label.lower() == answers['QuantityKind_refined'][k]['QKName'].lower():
                            answers['MathematicalFormulation'][key]['Element'][key2].update(
                                {'Info':
                                    {'Description':answers['QuantityKind_refined'][k].get('QKDescription',''),
                                    'QKID':answers['QuantityKind_refined'][k].get('MathModID') if answers['QuantityKind_refined'][k].get('MathModID') else answers['QuantityKind_refined'][k].get('QKID',''),
                                    'QKName':answers['QuantityKind_refined'][k].get('QKName','')}
                                })               
    
    # Add Definition to Quantities
    for key in answers.get('Quantity_refined',[]):
        for key2 in answers['MathematicalFormulation']:
            if answers['MathematicalFormulation'][key2].get('DefinedQuantity'):
                Id,label = answers['MathematicalFormulation'][key2]['DefinedQuantity'].split(' <|> ')[:2]
                if label == answers['Quantity_refined'][key]['QName']:
                    answers['Quantity_refined'][key].update({'MDef':answers['MathematicalFormulation'][key2]})
    
    # Add Mathematical Model to Task Relations
    for key in answers['Task']:
        for key2 in answers['Task'][key]['Model']:
            Id,label = answers['Task'][key]['Model'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['AllModels']):
                if label == answers['AllModels'][k]['Name']:
                    answers['Task'][key].setdefault('RelationMM',{}).update({key2:'MM'+str(idx+1)})
            if not answers['Task'][key].get('RelationMM',{}).get(key2):
                answers['Task'][key].setdefault('RelationMM',{}).update({key2:Id})
    
    # Add Research Problem to Task Relations
    for key in answers['Task']:
        for key2 in answers['Task'][key].get('ResearchProblem',{}):
            Id,label = answers['Task'][key]['ResearchProblem'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['ResearchProblem']):
                if label == answers['ResearchProblem'][k]['Name']:
                    answers['Task'][key].setdefault('RelationRP',{}).update({key2:'RP'+str(idx+1)})
            if not answers['Task'][key].get('RelationRP',{}).get(key2):
                answers['Task'][key].setdefault('RelationRP',{}).update({key2:Id})
    
    # Add Quantity / Quantity Kind to Task Relations
    for key in answers['Task']:
        for key2 in answers['Task'][key].get('Relation2',{}):
            Id,label_qqk = answers['Task'][key]['Other2'][key2].split(' <|> ')[:2]
            label,qqk = label_qqk.rsplit(' ',1)
            if qqk == '(Quantity)':
                for idx, k in enumerate(answers['Quantity_refined']):
                    if label == answers['Quantity_refined'][k]['QName']:
                        answers['Task'][key].setdefault('RelationQQK',{}).update({key2:[answers['Task'][key]['Relation2'][key2],'Q'+str(idx+1)]})
                if not answers['Task'][key].get('RelationQQK',{}).get(key2):
                    answers['Task'][key].setdefault('RelationQQK',{}).update({key2:[answers['Task'][key]['Relation2'][key2],Id]})
            elif qqk == '(QuantityKind)':
                for idx, k in enumerate(answers['QuantityKind_refined']):
                    if label == answers['QuantityKind_refined'][k]['QKName']:
                        answers['Task'][key].setdefault('RelationQQK',{}).update({key2:[answers['Task'][key]['Relation2'][key2],'QK'+str(idx+1)]})
                if not answers['Task'][key].get('RelationQQK',{}).get(key2):
                    answers['Task'][key].setdefault('RelationQQK',{}).update({key2:[answers['Task'][key]['Relation2'][key2],Id]})
    
    # Add Task to Task Relations
    for key in answers['Task']:
        for key2 in answers['Task'][key].get('Relation3',{}):
            Id,label = answers['Task'][key]['Other3'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['Task']):
                if label == answers['Task'][k]['Name']:
                    answers['Task'][key].setdefault('RelationT',{}).update({key2:[answers['Task'][key]['Relation3'][key2],'T'+str(idx+1)]})
            if not answers['Task'][key].get('RelationT',{}).get(key2):
                answers['Task'][key].setdefault('RelationT',{}).update({key2:[answers['Task'][key]['Relation3'][key2],Id]})
    
    # Add Entities to Publication Relations
    for key in answers['PublicationModel']:
        for key2 in answers['PublicationModel'][key].get('Relation1',{}):
    
            if len(answers['PublicationModel'][key]['Other1'][key2].split(' <|> ')) == 1:
                answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],answers['PublicationModel'][key]['Other1'][key2]]})
            elif len(answers['PublicationModel'][key]['Other1'][key2].split(' <|> ')) > 1:
                
                if len(answers['PublicationModel'][key]['Other1'][key2].split(' <|> ')) == 2:
                    Id,label_kind = answers['PublicationModel'][key]['Other1'][key2].split(' <|> ')
                    label,kind = label_kind.rsplit(' (',1)
                elif len(answers['PublicationModel'][key]['Other1'][key2].split(' <|> ')) == 3:
                    Id,label,quote_kind = answers['PublicationModel'][key]['Other1'][key2].split(' <|> ')
                    quote,kind = quote_kind.rsplit(' (',1)
                
                if kind[:-1] == 'Research Field':
                    for idx, k in enumerate(answers['ResearchField']):
                        if label == answers['ResearchField'][k]['Name']:
                            answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],'RF'+str(idx+1)]})
                    if not answers['PublicationModel'][key].get('RelationP',{}).get(key2):
                        answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],Id]})
                elif kind[:-1] == 'Research Problem':
                    for idx, k in enumerate(answers['ResearchProblem']):
                        if label == answers['ResearchProblem'][k]['Name']:
                            answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],'RP'+str(idx+1)]})
                    if not answers['PublicationModel'][key].get('RelationP',{}).get(key2):
                        answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],Id]})
    
                elif kind[:-1] == 'Mathematical Model':
                    for idx, k in enumerate(answers['AllModels']):
                        if label == answers['AllModels'][k]['Name']:
                            answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],'MM'+str(idx+1)]})
                    if not answers['PublicationModel'][key].get('RelationP',{}).get(key2):
                        answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],Id]})
    
                elif kind[:-1] == 'Quantity':
                    
                    if answers['PublicationModel'][key].get('RelationP'):
                        key2 = max(answers['PublicationModel'][key]['RelationP'].keys()) + 1
                    else: 
                        key2 = 0
                    
                    answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],label]})
    
                elif kind[:-1] == 'Quantity Kind':
                    
                    if answers['PublicationModel'][key].get('RelationP'):
                        key2 = max(answers['PublicationModel'][key]['RelationP'].keys()) + 1
                    else:
                        key2 = 0
                    
                    answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],label]})
                
                elif kind[:-1] == 'Mathematical Formulation':
                    for idx, k in enumerate(answers['MathematicalFormulation']):
                        if label == answers['MathematicalFormulation'][k]['Name']:
                            answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],'MF'+str(idx+1)]})
                    if not answers['PublicationModel'][key].get('RelationP',{}).get(key2):
                        answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],Id]})
    
                elif kind[:-1] == 'Task':
                    for idx, k in enumerate(answers['Task']):
                        if label == answers['Task'][k]['Name']:
                            answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],'T'+str(idx+1)]})
                    if not answers['PublicationModel'][key].get('RelationP',{}).get(key2):
                        answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation1'][key2],Id]})  
                        
    return answers

def find_item(label, description, api=mardi_api, language="en"):
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

