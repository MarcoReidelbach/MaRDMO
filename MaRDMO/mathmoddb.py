import requests

from .sparql import queryModelDocumentation
from .para import option, dataPropertyMapping, inversePropertyMapping, objectPropertyMapping
from .config import mardi_api, mathmoddb_endpoint

def ModelRetriever(answers,mathmoddb):
    '''Function queries MathModDB to gather further Model Information
       and connects them with Information provided by the User'''
    
    # Flag Tasks wanted by User in Workflow Documentation
    for key in answers['Task']:
        answers['Task'][key].update({'Include':False})

    # Get additional Model Information from  MathModDB

    search_string = searchGenerator(answers,['MathematicalModel'])
    req = queryMathModDB(queryModelDocumentation['MM'].format(search_string))
    
    for r in req:
        for key in answers['MathematicalModel']:
            if r.get('mm', {}).get('value') == answers['MathematicalModel'][key].get('MathModID'):

                # Evaluate Comment of Mathematical Model
                if r.get('quote', {}).get('value'):
                    answers['MathematicalModel'][key].update({'Description':r['quote']['value']})
                
                # Evaluate Data Properties of Mathematical Model
                dataProperties(answers['MathematicalModel'][key], r, dataPropertyMapping['Mathematical Model'], mathmoddb)
                 
                # Evaluate Research Problem(s) of Mathematical Model 
                if r.get('P', {}).get('value') and r.get('PL', {}).get('value'):
                    for idx, (Id, label) in enumerate(zip(r['P']['value'].split(' <|> '),r['PL']['value'].split(' <|> '))):
                        if f"{Id} <|> {label}" not in answers['MathematicalModel'][key].setdefault('ResearchProblem',{}).values():
                            answers['MathematicalModel'][key].setdefault('ResearchProblem',{}).update({f"pp{idx}":f"{Id} <|> {label}"})
                        for key2 in answers['ResearchProblem']:
                            if Id == answers['ResearchProblem'][key2].get('MathModID'):
                                break
                        else:
                            new_key = max(answers['ResearchProblem'].keys(), default=-1) + 1
                            answers['ResearchProblem'].setdefault(new_key,{})['MathModID'] = Id

                # Evaluate Task(s) of Mathematical Model
                if r.get('TA', {}).get('value') and r.get('TAL', {}).get('value'):
                    for idx, (Id, label, quote) in enumerate(zip(r['TA']['value'].split(' <|> '),r['TAL']['value'].split(' <|> '),r['TAQ']['value'].split(' <|> '))):
                        for key2 in answers['Task']:
                            if Id == answers['Task'][key2].get('MathModID'):
                                if f"{answers['MathematicalModel'][key]['MathModID']} <|> {answers['MathematicalModel'][key]['Name']}" not in answers['Task'][key2].setdefault('Model',{}).values():
                                    new_key2 = max(answers['Task'][key2]['Model'].keys(), default=-1) + 1
                                    answers['Task'][key2]['Model'].update({new_key2:f"{answers['MathematicalModel'][key]['MathModID']} <|> {answers['MathematicalModel'][key]['Name']}"}) 
                                break
                        else:
                            new_key = max(answers['Task'].keys(), default=-1) + 1
                            answers['Task'].setdefault(new_key,{}).update({'MathModID':Id,'Name':label,'Description':quote})
                            answers['Task'][new_key].setdefault('Model',{}).update({idx:f"{answers['MathematicalModel'][key]['MathModID']} <|> {answers['MathematicalModel'][key]['Name']}"})
                 
                # Evaluate Mathematical Model(s) contained in Mathematical Model
                if r.get('CMM', {}).get('value') and r.get('CMML', {}).get('value'):
                    for idx, (Id, label) in enumerate(zip(r['CMM']['value'].split(' <|> '),r['CMML']['value'].split(' <|> '))):
                        answers['MathematicalModel'][key].setdefault('IntraClassRelation', {}).update({f'mm{idx}': mathmoddb['Contains']})
                        answers['MathematicalModel'][key].setdefault('IntraClassElement', {}).update({f'mm{idx}': f'{Id} <|> {label}'})

                # Evaluate Mathematical Formulations of Mathematical Model
                for prop, mapping in objectPropertyMapping['ContainsMFRelations'].items():
                    # Retrieve values for the current mapping
                    values1 = r.get(mapping[0], {}).get('value')
                    values2 = r.get(mapping[1], {}).get('value')

                    # Skip if either value is missing
                    if not (values1 and values2):
                        continue

                    # Split values into lists
                    ids = values1.split(' <|> ')
                    labels = values2.split(' <|> ')

                    for idx, (Id, label) in enumerate(zip(ids, labels)):
                        found = False

                        # Search for existing MathematicalFormulation with the same MathModID
                        for math_form in answers['MathematicalFormulation'].values():
                            if math_form.get('MathModID') == Id:
                                found = True
                                relation1 = math_form.setdefault('Relation1', {})
                                other1 = math_form.setdefault('Other1', {})
                                relation1[f'{mapping[0]}{idx}'] = inversePropertyMapping[mathmoddb[prop]]
                                other1[f'{mapping[0]}{idx}'] = f"{answers['MathematicalModel'][key]['MathModID']} <|> {answers['MathematicalModel'][key]['Name']}"
                            break

                        if not found:
                            # Create a new key for the new MathematicalFormulation entry
                            new_key = max(answers['MathematicalFormulation'].keys(), default=-1) + 1
                            new_form = {
                                'MathModID': Id,
                                'Name': label,
                                'Relation1': {f'{mapping[0]}{idx}': inversePropertyMapping[mathmoddb[prop]]},
                                'Other1': {f'{mapping[0]}{idx}': f"{answers['MathematicalModel'][key]['MathModID']} <|> {answers['MathematicalModel'][key]['Name']}"}
                                }
                            answers['MathematicalFormulation'][new_key] = new_form
                        
    # Get additional Task Information from MathModDB
    
    search_string = searchGenerator(answers,['Task'])
    req = queryMathModDB(queryModelDocumentation['TA'].format(search_string))

    for r in req:
        for key in answers['Task']:
            if r.get('t', {}).get('value') == answers['Task'][key].get('MathModID'):
                    
                # Evaluate Comment of Task
                if r.get('quote', {}).get('value'):
                    answers['Task'][key].update({'Description':r['quote']['value']})
                    
                # Evaluate Data Properties of Task
                dataProperties(answers['Task'][key], r, dataPropertyMapping['Task'], mathmoddb)
                    
                # Evaluate Subclass of Task
                if r.get('subclass', {}).get('value'):
                    answers['Task'][key].setdefault('TaskClass',{}).update({0:mathmoddb[r['subclass']['value'].split('#')[-1]]})

                # Evaluate Tasks containend in Task
                if r.get('CT', {}).get('value') and r.get('CTL', {}).get('value'):
                    for idx, (Id, label) in enumerate(zip(r['CT']['value'].split(' <|> '),r['CTL']['value'].split(' <|> '))):
                        answers['Task'][key].setdefault('IntraClassRelation', {}).update({f't{idx}': mathmoddb['Contains']})
                        answers['Task'][key].setdefault('IntraClassElement', {}).update({f't{idx}': f'{Id} <|> {label}'})
                
                # Evaluate Task containing Task
                if r.get('ICT', {}).get('value') and r.get('ICTL', {}).get('value'):
                    for idx, (Id, label) in enumerate(zip(r['ICT']['value'].split(' <|> '),r['ICTL']['value'].split(' <|> '))):
                        answers['Task'][key].setdefault('IntraClassRelation', {}).update({f't{idx}': mathmoddb['ContainedIn']})
                        answers['Task'][key].setdefault('IntraClassElement', {}).update({f't{idx}': f'{Id} <|> {label}'})
                    
                # Evaluate Mathematical Formulations of Task
                for prop, mapping in objectPropertyMapping['ContainsMFRelations'].items():
                    # Retrieve values for the current mapping
                    values1 = r.get(mapping[0], {}).get('value')
                    values2 = r.get(mapping[1], {}).get('value')
        
                    # Skip if either value is missing
                    if not (values1 and values2):
                        continue
        
                    # Split values into lists
                    ids = values1.split(' <|> ')
                    labels = values2.split(' <|> ')
        
                    for idx, (Id, label) in enumerate(zip(ids, labels)):
                        found = False
            
                        # Search for existing MathematicalFormulation with the same MathModID
                        for math_form in answers['MathematicalFormulation'].values():
                            if math_form.get('MathModID') == Id:
                                found = True
                                relation4 = math_form.setdefault('Relation4', {})
                                other4 = math_form.setdefault('Other4', {})
                                relation4[f'{mapping[0]}{idx}'] = inversePropertyMapping[mathmoddb[prop]]
                                other4[f'{mapping[0]}{idx}'] = f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"
                            break
            
                        if not found:
                            # Create a new key for the new MathematicalFormulation entry
                            new_key = max(answers['MathematicalFormulation'].keys(), default=-1) + 1
                            new_form = {
                                'MathModID': Id,
                                'Name': label,
                                'Relation4': {f'{mapping[0]}{idx}': inversePropertyMapping[mathmoddb[prop]]},
                                'Other4': {f'{mapping[0]}{idx}': f"{answers['Task'][key]['MathModID']} <|> {answers['Task'][key]['Name']}"}
                                }
                            answers['MathematicalFormulation'][new_key] = new_form
                    
                    for prop, mapping in objectPropertyMapping['ContainsQQKRelations'].items():
                        
                        #Evaluate Quantities of Task
                        unique = set()
                        
                        # Retrieve values for the current mapping
                        values1 = r.get(mapping[0], {}).get('value')
                        values2 = r.get(mapping[1], {}).get('value')
                        values3 = r.get(mapping[2], {}).get('value')
                     
                        # Skip if any value is missing
                        if not (values1 and values2 and values3):
                            continue

                        # Split values into lists
                        ids = values1.split(' <|> ')
                        labels = values2.split(' <|> ')
                        classes = values3.split(' <|> ')
                        
                        unique.update(zip(ids, labels, classes))
                        
                        for idx, (Id, label, Class) in enumerate(unique):

                            # Determine class type
                            class_type = 'Quantity' if Class.split('#')[-1] == 'Quantity' else 'QuantityKind'
            
                            # Update answers with Relation2 and Other2
                            task_key = answers['Task'][key]
                            task_key.setdefault('Relation2', {})[f'{mapping[0]}{idx}'] = mathmoddb[prop]
                            task_key.setdefault('Other2', {})[f'{mapping[0]}{idx}'] = f'{Id} <|> {label}'
       
    # Add Mathematical Formulations from Task to Formulation List
    name_to_key = {v['Name']: k for k, v in answers['MathematicalFormulation'].items()}

    # Iterate through Tasks
    for idx, key in enumerate(answers['Task']):
        task = answers['Task'][key]

        # Process each relation
        for key2, relation in task.get('Relation1', {}).items():
            Id, label = task['Other1'][key2].split(' <|> ')[:2]

            # Check if the label already exists in Mathematical Formulation
            if label in name_to_key:
                k = name_to_key[label]
                math_form = answers['MathematicalFormulation'][k]
                relation4 = math_form.setdefault('Relation4', {})
                other4 = math_form.setdefault('Other4', {})
                relation4[f'TF{key}{idx}'] = inversePropertyMapping[relation]
                other4[f'TF{key}{idx}'] = f"{task.get('MathModID', idx)} <|> {task['Name']}"
            else:
                # Create a new entry for the Mathematical Formulation
                new_key = max(answers['MathematicalFormulation'].keys(), default=-1) + 1
                new_form = {
                    'MathModID': Id,
                    'Name': label,
                    'Relation4': {f'TF{key}{idx}': inversePropertyMapping[relation]},
                    'Other4': {f'TF{key}{idx}': f"{task.get('MathModID', idx)} <|> {task['Name']}"}
                }
                answers['MathematicalFormulation'][new_key] = new_form
                # Update the lookup dictionary
                name_to_key[label] = new_key

    # Get additional Mathematical Formulation Information from MathModDB

    search_string = searchGenerator(answers,['MathematicalFormulation'])
    req = queryMathModDB(queryModelDocumentation['MF'].format(search_string))
        
    for r in req:
        for key in answers['MathematicalFormulation']:
                
            if r.get('mf', {}).get('value') == answers['MathematicalFormulation'][key].get('MathModID'):
                    
                #Evaluate Comment of Mathematical Formulation
                if r.get('quote', {}).get('value'):
                    answers['MathematicalFormulation'][key].update({'Description':r['quote']['value']})
    
                #Evaluate Data Properties of Mathematical Formulation
                dataProperties(answers['MathematicalFormulation'][key], r, dataPropertyMapping['Mathematical Formulation'], mathmoddb)
                    
                #Evaluate Mathematical Formulations of Mathematical Formulations
                for prop, mapping in objectPropertyMapping['ContainsMFRelations'].items():
                    # Retrieve values for the current mapping
                    values1 = r.get(mapping[0], {}).get('value')
                    values2 = r.get(mapping[1], {}).get('value')

                    # Skip if either value is missing
                    if not (values1 and values2):
                        continue

                    # Split values into lists
                    ids = values1.split(' <|> ')
                    labels = values2.split(' <|> ')

                    for idx, (Id, label) in enumerate(zip(ids, labels)):
                        answers['MathematicalFormulation'][key].setdefault('Relation2', {}).update({f'{mapping[0]}{key}{idx}': mathmoddb[prop]})
                        answers['MathematicalFormulation'][key].setdefault('Other2', {}).update({f'{mapping[0]}{key}{idx}': f'{Id} <|> {label}'})

                #Evaluate Formula of Mathematical Formulation    
                if r.get('formula',{}).get('value'):
                    formulas = r['formula']['value'].split(' <|> ')
                    for idx,formula in enumerate(formulas):
                        answers['MathematicalFormulation'][key].setdefault('Formula',{}).update({idx:f'${formula}$'})
                
                #Evaluate Elements of Mathematical Formulation
                if r.get('formula_elements',{}).get('value'):
                    elements = r['formula_elements']['value'].split(' <|> ')
                    for idx,element in enumerate(elements):
                        answers['MathematicalFormulation'][key].setdefault('Element',{}).update({idx:{'Symbol':f'${element.split(",")[0]}$','Quantity':element.split(',')[-1].lstrip()}})
                
                #Evaluate Quantities of Mathematical Formulation
                values1 = r.get('quantity', {}).get('value')
                values2 = r.get('quantityLabel', {}).get('value')
                values3 = r.get('QC', {}).get('value')
    
                if values1 and values2 and values3:
                    #Split values into lists
                    quantities = values1.split(' <|> ')
                    labels = values2.split(' <|> ')
                    classes = values3.split(' <|> ')
        
                    #Add missing Quantities
                    existing_entries = {v.get('MathModID') for v in answers['Quantity'].values()}
                    for idx, (Id, label, Class) in enumerate(zip(quantities, labels, classes)):
                        if Id not in existing_entries:
                            new_key = max(answers['Quantity'].keys(), default=-1) + 1
                            answers['Quantity'].update({new_key:{
                                                            'MathModID': Id,
                                                            'Name': label,
                                                            'QorQK': mathmoddb[f'{Class.split("#")[1]}Class']
                                                                }
                                                      })
                            existing_entries.add(Id)

    # Get additional Intra-Class Information for Model, Task, Formulation and Quantity Relations from MathModDB
    
    search_string = searchGenerator(answers,['Task', 'MathematicalFormulation', 'MathematicalModel', 'Quantity'])
    req = queryMathModDB(queryModelDocumentation['IntraClass'].format(search_string))
    
    for r in req:
        Class = r.get('TC', {}).get('value').split('#')[1]
        if 'Task' in Class:
            Class = 'Task'
        elif 'Quantity' in Class:
            Class = 'Quantity'
        
        for key in answers[Class]:
            if r.get('t', {}).get('value') == answers[Class][key].get('MathModID'):
                
                # Evaluate Relations of Mathematical Formulations
                for prop, mapping in objectPropertyMapping['IntraClassRelations'].items():
                    # Retrieve values for the current mapping
                    values1 = r.get(mapping[0], {}).get('value')
                    values2 = r.get(mapping[1], {}).get('value')
                    values3 = r.get(mapping[2], {}).get('value')
                    
                    # Skip if either value is missing
                    if not (values1 and values2):
                        continue

                    # Split values into lists
                    ids = values1.split(' <|> ')
                    labels = values2.split(' <|> ')
                    entcs = values3.split(' <|> ')

                    if Class in ('MathematicalFormulation', 'Task', 'MathematicalModel'): 
                        for idx, (Id, label) in enumerate(zip(ids, labels)):
                            answers[Class][key].setdefault('IntraClassRelation',{}).update({f'{mapping[0]}{idx}':mathmoddb[prop]})
                            answers[Class][key].setdefault('IntraClassElement',{}).update({f'{mapping[0]}{idx}':f'{Id} <|> {label}'})
                    else:
                        for idx, (Id, label, entc) in enumerate(zip(ids, labels, entcs)):
                            if r.get('TC', {}).get('value').split('#')[1] == 'Quantity' and entc.split('#')[1] == 'Quantity':
                                answers[Class][key].setdefault('Relation1',{}).update({f'{mapping[0]}{idx}':mathmoddb[prop]})
                                answers[Class][key].setdefault('Other1',{}).update({f'{mapping[0]}{idx}':f'{Id} <|> {label}'})
                            elif r.get('TC', {}).get('value').split('#')[1] == 'QuantityKind' and entc.split('#')[1] == 'QuantityKind':
                                answers[Class][key].setdefault('Relation2',{}).update({f'{mapping[0]}{idx}':mathmoddb[prop]})
                                answers[Class][key].setdefault('Other2',{}).update({f'{mapping[0]}{idx}':f'{Id} <|> {label}'})
                            elif r.get('TC', {}).get('value').split('#')[1] == 'Quantity' and entc.split('#')[1] == 'QuantityKind':
                                answers[Class][key].setdefault('Relation3',{}).update({f'{mapping[0]}{idx}':mathmoddb[prop]})
                                answers[Class][key].setdefault('Other3',{}).update({f'{mapping[0]}{idx}':f'{Id} <|> {label}'})
                            elif r.get('TC', {}).get('value').split('#')[1] == 'QuantityKind' and entc.split('#')[1] == 'Quantity':
                                answers[Class][key].setdefault('Relation4',{}).update({f'{mapping[0]}{idx}':mathmoddb[prop]})
                                answers[Class][key].setdefault('Other4',{}).update({f'{mapping[0]}{idx}':f'{Id} <|> {label}'})
    
    # Get additional Quantity Information from MathModDB
    
    search_string_q = ''
    search_string_qk = ''
    
    for key in answers['Quantity']:
        
        if answers['Quantity'][key].get('MathModID') and answers['Quantity'][key]['MathModID'] != 'not in MathModDB':
            if answers['Quantity'][key]['QorQK'] == mathmoddb['QuantityClass']:
                search_string_q = search_string_q + f' :{answers["Quantity"][key]["MathModID"].split("#")[1]}'
            elif answers['Quantity'][key]['QorQK'] == mathmoddb['QuantityKindClass']:
                search_string_qk = search_string_qk + f' :{answers["Quantity"][key]["MathModID"].split("#")[1]}'
    
    req_q = queryMathModDB(queryModelDocumentation['Q'].format(search_string_q))

    req_q2 = queryMathModDB(queryModelDocumentation['Q2'].format(search_string_q))

    req_qk = queryMathModDB(queryModelDocumentation['QK'].format(search_string_qk))
 
    for r in req_q:
        for key in answers['Quantity']:
            if r.get('q', {}).get('value') == answers['Quantity'][key].get('MathModID'):
                
                #Evaluate Comment of Quantity
                if r.get('qquote', {}).get('value'):
                    answers['Quantity'][key].update({'Description':r['qquote']['value']})
                
                #Evaluate Data Properties of Quantities
                dataProperties(answers['Quantity'][key], r, dataPropertyMapping['Quantity'], mathmoddb)

                # Evaluate Quantity Kind (ID, Name, Description) of Quantity 
                if r.get('answer', {}).get('value'):
                    answers['Quantity'][key].update({'QKID':r['answer']['value']})
                
                if r.get('qklabel', {}).get('value'):
                    answers['Quantity'][key].update({'QKName':r['qklabel']['value']})
                
                if r.get('qkquote', {}).get('value'):
                    answers['Quantity'][key].update({'QKDescription':r['qkquote']['value']})

    for r in req_qk:
        for key in answers['Quantity']:
            if r.get('qk', {}).get('value') == answers['Quantity'][key].get('MathModID'):
    
                #Evaluate Comment of Quantity Kind
                if r.get('qkquote', {}).get('value'):
                    answers['Quantity'][key].update({'Description':r['qkquote']['value']})
        
                #Evaluate Data Properties of Quantity Kinds
                dataProperties(answers['Quantity'][key], r, dataPropertyMapping['Quantity Kind'], mathmoddb)

    for r in req_q2:

        key = max(answers['MathematicalFormulation'].keys(), default=-1) + 1

        #Evaluate Basic Information of Mathematical Formulation
        answers['MathematicalFormulation'].setdefault(key, {}).update({
            'MathModID': r.get('mf', {}).get('value'),
            'Name': r.get('label', {}).get('value'),
            'DefinedQuantity': f'{r.get("q", {}).get("value")} <|> {r.get("qlabel", {}).get("value")}'
            })

        #Evaluate Comment of Mathematical Formulation
        if r.get('quote', {}).get('value'):
            answers['MathematicalFormulation'][key].update({'Description':r['quote']['value']})
        
        #Evaluate Properties of Mathematical Formulation
        dataProperties(answers['MathematicalFormulation'][key], r, dataPropertyMapping['Mathematical Formulation'], mathmoddb)

        #Evaluate Formula of Mathematical Formulation    
        if r.get('formula',{}).get('value'):
            formulas = r['formula']['value'].split(' <|> ')
            for idx,formula in enumerate(formulas):
                answers['MathematicalFormulation'][key].setdefault('Formula',{}).update({idx:f'${formula}$'})
                
        #Evaluate Elements of Mathematical Formulation
        if r.get('formula_elements',{}).get('value'):
            elements = r['formula_elements']['value'].split(' <|> ')
            for idx,element in enumerate(elements):
                answers['MathematicalFormulation'][key].setdefault('Element',{}).update({idx:{'Symbol':f'${element.split(",")[0]}$','Quantity':element.split(',')[-1].lstrip()}})

        #Evaluate Quantities of Mathematical Formulation
        values1 = r.get('quantity', {}).get('value')
        values2 = r.get('quantityLabel', {}).get('value')
        values3 = r.get('QC', {}).get('value')
    
        if values1 and values2 and values3:
            #Split values into lists
            quantities = values1.split(' <|> ')
            labels = values2.split(' <|> ')
            classes = values3.split(' <|> ')
        
            #Add missing Quantities
            existing_entries = {v.get('MathModID') for v in answers['Quantity'].values()}
            for idx, (Id, label, Class) in enumerate(zip(quantities, labels, classes)):
                if Id not in existing_entries:
                    new_key = max(answers['Quantity'].keys(), default=-1) + 1
                    answers['Quantity'].update({new_key:{
                                                    'MathModID': Id,
                                                    'Name': label,
                                                    'QorQK': mathmoddb[f'{Class.split("#")[1]}Class']
                                                        }
                                                })
                    existing_entries.add(Id)

    # Get additional Publication Information from MathModDB

    search_string = searchGenerator(answers,['ResearchField','ResearchProblem','MathematicalModel','Quantity','MathematicalFormulation','Task'])
    req = queryMathModDB(queryModelDocumentation['PU'].format(search_string))
    
    for r in req:
        for prop, mapping in objectPropertyMapping['PublicationRelation'].items():
            if r.get(mapping[0],{}).get('value'):
            
                if 'Task' in r['class']['value']:
                    Class =  'Task'
                else:
                    Class = r['class']['value'].split('#')[1]
            
                for key in answers['PublicationModel']:
                    if answers['PublicationModel'][key].get('MathModID') == r[mapping[0]]['value']:
                        new_key = max(answers['PublicationModel'][key]['Relation'].keys(), default=-1) + 1
                        answers['PublicationModel'][key].setdefault('Relation',{}).update({new_key:mathmoddb[prop]})
                        answers['PublicationModel'][key].setdefault('Other',{}).update({new_key:f"{r['item']['value']} <|> {r['label']['value']} <|> {Class} <|> {''.join(filter(str.isupper, Class))}"})
                        break
                else:
                    new_key = max(answers['PublicationModel'].keys(), default=-1) + 1
                    answers['PublicationModel'].setdefault(new_key,{}).update({'MathModID':r[mapping[0]]['value'],
                                                                               'Name':r[mapping[1]]['value'],
                                                                               'Relation': {0:mathmoddb[prop]},
                                                                               'Other': {0:f"{r['item']['value']} <|> {r['label']['value']} <|> {Class} <|> {''.join(filter(str.isupper, Class))}"}})
    
    # Get additional Research Field Information from MathModDB

    search_string = searchGenerator(answers,['ResearchField'])
    req = queryMathModDB(queryModelDocumentation['RF'].format(search_string))
    
    for r in req:
        for key in answers['ResearchField']:
            if r.get('rf', {}).get('value') == answers['ResearchField'][key].get('MathModID'):
                
                # Evaluate Comment of Research Field
                answers['ResearchField'][key].update({'Description':r['quote']['value']})    
    
    # Get additional Research Problem Information from MathModDB

    search_string = searchGenerator(answers,['ResearchProblem'])
    req = queryMathModDB(queryModelDocumentation['RP'].format(search_string))

    for r in req:
        for key in answers['ResearchProblem']:
            if r.get('rp', {}).get('value') == answers['ResearchProblem'][key].get('MathModID'):

                # Evaluate Label of Research Problem
                if r.get('label'):
                    answers['ResearchProblem'][key].update({'Name':r['label']['value']})
                
                # Evaluate Comment of Research Problem
                if r.get('quote'):
                    answers['ResearchProblem'][key].update({'Description':r['quote']['value']})

                # Evaluate Research Field Information
                if r.get('FIELD'):

                    values1 = r.get('FIELD',{}).get('value')
                    values2 = r.get('FIELDLabel',{}).get('value')
                    values3 = r.get('FIELDQuote',{}).get('value')

                    if values1 and values2:
                        # Split values into lists
                        fields = values1.split(' <|> ')
                        fieldLabels = values2.split(' <|> ')
                        # Optional comment
                        if values3:
                            fieldQuotes = values3.split(' <|> ')
                        else:
                            fieldQuotes = [None] * len(fields)

                        # Add Research Fields to Research Problem
                        for idx, (field, fieldLabel, fieldQuote) in enumerate(zip(fields,fieldLabels,fieldQuotes)):
                            answers['ResearchProblem'][key].setdefault('ResearchField',{}).update({idx:f"{field} <|> {fieldLabel}"})
                            # Check if Research Field exists, if not create
                            for key2 in answers['ResearchField']:
                                if field == answers['ResearchField'][key2].get('MathModID'):
                                    break
                            else:
                                new_key = max(answers['ResearchField'].keys(), default=-1) + 1
                                if fieldQuote:
                                    answers['ResearchField'].setdefault(new_key,{}).update({'MathModID':field,'Name':fieldLabel,'Description':fieldQuote})
                                else:
                                    answers['ResearchField'].setdefault(new_key,{}).update({'MathModID':field,'Name':fieldLabel})

    # Research Field to Research Field Relations
    entityRelations(answers,'ResearchField','ResearchField','Relation1','Other1','RelationRF1','RF')

    # Research Field to Research Problem Relations
    label_to_index = {answers['ResearchField'][k]['Name']: idx for idx, k in enumerate(answers.get('ResearchField',{}))}
    for key in answers['ResearchProblem']:
        if answers['ResearchProblem'][key].get('ResearchField'):
            for key2 in answers['ResearchProblem'][key]['ResearchField']:
                Id, label = answers['ResearchProblem'][key]['ResearchField'][key2].split(' <|> ')[:2]
                if label in label_to_index:
                    idx = label_to_index[label]
                    answers['ResearchProblem'][key].setdefault('RelationRF1', {}).update({key2: f'RF{idx+1}'})

    # Research Problem to Research Problem Relations
    entityRelations(answers,'ResearchProblem','ResearchProblem','Relation1','Other1','RelationRP1','RP')
    
    # Convert Research Problems in additional Models
    for key in answers['MathematicalModel']:
        if answers['MathematicalModel'][key].get('ResearchProblem'):
            for key2 in answers['MathematicalModel'][key]['ResearchProblem']:
                Id,label = answers['MathematicalModel'][key]['ResearchProblem'][key2].split(' <|> ')[:2]
                for idx, k in enumerate(answers['ResearchProblem']):
                    if label == answers['ResearchProblem'][k]['Name']:
                        answers['MathematicalModel'][key].setdefault('RelationRP1',{}).update({key2:'RP'+str(idx+1)})
                if not answers['MathematicalModel'][key].get('RelationRP1',{}).get(key2):
                    answers['MathematicalModel'][key].setdefault('RelationRP1',{}).update({key2:Id})
    
    # Add Information to main Mathematical Model
    for key2 in answers['Models']:
        if answers['Models'][key2].get('MathModID') and answers['Models'][key2]['MathModID'] != 'not in MathModDB':
            for key in answers['MathematicalModel']:
                if answers['Models'][key2]['MathModID'] == answers['MathematicalModel'][key].get('MathModID'):
                    Name = answers['MathematicalModel'][key]['Name']
                    Description = answers['MathematicalModel'][key]['Description']
                    mardiID = find_item(Name,Description)
                    if mardiID:
                        answers['Models'][key2].update({'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description})
                    else:
                        answers['Models'][key2].update({'ID':None, 'Name':Name, 'Description':Description})
        else:
            for key in answers['MathematicalModel']:
                if answers['MathematicalModel'][key].get('Main') == option['Yes']:
                    Name = answers['MathematicalModel'][key]['Name']
                    Description = answers['MathematicalModel'][key]['Description']
                    mardiID = find_item(Name,Description)
                    if mardiID:
                        answers['Models'][key2].update({'ID':f"mardi:{mardiID}", 'Name':Name, 'Description':Description})
                    else:
                        answers['Models'][key2].update({'ID':None, 'Name':Name, 'Description':Description})
    
    # Add Mathematical Model to Mathematical Model Relations
    entityRelations(answers,'MathematicalModel','MathematicalModel','IntraClassRelation','IntraClassElement','RelationMM1','MM')

    # Add Mathematical Formulation to Mathematical Formulation Relations 1
    entityRelations(answers,'MathematicalFormulation','MathematicalFormulation','Relation2','Other2','RelationMF1','MF')

    # Add Mathematical Formulation to Mathematical Formulation Relations 2
    entityRelations(answers,'MathematicalFormulation','MathematicalFormulation','IntraClassRelation','IntraClassElement','RelationMF2','MF')
    
    # Add Mathematical Model to Mathematical Formulation Relations 1
    entityRelations(answers,'MathematicalFormulation','MathematicalModel','Relation1','Other1','RelationMM1','MM', 3)

    # Add Task to Mathematical Formulation Relations 1
    entityRelations(answers,'MathematicalFormulation','Task','Relation4','Other4','RelationT1','T', 3)

    # Add Quantity to Quantity Relations
    entityRelations(answers,'Quantity','Quantity','Relation1','Other1','RelationQQ','QQK')
    
    # Add QuantityKind to QuantityKind Relations
    entityRelations(answers,'Quantity','Quantity','Relation2','Other2','RelationQKQK','QQK')

    # Add Quantity to QuantityKind Relations
    entityRelations(answers,'Quantity','Quantity','Relation3','Other3','RelationQQK','QQK')

    # Add QuantityKind to Quantity Relations
    entityRelations(answers,'Quantity','Quantity','Relation4','Other4','RelationQKQ','QQK')
    
    # Add Quantity to Elements
    for key in answers['MathematicalFormulation']:
        for key2 in answers['MathematicalFormulation'][key].get('Element',{}):
            if len(answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].split(' <|> ')) == 1:
                label = answers['MathematicalFormulation'][key]['Element'][key2]['Quantity']
            elif len(answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].split(' <|> ')) >= 2:
                Id,label = answers['MathematicalFormulation'][key]['Element'][key2]['Quantity'].split(' <|> ')[:2]
                
            for k in answers['Quantity']:
                if label.lower() == answers['Quantity'][k]['Name'].lower():
                    if answers['Quantity'][k]['QorQK'] == mathmoddb['QuantityClass']:
                        answers['MathematicalFormulation'][key]['Element'][key2].update(
                            {'Info': 
                                {'Name':answers['Quantity'][k].get('Name',''),
                                 'Description':answers['Quantity'][k].get('Description',''),
                                 'QID':answers['Quantity'][k].get('MathModID','') if answers['Quantity'][k].get('MathModID','') else answers['Quantity'][k].get('ID','') if answers['Quantity'][k].get('ID','') else '', 
                                 'QKName':answers['Quantity'][k].get('QKName',''),
                                 'QKID':answers['Quantity'][k].get('QKID','')}
                            })
                    elif answers['Quantity'][k]['QorQK'] == mathmoddb['QuantityKindClass']:
                        answers['MathematicalFormulation'][key]['Element'][key2].update(
                            {'Info':
                                {'QKName':answers['Quantity'][k].get('Name',''),
                                 'Description':answers['Quantity'][k].get('Description',''),
                                 'QKID':answers['Quantity'][k].get('MathModID','') if answers['Quantity'][k].get('MathModID','') else answers['Quantity'][k].get('QKID','') if answers['Quantity'][k].get('QKID','') else ''}
                            })

    # Add Definition to Quantities
    for key in answers.get('Quantity',[]):
        for key2 in answers['MathematicalFormulation']:
            if answers['MathematicalFormulation'][key2].get('DefinedQuantity'):
                Id,label = answers['MathematicalFormulation'][key2]['DefinedQuantity'].split(' <|> ')[:2]
                if label == answers['Quantity'][key]['Name']:
                    answers['Quantity'][key].update({'MDef':answers['MathematicalFormulation'][key2]})
    
    # Add Mathematical Model to Task Relations
    for key in answers['Task']:
        for key2 in answers['Task'][key]['Model']:
            Id,label = answers['Task'][key]['Model'][key2].split(' <|> ')[:2]
            for idx, k in enumerate(answers['MathematicalModel']):
                if label == answers['MathematicalModel'][k]['Name']:
                    answers['Task'][key].setdefault('RelationMM',{}).update({key2:'MM'+str(idx+1)})
            if not answers['Task'][key].get('RelationMM',{}).get(key2):
                answers['Task'][key].setdefault('RelationMM',{}).update({key2:Id})
        
    # Add Quantity / Quantity Kind to Task Relations
    entityRelations(answers,'Task','Quantity','Relation2','Other2','RelationQQK','QQK')
    
    # Add Task to Task Relations
    entityRelations(answers,'Task','Task','IntraClassRelation','IntraClassElement','RelationT','T')

    # Add Entities to Publication Relations
    for key in answers['PublicationModel']:
        for key2 in answers['PublicationModel'][key].get('Relation',{}):
            
            Id,label,kind,abbr = answers['PublicationModel'][key]['Other'][key2].split(' <|> ')
            
            for idx, k in enumerate(answers[kind]):
                if label == answers[kind][k]['Name']:
                    answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation'][key2],f"{abbr}{str(idx+1)}"]})
            if not answers['PublicationModel'][key].get('RelationP',{}).get(key2):
                answers['PublicationModel'][key].setdefault('RelationP',{}).update({key2:[answers['PublicationModel'][key]['Relation'][key2],Id]})
      
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

def dataProperties(data, queryData, mapping, mathmoddb):
    # Add Data Property Information from Query to Data
    for p, m in mapping.items():
        if queryData.get(p, {}):
            if queryData[p]['value'] == 'true':
                data.setdefault('Properties',{}).update({m[0]:mathmoddb[m[1]]})
            else:
                data.setdefault('Properties',{}).update({m[2]:mathmoddb[m[3]]})
        elif len(m) == 6:
            data.setdefault('Properties',{}).update({m[4]:mathmoddb[m[5]]})

def entityRelations(data, fromIDX, toIDX, relationOld, entityOld, relationNew, enc, no=2):
    # Add relations between model entities
    label_to_index = {data[toIDX][k]['Name']: idx for idx, k in enumerate(data.get(toIDX,{}))}
    for key in data.get(fromIDX, []):
        for key2 in data[fromIDX][key].get(relationOld, {}):
            Id, label = data[fromIDX][key][entityOld][key2].split(' <|> ')[:2]
            if label in label_to_index:
                idx = label_to_index[label]
                if no == 2:
                    data[fromIDX][key].setdefault(relationNew, {}).update({key2: [data[fromIDX][key][relationOld][key2], f'{enc}{idx+1}']})
                else:
                    data[fromIDX][key].setdefault(relationNew, {}).update({key2: [data[fromIDX][key][relationOld][key2], idx+1, f'{enc}{idx+1}']})
            else:
                if no == 2:
                    data[fromIDX][key].setdefault(relationNew, {}).update({key2: [data[fromIDX][key][relationOld][key2], Id]})
                else:
                    data[fromIDX][key].setdefault(relationNew, {}).update({key2: [data[fromIDX][key][relationOld][key2], Id, Id]})

def queryMathModDB(query,endpoint=mathmoddb_endpoint):
    # Query MathModDB
    response = requests.post(mathmoddb_endpoint, 
                             data=query, 
                             headers={"Content-Type": "application/sparql-query","Accept": "application/sparql-results+json"}
                            )
    
    if response.status_code == 200:
        req = response.json().get('results',{}).get('bindings',[])
    else:
        req = []

    return req

def searchGenerator(data, class_list):
    """
    Generates a search string for SPARQL queries.

    Parameters:
        data (dict): The data structure containing relevant information.
        class_list (list): The list of keys to look up in the data.

    Returns:
        str: The generated search string.
    """
    search_string = ""

    for key in class_list:
        for key2 in data[key]:
            math_mod_id = data[key][key2].get('MathModID')
            if math_mod_id and math_mod_id != 'not in MathModDB':
                search_string += f" :{math_mod_id.split('#')[1]}"
    
    return search_string

