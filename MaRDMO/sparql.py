from .config import wd, wdt 

#SPARQL Query Base and components for Workflow Search

query_base="""
PREFIX wdt: """+wdt+"""
PREFIX wd: """+wd+"""
SELECT DISTINCT ?label ?qid
WHERE {{
?workflow wdt:P{0} wd:{1};
          rdfs:label ?label;
          {2}
          {3}
          {4}
{5}
BIND(STRAFTER(STR(?workflow),STR(wd:)) AS ?qid).
}}
LIMIT 10"""

quote_sparql = "schema:description ?quote;"
res_obj_sparql = "FILTER(CONTAINS(lcase(str(?quote)), '{}'@en)).\n"
res_disc_sparql = "wdt:P{0} wd:{1};\n"
mmsio_sparql = "wdt:P{0} wd:{1};\n"

#SPARQL Query parts

mbody = '''
OPTIONAL{{?chk rdfs:label '{0}'@en;schema:description '{1}'@en.BIND(STRAFTER(STR(?chk),STR(wd:)) AS ?qid).}}
'''

mbody2 = '''
OPTIONAL{{?chk rdfs:label '{0}'@en;schema:description '{1}'@en.BIND(STRAFTER(STR(?chk),STR(wd:)) AS ?qid).}}
OPTIONAL{{?chk wdt:P{2} ?author.}}
OPTIONAL{{?author wdt:P{3} ?orcid.}}
OPTIONAL{{?author wdt:P{4} ?zbmath.}}
'''



wini='''
SELECT {0}
WHERE
{{
{1}
}}
LIMIT {2}'''

mini='''
PREFIX wdt:'''+wdt+''' PREFIX wd:'''+wd+wini

#SPARQL Query for additional entities

pl_vars = '?qid ?label ?quote'

pl_query = '''
OPTIONAL{{wd:{0} wdt:{1} ?pl. ?pl rdfs:label ?label; schema:description ?quote.BIND(STRAFTER(STR(?pl),STR(wd:)) AS ?qid).FILTER (lang(?label) = 'en').FILTER (lang(?quote) = 'en').}}
'''

pro_vars = '?qid ?label ?quote'

pro_query = '''
OPTIONAL{{?pro wdt:{0} '{1}'. ?pro rdfs:label ?label; schema:description ?quote.BIND(STRAFTER(STR(?pro),STR(wd:)) AS ?qid).FILTER (lang(?label) = 'en').FILTER (lang(?quote) = 'en').}}
'''


#Queries to MaRDI KG and Wikidata for Publication Handler

queryPublication = {

       'All': '''SELECT ?publicationQid ?publicationLabel ?publicationDescription1         
                     ?authorInfo                                                        
                     ?entrytypeQid ?entrytypeLabel ?entrytypeDescription1               
                     ?journalQid ?journalLabel ?journalDescription1                     
                     ?languageQid ?languageLabel ?languageDescription1                  
                     ?title ?otherAuthor ?publicationDate ?volume ?issue ?page          

              WHERE {{?publication wdt:P{0} "{1}";
                              rdfs:label ?publicationLabel.
                      OPTIONAL {{?publication schema:description ?publicationDescription.}}
                      FILTER (lang(?publicationLabel) = 'en')
                      FILTER (lang(?publicationDescription) = 'en') 
                      BIND(COALESCE(?publicationDescription, "") As ?publicationDescription1)
                      BIND(STRAFTER(STR(?publication),STR(wd:)) AS ?publicationQid).
                      OPTIONAL {{?publication wdt:P{2} ?author.
                                 ?author rdfs:label ?authorLabel;
                                 OPTIONAL {{?author schema:description ?authorDescription.}}  
                                 OPTIONAL {{?author wdt:P{3} ?authorOrcid.}}
                                 OPTIONAL {{?author wdt:P{13} ?authorWikidataQid}}
                                 OPTIONAL {{?author wdt:P{14} ?authorZbmathID}}
                                 BIND(COALESCE(?authorOrcid, "") As ?authorOrcid1)
                                 BIND(COALESCE(?authorWikidataQid, "") As ?authorWikidataQid1)
                                 BIND(COALESCE(?authorZbmathID, "") As ?authorZbmathID1)
                                 BIND(COALESCE(?authorDescription, "") As ?authorDescription1)
                                 BIND(STRAFTER(STR(?author),STR(wd:)) AS ?authorQid).
                                 FILTER (lang(?authorLabel) = 'en')
                                 FILTER (lang(?authorDescription) = 'en')
                                 BIND(concat(?authorQid," <|> ",?authorLabel," <|> ",?authorDescription1," <|> ",?authorOrcid1,
                                             " <|> ",?authorWikidataQid1, " <|> ",?authorZbmathID1) AS ?authorInfo)}} 
                     OPTIONAL {{?publication wdt:P{4} ?entrytype.
                                ?entrytype rdfs:label ?entrytypeLabel.
                                OPTIONAL {{?entrytype schema:description ?entrytypeDescription.}}
                                FILTER (lang(?entrytypeLabel) = 'en')
                                FILTER (lang(?entrytypeDescription) = 'en')
                                BIND(COALESCE(?entrytypeDescription, "") As ?entrytypeDescription1)
                                BIND(STRAFTER(STR(?entrytype),STR(wd:)) AS ?entrytypeQid).}}
                     OPTIONAL {{?publication wdt:P{5} ?journal.
                                ?journal rdfs:label ?journalLabel.
                                OPTIONAL {{?journal schema:description ?journalDescription.}}
                                FILTER (lang(?journalLabel) = 'en')
                                FILTER (lang(?journalDescription) = 'en')
                                BIND(COALESCE(?journalDescription, "") As ?journalDescription1)
                                BIND(STRAFTER(STR(?journal),STR(wd:)) AS ?journalQid).}}
                     OPTIONAL {{?publication wdt:P{6} ?language.
                                ?language rdfs:label ?languageLabel.
                                OPTIONAL {{?language schema:description ?languageDescription.}}
                                FILTER (lang(?languageLabel) = 'en')
                                FILTER (lang(?languageDescription) = 'en')
                                BIND(COALESCE(?languageDescription, "") As ?languageDescription1)
                                BIND(STRAFTER(STR(?language),STR(wd:)) AS ?languageQid).}}
                     OPTIONAL {{?publication wdt:P{7} ?title.}}
                     OPTIONAL {{?publication wdt:P{8} ?otherAuthor.}}
                     OPTIONAL {{?publication wdt:P{9} ?publicationDate.}}
                     OPTIONAL {{?publication wdt:P{10} ?volume.}}
                     OPTIONAL {{?publication wdt:P{11} ?issue.}}
                     OPTIONAL {{?publication wdt:P{12} ?page.}}}}''',

       'WikiCheck': '''# Query for MaRDI portal                                              

             SELECT  ?publicationQid ?publicationLabel ?publicationDescription1                                               
             
             WHERE {{
                     # Publication via Wikidata QID

                     ?publication wdt:P{0} "{1}";
                             rdfs:label ?publicationLabel.
                     OPTIONAL {{?publication schema:description ?publicationDescription.}}

                     BIND(COALESCE(?publicationDescription, "") As ?publicationDescription1)
                     BIND(STRAFTER(STR(?publication),STR(wd:)) AS ?publicationQid).
                   
                   }}''',


       'AuthorViaOrcid': '''SELECT ?authorQid ?authorLabel ?authorDescription ?authorId        # Author of Publication via ORCID/zbMath

             WHERE {{

                     VALUES ?authorId {{{0}}}

                     OPTIONAL {{
                                # Author via ORCID
                                ?author wdt:P{1} ?authorId
                                BIND(STRAFTER(STR(?author),STR(wd:)) AS ?authorQid)
                              }}

                      SERVICE wikibase:label {{bd:serviceParam wikibase:language "en,en".}}

                    }}''',

       'AuthorViaWikidataQID': '''SELECT ?wikidataQid ?mardiQid ?authorLabel ?authorDescription         # Author of Publication via Wikidata QID

             WHERE {{

                     VALUES ?wikidataQid {{{0}}}

                     OPTIONAL {{
                                # Author via Wikidata QID
                                ?author wdt:P{1} ?wikidataQid
                                BIND(STRAFTER(STR(?author),STR(wd:)) AS ?mardiQid)
                              }}

                     SERVICE wikibase:label {{bd:serviceParam wikibase:language "en,en".}}

                   }}'''
       }

### SPARQL queries to get additional information from MathModDB during export

queryModelDocumentation = {

                  'RF': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?rf
                                        (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?quote)
                                 
                                 WHERE {{
                                         VALUES ?rf {{{0}}}
                                         ?rf rdfs:comment ?l.
                                         OPTIONAL {{FILTER (lang(?l) = 'en')}}
                                       }}
                                 
                                 GROUP BY ?rf ?quote''',
                  
                  'RP': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                 
                                 SELECT ?rp
                                        (GROUP_CONCAT(DISTINCT(?l2); SEPARATOR=" / ") AS ?quote) (GROUP_CONCAT(DISTINCT(?l1); SEPARATOR=" / ") AS ?label)
                                        (GROUP_CONCAT(DISTINCT(?field); separator=" <|> ") AS ?FIELD) (GROUP_CONCAT(DISTINCT(?fieldLabel); SEPARATOR=" <|> ") AS ?FIELDLabel)
                                        (GROUP_CONCAT(DISTINCT(?fieldQuote); SEPARATOR=" <|> ") AS ?FIELDQuote)
                  
                                 WHERE {{
                                         VALUES ?rp {{{0}}}
                                         ?rp rdfs:label ?l1.
                                         FILTER (lang(?l1) = 'en')
                                         OPTIONAL {{ ?rp rdfs:comment ?l2 .
                                                     FILTER (lang(?l2) = 'en').
                                                  }}
                                         
                                         OPTIONAL {{ ?rp :containedInField ?field.
                                                     ?field rdfs:label ?fieldLabel.
                                                     FILTER (lang(?fieldLabel) = 'en').
                  
                                                     OPTIONAL {{ ?field rdfs:comment ?fieldQuote.
                                                                 FILTER (lang(?fieldQuote) = 'en').}}
                                                  }}
                                       }}
                  
                                 GROUP BY ?rp ?label ?quote ?FIELD ?FIELDLabel ?FIELDQuote''',
                  
                  'Q': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                  	           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                  	           SELECT ?q ?answer ?qlinear ?qdimensionless
                                        (GROUP_CONCAT(DISTINCT ?l1; SEPARATOR=" / ") AS ?qlabel)   (GROUP_CONCAT(DISTINCT ?l2; SEPARATOR=" / ") AS ?qquote) 
                                        (GROUP_CONCAT(DISTINCT ?l21; SEPARATOR=" / ") AS ?qklabel) (GROUP_CONCAT(DISTINCT ?l22; SEPARATOR=" / ") AS ?qkquote)
                  
                                 WHERE {{
                                         VALUES ?q {{{0}}}
                  
                    	                  ?q a :Quantity .
                                        ?q rdfs:label ?l1.
                                        OPTIONAL {{ ?q rdfs:comment ?l2. 
                                                    FILTER (lang(?l2) = 'en')}}
                                        OPTIONAL {{ ?q :isLinear ?qlinear. }}
                                        OPTIONAL {{ ?q :isDimensionless ?qdimensionless.}}
                                        FILTER (lang(?l1) = 'en')
                                        OPTIONAL {{
                                        ?answer a :QuantityKind .
                                        ?answer rdfs:label ?l21 .
                                        ?answer rdfs:comment ?l22 .
                                        FILTER (lang(?l21) = 'en')
                                        FILTER (lang(?l22) = 'en')
                                        {{
                                         ?q (:generalizesQuantity|:generalizedByQuantity|:similarToQuantity)+ ?answer .
                                         ?q (:generalizesQuantity|:generalizedByQuantity|:similarToQuantity)* ?intermediate .
                                         ?intermediate (:generalizesQuantity|:generalizedByQuantity|:similarToQuantity)* ?answer .
                                         ?intermediate a :Quantity .
                                        }}}}
                                       }} 
                                  GROUP BY ?q ?answer ?qlabel ?qquote ?qlinear ?qdimensionless ?qklabel ?qkquote''',
                  
                  'Q2': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?q ?qlabel ?mf ?label ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont
                                        (GROUP_CONCAT(DISTINCT(?elements); separator=" <|> ") AS ?formula_elements) (GROUP_CONCAT(DISTINCT(?formulas); separator=" <|> ") AS ?formula)
                                        (GROUP_CONCAT(?quantities; separator=" <|> ") AS ?quantity) (GROUP_CONCAT(?quantityLabels; separator=" <|> ") AS ?quantityLabel)
                                        (GROUP_CONCAT(?qC; separator=" <|> ") AS ?QC)
                  
                                 WHERE {{
                                        
                                        VALUES ?q {{{0}}}
                  
                                        ?q rdfs:label ?qlabel.
                                        FILTER (lang(?qlabel) = 'en')
                                        ?q :definedBy ?mf.
                  
                                        OPTIONAL {{ ?mf rdfs:label ?label.
                                                    FILTER (lang(?label) = 'en')}}
                  
                                        OPTIONAL {{ ?mf rdfs:comment ?quote.
                                                    FILTER (lang(?quote) = 'en')}}
                  
                                        OPTIONAL {{ ?mf :isLinear ?linear.}}
                                        OPTIONAL {{ ?mf :isConvex ?convex.}}
                                        OPTIONAL {{ ?mf :isDynamic ?dynamic.}}
                                        OPTIONAL {{ ?mf :isDeterministic ?deterministic.}}
                                        OPTIONAL {{ ?mf :isDimensionless ?dimensionless.}}
                                        OPTIONAL {{ ?mf :isTimeContinuous ?timecont.}}
                                        OPTIONAL {{ ?mf :isSpaceContinuous ?spacecont.}}
                  
                                        OPTIONAL {{ ?mf :definingFormulation ?formulas.}}
                                        OPTIONAL {{ ?mf :inDefiningFormulation ?elements.}}
                  
                                        OPTIONAL {{ ?mf :containsQuantity ?quantities.
                                                    ?quantities rdfs:label ?quantityLabels;
                                                                a ?qC.
                                                    FILTER (?qC IN (:Quantity, :QuantityKind))
                                                    FILTER (lang(?quantityLabels) = 'en')}}
                  
                                        }}
                  
                                        GROUP BY ?q ?qlabel ?mf ?label ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont
                                                 ?formula_elements ?formula ?quantity ?quantityLabel ?QC''',
                  
                  'QK': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?qk ?qkdimensionless
                                        (GROUP_CONCAT(DISTINCT ?l1; SEPARATOR=" / ") AS ?qklabel) (GROUP_CONCAT(DISTINCT ?l2; SEPARATOR=" / ") AS ?qkquote)
                                 WHERE {{
                                         VALUES ?qk {{{0}}}
                  
                                        ?qk a :QuantityKind .
                                        ?qk rdfs:label ?l1 .
                                        OPTIONAL {{ ?qk rdfs:comment ?l2 . 
                                                    FILTER (lang(?l2) = 'en') }}
                                        OPTIONAL {{ ?qk :isDimensionless ?qkdimensionless. }}
                                        FILTER (lang(?l1) = 'en')
                                       }}
                                 GROUP BY ?qk ?qklabel ?qkquote ?qkdimensionless''',
                  
                  'TA': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?t ?subclass ?quote ?linear
                                        (GROUP_CONCAT(DISTINCT(?f); separator=" <|> ") AS ?F) (GROUP_CONCAT(DISTINCT(?fL); SEPARATOR=" <|> ") AS ?FL)
                                        (GROUP_CONCAT(DISTINCT(?a); separator=" <|> ") AS ?A) (GROUP_CONCAT(DISTINCT(?aL); SEPARATOR=" <|> ") AS ?AL)
                                        (GROUP_CONCAT(DISTINCT(?bc); separator=" <|> ") AS ?BC) (GROUP_CONCAT(DISTINCT(?bcL); SEPARATOR=" <|> ") AS ?BCL)
                                        (GROUP_CONCAT(DISTINCT(?cc); separator=" <|> ") AS ?CC) (GROUP_CONCAT(DISTINCT(?ccL); SEPARATOR=" <|> ") AS ?CCL)
                                        (GROUP_CONCAT(DISTINCT(?cpc); separator=" <|> ") AS ?CPC) (GROUP_CONCAT(DISTINCT(?cpcL); SEPARATOR=" <|> ") AS ?CPCL)
                                        (GROUP_CONCAT(DISTINCT(?ic); separator=" <|> ") AS ?IC) (GROUP_CONCAT(DISTINCT(?icL); SEPARATOR=" <|> ") AS ?ICL)
                                        (GROUP_CONCAT(DISTINCT(?fc); separator=" <|> ") AS ?FC) (GROUP_CONCAT(DISTINCT(?fcL); SEPARATOR=" <|> ") AS ?FCL)
                                        (GROUP_CONCAT(DISTINCT(?ct); separator=" <|> ") AS ?CT) (GROUP_CONCAT(DISTINCT(?ctL); SEPARATOR=" <|> ") AS ?CTL)
                                        (GROUP_CONCAT(DISTINCT(?ict); separator=" <|> ") AS ?ICT) (GROUP_CONCAT(DISTINCT(?ictL); SEPARATOR=" <|> ") AS ?ICTL)
                                        (GROUP_CONCAT(?in; separator=" <|> ") AS ?IN) (GROUP_CONCAT(?inL; SEPARATOR=" <|> ") AS ?INL)
                                        (GROUP_CONCAT(?inC; SEPARATOR=" <|> ") AS ?INC)
                                        (GROUP_CONCAT(?o; separator=" <|> ") AS ?O) (GROUP_CONCAT(?oL; SEPARATOR=" <|> ") AS ?OL)
                                        (GROUP_CONCAT(?oC; SEPARATOR=" <|> ") AS ?OC)
                                        (GROUP_CONCAT(DISTINCT(?ob); separator=" <|> ") AS ?OB) (GROUP_CONCAT(DISTINCT(?obL); SEPARATOR=" <|> ") AS ?OBL)
                                        (GROUP_CONCAT(DISTINCT(?obC); SEPARATOR=" <|> ") AS ?OBC)
                                        (GROUP_CONCAT(DISTINCT(?pa); separator=" <|> ") AS ?PA) (GROUP_CONCAT(DISTINCT(?paL); SEPARATOR=" <|> ") AS ?PAL)
                                        (GROUP_CONCAT(DISTINCT(?paC); SEPARATOR=" <|> ") AS ?PAC)
                                        (GROUP_CONCAT(DISTINCT(?co); separator=" <|> ") AS ?CO) (GROUP_CONCAT(DISTINCT(?coL); SEPARATOR=" <|> ") AS ?COL)
                                        (GROUP_CONCAT(DISTINCT(?coC); SEPARATOR=" <|> ") AS ?COC)
                  
                                 WHERE {{
                                        VALUES ?t {{{0}}}
                  
                                        OPTIONAL {{ ?subclass rdfs:subClassOf :Task.
                                                    ?t a ?subclass .}}
                                        OPTIONAL {{ ?t rdfs:comment ?quote.
                                                    FILTER (lang(?quote) = 'en')}}
                                        OPTIONAL {{ ?t :isLinear ?linear.}}
                                        OPTIONAL {{ ?t :containsFormulation ?f. 
                                                    ?f rdfs:label ?fL.
                                                    FILTER (lang(?fL) = 'en')}}
                                        OPTIONAL {{ ?t :containsAssumption ?a. 
                                                    ?a rdfs:label ?aL.
                                                    FILTER (lang(?aL) = 'en')}}
                                        OPTIONAL {{ ?t :containsBoundaryCondition ?bc. 
                                                    ?bc rdfs:label ?bcL.
                                                    FILTER (lang(?bcL) = 'en')}}
                                        OPTIONAL {{ ?t :containsConstraintCondition ?cc. 
                                                    ?cc rdfs:label ?ccL.
                                                    FILTER (lang(?ccL) = 'en')}}
                                        OPTIONAL {{ ?t :containsCouplingCondition ?cpc. 
                                                    ?cpc rdfs:label ?cpcL.
                                                    FILTER (lang(?cpcL) = 'en')}}
                                        OPTIONAL {{ ?t :containsInitialCondition ?ic. 
                                                    ?ic rdfs:label ?icL.
                                                    FILTER (lang(?icL) = 'en')}}
                                        OPTIONAL {{ ?t :containsFinalCondition ?fc. 
                                                    ?fc rdfs:label ?fcL.
                                                    FILTER (lang(?fcL) = 'en')}}
                                        OPTIONAL {{ ?t :containsTask ?ct. 
                                                    ?ct rdfs:label ?ctL.
                                                    FILTER (lang(?ctL) = 'en')}}
                                        OPTIONAL {{ ?t :containedInTask ?ict. 
                                                    ?ict rdfs:label ?ictL.
                                                    FILTER (lang(?ictL) = 'en')}}
                                        OPTIONAL {{ ?t :containsInput ?in.
                                                    ?in rdfs:label ?inL;
                                                           a ?inC.
                                                    FILTER (lang(?inL) = 'en')
                                                    FILTER (?inC IN (:Quantity, :QuantityKind))}}
                                        OPTIONAL {{ ?t :containsOutput ?o.
                                                    ?o rdfs:label ?oL;
                                                            a ?oC.      
                                                    FILTER (lang(?oL) = 'en')
                                                    FILTER (?oC IN (:Quantity, :QuantityKind))}}
                                        OPTIONAL {{ ?t :containsObjective ?ob.
                                                    ?ob rdfs:label ?obL;
                                                               a ?obC.
                                                    FILTER (lang(?obL) = 'en')
                                                    FILTER (?obC IN (:Quantity, :QuantityKind))}}
                                        OPTIONAL {{ ?t :containsParameter ?pa.
                                                    ?pa rdfs:label ?paL;
                                                               a ?paC.
                                                    FILTER (lang(?paL) = 'en')
                                                    FILTER (?paC IN (:Quantity, :QuantityKind))}}
                                        OPTIONAL {{ ?t :containsConstant ?co.
                                                    ?co rdfs:label ?coL;
                                                               a ?coC.
                                                    FILTER (lang(?coL) = 'en')
                                                    FILTER (?coC IN (:Quantity, :QuantityKind))}}
                                       }}
                  
                                 GROUP BY ?t ?subclass ?quote ?linear ?F ?FL ?A ?AL ?BC ?BCL ?CC ?CCL ?CPC ?CPCL ?IC ?ICL ?FC ?FCL ?IN ?INL ?INC ?O ?OL ?OC ?OB ?OBL ?OBC ?PA ?PAL ?PAC ?CO ?COL ?COC ?CT ?CTL ?ICT ?ICTL''',
                  
                  'IntraClass': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                        SELECT ?t 
                                               (GROUP_CONCAT(DISTINCT(?gb); separator=" <|> ") AS ?GB) (GROUP_CONCAT(DISTINCT(?gbL); SEPARATOR=" <|> ") AS ?GBL)
                                               (GROUP_CONCAT(DISTINCT(?g); separator=" <|> ") AS ?G) (GROUP_CONCAT(DISTINCT(?gL); SEPARATOR=" <|> ") AS ?GL)
                                               (GROUP_CONCAT(DISTINCT(?ab); separator=" <|> ") AS ?AB) (GROUP_CONCAT(DISTINCT(?abL); SEPARATOR=" <|> ") AS ?ABL)
                                               (GROUP_CONCAT(DISTINCT(?a); separator=" <|> ") AS ?A) (GROUP_CONCAT(DISTINCT(?aL); SEPARATOR=" <|> ") AS ?AL)
                                               (GROUP_CONCAT(DISTINCT(?db); separator=" <|> ") AS ?DB) (GROUP_CONCAT(DISTINCT(?dbL); SEPARATOR=" <|> ") AS ?DBL)
                                               (GROUP_CONCAT(DISTINCT(?d); separator=" <|> ") AS ?D) (GROUP_CONCAT(DISTINCT(?dL); SEPARATOR=" <|> ") AS ?DL)
                                               (GROUP_CONCAT(DISTINCT(?lb); separator=" <|> ") AS ?LB) (GROUP_CONCAT(DISTINCT(?lbL); SEPARATOR=" <|> ") AS ?LBL)
                                               (GROUP_CONCAT(DISTINCT(?l); separator=" <|> ") AS ?L) (GROUP_CONCAT(DISTINCT(?lL); SEPARATOR=" <|> ") AS ?LL)
                                               (GROUP_CONCAT(DISTINCT(?nb); separator=" <|> ") AS ?NB) (GROUP_CONCAT(DISTINCT(?nbL); SEPARATOR=" <|> ") AS ?NBL)
                                               (GROUP_CONCAT(DISTINCT(?n); separator=" <|> ") AS ?N) (GROUP_CONCAT(DISTINCT(?nL); SEPARATOR=" <|> ") AS ?NL)
                                               (GROUP_CONCAT(DISTINCT(?s); separator=" <|> ") AS ?S) (GROUP_CONCAT(DISTINCT(?sL); SEPARATOR=" <|> ") AS ?SL) 
                                               (GROUP_CONCAT(?gbC; separator=" <|> ") AS ?GBC) (GROUP_CONCAT(?gC; separator=" <|> ") AS ?GC)
                                               (GROUP_CONCAT(?abC; separator=" <|> ") AS ?ABC) (GROUP_CONCAT(?aC; separator=" <|> ") AS ?AC)                   
                                               (GROUP_CONCAT(?dbC; separator=" <|> ") AS ?DBC) (GROUP_CONCAT(?dC; separator=" <|> ") AS ?DC)
                                               (GROUP_CONCAT(?lbC; separator=" <|> ") AS ?LBC) (GROUP_CONCAT(?lC; separator=" <|> ") AS ?LC)
                                               (GROUP_CONCAT(?nbC; separator=" <|> ") AS ?NBC) (GROUP_CONCAT(?nC; separator=" <|> ") AS ?NC)
                                               (GROUP_CONCAT(?sC; separator=" <|> ") AS ?SC) (GROUP_CONCAT(DISTINCT(?tC); separator=" <|> ") AS ?TC)
                                               
                                        WHERE {{
                                                 VALUES ?t {{{0}}}
                                                 ?t a ?tC.
                                                 FILTER (?tC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                 OPTIONAL {{ 
                                                             ?t (:generalizedByTask | :generalizedByModel | :generalizedByFormulation |:generalizedByQuantity)  ?gb. 
                                                             ?gb rdfs:label ?gbL.
                                                             ?gb a ?gbC.
                                                             FILTER (lang(?gbL) = 'en')
                                                             FILTER (?gbC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:generalizesTask | :generalizesModel | :generalizesFormulation | :generalizesQuantity) ?g. 
                                                             ?g rdfs:label ?gL.
                                                             ?g a ?gC.
                                                             FILTER (lang(?gL) = 'en')
                                                             FILTER (?gC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:approximatedByTask | :approximatedByModel | :approximatedByFormulation | :approximatedByQuantity) ?ab. 
                                                             ?ab rdfs:label ?abL.
                                                             ?ab a ?abC.
                                                             FILTER (lang(?abL) = 'en')
                                                             FILTER (?abC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:approximatesTask | :approximatesModel | :approximatesFormulation | :approximatesQuantity) ?a. 
                                                             ?a rdfs:label ?aL.
                                                             ?a a ?aC.
                                                             FILTER (lang(?aL) = 'en')
                                                             FILTER (?aC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:discretizedByTask | :discretizedByModel | :discretizedByFormulation) ?db. 
                                                             ?db rdfs:label ?dbL.
                                                             ?db a ?dbC.
                                                             FILTER (lang(?dbL) = 'en')
                                                             FILTER (?dbC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ ?t (:discretizesTask | :discretizesModel | :discretizesFormulation) ?d. 
                                                             ?d rdfs:label ?dL.
                                                             ?d a ?dC.
                                                             FILTER (lang(?dL) = 'en')
                                                             FILTER (?dC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:linearizedByTask | :linearizedByModel | :linearizedByFormulation | :linearizedByQuantity) ?lb.
                                                             ?lb rdfs:label ?lbL.
                                                             ?lb a ?lbC.
                                                             FILTER (lang(?lbL) = 'en')
                                                             FILTER (?lbC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:linearizesTask | :linearizesModel | :linearizesFormulation | :linearizesQuantity) ?l.
                                                             ?l rdfs:label ?lL.
                                                             ?l a ?lC.
                                                             FILTER (lang(?lL) = 'en')
                                                             FILTER (?lC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:nondimensionalizedByFormulation | :nondimensionalizedByQuantity) ?nb.
                                                             ?nb rdfs:label ?nbL.
                                                             ?nb a ?nbC.
                                                             FILTER (lang(?nbL) = 'en')
                                                             FILTER (?nbC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:nondimensionalizesFormulation | :nondimensionalizesQuantity) ?n.
                                                             ?n rdfs:label ?nL.
                                                             ?n a ?nC.
                                                             FILTER (lang(?nL) = 'en')
                                                             FILTER (?nC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                                 OPTIONAL {{ 
                                                             ?t (:similarToTask | :similarToModel | :similarToFormulation | :similarToQuantity) ?s. 
                                                             ?s rdfs:label ?sL.
                                                             ?s a ?sC.
                                                             FILTER (lang(?sL) = 'en')
                                                             FILTER (?sC IN (:MathematicalModel, :MathematicalFormulation, :ComputationalTask, :Quantity, :QuantityKind))
                                                          }}
                                              }}
                  
                                  GROUP BY ?t ?TC ?GB ?GBL ?GBC ?G ?GL ?GC ?AB ?ABL ?ABC ?A ?AL ?AC ?DB ?DBL ?DBC ?D ?DL ?DC ?LB ?LBL ?LBC ?L ?LL ?LC ?NB ?NBL ?NBC ?N ?NL ?NC ?S ?SL ?SC''',
                
                  'MM': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?mm ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont 
                                        (GROUP_CONCAT(DISTINCT ?p; SEPARATOR=" <|> ") AS ?P) (GROUP_CONCAT(DISTINCT ?pL; SEPARATOR=" <|> ") AS ?PL)
                                        (GROUP_CONCAT(DISTINCT(?f); separator=" <|> ") AS ?F) (GROUP_CONCAT(DISTINCT(?fL); SEPARATOR=" <|> ") AS ?FL)
                                        (GROUP_CONCAT(DISTINCT(?a); separator=" <|> ") AS ?A) (GROUP_CONCAT(DISTINCT(?aL); SEPARATOR=" <|> ") AS ?AL)
                                        (GROUP_CONCAT(DISTINCT(?bc); separator=" <|> ") AS ?BC) (GROUP_CONCAT(DISTINCT(?bcL); SEPARATOR=" <|> ") AS ?BCL)
                                        (GROUP_CONCAT(DISTINCT(?cc); separator=" <|> ") AS ?CC) (GROUP_CONCAT(DISTINCT(?ccL); SEPARATOR=" <|> ") AS ?CCL)
                                        (GROUP_CONCAT(DISTINCT(?cpc); separator=" <|> ") AS ?CPC) (GROUP_CONCAT(DISTINCT(?cpcL); SEPARATOR=" <|> ") AS ?CPCL)
                                        (GROUP_CONCAT(DISTINCT(?ic); separator=" <|> ") AS ?IC) (GROUP_CONCAT(DISTINCT(?icL); SEPARATOR=" <|> ") AS ?ICL)
                                        (GROUP_CONCAT(DISTINCT(?fc); separator=" <|> ") AS ?FC) (GROUP_CONCAT(DISTINCT(?fcL); SEPARATOR=" <|> ") AS ?FCL)
                                        (GROUP_CONCAT(DISTINCT(?cmm); separator=" <|> ") AS ?CMM) (GROUP_CONCAT(DISTINCT(?cmmL); SEPARATOR=" <|> ") AS ?CMML)
                                        (GROUP_CONCAT(DISTINCT(?ta); separator=" <|> ") AS ?TA) (GROUP_CONCAT(DISTINCT(?taL); SEPARATOR=" <|> ") AS ?TAL)
                                        (GROUP_CONCAT(DISTINCT(COALESCE(?taQ, "")); SEPARATOR=" <|> ") AS ?TAQ)
                  
                                 WHERE {{
                                        
                                        VALUES ?mm {{{0}}}
                                        
                                        OPTIONAL {{ ?mm rdfs:comment ?quote.
                                                    FILTER (lang(?quote) = 'en')}}
                                        
                                        OPTIONAL {{ ?mm :isLinear ?linear.}}
                                        OPTIONAL {{ ?mm :isConvex ?convex.}}  
                                        OPTIONAL {{ ?mm :isDynamic ?dynamic.}}                             
                                        OPTIONAL {{ ?mm :isDeterministic ?deterministic.}}
                          		      OPTIONAL {{ ?mm :isDimensionless ?dimensionless.}}
                                        OPTIONAL {{ ?mm :isTimeContinuous ?timecont.}}
                                        OPTIONAL {{ ?mm :isSpaceContinuous ?spacecont.}}
                                        
                                        OPTIONAL {{ ?mm :models ?p.
                                                    ?p rdfs:label ?pL.
                                                    Filter (lang(?pL) = 'en')}}
                                        
                                        OPTIONAL {{ ?mm :containsFormulation ?f. 
                                                    ?f rdfs:label ?fL.
                                                    FILTER (lang(?fL) = 'en')}}
                                        OPTIONAL {{ ?mm :containsAssumption ?a. 
                                                    ?a rdfs:label ?aL.
                                                    FILTER (lang(?aL) = 'en')}}
                                        OPTIONAL {{ ?mm :containsBoundaryCondition ?bc. 
                                                    ?bc rdfs:label ?bcL.
                                                    FILTER (lang(?bcL) = 'en')}}
                                        OPTIONAL {{ ?mm :containsConstraintCondition ?cc. 
                                                    ?cc rdfs:label ?ccL.
                                                    FILTER (lang(?ccL) = 'en')}}
                                        OPTIONAL {{ ?mm :containsCouplingCondition ?cpc. 
                                                    ?cpc rdfs:label ?cpcL.
                                                    FILTER (lang(?cpcL) = 'en')}}
                                        OPTIONAL {{ ?mm :containsInitialCondition ?ic. 
                                                    ?ic rdfs:label ?icL.
                                                    FILTER (lang(?icL) = 'en')}}
                                        OPTIONAL {{ ?mm :containsFinalCondition ?fc. 
                                                    ?fc rdfs:label ?fcL.
                                                    FILTER (lang(?fcL) = 'en')}}
                  
                                        OPTIONAL {{ ?mm :containsModel ?cmm. 
                                                    ?cmm rdfs:label ?cmmL.
                                                    FILTER (lang(?cmmL) = 'en')}}
                                        OPTIONAL {{ ?mm :appliedByTask ?ta.
                                                    ?ta rdfs:label ?taL.
                                                    OPTIONAL {{ ?ta rdfs:comment ?taQ. }}
                                                    FILTER (!bound(?taQ) || (lang(?taQ) = 'en'))
                                                    FILTER (lang(?taL) = 'en')}}
                                       }}
                  
                                 GROUP BY ?mm ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont ?P ?PL ?F ?FL ?A ?AL ?BC ?BCL ?CC ?CCL ?CPC ?CPCL ?IC ?ICL ?FC ?FCL ?CMM ?CMML ?TA ?TAL ?TAQ''',
                  
                  'MF': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?mf ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont
                                        (GROUP_CONCAT(DISTINCT(?f); separator=" <|> ") AS ?F) (GROUP_CONCAT(DISTINCT(?fL); SEPARATOR=" <|> ") AS ?FL)
                                        (GROUP_CONCAT(DISTINCT(?a); separator=" <|> ") AS ?A) (GROUP_CONCAT(DISTINCT(?aL); SEPARATOR=" <|> ") AS ?AL)
                                        (GROUP_CONCAT(DISTINCT(?bc); separator=" <|> ") AS ?BC) (GROUP_CONCAT(DISTINCT(?bcL); SEPARATOR=" <|> ") AS ?BCL)
                                        (GROUP_CONCAT(DISTINCT(?cc); separator=" <|> ") AS ?CC) (GROUP_CONCAT(DISTINCT(?ccL); SEPARATOR=" <|> ") AS ?CCL)
                                        (GROUP_CONCAT(DISTINCT(?cpc); separator=" <|> ") AS ?CPC) (GROUP_CONCAT(DISTINCT(?cpcL); SEPARATOR=" <|> ") AS ?CPCL)
                                        (GROUP_CONCAT(DISTINCT(?ic); separator=" <|> ") AS ?IC) (GROUP_CONCAT(DISTINCT(?icL); SEPARATOR=" <|> ") AS ?ICL)
                                        (GROUP_CONCAT(DISTINCT(?fc); separator=" <|> ") AS ?FC) (GROUP_CONCAT(DISTINCT(?fcL); SEPARATOR=" <|> ") AS ?FCL)
                                        (GROUP_CONCAT(DISTINCT(?elements); separator=" <|> ") AS ?formula_elements) (GROUP_CONCAT(DISTINCT(?formulas); separator=" <|> ") AS ?formula)
                                        (GROUP_CONCAT(?quantities; separator=" <|> ") AS ?quantity) (GROUP_CONCAT(?quantityLabels; separator=" <|> ") AS ?quantityLabel)
                                        (GROUP_CONCAT(?qC; separator=" <|> ") AS ?QC)
                  
                                 WHERE {{
                                        
                                        VALUES ?mf {{{0}}}
                  
                                        OPTIONAL {{ ?mf rdfs:comment ?quote.
                                                    FILTER (lang(?quote) = 'en')}}
                  
                                        OPTIONAL {{ ?mf :isLinear ?linear.}}
                                        OPTIONAL {{ ?mf :isConvex ?convex.}}
                                        OPTIONAL {{ ?mf :isDynamic ?dynamic.}}
                                        OPTIONAL {{ ?mf :isDeterministic ?deterministic.}}
                                        OPTIONAL {{ ?mf :isDimensionless ?dimensionless.}}
                                        OPTIONAL {{ ?mf :isTimeContinuous ?timecont.}}
                                        OPTIONAL {{ ?mf :isSpaceContinuous ?spacecont.}}
                  
                                        OPTIONAL {{ ?mf :containsFormulation ?f.
                                                    ?f rdfs:label ?fL.
                                                    FILTER (lang(?fL) = 'en')}}
                                        OPTIONAL {{ ?mf :containsAssumption ?a.
                                                    ?a rdfs:label ?aL.
                                                    FILTER (lang(?aL) = 'en')}}
                                        OPTIONAL {{ ?mf :containsBoundaryCondition ?bc.
                                                    ?bc rdfs:label ?bcL.
                                                    FILTER (lang(?bcL) = 'en')}}
                                        OPTIONAL {{ ?mf :containsConstraintCondition ?cc.
                                                    ?cc rdfs:label ?ccL.
                                                    FILTER (lang(?ccL) = 'en')}}
                                        OPTIONAL {{ ?mf :containsCouplingCondition ?cpc.
                                                    ?cpc rdfs:label ?cpcL.
                                                    FILTER (lang(?cpcL) = 'en')}}
                                        OPTIONAL {{ ?mf :containsInitialCondition ?ic.
                                                    ?ic rdfs:label ?icL.
                                                    FILTER (lang(?icL) = 'en')}}
                                        OPTIONAL {{ ?mf :containsFinalCondition ?fc.
                                                    ?fc rdfs:label ?fcL.
                                                    FILTER (lang(?fcL) = 'en')}}
                  
                                        OPTIONAL {{ ?mf :definingFormulation ?formulas.}}
                                        OPTIONAL {{ ?mf :inDefiningFormulation ?elements.}}
                  
                                        OPTIONAL {{ ?mf :containsQuantity ?quantities.
                                                    ?quantities rdfs:label ?quantityLabels;
                                                                a ?qC.
                                                    FILTER (?qC IN (:Quantity, :QuantityKind))
                                                    FILTER (lang(?quantityLabels) = 'en')}}
                  
                                        }}
                  
                                        GROUP BY ?mf ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont ?F ?FL ?A ?AL ?BC ?BCL ?CC ?CCL ?CPC ?CPCL ?IC ?ICL ?FC ?FCL 
                                                 ?formula_elements ?formula ?quantity ?quantityLabel ?QC''',
                  
                  'PU': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                  
                                 SELECT ?item ?label ?class
                                        (GROUP_CONCAT(DISTINCT(?pu1); separator=" <|> ") AS ?PU1) (GROUP_CONCAT(DISTINCT(?label1); separator=" <|> ") AS ?LABEL1)
                                        (GROUP_CONCAT(DISTINCT(?pu2); separator=" <|> ") AS ?PU2) (GROUP_CONCAT(DISTINCT(?label2); separator=" <|> ") AS ?LABEL2)
                                        (GROUP_CONCAT(DISTINCT(?pu3); separator=" <|> ") AS ?PU3) (GROUP_CONCAT(DISTINCT(?label3); separator=" <|> ") AS ?LABEL3)
                                        (GROUP_CONCAT(DISTINCT(?pu4); separator=" <|> ") AS ?PU4) (GROUP_CONCAT(DISTINCT(?label4); separator=" <|> ") AS ?LABEL4)
                                        (GROUP_CONCAT(DISTINCT(?pu5); separator=" <|> ") AS ?PU5) (GROUP_CONCAT(DISTINCT(?label5); separator=" <|> ") AS ?LABEL5)
                  
                                 WHERE {{
                  
                                        VALUES ?item {{{0}}}
                                        
                                        ?item rdfs:label ?label;
                                              a ?class.
                                        
                                        FILTER (lang(?label) = 'en')
                                        FILTER (?class IN (:ResearchField, :ResearchProblem, :MathematicalModel, :MathematicalFormulation, :Quantity, :QuantityKind, :ComputationalTask))
                  
                                        OPTIONAL {{ ?item :documentedIn ?pu1.
                                                    ?pu1 rdfs:label ?label1.
                                                    FILTER (lang(?label1) = 'en')
                                                 }}
                  
                                        OPTIONAL {{ ?item :inventedIn ?pu2.
                                                    ?pu2 rdfs:label ?label2.
                                                    FILTER (lang(?label2) = 'en')
                                                 }}
                  
                                        OPTIONAL {{ ?item :studiedIn ?pu3.
                                                    ?pu3 rdfs:label ?label3.
                                                    FILTER (lang(?label3) = 'en')
                                                 }}
                  
                                        OPTIONAL {{ ?item :surveyedIn ?pu4.
                                                    ?pu4 rdfs:label ?label4.
                                                    FILTER (lang(?label4) = 'en')
                                                 }}
                  
                                        OPTIONAL {{ ?item :usedIn ?pu5.
                                                    ?pu5 rdfs:label ?label5.
                                                    FILTER (lang(?label5) = 'en')
                                                 }}
                  
                                       }}
                  
                                 GROUP BY ?item ?label ?class ?PU1 ?LABEL1 ?PU2 ?LABEL2 ?PU3 ?LABEL3 ?PU4 ?LABEL4 ?PU5 ?LABEL5'''
                 }    

queryProvider = {
                 'RT': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                          SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)
                          WHERE {{
                                  {0} :appliedByTask ?answer .
                                  ?answer rdfs:label ?l .
                                  FILTER (lang(?l) = 'en')
                                }}
                         GROUP BY ?answer ?label''',

                 'RF': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                                SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                                WHERE { 
                                       ?answer a :ResearchField .
                                       ?answer rdfs:label ?l .
                                       FILTER (lang(?l) = 'en')
                                      }
                                GROUP BY ?answer ?label''',
                 
                 'RP': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                                SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                                WHERE { 
                                       ?answer a :ResearchProblem .
                                       ?answer rdfs:label ?l .
                                       FILTER (lang(?l) = 'en')
                                      }
                                GROUP BY ?answer ?label''',
                 
                 'MM': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                              SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                              WHERE { 
                                     ?answer a :MathematicalModel .
                                     ?answer rdfs:label ?l .
                                     FILTER (lang(?l) = 'en')
                                    }
                               GROUP BY ?answer ?label''',
                 
                 'MF': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                                SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                                WHERE { 
                                       ?answer a :MathematicalFormulation .
                                       ?answer rdfs:label ?l .
                                       FILTER (lang(?l) = 'en')
                                      }
                                GROUP BY ?answer ?label''',
                 
                 'Q': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                             PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                             SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                             WHERE { 
                                    ?answer a :Quantity .
                                    ?answer rdfs:label ?l .
                                    FILTER (lang(?l) = 'en')
                                   }
                             GROUP BY ?answer ?label''',
                 
                 'QK': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                              SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                              WHERE { 
                                     ?answer a :QuantityKind .
                                     ?answer rdfs:label ?l .
                                     FILTER (lang(?l) = 'en')
                                    }
                              GROUP BY ?answer ?label''',
                 
                 'T': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                              SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                              WHERE {
                                     ?answer a :ComputationalTask . 
                                     ?answer rdfs:label ?l .
                                     FILTER (lang(?l) = 'en')
                                    }
                               GROUP BY ?answer ?label''',
                 
                 'P': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                              SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)  
                              WHERE {
                                     ?answer a :Publication . 
                                     ?answer rdfs:label ?l .
                                     FILTER (lang(?l) = 'en')
                                    }
                               GROUP BY ?answer ?label''',
                 
                 'QQK': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
                              
                               SELECT DISTINCT ?answer ?class (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)
                                               
                               WHERE { 
                                      {
                                      ?answer a :Quantity.
                                      BIND(:Quantity AS ?class)
                                      } UNION {
                                      ?answer a :QuantityKind.
                                      BIND(:QuantityKind AS ?class)
                                      }
                                      ?answer rdfs:label ?l.
                                      FILTER (lang(?l) = 'en')
                                     }
                                GROUP BY ?answer ?class ?label'''
                }

queryModelHandler = {
    
       'All':   '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
             
                   SELECT DISTINCT ?mm ?mml ?rp ?rpl ?rf ?rfl ?ta ?tal ?gbmm ?gbmml ?gmm ?gmml ?abmm ?abmml ?amm ?amml ?dbmm ?dbmml ?dmm ?dmml 
                                   ?lbmm ?lbmml ?lmm ?lmml ?cmm ?cmml ?cimm ?cimml ?smm ?smml ?fmf ?fmfl ?fmfq ?fmfql ?fmfqc ?amf ?amfl ?amfq 
                                   ?amfql ?amfqc ?bcmf ?bcmfl ?bcmfq ?bcmfql ?bcmfqc ?ccmf ?ccmfl ?ccmfq ?ccmfql ?ccmfqc ?cpcmf ?cpcmfl ?cpcmfq 
                                   ?cpcmfql ?cpcmfqc ?icmf ?icmfl ?icmfq ?icmfql ?icmfqc ?fcmf ?fcmfl ?fcmfq ?fcmfql ?fcmfqc

                   WHERE {{ 
                   
                           VALUES ?mm {{{0}}}
                     
                           ?mm rdfs:label ?mml.
                           FILTER (lang(?mml) = 'en')

                           OPTIONAL {{ 
                                      ?mm :generalizedByModel ?gbmm. 
                                      ?gbmm rdfs:label ?gbmml.
                                      FILTER (lang(?gbmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :generalizesModel ?gmm. 
                                      ?gmm rdfs:label ?gmml.
                                      FILTER (lang(?gmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :approximatedByModel ?abmm. 
                                      ?abmm rdfs:label ?abmml.
                                      FILTER (lang(?abmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :approximatesModel ?amm. 
                                      ?amm rdfs:label ?amml.
                                      FILTER (lang(?amml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :discretizedByModel ?dbmm. 
                                      ?dbmm rdfs:label ?dbmml.
                                      FILTER (lang(?dbmml) = 'en')
                                    }}

                           OPTIONAL {{
                                      ?mm :discretizesModel ?dmm. 
                                      ?dmm rdfs:label ?dmml.
                                      FILTER (lang(?dmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :linearizedByModel ?lbmm.
                                      ?lbmm rdfs:label ?lbmml.
                                      FILTER (lang(?lbmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :linearizesModel ?lmm.
                                      ?lmm rdfs:label ?lmml.
                                      FILTER (lang(?lmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :similarToModel ?smm. 
                                      ?smm rdfs:label ?smml.
                                      FILTER (lang(?smml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :containsModel ?cmm. 
                                      ?cmm rdfs:label ?cmml.
                                      FILTER (lang(?cmml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :containedInModel ?cimm. 
                                      ?cimm rdfs:label ?cimml.
                                      FILTER (lang(?cimml) = 'en')
                                    }}

                           OPTIONAL {{ 
                                      ?mm :containsFormulation ?fmf. 
                                      ?fmf rdfs:label ?fmfl.
                                      FILTER (lang(?fmfl) = 'en')

                                      OPTIONAL {{
                                                 ?fmf :containsQuantity ?fmfq.
                                                 ?fmfq rdfs:label ?fmfql.
                                                 ?fmfq a ?fmfqc.
                                                 FILTER (lang(?fmfql) = 'en')
                                                 FILTER (?fmfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}
                      
                           OPTIONAL {{
                                      ?mm :containsAssumption ?amf. 
                                      ?amf rdfs:label ?amfl.
                                      FILTER (lang(?amfl) = 'en')

                                      OPTIONAL {{
                                                 ?amf :containsQuantity ?amfq.
                                                 ?amfq rdfs:label ?amfql.
                                                 ?amfq a ?amfqc.
                                                 FILTER (lang(?amfql) = 'en')
                                                 FILTER (?amfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}
                           
                           OPTIONAL {{ 
                                      ?mm :containsBoundaryCondition ?bcmf. 
                                      ?bcmf rdfs:label ?bcmfl.
                                      FILTER (lang(?bcmfl) = 'en')

                                      OPTIONAL {{
                                                 ?bcmf :containsQuantity ?bcmfq.
                                                 ?bcmfq rdfs:label ?bcmfql.
                                                 ?bcmfq a ?bcmfqc.
                                                 FILTER (lang(?bcmfql) = 'en')
                                                 FILTER (?bcmfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}

                           OPTIONAL {{ 
                                      ?mm :containsConstraintCondition ?ccmf. 
                                      ?ccmf rdfs:label ?ccmfl.
                                      FILTER (lang(?ccmfl) = 'en')

                                      OPTIONAL {{
                                                 ?ccmf :containsQuantity ?ccmfq.
                                                 ?ccmfq rdfs:label ?ccmfql.
                                                 ?ccmfq a ?ccmfqc.
                                                 FILTER (lang(?ccmfql) = 'en')
                                                 FILTER (?ccmfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}

                           OPTIONAL {{ 
                                      ?mm :containsCouplingCondition ?cpcmf. 
                                      ?cpcmf rdfs:label ?cpcmfl.
                                      FILTER (lang(?cpcmfl) = 'en')

                                      OPTIONAL {{
                                                 ?cpcmf :containsQuantity ?cpcmfq.
                                                 ?cpcmfq rdfs:label ?cpcmfql.
                                                 ?cpcmfq a ?cpcmfqc.
                                                 FILTER (lang(?cpcmfql) = 'en')
                                                 FILTER (?cpcmfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}

                           OPTIONAL {{ 
                                      ?mm :containsInitialCondition ?icmf. 
                                      ?icmf rdfs:label ?icmfl.
                                      FILTER (lang(?icmfl) = 'en')

                                      OPTIONAL {{
                                                 ?icmf :containsQuantity ?icmfq.
                                                 ?icmfq rdfs:label ?icmfql.
                                                 ?icmfq a ?icmfqc.
                                                 FILTER (lang(?icmfql) = 'en')
                                                 FILTER (?icmfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}

                           OPTIONAL {{ 
                                      ?mm :containsFinalCondition ?fcmf. 
                                      ?fcmf rdfs:label ?fcmfl.
                                      FILTER (lang(?fcmfl) = 'en')

                                      OPTIONAL {{
                                                 ?fcmf :containsQuantity ?fcmfq.
                                                 ?fcmfq rdfs:label ?fcmfql.
                                                 ?fcmfq a ?fcmfqc.
                                                 FILTER (lang(?fcmfql) = 'en')
                                                 FILTER (?fcmfqc IN (:Quantity, :QuantityKind))
                                               }}

                                    }}
                    
                           OPTIONAL {{
                                      ?mm :models ?rp.
                                      ?rp rdfs:label ?rpl. 
                                      FILTER (lang(?rpl) = 'en')  

                                      OPTIONAL {{
                                                 ?rp :containedInField ?rf.
                                                 ?rf rdfs:label ?rfl.
                                                 FILTER (lang(?rfl) = 'en')
                                               }}

                                    }}

                           OPTIONAL {{         
                                      ?mm :appliedByTask ?ta.
                                      ?ta rdfs:label ?tal.
                                      FILTER (lang(?tal) = 'en')
                                    }} 
                    }}

               GROUP BY ?mm ?mml ?fmf ?rp ?rpl ?rf ?rfl ?ta ?tal ?gbmm ?gbmml ?gmm ?gmml ?abmm ?abmml ?amm ?amml ?dbmm ?dbmml ?dmm ?dmml ?lbmm ?lbmml 
                        ?lmm ?lmml ?cmm ?cmml ?cimm ?cimml ?smm ?smml ?fmf ?fmfl ?fmfq ?fmfql ?fmfqc ?amf ?amfl ?amfq ?amfql ?amfqc ?bcmf ?bcmfl ?bcmfq 
                        ?bcmfql ?bcmfqc ?ccmf ?ccmfl ?ccmfq ?ccmfql ?ccmfqc ?cpcmf ?cpcmfl ?cpcmfq ?cpcmfql ?cpcmfqc ?icmf ?icmfl ?icmfq ?icmfql ?icmfqc 
                        ?fcmf ?fcmfl ?fcmfq ?fcmfql ?fcmfqc''',

       'MFRelations':  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                          SELECT ?mf 
                                 (GROUP_CONCAT(DISTINCT(?f); separator=" <|> ") AS ?F) (GROUP_CONCAT(DISTINCT(?fL); SEPARATOR=" <|> ") AS ?FL)
                                 (GROUP_CONCAT(DISTINCT(?fd); separator=" <|> ") AS ?FD) (GROUP_CONCAT(DISTINCT(?fdL); SEPARATOR=" <|> ") AS ?FDL)
                                 (GROUP_CONCAT(DISTINCT(?a); separator=" <|> ") AS ?A) (GROUP_CONCAT(DISTINCT(?aL); SEPARATOR=" <|> ") AS ?AL)
                                 (GROUP_CONCAT(DISTINCT(?ad); separator=" <|> ") AS ?AD) (GROUP_CONCAT(DISTINCT(?adL); SEPARATOR=" <|> ") AS ?ADL)
                                 (GROUP_CONCAT(DISTINCT(?bc); separator=" <|> ") AS ?BC) (GROUP_CONCAT(DISTINCT(?bcL); SEPARATOR=" <|> ") AS ?BCL)
                                 (GROUP_CONCAT(DISTINCT(?bcd); separator=" <|> ") AS ?BCD) (GROUP_CONCAT(DISTINCT(?bcdL); SEPARATOR=" <|> ") AS ?BCDL)
                                 (GROUP_CONCAT(DISTINCT(?cc); separator=" <|> ") AS ?CC) (GROUP_CONCAT(DISTINCT(?ccL); SEPARATOR=" <|> ") AS ?CCL)
                                 (GROUP_CONCAT(DISTINCT(?ccd); separator=" <|> ") AS ?CCD) (GROUP_CONCAT(DISTINCT(?ccdL); SEPARATOR=" <|> ") AS ?CCDL)
                                 (GROUP_CONCAT(DISTINCT(?cpc); separator=" <|> ") AS ?CPC) (GROUP_CONCAT(DISTINCT(?cpcL); SEPARATOR=" <|> ") AS ?CPCL)
                                 (GROUP_CONCAT(DISTINCT(?cpcd); separator=" <|> ") AS ?CPCD) (GROUP_CONCAT(DISTINCT(?cpcdL); SEPARATOR=" <|> ") AS ?CPCDL)
                                 (GROUP_CONCAT(DISTINCT(?ic); separator=" <|> ") AS ?IC) (GROUP_CONCAT(DISTINCT(?icL); SEPARATOR=" <|> ") AS ?ICL)
                                 (GROUP_CONCAT(DISTINCT(?icd); separator=" <|> ") AS ?ICD) (GROUP_CONCAT(DISTINCT(?icdL); SEPARATOR=" <|> ") AS ?ICDL)
                                 (GROUP_CONCAT(DISTINCT(?fc); separator=" <|> ") AS ?FC) (GROUP_CONCAT(DISTINCT(?fcL); SEPARATOR=" <|> ") AS ?FCL)
                                 (GROUP_CONCAT(DISTINCT(?fcd); separator=" <|> ") AS ?FCD) (GROUP_CONCAT(DISTINCT(?fcdL); SEPARATOR=" <|> ") AS ?FCDL)
                                 (GROUP_CONCAT(DISTINCT(?fgbf); separator=" <|> ") AS ?FGBF) (GROUP_CONCAT(DISTINCT(?fgbfL); SEPARATOR=" <|> ") AS ?FGBFL)
                                 (GROUP_CONCAT(DISTINCT(?fgf); separator=" <|> ") AS ?FGF) (GROUP_CONCAT(DISTINCT(?fgfL); SEPARATOR=" <|> ") AS ?FGFL)
                                 (GROUP_CONCAT(DISTINCT(?fabf); separator=" <|> ") AS ?FABF) (GROUP_CONCAT(DISTINCT(?fabfL); SEPARATOR=" <|> ") AS ?FABFL)
                                 (GROUP_CONCAT(DISTINCT(?faf); separator=" <|> ") AS ?FAF) (GROUP_CONCAT(DISTINCT(?fafL); SEPARATOR=" <|> ") AS ?FAFL)
                                 (GROUP_CONCAT(DISTINCT(?fdbf); separator=" <|> ") AS ?FDBF) (GROUP_CONCAT(DISTINCT(?fdbfL); SEPARATOR=" <|> ") AS ?FDBFL)
                                 (GROUP_CONCAT(DISTINCT(?fdf); separator=" <|> ") AS ?FDF) (GROUP_CONCAT(DISTINCT(?fdfL); SEPARATOR=" <|> ") AS ?FDFL)
                                 (GROUP_CONCAT(DISTINCT(?flbf); separator=" <|> ") AS ?FLBF) (GROUP_CONCAT(DISTINCT(?flbfL); SEPARATOR=" <|> ") AS ?FLBFL)
                                 (GROUP_CONCAT(DISTINCT(?flf); separator=" <|> ") AS ?FLF) (GROUP_CONCAT(DISTINCT(?flfL); SEPARATOR=" <|> ") AS ?FLFL)
                                 (GROUP_CONCAT(DISTINCT(?fnbf); separator=" <|> ") AS ?FNBF) (GROUP_CONCAT(DISTINCT(?fnbfL); SEPARATOR=" <|> ") AS ?FNBFL)
                                 (GROUP_CONCAT(DISTINCT(?fnf); separator=" <|> ") AS ?FNF) (GROUP_CONCAT(DISTINCT(?fnfL); SEPARATOR=" <|> ") AS ?FNFL)
                                 (GROUP_CONCAT(DISTINCT(?fsf); separator=" <|> ") AS ?FSF) (GROUP_CONCAT(DISTINCT(?fsfL); SEPARATOR=" <|> ") AS ?FSFL)
                                 
                          WHERE {{
                                 
                                 VALUES ?mf {{{0}}}
          
                                 OPTIONAL {{ ?mf :containsFormulation ?f.
                                             ?f a :MathematicalFormulation.
                                             ?f rdfs:label ?fL.
                                             FILTER (lang(?fL) = 'en')}}

                                 OPTIONAL {{ ?mf :containedAsFormulationIn ?fd.
                                             ?fd a :MathematicalFormulation.
                                             ?fd rdfs:label ?fdL.
                                             FILTER (lang(?fdL) = 'en')}}

                                 OPTIONAL {{ ?mf :containsAssumption ?a.
                                             ?a a :MathematicalFormulation.
                                             ?a rdfs:label ?aL.
                                             FILTER (lang(?aL) = 'en')}}

                                 OPTIONAL {{ ?mf :containedAsAssumptionIn ?ad.
                                             ?ad a :MathematicalFormulation.
                                             ?ad rdfs:label ?adL.
                                             FILTER (lang(?adL) = 'en')}}

                                 OPTIONAL {{ ?mf :containsBoundaryCondition ?bc.
                                             ?bc a :MathematicalFormulation.
                                             ?bc rdfs:label ?bcL.
                                             FILTER (lang(?bcL) = 'en')}}

                                 OPTIONAL {{ ?mf :containedAsBoundaryConditionIn ?bcd.
                                             ?bcd a :MathematicalFormulation.
                                             ?bcd rdfs:label ?bcdL.
                                             FILTER (lang(?bcdL) = 'en')}}

                                 OPTIONAL {{ ?mf :containsConstraintCondition ?cc.
                                             ?cc a :MathematicalFormulation.
                                             ?cc rdfs:label ?ccL.
                                             FILTER (lang(?ccL) = 'en')}}

                                 OPTIONAL {{ ?mf :containedAsConstraintConditionIn ?ccd.
                                             ?ccd a :MathematicalFormulation.
                                             ?ccd rdfs:label ?ccdL.
                                             FILTER (lang(?ccdL) = 'en')}}

                                 OPTIONAL {{ ?mf :containsCouplingCondition ?cpc.
                                             ?cpc a :MathematicalFormulation.
                                             ?cpc rdfs:label ?cpcL.
                                             FILTER (lang(?cpcL) = 'en')}}

                                 OPTIONAL {{ ?mf :containedAsCouplingConditionIn ?cpcd.
                                             ?cpcd a :MathematicalFormulation.
                                             ?cpcd rdfs:label ?cpcdL.
                                             FILTER (lang(?cpcdL) = 'en')}}

                                 OPTIONAL {{ ?mf :containsInitialCondition ?ic.
                                             ?ic a :MathematicalFormulation.
                                             ?ic rdfs:label ?icL.
                                             FILTER (lang(?icL) = 'en')}}

                                 OPTIONAL {{ ?mf :containedAsInitialConditionIn ?icd.
                                             ?icd a :MathematicalFormulation. 
                                             ?icd rdfs:label ?icdL.
                                             FILTER (lang(?icdL) = 'en')}}

                                 OPTIONAL {{ ?mf :containsFinalCondition ?fc.
                                             ?fc a :MathematicalFormulation.
                                             ?fc rdfs:label ?fcL.
                                             FILTER (lang(?fcL) = 'en')}}
                                
                                 OPTIONAL {{ ?mf :containedAsFinalConditionIn ?fcd.
                                             ?fcd a :MathematicalFormulation.
                                             ?fcd rdfs:label ?fcdL.
                                             FILTER (lang(?fcdL) = 'en')}}

                                 OPTIONAL {{ 
                                           ?mf :generalizedByFormulation ?fgbf. 
                                           ?fgbf rdfs:label ?fgbfL.
                                           FILTER (lang(?fgbfL) = 'en')
                                        }}

                               OPTIONAL {{ 
                                           ?mf :generalizesFormulation ?fgf. 
                                           ?fgf rdfs:label ?fgfL.
                                           FILTER (lang(?fgfL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :approximatedByFormulation ?fabf. 
                                           ?fabf rdfs:label ?fabfL.
                                           FILTER (lang(?abL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :approximatesFormulation ?faf. 
                                           ?faf rdfs:label ?fafL.
                                           FILTER (lang(?fafL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :discretizedByFormulation ?fdbf. 
                                           ?fdbf rdfs:label ?fdbfL.
                                           FILTER (lang(?fdbfL) = 'en')
                                        }}
                               OPTIONAL {{ ?mf :discretizesFormulation ?fdf. 
                                           ?fdf rdfs:label ?fdfL.
                                           FILTER (lang(?fdfL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :linearizedByFormulation ?flbf.
                                           ?flbf rdfs:label ?flbfL.
                                           FILTER (lang(?flbfL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :linearizesFormulation ?flf.
                                           ?flf rdfs:label ?flfL.
                                           FILTER (lang(?flfL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :nondimensionalizedByFormulation ?fnbf.
                                           ?fnbf rdfs:label ?fnbfL.
                                           FILTER (lang(?fnbfL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :nondimensionalizesFormulation ?fnf.
                                           ?fnf rdfs:label ?fnfL.
                                           FILTER (lang(?fnfL) = 'en')
                                        }}
                               OPTIONAL {{ 
                                           ?mf :similarToFormulation ?fsf. 
                                           ?fsf rdfs:label ?fsfL.
                                           FILTER (lang(?fsfL) = 'en')
                                        }}

                                }}
          
                              GROUP BY ?mf ?F ?FL ?A ?AL ?BC ?BCL ?CC ?CCL ?CPC ?CPCL ?IC ?ICL ?FC ?FCL 
                                           ?FD ?FDL ?AD ?ADL ?BCD ?BCDL ?CCD ?CCDL ?CPCD ?CPCDL ?ICD ?ICDL ?FCD ?FCDL
                                           ?FGBF ?FGBFL ?FGF ?FGFL ?FABF ?FABFL ?FAF ?FAFL ?FDBF ?FDBFL ?FDF ?FDFL ?FLBF ?FLBFL ?FLF ?FLFL
                                           ?FNBF ?FNBFL ?FNF ?FNFL ?FSF ?FSFL''',

       'TRelation':    '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
                          SELECT ?t 
                                 (GROUP_CONCAT(DISTINCT(?tgbt); separator=" <|> ") AS ?TGBT) (GROUP_CONCAT(DISTINCT(?tgbtL); SEPARATOR=" <|> ") AS ?TGBTL)
                                 (GROUP_CONCAT(DISTINCT(?tgt); separator=" <|> ") AS ?TGT) (GROUP_CONCAT(DISTINCT(?tgtL); SEPARATOR=" <|> ") AS ?TGTL)
                                 (GROUP_CONCAT(DISTINCT(?tabt); separator=" <|> ") AS ?TABT) (GROUP_CONCAT(DISTINCT(?tabtL); SEPARATOR=" <|> ") AS ?TABTL)
                                 (GROUP_CONCAT(DISTINCT(?tat); separator=" <|> ") AS ?TAT) (GROUP_CONCAT(DISTINCT(?tatL); SEPARATOR=" <|> ") AS ?TATL)
                                 (GROUP_CONCAT(DISTINCT(?tdbt); separator=" <|> ") AS ?TDBT) (GROUP_CONCAT(DISTINCT(?tdbtL); SEPARATOR=" <|> ") AS ?TDBTL)
                                 (GROUP_CONCAT(DISTINCT(?tdt); separator=" <|> ") AS ?TDT) (GROUP_CONCAT(DISTINCT(?tdtL); SEPARATOR=" <|> ") AS ?TDTL)
                                 (GROUP_CONCAT(DISTINCT(?tict); separator=" <|> ") AS ?TICT) (GROUP_CONCAT(DISTINCT(?tictL); SEPARATOR=" <|> ") AS ?TICTL)
                                 (GROUP_CONCAT(DISTINCT(?tct); separator=" <|> ") AS ?TCT) (GROUP_CONCAT(DISTINCT(?tctL); SEPARATOR=" <|> ") AS ?TCTL)
                                 (GROUP_CONCAT(DISTINCT(?tlbt); separator=" <|> ") AS ?TLBT) (GROUP_CONCAT(DISTINCT(?tlbtL); SEPARATOR=" <|> ") AS ?TLBTL)
                                 (GROUP_CONCAT(DISTINCT(?tlt); separator=" <|> ") AS ?TLT) (GROUP_CONCAT(DISTINCT(?tltL); SEPARATOR=" <|> ") AS ?TLTL)
                                 (GROUP_CONCAT(DISTINCT(?tst); separator=" <|> ") AS ?TST) (GROUP_CONCAT(DISTINCT(?tstL); SEPARATOR=" <|> ") AS ?TSTL) 
                                                              
                          WHERE {{
                                   VALUES ?t {{{0}}}
                                   
                                   OPTIONAL {{ 
                                               ?t :generalizedByTask ?tgbt. 
                                               ?tgbt rdfs:label ?tgbtL.
                                               FILTER (lang(?tgbtL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :generalizesTask ?tgt. 
                                               ?tgt rdfs:label ?tgtL.
                                               FILTER (lang(?tgtL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :approximatedByTask ?tabt. 
                                               ?tabt rdfs:label ?tabtL.
                                               FILTER (lang(?tabtL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :approximatesTask ?tat. 
                                               ?tat rdfs:label ?tatL.
                                               FILTER (lang(?tatL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :discretizedByTask ?tdbt. 
                                               ?tdbt rdfs:label ?tdbtL.
                                               FILTER (lang(?tdbtL) = 'en')
                                            }}
                                   OPTIONAL {{ ?t :discretizesTask ?tdt. 
                                               ?tdt rdfs:label ?tdtL.
                                               FILTER (lang(?tdtL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :containedInTask ?tict. 
                                               ?tict rdfs:label ?tictL.
                                               FILTER (lang(?tictL) = 'en')
                                            }}
                                   OPTIONAL {{ ?t :containsTask ?tct. 
                                               ?tct rdfs:label ?tctL.
                                               FILTER (lang(?tctL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :linearizedByTask ?tlbt.
                                               ?tlbt rdfs:label ?tlbtL.
                                               FILTER (lang(?tlbtL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :linearizesTask ?tlt.
                                               ?tlt rdfs:label ?tltL.
                                               FILTER (lang(?tltL) = 'en')
                                            }}
                                   OPTIONAL {{ 
                                               ?t :similarToTask ?tst. 
                                               ?tst rdfs:label ?tstL.
                                               FILTER (lang(?tstL) = 'en')
                                            }}
                                }}
    
                    GROUP BY ?t ?TGBT ?TGBTL ?TGT ?TGTL ?TABT ?TABTL ?TAT ?TATL ?TDBT ?TDBTL ?TDT ?TDTL ?TICT ?TICTL ?TCT ?TCTL ?TLBT ?TLBTL ?TLT ?TLTL 
                             ?TST ?TSTL''',

       'PRelation': '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
         
                       SELECT ?item ?label ?class
                              (GROUP_CONCAT(DISTINCT(?pu1); separator=" <|> ") AS ?PU1) (GROUP_CONCAT(DISTINCT(?label1); separator=" <|> ") AS ?LABEL1)
                              (GROUP_CONCAT(DISTINCT(?pu2); separator=" <|> ") AS ?PU2) (GROUP_CONCAT(DISTINCT(?label2); separator=" <|> ") AS ?LABEL2)
                              (GROUP_CONCAT(DISTINCT(?pu3); separator=" <|> ") AS ?PU3) (GROUP_CONCAT(DISTINCT(?label3); separator=" <|> ") AS ?LABEL3)
                              (GROUP_CONCAT(DISTINCT(?pu4); separator=" <|> ") AS ?PU4) (GROUP_CONCAT(DISTINCT(?label4); separator=" <|> ") AS ?LABEL4)
                              (GROUP_CONCAT(DISTINCT(?pu5); separator=" <|> ") AS ?PU5) (GROUP_CONCAT(DISTINCT(?label5); separator=" <|> ") AS ?LABEL5)
         
                       WHERE {{
         
                              VALUES ?item {{{0}}}
                              
                              ?item rdfs:label ?label;
                                    a ?class.
                              
                              FILTER (lang(?label) = 'en')
                              FILTER (?class IN (:ResearchField, :ResearchProblem, :MathematicalModel, :MathematicalFormulation, :Quantity, :QuantityKind, :ComputationalTask))
         
                              OPTIONAL {{ ?item :documentedIn ?pu1.
                                          ?pu1 rdfs:label ?label1.
                                          FILTER (lang(?label1) = 'en')
                                       }}
         
                              OPTIONAL {{ ?item :inventedIn ?pu2.
                                          ?pu2 rdfs:label ?label2.
                                          FILTER (lang(?label2) = 'en')
                                       }}
         
                              OPTIONAL {{ ?item :studiedIn ?pu3.
                                          ?pu3 rdfs:label ?label3.
                                          FILTER (lang(?label3) = 'en')
                                       }}
         
                              OPTIONAL {{ ?item :surveyedIn ?pu4.
                                          ?pu4 rdfs:label ?label4.
                                          FILTER (lang(?label4) = 'en')
                                       }}
         
                              OPTIONAL {{ ?item :usedIn ?pu5.
                                          ?pu5 rdfs:label ?label5.
                                          FILTER (lang(?label5) = 'en')
                                       }}
         
                             }}
         
                       GROUP BY ?item ?label ?class ?PU1 ?LABEL1 ?PU2 ?LABEL2 ?PU3 ?LABEL3 ?PU4 ?LABEL4 ?PU5 ?LABEL5''' 
       }

                      
