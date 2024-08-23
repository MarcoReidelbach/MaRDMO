import requests
import os
import json

from rdmo.options.providers import Provider
from rdmo.domain.models import Attribute
from rdmo.options.models import Option

from multiprocessing.pool import ThreadPool

from .config import wikidata_api, mardi_api, mathmoddb_endpoint
from .para import BASE_URI
from .sparql import queryProvider
from .mathmoddb import queryMathModDB

class WikidataSearch(Provider):
    
    search = True

    def get_options(self, project, search):
        '''Function which queries Wikidata and MaRDI KG for user input.'''
        if not search or len(search) < 3:
            return []
        
        # Use a ThreadPool to make concurrent API requests
        pool = ThreadPool(processes=2)
        wikidata_results, mardi_results = pool.map(lambda api_url: query_api(api_url, search), [wikidata_api, mardi_api])

        # Process Results to fit RDMO Provider Output Requirements
        options = [
            process_result(result, 'wikidata') for result in wikidata_results[:10]
        ]
        options += [ 
            process_result(result, 'mardi') for result in mardi_results[:10]
        ]

        # Return unique options (if similar Results returned from MaRDI KG and Wikidata, only keep the MaRDI KG result)
        options = list({option['text']:option for option in options}.values())
        
        return options

class AvailableSoftware(Provider):

    search = True

    SUBJECT_ATTRIBUTES = [
        f'{BASE_URI}Section_4/Set_3/Question_02',
        f'{BASE_URI}Section_4/Set_3/Question_03'
    ]

    def get_options(self, project, search):
        '''Function which queries Wikidata and MaRDI KG for user input.'''
        if not search or len(search) < 3:
            return []

        options = []

        values1 = get_attribute_values(project, get_attribute(self.SUBJECT_ATTRIBUTES[0]))
        values2 = get_attribute_values(project, get_attribute(self.SUBJECT_ATTRIBUTES[1]))

        for v1, v2 in zip(values1, values2):
            if v1.text or v2.text:
                options.append({'id': 'no ID <|> ' + v1.text + ' <|> ' + v2.text, 'text': v1.text + ' (' + v2.text + ')'})

        # Use a ThreadPool to make concurrent API requests
        pool = ThreadPool(processes=2)
        wikidata_results, mardi_results = pool.map(lambda api_url: query_api(api_url, search), [wikidata_api, mardi_api])

        # Process Results to fit RDMO Provider Output Requirements
        options += [
            process_result(result, 'wikidata') for result in wikidata_results[:10]
        ]
        options += [
            process_result(result, 'mardi') for result in mardi_results[:10]
        ]

        # Return unique options (if similar Results returned from MaRDI KG and Wikidata, only keep the MaRDI KG result)
        options = list({option['text']:option for option in options}.values())

        return options

class ComponentSearch(Provider):

    search = True

    def get_options(self, project, search):
        '''Function which queries MaRDI KG for user input.'''
        if not search or len(search) < 3:
            return []

        mardi_results = query_api(mardi_api, search)

        options = [
            process_result(result, 'mardi') for result in mardi_results[:20]
        ]

        return options

class MSCProvider(Provider):

    path = os.path.join(os.path.dirname(__file__), 'data', 'msc2020.json')

    with open(path, "r") as json_file:
        msc = json.load(json_file)

    search = True

    def get_options(self, project, search):
        '''Function which get MSC Classification.'''
        if not search or len(search) < 3:
            return []

        options = []

        options = [{'id': self.msc[key]['id'] + ' - ' + key , 'text': key} for key in self.msc if search.lower() in key.lower()]

        return options[:20]

class ProcessorProvider(Provider):

    search = True
    api_url = 'https://en.wikichip.org/w/api.php?' 

    def get_options(self, project, search):
        '''Function which get MSC Classification.'''
        if not search or len(search) < 3:
            return []
        
        response = requests.get(self.api_url, params={
            'action': 'opensearch',
            'search': search
            }, headers={'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'}).json()
        
        if response[1]:
            options = [{'id': wikichipId + ' <|> ' + wikichipLabel + ' <|> processor', 'text': wikichipLabel} for wikichipId, wikichipLabel in zip(response[-1],response[1])]
        else:
            options = []
    
        return options[:20]


class MathAreaProvider(Provider):
    
    SUBJECT_ATTRIBUTE = f'{BASE_URI}Section_2/Set_3/Question_00'

    def get_options(self, project, search=None):
        """
        Function providing the user-defined mathematical areas.
        """
        subject_attribute = get_attribute(self.SUBJECT_ATTRIBUTE)
        if not subject_attribute:
            return []

        options = []
        values = get_attribute_values(project, subject_attribute)

        options = add_options(options, values, 0)

        return options

class EnvironmentProvider(Provider):
    
    SUBJECT_ATTRIBUTES = [
        f'{BASE_URI}Section_4/Set_3/Question_01',
        f'{BASE_URI}Section_4/Set_3/Question_02',
        f'{BASE_URI}Section_4/Set_5/Question_02'
    ]

    def get_options(self, project, search=None):
        """
        Function providing the user-defined environments.
        """
        options = []

        for index, attribute_uri in enumerate(self.SUBJECT_ATTRIBUTES):
            subject_attribute = get_attribute(attribute_uri)
            if not subject_attribute:
                continue

            values = get_attribute_values(project, subject_attribute)

            # Define a lambda function for text processing
            process_text_fn = lambda text: text.split(' <|> ')[1] if ' <|> ' in text else text

            options = add_options(options, values, len(options), process_text_fn=process_text_fn)

        return options

class MethodProvider(Provider):
    
    SUBJECT_ATTRIBUTES = [
        f'{BASE_URI}Section_4/Set_2/Question_01',
        f'{BASE_URI}Section_4/Set_2/Question_02'
    ]

    def get_options(self, project, search=None):
        """
        Function providing the user-defined methods.
        """
        options = []

        for index, attribute_uri in enumerate(self.SUBJECT_ATTRIBUTES):
            subject_attribute = get_attribute(attribute_uri)
            if not subject_attribute:
                continue

            values = get_attribute_values(project, subject_attribute)

            # Process text differently for each subject_attribute
            if index == 0:
                process_text_fn = lambda text: text.split(' <|> ')[1] if ' <|> ' in text else text
            else:
                process_text_fn = lambda text: text

            options = add_options(options, values, len(options), process_text_fn=process_text_fn)

        return options

class DataProvider(Provider):
    
    SUBJECT_ATTRIBUTES = [
        f'{BASE_URI}Section_4/Set_6/Question_00',
        f'{BASE_URI}Section_4/Set_6/Question_01',
    ]

    def get_options(self, project, search=None):
        """
        Function providing the user-defined input and output data sets.
        """
        options = []

        for index, attribute_uri in enumerate(self.SUBJECT_ATTRIBUTES):
            subject_attribute = get_attribute(attribute_uri)
            if not subject_attribute:
                continue

            values = get_attribute_values(project, subject_attribute)

            if index in (0, 2):  # Split text for zeroth and second attributes
                process_text_fn = lambda text: text.split(' <|> ')[1] if ' <|> ' in text else text
            else:
                process_text_fn = lambda text: text
            options = add_options(options, values, len(options)+10*index, process_text_fn=process_text_fn)
        return options

class SoftwareProvider(Provider):
    
    SUBJECT_ATTRIBUTES = [
        f'{BASE_URI}Section_4/Set_3/Question_01',
        f'{BASE_URI}Section_4/Set_3/Question_02'
    ]

    def get_options(self, project, search=None):
        """
        Function providing the user-defined software.
        """
        options = []

        for index, attribute_uri in enumerate(self.SUBJECT_ATTRIBUTES):
            subject_attribute = get_attribute(attribute_uri)
            if not subject_attribute:
                continue

            values = get_attribute_values(project, subject_attribute)

            # Process text differently for each subject_attribute
            if index == 0:
                process_text_fn = lambda text: text.split(' <|> ')[1] if ' <|> ' in text else text
            else:
                process_text_fn = lambda text: text

            options = add_options(options, values, len(options), process_text_fn=process_text_fn)
        return options

class ResearchField(Provider):

    search = True

    def get_options(self, project, search=None):

        options = MathModDBProvider(search,queryProvider['RF'])
        
        return options
    
class ResearchFieldRelations(Provider):

    search = True

    def get_options(self, project, search=None):
        
        if not search:
            return []

        # Fetch research fields from the MathModDB knowledge graph
        results = queryMathModDB(queryProvider['RF'])

        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        # Fetch user-defined research fields from the project
        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_0/Question_3'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_0/Question_0'))

        for value1 in values1: 
            if value1.text:
                dic.update({value1.text: {'id': value1.external_id}})

        for idx, value2 in enumerate(values2): 
            if value2.text:
                dic.update({value2.text: {'id': f"{idx} <|> {value2.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])
    
        return options
    
class ResearchProblem(Provider):

    search = True

    def get_options(self, project, search=None):

        options = MathModDBProvider(search,queryProvider['RP'])

        return options
    
class MathematicalModel(Provider):

    search = True

    def get_options(self, project, search=None):

        options = MathModDBProvider(search,queryProvider['MM'])
        
        return options

class Publication(Provider):

    search = True

    def get_options(self, project, search=None):

        options = MathModDBProvider(search,queryProvider['P'])
        
        return options

class ResearchProblemRelations(Provider):

    search = True

    def get_options(self, project, search=None):
        
        if not search:
            return []

        # Fetch research problems from the MathModDB knowledge graph
        results = queryMathModDB(queryProvider['RP'])
        
        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        # Fetch user-defined research fields from the project
        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_1/Question_5'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_1/Question_0'))

        for value1 in values1: 
            if value1.text:
                dic.update({value1.text: {'id': value1.external_id}})

        for idx, value2 in enumerate(values2): 
            if value2.text:
                dic.update({value2.text: {'id': f"{idx} <|> {value2.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])

        return options

class ResearchFieldUser(Provider):

        def get_options(self, project, search=None):
        
            values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_0/Question_3'))
            values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_0/Question_0'))
            values3 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3/Set_0/Set_0/Question_04'))

            options = []

            for idx, value1 in enumerate(values1):
                if value1.text:
                    options.extend([{'id': value1.external_id, 'text': value1.text}])
            for idx, value2 in enumerate(values2):
                if value2.text:
                    options.extend([{'id': f"{idx} <|> {value2.text}", 'text': value2.text}])
            for idx, value3 in enumerate(values3):
                if value3.text and value3.text != 'not in MathModDB':
                    options.extend([{'id': value3.external_id, 'text': value3.text}])

            options = sorted(options, key=lambda option: option['text'])

            return options

class MathematicalModelRelation(Provider):

    search = True

    def get_options(self, project, search=None):

        if not search:
            return []
        
        # Fetch mathematical models from the MathModDB knowledge graph
        results = queryMathModDB(queryProvider['MM'])
        
        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        # Fetch user-defined research fields from the project
        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Set_1/Question_0'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Set_1/Question_1'))

        for value1 in values1: 
            if value1.text:
                dic.update({value1.text: {'id': value1.external_id}})

        for idx, value2 in enumerate(values2): 
            if value2.text:
                dic.update({value2.text: {'id': f"{idx} <|> {value2.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])

        return options

class MathematicalModelRelation2(Provider):

    def get_options(self, project, search=None):

        options = []
        
        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Question_0'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Set_1/Question_0'))
        values3 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Set_1/Question_1'))

        for idx, value1 in enumerate(values1):
            if value1.text and value1.text != 'not in MathModDB':
                options.extend([{'id': value1.external_id, 'text': value1.text}])
        for idx, value2 in enumerate(values2):
            if value2.text:
                options.extend([{'id': value2.external_id, 'text': value2.text}])
        for idx, value3 in enumerate(values3):
            if value3.text:
                options.extend([{'id': f"{idx} <|> {value3.text}", 'text': value3.text}])
        
        options = sorted(options, key=lambda option: option['text'])

        return options

class Quantity(Provider):

    search = True

    def get_options(self, project, search):

        options = MathModDBProvider(search,queryProvider['QQK'])

        return options

class QuantityRelations(Provider):

    search = True

    path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')

    with open(path, "r") as json_file:
        mathmoddb = json.load(json_file)

    def get_options(self, project, search=None):

        if not search:
            return []

        # Fetch quantities from th MathModDB knowledge graph
        results = queryMathModDB(queryProvider['Q'])
        
        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_6'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_5'))
        values3 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_0'))

        for value1 in values1:
            if value1.option == Option.objects.get(uri=self.mathmoddb['QuantityClass']):
                for value2 in values2: 
                    if value2.text and value1.set_index == value2.set_index:
                        dic.update({value2.text: {'id': value2.external_id}})
                for idx, value3 in enumerate(values3): 
                    if value3.text and value1.set_index == value3.set_index:
                        dic.update({value3.text: {'id': f"{idx} <|> {value3.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])

        return options

class QuantityKindRelations(Provider):

    search =True

    path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')

    with open(path, "r") as json_file:
        mathmoddb = json.load(json_file)

    def get_options(self, project, search=None):

        if not search:
            return []

        # Fetch quantities from th MathModDB knowledge graph
        results = queryMathModDB(queryProvider['QK'])

        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_6'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_5'))
        values3 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_0'))

        for value1 in values1:
            if value1.option == Option.objects.get(uri=self.mathmoddb['QuantityKindClass']):
                for value2 in values2: 
                    if value2.text and value1.set_index == value2.set_index:
                        dic.update({value2.text: {'id': value2.external_id}})
                for idx, value3 in enumerate(values3): 
                    if value3.text and value1.set_index == value3.set_index:
                        dic.update({value3.text: {'id': f"{idx} <|> {value3.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])

        return options

class MathematicalFormulation(Provider):

    search = True

    def get_options(self, project, search=None):

        options = MathModDBProvider(search,queryProvider['MF'])
        
        return options

class MathematicalFormulation2(Provider):

    search = True

    def get_options(self, project, search=None):
        
        if not search:
            return []

        # Fetch mathematical models from the MathModDB knowledge graph
        results = queryMathModDB(queryProvider['MF'])
        
        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        # Fetch user-defined research fields from the project
        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_5/Set_4/Question_0'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_5/Set_4/Question_1'))

        for value1 in values1: 
            if value1.text:
                dic.update({value1.text: {'id': value1.external_id}})

        for idx, value2 in enumerate(values2): 
            if value2.text:
                dic.update({value2.text: {'id': f"{idx} <|> {value2.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])

        return options

class QuantityAll(Provider):

    path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')

    with open(path, "r") as json_file:
        mathmoddb = json.load(json_file)

    def get_options(self, project, search=None):

        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3/Set_0/Set_0/Question_07'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_5'))
        values3 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_0'))
        values4 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_6'))

        options = []

        for idx, value1 in enumerate(values1):
            if value1.text and value1.text != 'not in MathModDB':
                options.extend([{'id': value1.external_id, 'text': value1.text}])

        for idx, value4 in enumerate(values4):
            if value4.option == Option.objects.get(uri=self.mathmoddb['QuantityClass']):
                for idx, value2 in enumerate(values2):
                    if value2.text and value4.set_prefix == value2.set_prefix:
                        Id,label,quote = value2.external_id.split(' <|> ')
                        options.extend([{'id': f"{Id} <|> {label} <|> Quantity", 'text': f"{label} (Quantity)"}])
                for idx, value3 in enumerate(values3):
                    if value3.text and value4.set_prefix == value3.set_prefix:
                        options.extend([{'id': f"{idx} <|> {value3.text} <|> Quantity", 'text': f"{value3.text} (Quantity)"}])
            elif value4.option == Option.objects.get(uri=self.mathmoddb['QuantityKindClass']):
                for idx, value2 in enumerate(values2):
                    if value2.text and value4.set_prefix == value2.set_prefix:
                        Id,label,quote = value2.external_id.split(' <|> ')
                        options.extend([{'id': f"{Id} <|> {label} <|> QuantityKind", 'text': f"{label} (Quantity Kind)"}])
                for idx, value3 in enumerate(values3):
                    if value3.text and value4.set_prefix == value3.set_prefix:
                        options.extend([{'id': f"{idx} <|> {value3.text} <|> QuantityKind", 'text': f"{value3.text} (Quantity Kind)"}])

        # Sort user options by text
        options = sorted(options, key=lambda option: option['text'])

        return options

class WorkflowTask(Provider):

    def get_options(self, project, search=None):

        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3/Set_0/Wiki_01'))

        model = ''
        options = []

        for value1 in values1:
            if value1.text:
                model = f":{value1.external_id.split(' <|> ')[0].split('#')[1]}"
        
        if model:
            # Fetch tasks from the MathModDB knowledge graph
            results = queryMathModDB(queryProvider['RT'].format(model))

            options.extend([{'id': f"{result['answer']['value']} <|> {result['label']['value']}", 'text': result['label']['value']} for result in results])      
        
        return options

class Task(Provider):

    search = True

    def get_options(self, project, search=None):

        options = MathModDBProvider(search,queryProvider['T'])
        
        return options

class Task2(Provider):

    search = True

    def get_options(self, project, search=None):

        if not search:
            return []
        
        # Fetch mathematical models from the MathModDB knowledge graph
        results = queryMathModDB(queryProvider['T'])
        
        # Extract options from the knowledge graph
        dic = {}
        options = []
        
        for result in results:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

        # Fetch user-defined research fields from the project
        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_6/Set_0/Question_0'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_6/Set_0/Question_1'))

        for value1 in values1: 
            if value1.text:
                dic.update({value1.text: {'id': value1.external_id}})

        for idx, value2 in enumerate(values2): 
            if value2.text:
                dic.update({value2.text: {'id': f"{idx} <|> {value2.text}"}})

        options.extend([{'id': f"{dic[key]['id']} <|> {key}", 'text': key } for key in dic if search.lower() in key.lower()])

        options = sorted(options, key=lambda option: option['text'])

        return options

class AllEntities(Provider):

    path = os.path.join(os.path.dirname(__file__), 'data', 'mathmoddb.json')

    with open(path, "r") as json_file:
        mathmoddb = json.load(json_file)

    def get_options(self, project, search=None):
        options =[]

        values1 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3/Set_0/Set_0/Question_04'))
        values2 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_0/Question_3'))
        values3 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_0/Question_0'))
        values4 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3/Set_0/Set_0/Question_05'))
        values5 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_1/Question_5'))
        values6 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_1/Question_0'))
        values9 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Question_0'))
        values10 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Set_1/Question_0'))
        values11 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_2/Set_1/Question_1'))
        values12 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3/Set_0/Set_0/Question_07'))
        values13 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_5'))
        values14 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_0'))
        values15 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_5/Question_0'))
        values16 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_5/Set_4/Question_0'))
        values17 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_5/Set_4/Question_1'))
        values18 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_6/Question_0'))
        values19 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_6/Set_0/Question_0'))
        values20 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_6/Set_0/Question_1'))
        values21 = project.values.filter(snapshot=None, attribute=Attribute.objects.get(uri=f'{BASE_URI}Section_3a/Set_3/Question_6'))

        for idx, value1 in enumerate(values1):
            if value1.text and value1.text != 'not in MathModDB':
                options.append({'id': f"{value1.external_id} <|> ResearchField <|> RF",'text': f"{value1.text} (Research Field)"})
        for idx, value2 in enumerate(values2):
            if value2.text:
                options.append({'id': f"{value2.external_id.split(' <|>')[:2]} <|> ResearchField <|> RF",'text': f"{value2.text} (Research Field)"})
        for idx, value3 in enumerate(values3):
            if value3.text:
                options.append({'id': f"RF{str(idx+1)} <|> {value3.text} <|> ResearchField <|> RF",'text': f"{value3.text} (Research Field)"})
        for idx, value4 in enumerate(values4):
            if value4.text and value4.text != 'not in MathModDB':
                options.append({'id': f"{value4.external_id} <|> ResearchProblem <|> RP",'text': f"{value4.text} (Research Problem)"})
        for idx, value5 in enumerate(values5):
            if value5.text:
                options.append({'id': f"{' <|> '.join(value5.external_id.split(' <|>')[:2])} <|> ResearchProblem <|> RP",'text': f"{value5.text} (Research Problem)"})
        for idx, value6 in enumerate(values6):
            if value6.text:
                options.append({'id': f"RP{str(idx+1)} <|> {value6.text} <|> ResearchProblem <|> RP",'text': f"{value6.text} (Research Problem)"})
        for idx, value9 in enumerate(values9):
            if value9.text:
                options.append({'id': f"{value9.external_id} <|> MathematicalModel <|> MM",'text': f"{value9.text} (Mathematical Model)"})
        for idx, value10 in enumerate(values10):
            if value10.text:
                options.append({'id': f"{' <|> '.join(value10.external_id.split(' <|>')[:2])} <|> MathematicalModel <|> MM",'text': f"{value10.text} (Mathematical Model)"})
        for idx, value11 in enumerate(values11):
            if value11.text:
                options.append({'id': f"MM{str(idx+1)} <|> {value11.text} <|> MathematicalModel <|> MM",'text': f"{value11.text} (Mathematical Model)"})
        for idx, value12 in enumerate(values12):
            if value12.text and value12.text != 'not in MathModDB':
                Id,label,qqk = value12.external_id.split(' <|> ')
                if qqk == 'Quantity':
                    options.append({'id':f"{Id} <|> {label} <|> Quantity <|> QQK",'text':f"{label} (Quantity)"})
                elif qqk == 'QuantityKind':
                    options.append({'id':f"{Id} <|> {label} <|> QuantityKind <|> QQK",'text':f"{label} (Quantity Kind)"})    
        for idx, value21 in enumerate(values21):
            if value21.option == Option.objects.get(uri=self.mathmoddb['QuantityClass']):
                for idx, value13 in enumerate(values13):
                    if value13.text and value21.set_prefix == value13.set_prefix:
                        Id,label,quote = value13.external_id.split(' <|> ')
                        options.append({'id': f"{' <|> '.join(value13.external_id.split(' <|>')[:2])} <|> Quantity <|> QQK",'text': f"{label} (Quantity)"})
                for idx, value14 in enumerate(values14):
                    if value14.text and value21.set_prefix == value14.set_prefix:
                        options.append({'id': f"QQK{str(idx+1)} <|> {value14.text} <|> Quantity <|> QQK",'text': f"{value14.text} (Quantity)"})
            elif value21.option == Option.objects.get(uri=self.mathmoddb['QuantityKindClass']):
                for idx, value13 in enumerate(values13):
                    if value13.text and value21.set_prefix == value13.set_prefix:
                        Id,label,quote = value13.external_id.split(' <|> ')
                        options.append({'id': f"{' <|> '.join(value13.external_id.split(' <|>')[:2])} <|> QuantityKind <|> QQK",'text': f"{label} (Quantity Kind)"})
                for idx, value14 in enumerate(values14):
                    if value14.text and value21.set_prefix == value14.set_prefix:
                        options.append({'id': f"QQK{str(idx+1)} <|> {value14.text} <|> QuantityKind <|> QQK",'text': f"{value14.text} (Quantity Kind)"})
        for idx, value15 in enumerate(values15):
            if value15.text and value15.text != 'not in MathModDB':
                options.append({'id': f"{value15.external_id} <|> MathematicalFormulation <|> MF",'text': f"{value15.text} (Mathematical Formulation)"})
        for idx, value16 in enumerate(values16):
            if value16.text:
                options.append({'id': f"{' <|> '.join(value16.external_id.split(' <|>')[:2])} <|> MathematicalFormulation <|> MF",'text': f"{value16.text} (Mathematical Formulation)"})
        for idx, value17 in enumerate(values17):
            if value17.text:
                options.append({'id': f"MF{str(idx+1)} <|> {value17.text} <|> MathematicalFormulation <|> MF",'text': f"{value17.text} (Mathematical Formulation)"})
        for idx, value18 in enumerate(values18):
            if value18.text and value18.text != 'not in MathModDB':
                options.append({'id': f"{value18.external_id} <|> Task <|> T",'text': f"{value18.text} (Task)"})
        for idx, value19 in enumerate(values19):
            if value19.text:
                options.append({'id': f"{' <|> '.join(value19.external_id.split(' <|>')[:2])} <|> Task <|> T",'text': f"{value19.text} (Task)"})
        for idx, value20 in enumerate(values20):
            if value20.text:
                options.append({'id': f"T{str(idx+1)} <|> {value20.text} <|> Task <|> T",'text': f"{value20.text} (Task)"})
        
        return options


def query_api(api_url, search_term):
    '''Function to query an API and return the JSON response.'''
    response = requests.get(api_url, params={
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'type': 'item',
        'limit': 10,
        'search': search_term
    }, headers={'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'})
    return response.json().get('search', [])

def process_result(result, location):
    '''Function to process the result and return a dictionary with id, text, and description.'''
    try:
        description = result['display']['description']['value']
    except (KeyError, TypeError):
        description = 'No Description Provided!'
    return {
         'id': f"{location}:{result['id']} <|> {result['display']['label']['value']} <|> {description}",
         'text': f"{result['display']['label']['value']} ({description})"
    }

def get_attribute(uri):
    """
    Retrieve attribute object based on URI.
    """
    try:
        return Attribute.objects.get(uri=uri)
    except Attribute.DoesNotExist:
        return None

def get_attribute_values(project, attribute):
    """
    Retrieve values for a given attribute in a project.
    """
    if attribute:
        return project.values.filter(snapshot=None, attribute=attribute)
    return []

def add_options(options, values, start_index, process_text_fn=None):
    """
    Add options to the list based on values.
    """
    for index, value in enumerate(values, start=start_index):
        if value.text or value.external_id:
            if value.external_id:
                text = value.external_id
            else:
                text = value.text
            if process_text_fn:
                text = process_text_fn(text)
            options.append({'id': f'Environment{index}', 'text': text})
    return options

def MathModDBProvider(search,query):
    """
    Dynamic query of MathModDB, results as options for Provider.
    """
    if not search:
        return []

    # Fetch results from the MathModDB knowledge graph
    results = queryMathModDB(query)
    
    dic = {}
    options = []
    
    # Store results in dict
    for result in results:
        if result.get('class',{}).get('value'):
            if result['class']['value'].split('#')[1] == 'Quantity':
                dic.update({f"{result['label']['value']} (Quantity)":{'id':f"{result['answer']['value']} <|> {result['label']['value']} <|> Quantity"}})
            elif result['class']['value'].split('#')[1] == 'QuantityKind':
                dic.update({f"{result['label']['value']} (Quantity Kind)":{'id':f"{result['answer']['value']} <|> {result['label']['value']} <|> QuantityKind"}})
        else:
            dic.update({result['label']['value']:{'id':result['answer']['value']}})

    # Filter results by user-defined search
    options.extend([{'id': f"{dic[key]['id']} <|> {key}" if len(dic[key]['id'].split(' <|> ')) == 1 else dic[key]['id'], 'text': key } for key in dic if search.lower() in key.lower()])

    # Add 'not in MathModDB' option
    options = [{'id': 'not in MathModDB', 'text': 'not in MathModDB'}] + sorted(options, key=lambda option: option['text'])

    return options
