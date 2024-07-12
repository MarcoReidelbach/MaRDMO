# MaRDMO-Export-Plugin

This repository contains the MaRDMO-Export-Plugin for the [Research Datamanagement Organizer](https://rdmorganiser.github.io/) (RDMO) developed within Task Area 4 "Interdisciplinary Mathematics" of the [Mathematical Research Data Initiative](https://www.mardi4nfdi.de/about/mission) (MaRDI). The plugin allows a standardized documentation of interdisciplinary workflows (Math + X), where the connection to experiments or theoretical approaches, like simulations, is possible and desired. Documented workflows can be stored locally (depreciated) or shared with other scientists on the [MaRDI Portal](https://portal.mardi4nfdi.de/wiki/Portal). In the latter case a Wiki Page is created for the documented workflow and integral aspects of the workflow are integrated into the MaRDI knowledge grarph. Integration into the MaRDI knowledge graph allows specific workflow queries which are also possible through the MaRDMO plugin.

To document the underlying mathematical model(s) MaRDMO relies on the [MathModDB](https://portal.mardi4nfdi.de/wiki/MathModDB) ontology developed within Task Area 4 of MaRDI. Existing model documentations are retrieved from the MathModDB Knowledge Graph, direct publication of documented models into the MathModDB Knowledge Graph will be enabled in the near future. So far, documented models can only be exported into a Model Documentation Template. Upon request these documentations will be reviewed and integrated into the Knowledge Graph. Model documentations are possible as part of the workflow documentation and individually. 

## Structure of MaRDMO-Export-Plugin directory

```bash
.  
├── MaRDMO - Plugin Files
│   ├── citation.py - get citation from DOI and ORCID API
│   ├── apps.py - application configuration
│   ├── handlers.py - Additional Functions in background upon click 
│   ├── config.py - MaRDI portal information (API,SPARQL endpoint)
│   ├── export.py - Export/Query Function 
│   ├── id.py - wikibase item and property ids 
│   ├── para.py - Export/Query Parameters
│   ├── providers.py - Dynamic Option Sets via Wikidata / MaRDI KG
│   ├── sparql.py - SPARQL query selection
│   ├── templates
│   │   ├── workflowError.html - HTML Template for MaRDMO Errors
│   │   ├── workflowExport.html - HTML Template for MaRDMO Export
│   │   ├── workflowTemplate.html - HTML Template for Workflow Documentation
│   │   ├── workflowTemplate.md - Markdown Template for Workflow Documentation
│   │   ├── workflowTemplate.mediawiki - Mediawiki Template for Workflow Documentation
│   │   ├── workflowSearch.html - HTML Template for MaRDMO Search
│   │   └── modelTemplate.md - Markdown Template for Model Documentation
│   └── data
│       ├── lang.json - Language Classification
│       └── msc2020.json - Mathematics Subject Classification 2020
├── setup.py 
│
├── README.md
│ 
└── LICENSE.md 
```
  
## MaRDMO-Export-Plugin Installation

To use the MaRDMO-Export-Plugin at least `RDMO v2.0.0` is required. Follow the installation / update instructions of [RDMO](https://rdmo.readthedocs.io/en/latest/installation) if required. 

Go to the `rdmo-app` directory of your RDMO installation. In the virtual environment of the RDMO installation install the MaRDMO-Export-Plugin:

```bash
pip install git+https://github.com/MarcoReidelbach/MaRDMO-Export-Plugin
```

To connect the MaRDMO-Export-Plugin with the RDMO installation add the following lines to `config/settings/local.py` (if not already present):

```python
from django.utils.translation import gettext_lazy as _ 
``` 

```python
INSTALLED_APPS = ['MaRDMO'] + INSTALLED_APPS

PROJECT_EXPORTS += [
        ('mde', _('MaRDI Export/Query'), 'MaRDMO.export.MaRDIExport'),
        ]

OPTIONSET_PROVIDERS = [
    ('WikidataSearch', _('Options for Wikidata Search'), 'MaRDMO.providers.WikidataSearch'),
    ('ComponentSearch', _('Options for MaRDI Search'), 'MaRDMO.providers.ComponentSearch'),
    ('MSCProvider', _('Options for MSC Search'), 'MaRDMO.providers.MSCProvider'),
    ('ProcessorProvider', _('Options for Processor Search'), 'MaRDMO.providers.ProcessorProvider'),
    ('AvailableSoftware', _('Options for Available Software'), 'MaRDMO.providers.AvailableSoftware'),
    ('MathAreaProvider', _('Options for Math Areas'), 'MaRDMO.providers.MathAreaProvider'),
    ('EnvironmentProvider', _('Options for Environments'), 'MaRDMO.providers.EnvironmentProvider'),
    ('MethodProvider', _('Options for Methods'), 'MaRDMO.providers.MethodProvider'),
    ('DataProvider', _('Options for Data Sets'), 'MaRDMO.providers.DataProvider'),
    ('SoftwareProvider', _('Options for Software'), 'MaRDMO.providers.SoftwareProvider'),
    ('ResearchField', _('Options for Research Fields'), 'MaRDMO.providers.ResearchField'),
    ('ResearchFieldRelations', _('Options for Research Field Relations'), 'MaRDMO.providers.ResearchFieldRelations'),
    ('ResearchProblem', _('Options for Research Problems'), 'MaRDMO.providers.ResearchProblem'),
    ('ResearchFieldUser', _('Options for User Research Fields'), 'MaRDMO.providers.ResearchFieldUser'),
    ('ResearchProblemRelations', _('Options for Research Problem Relations'), 'MaRDMO.providers.ResearchProblemRelations'),
    ('MathematicalModel', _('Options for Mathematical Models'), 'MaRDMO.providers.MathematicalModel'),
    ('MathematicalModelRelation', _('Options for Mathematical Model Relations'), 'MaRDMO.providers.MathematicalModelRelation'),
    ('MathematicalModelRelation2', _('Options for Mathematical Model Relations 2'), 'MaRDMO.providers.MathematicalModelRelation2'),
    ('Quantity', _('Options for Quantities'), 'MaRDMO.providers.Quantity'),
    ('QuantityRelations', _('Options for Quantity Relations'), 'MaRDMO.providers.QuantityRelations'),
    ('QuantityKindRelations', _('Options for Quantity Kind Relations'), 'MaRDMO.providers.QuantityKindRelations'),
    ('MathematicalFormulation', _('Options for Mathematical Formulation'), 'MaRDMO.providers.MathematicalFormulation'),
    ('MathematicalFormulation2', _('Options for Mathematical Formulation 2'), 'MaRDMO.providers.MathematicalFormulation2'),
    ('QuantityAll', _('Options for all Quantities'), 'MaRDMO.providers.QuantityAll'),
    ('WorkflowTask', _('Options for Workflow Task'), 'MaRDMO.providers.WorkflowTask'),
    ('Task', _('Options for Task'), 'MaRDMO.providers.Task'),
    ('Task2', _('Options for Task2'), 'MaRDMO.providers.Task2'),
    ('Publication', _('Options for Publications'), 'MaRDMO.providers.Publication'),
    ('AllEntities', _('Options for All Entities'), 'MaRDMO.providers.AllEntities')
    ]


```

Thereby, the MaRDMO-Export-Plugin is installed and a "MaRDI Export/Query" button is added in the project view.

## MaRDI Portal Connection

To add data to the MaRDI Portal, so far, a login is required. In the MaRDMO-Export-Plugin this is facilitated using a bot. To set up the bot visit the MaRDI Portal, log in with your user credentials, choose `Special Pages` and `Bot passwords`. Provide a name for the new bot, select `Create`, grant the bot permission for `High-volume (bot) access`, `Edit existing pages` and `Create, edit, and move pages` and select again `Create`. Thereby, a bot is created. Add its credentials to `config/settigs/local.py`:

```python
lgname = 'username@botname'
lgpassword = 'password'
```

Workflow search and local documentations are possible without login credentials. Non-MaRDI users may contact the owner of the repository to facilitate the login for MaRDI portal publication.

## MaRDMO-Questionnaire        

The MaRDMO-Export-Plugin requires the [MaRDMO-Questionnaire](https://github.com/MarcoReidelbach/MaRDMO-Questionnaire). To get the Questionnaire clone the repository to an appropriate location: 

```bash
git clone https://github.com/MarcoReidelbach/MaRDMO-Questionnaire.git
```

Integrate the MaRDMO-Questionnaire into your RDMO instance through the user interface of your RDMO instance (`Management -> Import -> attributes.xml/optionsets.xml/conditions.xml/catalogs.xml`) or via 

```bash
python manage.py import /path/to/MaRDMO-Questionnaire/catalog/attributes.xml
python manage.py import /path/to/MaRDMO-Questionnaire/catalog/optionsets.xml
python manage.py import /path/to/MaRDMO-Questionnaire/catalog/conditions.xml
python manage.py import /path/to/MaRDMO-Questionnaire/catalog/catalogs.xml
```

## Usage of MaRDMO-Export-Plugin

Once the MaRDMO-Export-Plugin is set up, the Questionnaire can be used to document and query interdisciplinary workflows. Therefore, select "Create New Project" in RDMO, choose a proper project name (project name will be used as wokflow name and label in the MaRDI portal), assign the "MaRDI Workflow Documentation" catalog and select "Create Project". The project is created. On the right hand side in the "Export" category the "MaRDI Export/Query" button is located to process the completed Questionnaire.     

Choose "Answer Questions" to start the interview. With the first question the Operation Modus of the MaRDMO-Export-Plugin is determined:

1) Choose **"Workflow Documentation"** and click on "Save and proceed". Next, decide whether the completed Questionnaire should be exported locally or publicly to the MaRDI Portal. If a public export is desired a preview of the rendered Wiki Page could be displayed. Please, check the preview before publishing the workflow on the MaRDI Portal. Once the general settings are completed the workflow will be documented by providing general information, model information, process information and reproducibility information. Upon completion return to the project page and choose "MaRDI Export/Query" to compile the answers and return it in the desired format. 

2) Choose **"Workflow Search"** and click on "Save and proceed". Next, choose by which components (keywords of research objective, associated research disciplines, and applied mathematical models, methods, software, input or output data sets) existing workflow documentations should be searched and specify the component. Once completed, return to the project page and choose "MaRDI Export/Query". If appropriate workflow documentations are located on the MaRDI Portal, the title of the workflow and links to the corresponding Wiki Page and Knowledge Graph entry are provided.

