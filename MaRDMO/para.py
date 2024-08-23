BASE = 'https://rdmo.mardi4nfdi.de/terms/'
BASE_URI = f'{BASE}domain/'
BASE_OPT = f'{BASE}options/'

# Option Dictionary

option = {'YesText': 'https://rdmorganiser.github.io/terms/options/yes_with_text_no/yes',
          'NoText': 'https://rdmorganiser.github.io/terms/options/yes_with_text_no/no',
          'TaskInput': 'https://rdmo.mardi4nfdi.de/terms/options/QuantityAndQuantityKind_kind0',
          'TaskOutput': 'https://rdmo.mardi4nfdi.de/terms/options/QuantityAndQuantityKind_kind1',
          'TaskParameter': 'https://rdmo.mardi4nfdi.de/terms/options/QuantityAndQuantityKind_kind3',
          'Documentation': 'https://rdmo.mardi4nfdi.de/terms/options/operation_modus/modus_0',
          'Search': 'https://rdmo.mardi4nfdi.de/terms/options/operation_modus/modus_1',
          'Local': 'https://rdmo.mardi4nfdi.de/terms/options/publication_type/type_1',
          'Public': 'https://rdmo.mardi4nfdi.de/terms/options/publication_type/type_0',
          'No': 'https://rdmo.mardi4nfdi.de/terms/options/yes_no/no',
          'Yes': 'https://rdmo.mardi4nfdi.de/terms/options/yes_no/yes',
          'Analysis': 'https://rdmo.mardi4nfdi.de/terms/options/workflow_type/type_0',
          'Computation': 'https://rdmo.mardi4nfdi.de/terms/options/workflow_type/type_1',
          'Small': 'https://rdmo.mardi4nfdi.de/terms/options/size/KB',
          'Medium': 'https://rdmo.mardi4nfdi.de/terms/options/size/MB',
          'Large': 'https://rdmo.mardi4nfdi.de/terms/options/size/GB',
          'VeryLarge': 'https://rdmo.mardi4nfdi.de/terms/options/size/TB',
          'Binary': 'https://rdmo.mardi4nfdi.de/terms/options/data_type/type_0',
          'Text': 'https://rdmo.mardi4nfdi.de/terms/options/data_type/type_1',
          'Workflow': 'https://rdmo.mardi4nfdi.de/terms/options/operation_modus_2/workflow',
          'Model': 'https://rdmo.mardi4nfdi.de/terms/options/operation_modus_2/model',
          'English': 'https://rdmo.mardi4nfdi.de/terms/options/languages/english',
          'German': 'https://rdmo.mardi4nfdi.de/terms/options/languages/german'}

# Operation Modus

OperationModus = {

            'WorkflowOrModel': {

                'mod': [f'{BASE_URI}Section_3/Set_0', f'{BASE_URI}Section_3a/Set_0_hidden', 
                        f'{BASE_URI}Section_3a/Set_1_hidden', f'{BASE_URI}Section_3a/Set_2_hidden', 
                        f'{BASE_URI}Section_3a/Set_3_hidden', f'{BASE_URI}Section_3a/Set_5_hidden', 
                        f'{BASE_URI}Section_3a/Set_6_hidden', f'{BASE_URI}Section_3a/Set_7_hidden'],
        
                'doc': [f'{BASE_URI}Section_2/Set_1', f'{BASE_URI}Section_2/Set_3',
                        f'{BASE_URI}Section_3a/Set_8_hidden', f'{BASE_URI}Section_4/Set_3_hidden',
                        f'{BASE_URI}Section_4/Set_4_hidden', f'{BASE_URI}Section_4/Set_5_hidden',
                        f'{BASE_URI}Section_4/Set_6_hidden', f'{BASE_URI}Section_4/Set_2_hidden',
                        f'{BASE_URI}Section_4/Set_1_hidden', f'{BASE_URI}Section_5/Set_1'],
        
                'ide': [f'{BASE_URI}Section_0a/Set_1'],

                'pub': [f'{BASE_URI}Section_2/Set_2'],
        
                'exp': [f'{BASE_URI}Section_6/Set_1']

                },

            'SearchOrDocument': {
                
                'sea': [f'{BASE_URI}Section_1/Set_1'],

                'doc': [f'{BASE_URI}Section_2/Set_1',f'{BASE_URI}Section_2/Set_3',
                        f'{BASE_URI}Section_3/Set_0',f'{BASE_URI}Section_4/Set_3_hidden',
                        f'{BASE_URI}Section_4/Set_4_hidden',f'{BASE_URI}Section_4/Set_5_hidden',
                        f'{BASE_URI}Section_4/Set_6_hidden',f'{BASE_URI}Section_4/Set_2_hidden',
                        f'{BASE_URI}Section_4/Set_1_hidden',f'{BASE_URI}Section_5/Set_1',
                        f'{BASE_URI}Section_3a/Set_0_hidden',f'{BASE_URI}Section_3a/Set_1_hidden',
                        f'{BASE_URI}Section_3a/Set_2_hidden',f'{BASE_URI}Section_3a/Set_3_hidden',
                        f'{BASE_URI}Section_3a/Set_5_hidden',f'{BASE_URI}Section_3a/Set_6_hidden',
                        f'{BASE_URI}Section_3a/Set_7_hidden',f'{BASE_URI}Section_3a/Set_8_hidden',
                        f'{BASE_URI}Section_6/Set_1'],
        
                'ide': [f'{BASE_URI}Section_0a/Set_1'],
        
                'pub': [f'{BASE_URI}Section_2/Set_2']
            
                },

            'ComputationalOrExperimental': {
                
                'doc': [f'{BASE_URI}Section_2/Set_1',f'{BASE_URI}Section_3/Set_0',
                        f'{BASE_URI}Section_3a/Set_0_hidden',f'{BASE_URI}Section_3a/Set_1_hidden',
                        f'{BASE_URI}Section_3a/Set_2_hidden',f'{BASE_URI}Section_3a/Set_3_hidden',
                        f'{BASE_URI}Section_3a/Set_5_hidden',f'{BASE_URI}Section_3a/Set_6_hidden',
                        f'{BASE_URI}Section_3a/Set_7_hidden',f'{BASE_URI}Section_3a/Set_8_hidden',
                        f'{BASE_URI}Section_4/Set_3_hidden',f'{BASE_URI}Section_4/Set_6_hidden',
                        f'{BASE_URI}Section_4/Set_2_hidden',f'{BASE_URI}Section_4/Set_1_hidden',
                        f'{BASE_URI}Section_5/Set_1',f'{BASE_URI}Section_6/Set_1'],
                
                'com': [f'{BASE_URI}Section_4/Set_4_hidden'],
        
                'exp': [f'{BASE_URI}Section_4/Set_5_hidden']
            
                }

            }

# Mappings

dataPropertyMapping = {'Mathematical Model': {
                     'convex': (0, 'IsConvex', 1, 'IsNotConvex'),
                     'deterministic': (2, 'IsDeterministic', 3, 'IsStochastic'),
                     'dimensionless': (4, 'IsDimensionless', 5, 'IsDimensional'),
                     'dynamic': (6, 'IsDynamic', 7, 'IsStatic'),
                     'linear': (8, 'IsLinear', 9, 'IsNotLinear'),
                     'spacecont': (10, 'IsSpaceContinuous', 11, 'IsSpaceDiscrete', 12, 'IsSpaceIndependent'),
                     'timecont': (13, 'IsTimeContinuous', 14, 'IsTimeDiscrete', 15, 'IsTimeIndependent')
                        },
                   'Mathematical Formulation': {
                     'convex': (0, 'IsConvex', 1, 'IsNotConvex'),
                     'deterministic': (2, 'IsDeterministic', 3, 'IsStochastic'),
                     'dimensionless': (4, 'IsDimensionless', 5, 'IsDimensional'),
                     'dynamic': (6, 'IsDynamic', 7, 'IsStatic'),
                     'linear': (8, 'IsLinear', 9, 'IsNotLinear'),
                     'spacecont': (10, 'IsSpaceContinuous', 11, 'IsSpaceDiscrete', 12, 'IsSpaceIndependent'),
                     'timecont': (13, 'IsTimeContinuous', 14, 'IsTimeDiscrete', 15, 'IsTimeIndependent')
                        },
                   'Task': {
                     'linear': (0, 'IsLinear', 1, 'IsNotLinear'),
                        },
                   'Quantity': {
                     'qdimensionless': (0, 'IsDimensionless', 1, 'IsDimensional'),
                     'qlinear': (2, 'IsLinear', 3, 'IsNotLinear')
                        },
                   'Quantity Kind': {
                     'qdimensionless': (0, 'IsDimensionless', 1, 'IsDimensional'),
                        }
                  }

objectPropertyMapping = {'IntraClassRelations': {
                      'GeneralizedBy': ('GB', 'GBL', 'GBC'),
                      'Generalizes': ('G', 'GL', 'GC'),
                      'ApproximatedBy': ('AB', 'ABL', 'ABC'),
                      'Approximates': ('A', 'AL', 'AC'),
                      'DiscretizedBy': ('DB', 'DBL', 'DBC'),
                      'Discretizes': ('D', 'DL', 'DC'),
                      'LinearizedBy': ('LB', 'LBL', 'LBC'),
                      'Linearizes': ('L', 'LL', 'LC'),
                      'NondimensionalizedBy': ('NB', 'NBL', 'NBC'),
                      'Nondimensionalizes': ('N', 'NL', 'NC'),
                      'SimilarTo': ('S', 'SL', 'SC')
                        },
                    'ContainsQQKRelations': {
                      'ContainsInput': ('IN','INL','INC'),
                      'ContainsOutput': ('O','OL','OC'),
                      'ContainsObjective': ('OB','OBL','OBC'),
                      'ContainsParameter': ('PA','PAL','PAC'),
                      'ContainsConstant': ('CO','COL','COC')
                        },
                    'ContainsMFRelations': {
                      'ContainsFormulation': ('F','FL'),
                      'ContainsAssumption': ('A','AL'),
                      'ContainsBoundaryCondition': ('BC','BCL'),
                      'ContainsConstraintCondition': ('CC','CCL'),
                      'ContainsCouplingCondition': ('CPC','CPCL'),
                      'ContainsInitialCondition': ('IC','ICL'),
                      'ContainsFinalCondition': ('FC','FCL')
                        },
                    'PublicationRelation': {
                      'Documents': ('PU1','LABEL1'),
                      'Invents': ('PU2','LABEL2'),
                      'Studies': ('PU3','LABEL3'),
                      'Surveys': ('PU4','LABEL4'),
                      'Uses': ('PU5','LABEL5')
                        }
                }

inversePropertyMapping = {
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsAssumption': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsAssumptionIn',
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsBoundaryCondition': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsBoundaryConditionIn',
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsConstraintCondition': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsConstraintConditionIn',
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsCouplingCondition': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsCouplingConditionIn',
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsFormulation': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsFormulationIn',
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsInitialCondition': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsInitialConditionIn',
                       'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainsFinalCondition': 'https://rdmo.mardi4nfdi.de/terms/options/MathModDB/ContainedAsFinalConditionIn',
                      }

# Answer Dictionary

uNames =['Settings', 'GeneralInformation', 'Creator', 'ProcessStep', 'Publication', 'Models', 'Software', 'Hardware', 'ExperimentalDevice', 'MathematicalArea', 'NonMathematicalDiscipline',
         'DataSet', 'Method', 'Quantity', 'Task', 'ReproducibilityComputational', 'ReproducibilityAnalysis', 'Search', 'ResearchField', 'ResearchProblem', 'MathematicalModel',
         'MathematicalFormulation', 'PublicationModel', 'SpecificTask']

questions = {# Export and Workflow Settings
              uNames[0]+' Documentation': {'uName':uNames[0],'dName':'Documentation','Id': BASE_URI+'Section_0/Set_1/Question_01', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[0]+' DocumentationType': {'uName':uNames[0],'dName':'DocumentationType','Id': BASE_URI+'Section_0/Set_1/Question_02', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[0]+' Public': {'uName':uNames[0],'dName':'Public','Id': BASE_URI+'Section_6/Set_1/Question_01', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[0]+' Preview': {'uName':uNames[0],'dName':'Preview','Id': BASE_URI+'Section_6/Set_1/Question_02', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[0]+' WorkflowType': {'uName':uNames[0],'dName':'WorkflowType','Id': BASE_URI+'Section_2/Set_1/Question_03', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              # General Workflow Information
              uNames[1]+' ProblemStatement': {'uName':uNames[1],'dName':'ProblemStatement','Id': BASE_URI + 'Section_2/Set_1/Question_01', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[1]+' ResearchObjective': {'uName':uNames[1],'dName':'ResearchObjective','Id': BASE_URI + 'Section_2/Set_1/Question_04', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[1]+' Procedure': {'uName':uNames[1],'dName':'Procedure','Id': BASE_URI + 'Section_2/Set_1/Question_05', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[1]+' DataStream': {'uName':uNames[1],'dName':'DataStream','Id': BASE_URI + 'Section_2/Set_3/Question_02', 'set_prefix':False, 'set_index': False, 'collection_index': True},
              # Mathematical Area Information
              uNames[9]+' ID': {'uName':uNames[9],'dName':'ID','Id': BASE_URI+'Section_2/Set_3/Question_00', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              # Non-Mathematical Discipline Information
              uNames[10]+' ID': {'uName':uNames[10],'dName':'ID','Id': BASE_URI+'Section_2/Set_3/Question_01', 'set_prefix':False, 'set_index':True, 'collection_index':True, 'option_text':False, 'external_id':True},
              # Workflow Documentation Creator Information
              uNames[2]+' Name': {'uName':uNames[2],'dName':'Name','Id': BASE_URI + 'Section_0a/Set_1/Question_01', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[2]+' IDs': {'uName':uNames[2],'dName':'IDs','Id': BASE_URI + 'Section_0a/Set_1/Question_02', 'set_prefix':False, 'set_index': False, 'collection_index': True},
              # Related Publication Information
              uNames[4]+' Exists': {'uName':uNames[4],'dName':'Exists','Id': BASE_URI + 'Section_2/Set_1/Question_02', 'set_prefix':False, 'set_index': False, 'collection_index': False, 'option_text': True},
              uNames[4]+' All Authors': {'uName':uNames[4],'dName':'All Authors','Id': BASE_URI + 'Section_2/Set_2/Question_03', 'set_prefix':False, 'set_index': False, 'collection_index': True},
              uNames[4]+' Info': {'uName':uNames[4],'dName':'Info','Id': BASE_URI + 'Section_2/Set_2/Question_00_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Type': {'uName':uNames[4],'dName':'Type','Id': BASE_URI + 'Section_2/Set_2/Question_01_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Title': {'uName':uNames[4],'dName':'Title','Id': BASE_URI + 'Section_2/Set_2/Question_02_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Identified Authors': {'uName':uNames[4],'dName':'Identified Authors','Id':BASE_URI + 'Section_2/Set_2/Question_03_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': True},
              uNames[4]+' Language': {'uName':uNames[4],'dName':'Language','Id': BASE_URI + 'Section_2/Set_2/Question_04_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Journal': {'uName':uNames[4],'dName':'Journal','Id': BASE_URI + 'Section_2/Set_2/Question_05_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Volume': {'uName':uNames[4],'dName':'Volume','Id': BASE_URI + 'Section_2/Set_2/Question_06_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Issue': {'uName':uNames[4],'dName':'Issue','Id': BASE_URI + 'Section_2/Set_2/Question_07_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Pages': {'uName':uNames[4],'dName':'Pages','Id': BASE_URI + 'Section_2/Set_2/Question_08_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              uNames[4]+' Date': {'uName':uNames[4],'dName':'Date','Id': BASE_URI + 'Section_2/Set_2/Question_09_hidden', 'set_prefix':False, 'set_index': False, 'collection_index': False},
              # Model Information
              ## Main Model Info
              uNames[5]+' MathModID': {'uName':uNames[5],'dName':'MathModID','Id': BASE_URI+'Section_3/Set_0/Wiki_01', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[5]+' ID': {'uName':uNames[5],'dName':'ID','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_00', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[5]+' Name': {'uName':uNames[5],'dName':'Name','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_01', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[5]+' Description': {'uName':uNames[5],'dName':'Description','Id': BASE_URI+'Section_3/Set_0/Set_0/Wiki_02', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[5]+' Properties': {'uName':uNames[5],'dName':'Properties','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_02', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              uNames[5]+' Reference': {'uName':uNames[5],'dName':'Reference','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_03', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[5]+' Additional': {'uName':uNames[5],'dName':'Additional','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_06', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              ## Specific Task
              uNames[23]+' MathModID': {'uName':uNames[23],'dName':'MathModID','Id': BASE_URI+'Section_3/Set_0/Set_1/Question_0', 'set_prefix':False, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':True},
              ## Research Field
              uNames[18]+' MathModID': {'uName':uNames[18],'dName':'MathModID','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_04', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[18]+' ID': {'uName':uNames[18],'dName':'ID','Id': BASE_URI+'Section_3a/Set_0/Question_3', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[18]+' Name': {'uName':uNames[18],'dName':'Name','Id': BASE_URI+'Section_3a/Set_0/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[18]+' Description': {'uName':uNames[18],'dName':'Description','Id': BASE_URI+'Section_3a/Set_0/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[18]+' Reference': {'uName':uNames[18],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_0/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[18]+' Relation1': {'uName':uNames[18],'dName':'Relation1','Id': BASE_URI+'Section_3a/Set_0/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[18]+' Other1': {'uName':uNames[18],'dName':'Other1','Id': BASE_URI+'Section_3a/Set_0/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              #Research Problem
              uNames[19]+' MathModID': {'uName':uNames[19],'dName':'MathModID','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_05', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[19]+' ID': {'uName':uNames[19],'dName':'ID','Id': BASE_URI+'Section_3a/Set_1/Question_5', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[19]+' Name': {'uName':uNames[19],'dName':'Name','Id': BASE_URI+'Section_3a/Set_1/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[19]+' Description': {'uName':uNames[19],'dName':'Description','Id': BASE_URI+'Section_3a/Set_1/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[19]+' Reference': {'uName':uNames[19],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_1/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[19]+' ResearchField': {'uName':uNames[19],'dName':'ResearchField','Id': BASE_URI+'Section_3a/Set_1/Question_3', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':True},
              #uNames[19]+' Models': {'uName':uNames[19],'dName':'Models','Id': BASE_URI+'Section_3a/Set_1/Question_4', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[19]+' Relation1': {'uName':uNames[19],'dName':'Relation1','Id': BASE_URI+'Section_3a/Set_1/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[19]+' Other1': {'uName':uNames[19],'dName':'Other1','Id': BASE_URI+'Section_3a/Set_1/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              ## Additional Models
              uNames[20]+' MathModID': {'uName':uNames[20],'dName':'MathModID','Id': BASE_URI+'Section_3a/Set_2/Question_0', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[20]+' ID': {'uName':uNames[20],'dName':'ID','Id': BASE_URI+'Section_3a/Set_2/Set_1/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[20]+' Name': {'uName':uNames[20],'dName':'Name','Id': BASE_URI+'Section_3a/Set_2/Set_1/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[20]+' Description': {'uName':uNames[20],'dName':'Description','Id': BASE_URI+'Section_3a/Set_2/Set_1/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[20]+' Reference': {'uName':uNames[20],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_2/Set_1/Question_3', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[20]+' Properties': {'uName':uNames[20],'dName':'Properties','Id': BASE_URI+'Section_3a/Set_2/Set_1/Question_4', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[20]+' Main': {'uName':uNames[20],'dName':'Main','Id': BASE_URI+'Section_3a/Set_2/Question_1', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[20]+' ResearchProblem': {'uName':uNames[20],'dName':'ResearchProblem','Id': BASE_URI+'Section_3a/Set_2/Question_4', 'set_prefix':False, 'set_index':True, 'collection_index':True, 'option_text':False, 'external_id':True},
              uNames[20]+' IntraClassRelation': {'uName':uNames[20],'dName':'IntraClassRelation','Id': BASE_URI+'Section_3a/Set_2/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[20]+' IntraClassElement': {'uName':uNames[20],'dName':'IntraClassElement','Id': BASE_URI+'Section_3a/Set_2/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              ## Mathematical Formulation
              uNames[21]+' MathModID': {'uName':uNames[21],'dName':'MathModID','Id': BASE_URI+'Section_3a/Set_5/Question_0', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' Definition': {'uName':uNames[21],'dName':'Definition','Id': BASE_URI+'Section_3a/Set_5/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[21]+' DefinedQuantity': {'uName':uNames[21],'dName':'DefinedQuantity','Id': BASE_URI+'Section_3a/Set_5/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' ID': {'uName':uNames[21],'dName':'ID','Id': BASE_URI+'Section_3a/Set_5/Set_4/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' Name': {'uName':uNames[21],'dName':'Name','Id': BASE_URI+'Section_3a/Set_5/Set_4/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[21]+' Description': {'uName':uNames[21],'dName':'Description','Id': BASE_URI+'Section_3a/Set_5/Set_4/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[21]+' Reference': {'uName':uNames[21],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_5/Set_4/Question_3', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[21]+' Properties': {'uName':uNames[21],'dName':'Properties','Id': BASE_URI+'Section_3a/Set_5/Set_4/Question_4', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[21]+' Formula': {'uName':uNames[21],'dName':'Formula','Id': BASE_URI+'Section_3a/Set_5/Set_4/Question_5', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[21]+' Element Symbol': {'uName':uNames[21],'dName':'Element Symbol','Id': BASE_URI+'Section_3a/Set_5/Set_4/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[21]+' Element Quantity': {'uName':uNames[21],'dName':'Element Quantity','Id': BASE_URI+'Section_3a/Set_5/Set_4/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' Relation1': {'uName':uNames[21],'dName':'Relation1','Id': BASE_URI+'Section_3a/Set_5/Set_2/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' Other1': {'uName':uNames[21],'dName':'Other1','Id': BASE_URI+'Section_3a/Set_5/Set_2/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' Relation2': {'uName':uNames[21],'dName':'Relation2','Id': BASE_URI+'Section_3a/Set_5/Set_1/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' Other2': {'uName':uNames[21],'dName':'Other2','Id': BASE_URI+'Section_3a/Set_5/Set_1/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' IntraClassRelation': {'uName':uNames[21],'dName':'IntraClassRelation','Id': BASE_URI+'Section_3a/Set_5/Set_3/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[21]+' IntraClassElement': {'uName':uNames[21],'dName':'IntraClassElement','Id': BASE_URI+'Section_3a/Set_5/Set_3/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              ## Quantities
              uNames[13]+' MathModID': {'uName':uNames[13],'dName':'MathModID','Id': BASE_URI+'Section_3/Set_0/Set_0/Question_07', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' ID': {'uName':uNames[13],'dName':'ID','Id': BASE_URI+'Section_3a/Set_3/Question_5', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' Name': {'uName':uNames[13],'dName':'Name','Id': BASE_URI+'Section_3a/Set_3/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[13]+' Description': {'uName':uNames[13],'dName':'Description','Id': BASE_URI+'Section_3a/Set_3/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[13]+' Reference': {'uName':uNames[13],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_3/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[13]+' QorQK': {'uName':uNames[13],'dName':'QorQK','Id': BASE_URI+'Section_3a/Set_3/Question_6', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[13]+' QProperties': {'uName':uNames[13],'dName':'Properties','Id': BASE_URI+'Section_3a/Set_3/Question_3', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[13]+' QKProperties': {'uName':uNames[13],'dName':'Properties','Id': BASE_URI+'Section_3a/Set_3/Question_7', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[13]+' RelationQ1': {'uName':uNames[13],'dName':'Relation1','Id': BASE_URI+'Section_3a/Set_3/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' OtherQ1': {'uName':uNames[13],'dName':'Other1','Id': BASE_URI+'Section_3a/Set_3/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' RelationQK2': {'uName':uNames[13],'dName':'Relation2','Id': BASE_URI+'Section_3a/Set_4/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' OtherQK2': {'uName':uNames[13],'dName':'Other2','Id': BASE_URI+'Section_3a/Set_4/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' RelationQ2': {'uName':uNames[13],'dName':'Relation3','Id': BASE_URI+'Section_3a/Set_4/Set_1/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' OtherQ2': {'uName':uNames[13],'dName':'Other3','Id': BASE_URI+'Section_3a/Set_4/Set_1/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' RelationQK1': {'uName':uNames[13],'dName':'Relation4','Id': BASE_URI+'Section_3a/Set_3/Set_1/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[13]+' OtherQK1': {'uName':uNames[13],'dName':'Other4','Id': BASE_URI+'Section_3a/Set_3/Set_1/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              ## Task
              uNames[14]+' MathModID': {'uName':uNames[14],'dName':'MathModID','Id': BASE_URI+'Section_3a/Set_6/Question_0', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[14]+' ID': {'uName':uNames[14],'dName':'ID','Id': BASE_URI+'Section_3a/Set_6/Set_0/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[14]+' Name': {'uName':uNames[14],'dName':'Name','Id': BASE_URI+'Section_3a/Set_6/Set_0/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[14]+' Description': {'uName':uNames[14],'dName':'Description','Id': BASE_URI+'Section_3a/Set_6/Set_0/Question_2', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[14]+' Reference': {'uName':uNames[14],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_6/Set_0/Question_3', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[14]+' Properties': {'uName':uNames[14],'dName':'Properties','Id': BASE_URI+'Section_3a/Set_6/Set_0/Question_4', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[14]+' TaskClass': {'uName':uNames[14],'dName':'TaskClass','Id': BASE_URI+'Section_3a/Set_6/Set_0/Question_5', 'set_prefix':True, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':False},
              uNames[14]+' Relation1': {'uName':uNames[14],'dName':'Relation1','Id': BASE_URI+'Section_3a/Set_6/Set_0/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[14]+' Other1': {'uName':uNames[14],'dName':'Other1','Id': BASE_URI+'Section_3a/Set_6/Set_0/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[14]+' Relation2': {'uName':uNames[14],'dName':'Relation2','Id': BASE_URI+'Section_3a/Set_6/Set_0/Set_1/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[14]+' Other2': {'uName':uNames[14],'dName':'Other2','Id': BASE_URI+'Section_3a/Set_6/Set_0/Set_1/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[14]+' Model': {'uName':uNames[14],'dName':'Model','Id': BASE_URI+'Section_3a/Set_6/Question_1', 'set_prefix':False, 'set_index':True, 'collection_index':True, 'option_text':False, 'external_id':True},
              uNames[14]+' ResearchProblem': {'uName':uNames[14],'dName':'ResearchProblem','Id': BASE_URI+'Section_3a/Set_6/Question_2', 'set_prefix':False, 'set_index':True, 'collection_index':True, 'option_text':False, 'external_id':True},
              uNames[14]+' IntraClassRelation': {'uName':uNames[14],'dName':'IntraClassRelation','Id': BASE_URI+'Section_3a/Set_6/Set_1/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[14]+' IntraClassElement': {'uName':uNames[14],'dName':'IntraClassElement','Id': BASE_URI+'Section_3a/Set_6/Set_1/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              ## Publication Model
              uNames[22]+' MathModID': {'uName':uNames[22],'dName':'MathModID','Id': BASE_URI+'Section_3a/Set_7/Question_0', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[22]+' Name': {'uName':uNames[22],'dName':'Name','Id': BASE_URI+'Section_3a/Set_7/Set_1/Question_1', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[22]+' Reference': {'uName':uNames[22],'dName':'Reference','Id': BASE_URI+'Section_3a/Set_7/Set_1/Question_0', 'set_prefix':True, 'set_index':False, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[22]+' Relation': {'uName':uNames[22],'dName':'Relation','Id': BASE_URI+'Section_3a/Set_7/Set_0/Question_1', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':False},
              uNames[22]+' Other': {'uName':uNames[22],'dName':'Other','Id': BASE_URI+'Section_3a/Set_7/Set_0/Question_0', 'set_prefix':True, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              # Software Information
              uNames[6]+' ID': {'uName':uNames[6],'dName':'ID','Id': BASE_URI+'Section_4/Set_3/Question_01', 'set_prefix':False, 'set_index': True, 'collection_index': False, 'option_text':False, 'external_id':True},
              uNames[6]+' Name': {'uName':uNames[6],'dName':'Name','Id': BASE_URI+'Section_4/Set_3/Question_02', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[6]+' Description': {'uName':uNames[6],'dName':'Description','Id': BASE_URI+'Section_4/Set_3/Question_03', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[6]+' SubProperty': {'uName':uNames[6],'dName':'SubProperty','Id': BASE_URI+'Section_4/Set_3/Question_05', 'set_prefix':False, 'set_index': True, 'collection_index': True, 'option_text': False, 'external_id': True},
              uNames[6]+' Reference': {'uName':uNames[6],'dName':'Reference','Id': BASE_URI+'Section_4/Set_3/Question_00', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[6]+' Version': {'uName':uNames[6],'dName':'Version','Id': BASE_URI+'Section_4/Set_3/Question_04', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[6]+' Dependency': {'uName':uNames[6],'dName':'Dependency','Id': BASE_URI+'Section_4/Set_3/Question_06', 'set_prefix':False, 'set_index': True, 'collection_index': True},
              uNames[6]+' Versioned': {'uName':uNames[6],'dName':'Versioned','Id': BASE_URI+'Section_4/Set_3/Question_07', 'set_prefix':False, 'set_index': True, 'collection_index': False, 'option_text': True},
              uNames[6]+' Published': {'uName':uNames[6],'dName':'Published','Id': BASE_URI+'Section_4/Set_3/Question_08',  'set_prefix':False, 'set_index': True, 'collection_index': False, 'option_text': True},
              uNames[6]+' Documented': {'uName':uNames[6],'dName':'Documented','Id': BASE_URI+'Section_4/Set_3/Question_09', 'set_prefix':False, 'set_index': True, 'collection_index': False, 'option_text': True},
              # Hardware Information
              uNames[7]+' ID': {'uName':uNames[7],'dName':'ID','Id': BASE_URI+'Section_4/Set_4/Question_01', 'set_prefix':False, 'set_index': True, 'collection_index': False, 'option_text':False, 'external_id':True},
              uNames[7]+' Name': {'uName':uNames[7],'dName':'Name','Id': BASE_URI+'Section_4/Set_4/Question_02', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[7]+' Description': {'uName':uNames[7],'dName':'Description','Id': BASE_URI+'Section_4/Set_4/Question_07', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[7]+' SubProperty': {'uName':uNames[7],'dName':'SubProperty','Id': BASE_URI+'Section_4/Set_4/Question_03', 'set_prefix':False, 'set_index': True, 'collection_index': True, 'option_text':False, 'external_id':True},
              uNames[7]+' SubProperty2': {'uName':uNames[7],'dName':'SubProperty2','Id': BASE_URI+'Section_4/Set_4/Question_04', 'set_prefix':False, 'set_index': True, 'collection_index': True, 'option_text':False, 'external_id':True},
              uNames[7]+' Node': {'uName':uNames[7],'dName':'Node','Id': BASE_URI+'Section_4/Set_4/Question_05', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[7]+' Core': {'uName':uNames[7],'dName':'Core','Id': BASE_URI+'Section_4/Set_4/Question_06', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              # Experimental Device Information
              uNames[8]+' ID': {'uName':uNames[8],'dName':'ID','Id': BASE_URI+'Section_4/Set_5/Question_01', 'set_prefix':False, 'set_index': True, 'collection_index': False, 'option_text': False, 'external_id': True},
              uNames[8]+' Name': {'uName':uNames[8],'dName':'Name','Id': BASE_URI+'Section_4/Set_5/Question_02', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[8]+' Description': {'uName':uNames[8],'dName':'Description','Id': BASE_URI+'Section_4/Set_5/Question_03', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[8]+' Version': {'uName':uNames[8],'dName':'Version','Id': BASE_URI+'Section_4/Set_5/Question_04', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[8]+' PartNumber': {'uName':uNames[8],'dName':'PartNumber','Id': BASE_URI+'Section_4/Set_5/Question_05', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[8]+' SerialNumber': {'uName':uNames[8],'dName':'SerialNumber','Id': BASE_URI+'Section_4/Set_5/Question_06', 'set_prefix':False, 'set_index': True, 'collection_index': False},
              uNames[8]+' SubProperty': {'uName':uNames[8],'dName':'SubProperty','Id': BASE_URI+'Section_4/Set_5/Question_07', 'set_prefix':False, 'set_index': True, 'collection_index': True, 'option_text':False, 'external_id':True},
              uNames[8]+' SubProperty2': {'uName':uNames[8],'dName':'SubProperty2','Id': BASE_URI+'Section_4/Set_5/Question_08', 'set_prefix':False, 'set_index': True, 'collection_index': True, 'option_text':False, 'external_id':True},
              # Data Set Information
              uNames[11]+' ID': {'uName':uNames[11],'dName':'ID','Id': BASE_URI+'Section_4/Set_6/Question_00', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[11]+' Name': {'uName':uNames[11],'dName':'Name','Id':  BASE_URI+'Section_4/Set_6/Question_01', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' Description': {'uName':uNames[11],'dName':'Description','Id':  BASE_URI+'Section_4/Set_6/Question_11', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' Reference': {'uName':uNames[11],'dName':'Reference','Id': BASE_URI+'Section_4/Set_6/Question_10', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' Size': {'uName':uNames[11],'dName':'Size','Id':  BASE_URI+'Section_4/Set_6/Question_02', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' DataStructure': {'uName':uNames[11],'dName':'DataStructure','Id':  BASE_URI+'Section_4/Set_6/Question_03', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' RepresentationFormat': {'uName':uNames[11],'dName':'RepresentationFormat','Id':  BASE_URI+'Section_4/Set_6/Question_04', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' ExchangeFormat': {'uName':uNames[11],'dName':'ExchangeFormat','Id':  BASE_URI+'Section_4/Set_6/Question_05', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' BinaryText': {'uName':uNames[11],'dName':'BinaryText','Id':  BASE_URI+'Section_4/Set_6/Question_06', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' Proprietary': {'uName':uNames[11],'dName':'Proprietary','Id':  BASE_URI+'Section_4/Set_6/Question_07', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' Publication': {'uName':uNames[11],'dName':'Publication','Id':  BASE_URI+'Section_4/Set_6/Question_08', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[11]+' Archiving': {'uName':uNames[11],'dName':'Archiving','Id':  BASE_URI+'Section_4/Set_6/Question_09', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':True},
              # Method Information
              uNames[12]+' ID': {'uName':uNames[12],'dName':'ID','Id': BASE_URI+'Section_4/Set_2/Question_01', 'set_prefix':False, 'set_index':True, 'collection_index':False, 'option_text':False, 'external_id':True},
              uNames[12]+' Name': {'uName':uNames[12],'dName':'Name','Id': BASE_URI+'Section_4/Set_2/Question_02', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[12]+' Description': {'uName':uNames[12],'dName':'Description','Id':  BASE_URI+'Section_4/Set_2/Wiki_02', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[12]+' SubProperty': {'uName':uNames[12],'dName':'SubProperty','Id': BASE_URI+'Section_4/Set_2/Wiki_03', 'set_prefix':False, 'set_index':True, 'collection_index':True, 'option_text':False,'external_id':True},
              uNames[12]+' Formular': {'uName':uNames[12],'dName':'Formular','Id': BASE_URI+'Section_4/Set_2/Wiki_04', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              uNames[12]+' Reference': {'uName':uNames[12],'dName':'Reference','Id': BASE_URI+'Section_4/Set_2/Question_00', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[12]+' Parameter': {'uName':uNames[12],'dName':'Parameter','Id': BASE_URI+'Section_4/Set_2/Question_04', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[12]+' Software': {'uName':uNames[12],'dName':'Software','Id': BASE_URI+'Section_4/Set_2/Question_05', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              # Process Step Information
              uNames[3]+' Name': {'uName':uNames[3],'dName':'Name','Id': BASE_URI+'Section_4/Set_1/Question_01', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[3]+' Description': {'uName':uNames[3],'dName':'Description','Id': BASE_URI+'Section_4/Set_1/Question_02', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[3]+' Input': {'uName':uNames[3],'dName':'Input','Id': BASE_URI+'Section_4/Set_1/Question_03', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              uNames[3]+' Output': {'uName':uNames[3],'dName':'Output','Id': BASE_URI+'Section_4/Set_1/Question_04', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              uNames[3]+' Method': {'uName':uNames[3],'dName':'Method','Id': BASE_URI+'Section_4/Set_1/Question_05', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              uNames[3]+' Parameter': {'uName':uNames[3],'dName':'Parameter','Id': BASE_URI+'Section_4/Set_1/Question_06', 'set_prefix':False, 'set_index':True, 'collection_index':False},
              uNames[3]+' Environment': {'uName':uNames[3],'dName':'Environment','Id': BASE_URI+'Section_4/Set_1/Question_07', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              uNames[3]+' MathArea': {'uName':uNames[3],'dName':'MathArea','Id': BASE_URI+'Section_4/Set_1/Question_08', 'set_prefix':False, 'set_index':True, 'collection_index':True},
              # Reproducibility
              uNames[15]+ ' Mathematically': {'uName':uNames[15], 'dName':'Mathematically', 'Id':BASE_URI+'Section_5/Set_1/Question_01', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' MathematicallyInfo': {'uName':uNames[15], 'dName':'MathematicallyInfo', 'Id':BASE_URI+'Section_5/Set_1/Question_01a', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' Runtime': {'uName':uNames[15], 'dName':'Runtime', 'Id':BASE_URI+'Section_5/Set_1/Question_02', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' RuntimeInfo': {'uName':uNames[15], 'dName':'RuntimeInfo', 'Id':BASE_URI+'Section_5/Set_1/Question_02a', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' Result': {'uName':uNames[15], 'dName':'Result', 'Id':BASE_URI+'Section_5/Set_1/Question_03', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' ResultInfo': {'uName':uNames[15], 'dName':'ResultInfo', 'Id':BASE_URI+'Section_5/Set_1/Question_03a', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' OriginalHardware': {'uName':uNames[15], 'dName':'OriginalHardware', 'Id':BASE_URI+'Section_5/Set_1/Question_04', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' OriginalHardwareInfo': {'uName':uNames[15], 'dName':'OriginalHardwareInfo', 'Id':BASE_URI+'Section_5/Set_1/Question_04a', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' OtherHardware': {'uName':uNames[15], 'dName':'OtherHardware', 'Id':BASE_URI+'Section_5/Set_1/Question_05', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' OtherHardwareInfo': {'uName':uNames[15], 'dName':'OtherHardwareInfo', 'Id':BASE_URI+'Section_5/Set_1/Question_05a', 'set_prefix':False,'set_index':False,'collection_index':False,'option_text':False},
              uNames[15]+ ' Transferability': {'uName':uNames[15], 'dName':'Transferability', 'Id':BASE_URI+'Section_5/Set_1/Question_06', 'set_prefix':False,'set_index':False,'collection_index':True},
              # Workflow Search 
              uNames[17]+' Search Objective': {'uName':uNames[17], 'dName':'Search Objective', 'Id':BASE_URI+'Section_1/Set_1/Question_00', 'set_prefix':False, 'set_index':False, 'collection_index':False},
              uNames[17]+' Objective Keywords': {'uName':uNames[17], 'dName':'Objective Keywords', 'Id':BASE_URI+'Section_1/Set_1/Question_01', 'set_prefix':False, 'set_index':False, 'collection_index':True},
              uNames[17]+' Search Discipline': {'uName':uNames[17], 'dName':'Search Discipline', 'Id':BASE_URI+'Section_1/Set_1/Question_02', 'set_prefix':False, 'set_index':False, 'collection_index':False},
              uNames[17]+' Discipline Keywords': {'uName':uNames[17], 'dName':'Discipline Keywords', 'Id':BASE_URI+'Section_1/Set_1/Question_03', 'set_prefix':False, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':True},
              uNames[17]+' Search Entities': {'uName':uNames[17], 'dName':'Search Entities', 'Id':BASE_URI+'Section_1/Set_1/Question_04', 'set_prefix':False, 'set_index':False, 'collection_index':False},
              uNames[17]+' Entities Keywords': {'uName':uNames[17], 'dName':'Entities Keywords', 'Id':BASE_URI+'Section_1/Set_1/Question_05', 'set_prefix':False, 'set_index':False, 'collection_index':True, 'option_text':False, 'external_id':True}}
              

