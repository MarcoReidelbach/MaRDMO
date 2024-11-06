import re
import requests

from rdmo.projects.models import Value
from rdmo.domain.models import Attribute
from rdmo.options.models import Option

from .config import BASE_URI, mardi_api, mathmoddb_endpoint

def add_new_mathmoddb_entries_to_questionnaire(project, ids, query):
    '''Request IDs for new MathModDB Items and add them to the Questionnaire'''
    for key, id_value in ids.items():
        # Identify Items missing a MathModDB ID
        if not id_value.startswith('https://mardi4nfdi.de/mathmoddb#'):
            # Get MathModDB ID
            results = query_sparql(query.format(f"'{key}'"))
            if results and results[0].get('ID', {}).get('value'):
                match = re.match(r"(\d+)(\D+)", id_value)
                if not match:
                    continue
                setID, setName = match.groups()
                # Add retreived MathModDB ID to Items
                label = key
                if setName == 'Quantity':
                    # Handle Quantity specifics
                    qc = results[0].get('qC', {}).get('value', '').split('#')[1]
                    label = f"{key} (Quantity Kind)" if qc == 'QuantityKind' else f"{key} (Quantity)"
                    value = f"{results[0]['ID']['value']} <|> {label} <|> {qc}"
                else:
                    # General case
                    value = f"{results[0]['ID']['value']} <|> {label}"
                
                print(BASE_URI,setName,f"{BASE_URI}domain/{setName}MathModDBID")
                # Call valueEditor with constructed values
                value_editor(project, f"{BASE_URI}domain/{setName}MathModDBID", label, value, None, None, setID)

def extract_parts(string):
    # Split string into Name, Description and Source
    pattern = r'^(.*?)\s*\((.*)\)\s*\[(.*)\]$'
    match = re.match(pattern, string)
    if match:
        name, description, source = match.groups()
        return name.strip(), description.strip(), source.strip()    
    return None, None, None

def find_item(label, description, api=mardi_api, language="en"):
    '''API request returning an Item with matching label and description.'''
    data = query_api(api,label)
    # Filter results based on description
    matched_items = [item for item in data if item.get('description') == description]
    if matched_items:
        # Return the ID of the first matching item
        return matched_items[0]['id']
    else:
        # No matching item found
        return None
    
def query_api(api_url, search_term):
    '''API requests returning all Items with matching label'''
    response = requests.get(api_url, params={
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'type': 'item',
        'limit': 10,
        'search': search_term
    }, headers={'User-Agent': 'MaRDMO_0.1 (https://zib.de; reidelbach@zib.de)'})
    return response.json().get('search', [])

def query_sparql(query,endpoint=mathmoddb_endpoint):
    '''SPARQL request returning all Items with matching properties.'''
    response = requests.post(endpoint,
                             data=query,
                             headers={"Content-Type": "application/sparql-query","Accept": "application/sparql-results+json"}
                            )
    # Check if request was successfull
    if response.status_code == 200:
        req = response.json().get('results',{}).get('bindings',[])
    else:
        req = []

    return req

def value_editor(project, uri, text=None, external_id=None, option=None, collection_index=None, set_index=None, set_prefix=None):
    '''Add values to the Questionnaire'''
    attribute_object = Attribute.objects.get(uri=uri)

    # Prepare the defaults dictionary
    defaults = {
        'project': project,
        'attribute': attribute_object,
    }

    if text is not None:
        defaults['text'] = text

    if external_id is not None:
        defaults['external_id'] = external_id

    if option is not None:
        defaults['option'] = Option.objects.get(uri=option)

    # Prepare the fields for update_or_create
    update_fields = {
        'project': project,
        'attribute': attribute_object,
        'defaults': defaults
    }

    if collection_index is not None:
        update_fields['collection_index'] = collection_index

    if set_index is not None:
        update_fields['set_index'] = set_index

    if set_prefix is not None:
        update_fields['set_prefix'] = set_prefix

    # Update or create the value
    obj, created = Value.objects.update_or_create(**update_fields)

    return obj, created
