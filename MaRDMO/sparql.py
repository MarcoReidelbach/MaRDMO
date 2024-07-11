from .config import *
from .id import *

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

query_1  = '''SELECT ?publicationQid ?publicationLabel ?publicationDescription1         
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
                     OPTIONAL {{?publication wdt:P{12} ?page.}}}}'''

query_2 = '''# Query for MaRDI portal                                              

             SELECT  ?publicationQid ?publicationLabel ?publicationDescription1                                               
             
             WHERE {{
                     # Publication via Wikidata QID

                     ?publication wdt:P{0} "{1}";
                             rdfs:label ?publicationLabel.
                     OPTIONAL {{?publication schema:description ?publicationDescription.}}

                     BIND(COALESCE(?publicationDescription, "") As ?publicationDescription1)
                     BIND(STRAFTER(STR(?publication),STR(wd:)) AS ?publicationQid).
                   
                   }}'''


query_3 = '''SELECT ?authorQid ?authorLabel ?authorDescription ?authorId        # Author of Publication via ORCID/zbMath

             WHERE {{

                     VALUES ?authorId {{{0}}}

                     OPTIONAL {{
                                # Author via ORCID
                                ?author wdt:P{1} ?authorId
                                BIND(STRAFTER(STR(?author),STR(wd:)) AS ?authorQid)
                              }}

                      SERVICE wikibase:label {{bd:serviceParam wikibase:language "en,en".}}

                    }}'''

query_4 = '''SELECT ?wikidataQid ?mardiQid ?authorLabel ?authorDescription         # Author of Publication via Wikidata QID

             WHERE {{

                     VALUES ?wikidataQid {{{0}}}

                     OPTIONAL {{
                                # Author via Wikidata QID
                                ?author wdt:P{1} ?wikidataQid
                                BIND(STRAFTER(STR(?author),STR(wd:)) AS ?mardiQid)
                              }}

                     SERVICE wikibase:label {{bd:serviceParam wikibase:language "en,en".}}

                   }}'''


### SPARQL queries to get additional information from MathModDB during export

query_models = '''PREFIX : <https://mardi4nfdi.de/mathmoddb>
                  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
                  SELECT DISTINCT ?answer (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?label)
                  WHERE {{
                          <{0}> :models ?answer.
                          ?answer rdfs:label ?l.
                          FILTER (lang(?l) = 'en')
                        }}
                  GROUP BY ?answer ?label'''

query_rfs = '''PREFIX : <https://mardi4nfdi.de/mathmoddb>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

               SELECT DISTINCT (GROUP_CONCAT(DISTINCT(?l); SEPARATOR=" / ") AS ?quote)
               WHERE {{
                       <{0}> rdfs:comment ?l.
                       FILTER (lang(?l) = 'en')
                     }}
               GROUP BY ?quote'''

query_rps = '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
               
               SELECT (GROUP_CONCAT(DISTINCT(?l2); SEPARATOR=" / ") AS ?quote) (GROUP_CONCAT(DISTINCT(?l1); SEPARATOR=" / ") AS ?label)
                      (GROUP_CONCAT(DISTINCT(?field); separator=" <|> ") AS ?FIELD) (GROUP_CONCAT(DISTINCT(?fieldLabel); SEPARATOR=" <|> ") AS ?FIELDLabel)
                      (GROUP_CONCAT(DISTINCT(?fieldQuote); SEPARATOR=" <|> ") AS ?FIELDQuote)

               WHERE {{
                       <{0}> rdfs:label ?l1.
                       FILTER (lang(?l1) = 'en')
                       OPTIONAL {{ <{0}> rdfs:comment ?l2 .
                                   FILTER (lang(?l2) = 'en').
                                }}
                       
                       OPTIONAL {{ <{0}> :containedInField ?field.
                                   ?field rdfs:label ?fieldLabel.
                                   FILTER (lang(?fieldLabel) = 'en').

                                   OPTIONAL {{ ?field rdfs:comment ?fieldQuote.
                                               FILTER (lang(?fieldQuote) = 'en').}}
                                }}
                     }}

               GROUP BY ?label ?quote ?FIELD ?FIELDLabel ?FIELDQuote'''

query_q =   '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
	           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

	           SELECT ?q ?answer ?qlinear ?qdimensionless ?qkdimensionless 
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
                      OPTIONAL {{ ?answer :isDimensionless ?qkdimensionless.}}
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
                GROUP BY ?q ?answer ?qlabel ?qquote ?qlinear ?qdimensionless ?qklabel ?qkquote ?qkdimensionless'''

query_q2 =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
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
                               ?formula_elements ?formula ?quantity ?quantityLabel ?QC'''

query_q3 =   '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?q
                       (GROUP_CONCAT(DISTINCT(?gbQuantity); separator=" <|> ") AS ?GBQUANTITY) (GROUP_CONCAT(DISTINCT(?gbqLabel); SEPARATOR=" <|> ") AS ?GBQLabel)
                       (GROUP_CONCAT(DISTINCT(?gQuantity); separator=" <|> ") AS ?GQUANTITY) (GROUP_CONCAT(DISTINCT(?gqLabel); SEPARATOR=" <|> ") AS ?GQLabel)
                       (GROUP_CONCAT(DISTINCT(?abQuantity); separator=" <|> ") AS ?ABQUANTITY) (GROUP_CONCAT(DISTINCT(?abqLabel); SEPARATOR=" <|> ") AS ?ABQLabel)
                       (GROUP_CONCAT(DISTINCT(?aQuantity); separator=" <|> ") AS ?AQUANTITY) (GROUP_CONCAT(DISTINCT(?aqLabel); SEPARATOR=" <|> ") AS ?AQLabel)
                       (GROUP_CONCAT(DISTINCT(?lbQuantity); separator=" <|> ") AS ?LBQUANTITY) (GROUP_CONCAT(DISTINCT(?lbqLabel); SEPARATOR=" <|> ") AS ?LBQLabel)
                       (GROUP_CONCAT(DISTINCT(?lQuantity); separator=" <|> ") AS ?LQUANTITY) (GROUP_CONCAT(DISTINCT(?lqLabel); SEPARATOR=" <|> ") AS ?LQLabel)
                       (GROUP_CONCAT(DISTINCT(?nbQuantity); separator=" <|> ") AS ?NBQUANTITY) (GROUP_CONCAT(DISTINCT(?nbqLabel); SEPARATOR=" <|> ") AS ?NBQLabel)
                       (GROUP_CONCAT(DISTINCT(?nQuantity); separator=" <|> ") AS ?NQUANTITY) (GROUP_CONCAT(DISTINCT(?nqLabel); SEPARATOR=" <|> ") AS ?NQLabel)
                       (GROUP_CONCAT(DISTINCT(?sQuantity); separator=" <|> ") AS ?SQUANTITY) (GROUP_CONCAT(DISTINCT(?sqLabel); SEPARATOR=" <|> ") AS ?SQLabel)
                       (GROUP_CONCAT(?gbClass; separator=" <|> ") AS ?GBCLASS) (GROUP_CONCAT(?gClass; separator=" <|> ") AS ?GCLASS)
                       (GROUP_CONCAT(?abClass; separator=" <|> ") AS ?ABCLASS) (GROUP_CONCAT(?aClass; separator=" <|> ") AS ?ACLASS)
                       (GROUP_CONCAT(?lbClass; separator=" <|> ") AS ?LBCLASS) (GROUP_CONCAT(?lClass; separator=" <|> ") AS ?LCLASS)
                       (GROUP_CONCAT(?nbClass; separator=" <|> ") AS ?NBCLASS) (GROUP_CONCAT(?nClass; separator=" <|> ") AS ?NCLASS)
                       (GROUP_CONCAT(?sClass; separator=" <|> ") AS ?SCLASS)

                WHERE {{
                        VALUES ?q {{{0}}}

                        OPTIONAL {{ ?q :generalizedByQuantity ?gbQuantity. 
                                    ?gbQuantity rdfs:label ?gbqLabel.
                                    ?gbQuantity a ?gbClass.
                                    FILTER (lang(?gbqLabel) = 'en')
                                    FILTER (?gbClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :generalizesQuantity ?gQuantity. 
                                    ?gQuantity rdfs:label ?gqLabel.
                                    ?gQuantity a ?gClass.
                                    FILTER (lang(?gqLabel) = 'en')
                                    FILTER (?gClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :approximatedByQuantity ?abQuantity. 
                                    ?abQuantity rdfs:label ?abqLabel.
                                    ?abQuantity a ?abClass.
                                    FILTER (lang(?abqLabel) = 'en')
                                    FILTER (?abClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :approximatesQuantity ?aQuantity. 
                                    ?aQuantity rdfs:label ?aqLabel.
                                    ?aQuantity a ?aClass.
                                    FILTER (lang(?aqLabel) = 'en')
                                    FILTER (?aClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :linearizedByQuantity ?lbQuantity.
                                    ?lbQuantity rdfs:label ?lbqLabel.
                                    ?lbQuantity a ?lbClass.
                                    FILTER (lang(?lbqLabel) = 'en')
                                    FILTER (?lbClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :linearizesQuantity ?lQuantity.
                                    ?lQuantity rdfs:label ?lqLabel.
                                    ?lQuantity a ?lClass.
                                    FILTER (lang(?lqLabel) = 'en')
                                    FILTER (?lClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :nondimensionalizedByQuantity ?nbQuantity.
                                    ?nbQuantity rdfs:label ?nbqLabel.
                                    ?nbQuantity a ?nbClass.
                                    FILTER (lang(?nbqLabel) = 'en')
                                    FILTER (?nbClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :nondimensionalizesQuantity ?nQuantity.
                                    ?nQuantity rdfs:label ?nqLabel.
                                    ?nQuantity a ?nClass.
                                    FILTER (lang(?nqLabel) = 'en')
                                    FILTER (?nClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :similarToQuantity ?sQuantity. 
                                    ?sQuantity rdfs:label ?sqLabel.
                                    ?sQuantity a ?sClass.
                                    FILTER (lang(?sqLabel) = 'en')
                                    FILTER (?sClass IN (:Quantity, :QuantityKind))}}
                     }}

                GROUP BY ?q ?GBQUANTITY ?GBQLabel ?GBCLASS ?GQUANTITY ?GQLabel ?GCLASS ?ABQUANTITY ?ABQLabel ?ABCLASS ?AQUANTITY ?AQLabel ?ACLASS 
                         ?LBQUANTITY ?LBQLabel ?LBCLASS ?LQUANTITY ?LQLabel ?LCLASS ?NBQUANTITY ?NBQLabel ?NBCLASS ?NQUANTITY ?NQLabel ?NCLASS ?SQUANTITY ?SQLabel ?SCLASS'''

query_qk2 =   '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?q
                       (GROUP_CONCAT(DISTINCT(?gbQuantity); separator=" <|> ") AS ?GBQUANTITY) (GROUP_CONCAT(DISTINCT(?gbqLabel); SEPARATOR=" <|> ") AS ?GBQLabel)
                       (GROUP_CONCAT(DISTINCT(?gQuantity); separator=" <|> ") AS ?GQUANTITY) (GROUP_CONCAT(DISTINCT(?gqLabel); SEPARATOR=" <|> ") AS ?GQLabel)
                       (GROUP_CONCAT(DISTINCT(?nbQuantity); separator=" <|> ") AS ?NBQUANTITY) (GROUP_CONCAT(DISTINCT(?nbqLabel); SEPARATOR=" <|> ") AS ?NBQLabel)
                       (GROUP_CONCAT(DISTINCT(?nQuantity); separator=" <|> ") AS ?NQUANTITY) (GROUP_CONCAT(DISTINCT(?nqLabel); SEPARATOR=" <|> ") AS ?NQLabel)
                       (GROUP_CONCAT(DISTINCT(?sQuantity); separator=" <|> ") AS ?SQUANTITY) (GROUP_CONCAT(DISTINCT(?sqLabel); SEPARATOR=" <|> ") AS ?SQLabel)
                       (GROUP_CONCAT(?gbClass; separator=" <|> ") AS ?GBCLASS) (GROUP_CONCAT(?gClass; separator=" <|> ") AS ?GCLASS)
                       (GROUP_CONCAT(?nbClass; separator=" <|> ") AS ?NBCLASS) (GROUP_CONCAT(?nClass; separator=" <|> ") AS ?NCLASS)
                       (GROUP_CONCAT(?sClass; separator=" <|> ") AS ?SCLASS)

                WHERE {{
                        VALUES ?q {{{0}}}

                        OPTIONAL {{ ?q :generalizedByQuantity ?gbQuantity. 
                                    ?gbQuantity rdfs:label ?gbqLabel.
                                    ?gbQuantity a ?gbClass.
                                    FILTER (lang(?gbqLabel) = 'en')
                                    FILTER (?gbClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :generalizesQuantity ?gQuantity. 
                                    ?gQuantity rdfs:label ?gqLabel.
                                    ?gQuantity a ?gClass.
                                    FILTER (lang(?gqLabel) = 'en')
                                    FILTER (?gClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :nondimensionalizedByQuantity ?nbQuantity.
                                    ?nbQuantity rdfs:label ?nbqLabel.
                                    ?nbQuantity a ?nbClass.
                                    FILTER (lang(?nbqLabel) = 'en')
                                    FILTER (?nbClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :nondimensionalizesQuantity ?nQuantity.
                                    ?nQuantity rdfs:label ?nqLabel.
                                    ?nQuantity a ?nClass.
                                    FILTER (lang(?nqLabel) = 'en')
                                    FILTER (?nClass IN (:Quantity, :QuantityKind))}}
                        OPTIONAL {{ ?q :similarToQuantity ?sQuantity. 
                                    ?sQuantity rdfs:label ?sqLabel.
                                    ?sQuantity a ?sClass.
                                    FILTER (lang(?sqLabel) = 'en')
                                    FILTER (?sClass IN (:Quantity, :QuantityKind))}}
                     }}

                GROUP BY ?q ?GBQUANTITY ?GBQLabel ?GBCLASS ?GQUANTITY ?GQLabel ?GCLASS ?NBQUANTITY ?NBQLabel ?NBCLASS ?NQUANTITY ?NQLabel ?NCLASS ?SQUANTITY ?SQLabel ?SCLASS'''

query_qk =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
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
               GROUP BY ?qk ?qklabel ?qkquote ?qkdimensionless'''

query_ta =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

               SELECT ?t ?subclass ?quote ?linear 
                      (GROUP_CONCAT(DISTINCT ?p; SEPARATOR=" <|> ") AS ?P) (GROUP_CONCAT(DISTINCT ?pL; SEPARATOR=" <|> ") AS ?PL)
                      (GROUP_CONCAT(DISTINCT(?f); separator=" <|> ") AS ?F) (GROUP_CONCAT(DISTINCT(?fL); SEPARATOR=" <|> ") AS ?FL)
                      (GROUP_CONCAT(DISTINCT(?a); separator=" <|> ") AS ?A) (GROUP_CONCAT(DISTINCT(?aL); SEPARATOR=" <|> ") AS ?AL)
                      (GROUP_CONCAT(DISTINCT(?bc); separator=" <|> ") AS ?BC) (GROUP_CONCAT(DISTINCT(?bcL); SEPARATOR=" <|> ") AS ?BCL)
                      (GROUP_CONCAT(DISTINCT(?cc); separator=" <|> ") AS ?CC) (GROUP_CONCAT(DISTINCT(?ccL); SEPARATOR=" <|> ") AS ?CCL)
                      (GROUP_CONCAT(DISTINCT(?cpc); separator=" <|> ") AS ?CPC) (GROUP_CONCAT(DISTINCT(?cpcL); SEPARATOR=" <|> ") AS ?CPCL)
                      (GROUP_CONCAT(DISTINCT(?ic); separator=" <|> ") AS ?IC) (GROUP_CONCAT(DISTINCT(?icL); SEPARATOR=" <|> ") AS ?ICL)
                      (GROUP_CONCAT(DISTINCT(?fc); separator=" <|> ") AS ?FC) (GROUP_CONCAT(DISTINCT(?fcL); SEPARATOR=" <|> ") AS ?FCL)
                      (GROUP_CONCAT(?in; separator=" <|> ") AS ?IN) (GROUP_CONCAT(?inL; SEPARATOR=" <|> ") AS ?INL)
                      (GROUP_CONCAT(?inC; SEPARATOR=" <|> ") AS ?INC)
                      (GROUP_CONCAT(?o; separator=" <|> ") AS ?O) (GROUP_CONCAT(?oL; SEPARATOR=" <|> ") AS ?OL)
                      (GROUP_CONCAT(?oC; SEPARATOR=" <|> ") AS ?OC)
                      (GROUP_CONCAT(DISTINCT(?ob); separator=" <|> ") AS ?OB) (GROUP_CONCAT(DISTINCT(?obL); SEPARATOR=" <|> ") AS ?OBL)
                      (GROUP_CONCAT(DISTINCT(?obC); SEPARATOR=" <|> ") AS ?OBC)
                      (GROUP_CONCAT(DISTINCT(?pa); separator=" <|> ") AS ?PA) (GROUP_CONCAT(DISTINCT(?paL); SEPARATOR=" <|> ") AS ?PAL)
                      (GROUP_CONCAT(DISTINCT(?paC); SEPARATOR=" <|> ") AS ?PAC)

               WHERE {{
                      VALUES ?t {{{0}}}

                      OPTIONAL {{ ?subclass rdfs:subClassOf :Task.
                                  ?t a ?subclass .}}
                      OPTIONAL {{ ?t rdfs:comment ?quote.
                                  FILTER (lang(?quote) = 'en')}}
                      OPTIONAL {{ ?t :isLinear ?linear.}}
                      OPTIONAL {{ ?t :containedInProblem ?p.
                                  ?p rdfs:label ?pL.
                                  Filter (lang(?pL) = 'en')}}
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
                      OPTIONAL {{ ?t :containsInput ?in.
                                  ?in rdfs:label ?inL;
                                         a ?inC.
                                  FILTER (lang(?inL) = 'en')
                                  FILTER (?inC IN (:Quantity, :QuantityKind, :MathematicalFormulation))}}
                      OPTIONAL {{ ?t :containsOutput ?o.
                                  ?o rdfs:label ?oL;
                                          a ?oC.      
                                  FILTER (lang(?oL) = 'en')
                                  FILTER (?oC IN (:Quantity, :QuantityKind, :MathematicalFormulation))}}
                      OPTIONAL {{ ?t :containsObjective ?ob.
                                  ?ob rdfs:label ?obL;
                                             a ?obC.
                                  FILTER (lang(?obL) = 'en')
                                  FILTER (?obC IN (:Quantity, :QuantityKind, :MathematicalFormulation))}}
                      OPTIONAL {{ ?t :containsParameter ?pa.
                                  ?pa rdfs:label ?paL;
                                             a ?paC.
                                  FILTER (lang(?paL) = 'en')
                                  FILTER (?paC IN (:Quantity, :QuantityKind, :MathematicalFormulation))}}
                     }}

               GROUP BY ?t ?subclass ?quote ?linear ?P ?PL ?F ?FL ?A ?AL ?BC ?BCL ?CC ?CCL ?CPC ?CPCL ?IC ?ICL ?FC ?FCL ?IN ?INL ?INC ?O ?OL ?OC ?OB ?OBL ?OBC ?PA ?PAL ?PAC '''
                    
query_ta2 =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?t
                       (GROUP_CONCAT(DISTINCT(?gbTask); separator=" <|> ") AS ?GBTASK) (GROUP_CONCAT(DISTINCT(?gbtLabel); SEPARATOR=" <|> ") AS ?GBTLabel)
                       (GROUP_CONCAT(DISTINCT(?gTask); separator=" <|> ") AS ?GTASK) (GROUP_CONCAT(DISTINCT(?gtLabel); SEPARATOR=" <|> ") AS ?GTLabel)
                       (GROUP_CONCAT(DISTINCT(?abTask); separator=" <|> ") AS ?ABTASK) (GROUP_CONCAT(DISTINCT(?abtLabel); SEPARATOR=" <|> ") AS ?ABTLabel)
                       (GROUP_CONCAT(DISTINCT(?aTask); separator=" <|> ") AS ?ATASK) (GROUP_CONCAT(DISTINCT(?atLabel); SEPARATOR=" <|> ") AS ?ATLabel)
                       (GROUP_CONCAT(DISTINCT(?dbTask); separator=" <|> ") AS ?DBTASK) (GROUP_CONCAT(DISTINCT(?dbtLabel); SEPARATOR=" <|> ") AS ?DBTLabel)
                       (GROUP_CONCAT(DISTINCT(?dTask); separator=" <|> ") AS ?DTASK) (GROUP_CONCAT(DISTINCT(?dtLabel); SEPARATOR=" <|> ") AS ?DTLabel)
                       (GROUP_CONCAT(DISTINCT(?lbTask); separator=" <|> ") AS ?LBTASK) (GROUP_CONCAT(DISTINCT(?lbtLabel); SEPARATOR=" <|> ") AS ?LBTLabel)
                       (GROUP_CONCAT(DISTINCT(?lTask); separator=" <|> ") AS ?LTASK) (GROUP_CONCAT(DISTINCT(?ltLabel); SEPARATOR=" <|> ") AS ?LTLabel)
                       (GROUP_CONCAT(DISTINCT(?sTask); separator=" <|> ") AS ?STASK) (GROUP_CONCAT(DISTINCT(?stLabel); SEPARATOR=" <|> ") AS ?STLabel)
                    

                WHERE {{
                        VALUES ?t {{{0}}}

                        OPTIONAL {{ ?t :generalizedByTask ?gbTask. 
                                    ?gbTask rdfs:label ?gbtLabel
                                    FILTER (lang(?gbtLabel) = 'en')}}
                        OPTIONAL {{ ?t :generalizesTask ?gTask. 
                                    ?gTask rdfs:label ?gtLabel
                                    FILTER (lang(?gtLabel) = 'en')}}
                        OPTIONAL {{ ?t :approximatedByTask ?abTask. 
                                    ?abTask rdfs:label ?abtLabel
                                    FILTER (lang(?abtLabel) = 'en')}}
                        OPTIONAL {{ ?t :approximatesTask ?aTask. 
                                    ?aTask rdfs:label ?atLabel
                                    FILTER (lang(?atLabel) = 'en')}}
                        OPTIONAL {{ ?t :discretizedByTask ?dbTask. 
                                    ?dbTask rdfs:label ?dbtLabel
                                    FILTER (lang(?dbtLabel) = 'en')}}
                        OPTIONAL {{ ?t :discretizesTask ?dTask. 
                                    ?dTask rdfs:label ?dtLabel
                                    FILTER (lang(?dtLabel) = 'en')}}
                        OPTIONAL {{ ?t :linearizedByTask ?lbTask.
                                    ?lbTask rdfs:label ?lbtLabel
                                    FILTER (lang(?lbtLabel) = 'en')}}
                        OPTIONAL {{ ?t :linearizesTask ?lTask.
                                    ?lTask rdfs:label ?ltLabel
                                    FILTER (lang(?ltLabel) = 'en')}}
                        OPTIONAL {{ ?t :similarToTask ?sTask. 
                                    ?sTask rdfs:label ?stLabel
                                    FILTER (lang(?stLabel) = 'en')}}
                        
                     }}

                GROUP BY ?t ?GBTASK ?GBTLabel ?GTASK ?GTLabel ?ABTASK ?ABTLabel ?ATASK ?ATLabel ?DBTASK ?DBTLabel ?DTASK ?DTLabel ?LBTASK ?LBTLabel ?LTASK ?LTLabel ?STASK ?STLabel'''
                
query_mm =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

               SELECT ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont 
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
                      (GROUP_CONCAT(COALESCE(?taQ, ""); SEPARATOR=" <|> ") AS ?TAQ)

               WHERE {{
                      BIND(:{0} AS ?mm)
                      
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

               GROUP BY ?quote ?linear ?convex ?dynamic ?deterministic ?dimensionless ?timecont ?spacecont ?P ?PL ?F ?FL ?A ?AL ?BC ?BCL ?CC ?CCL ?CPC ?CPCL ?IC ?ICL ?FC ?FCL ?CMM ?CMML ?TA ?TAL ?TAQ'''

query_mm2 =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT (GROUP_CONCAT(DISTINCT(?gbModel); separator=" <|> ") AS ?GBMODEL) (GROUP_CONCAT(DISTINCT(?gbmLabel); SEPARATOR=" <|> ") AS ?GBMLabel)
                       (GROUP_CONCAT(DISTINCT(?gModel); separator=" <|> ") AS ?GMODEL) (GROUP_CONCAT(DISTINCT(?gmLabel); SEPARATOR=" <|> ") AS ?GMLabel)
                       (GROUP_CONCAT(DISTINCT(?abModel); separator=" <|> ") AS ?ABMODEL) (GROUP_CONCAT(DISTINCT(?abmLabel); SEPARATOR=" <|> ") AS ?ABMLabel)
                       (GROUP_CONCAT(DISTINCT(?aModel); separator=" <|> ") AS ?AMODEL) (GROUP_CONCAT(DISTINCT(?amLabel); SEPARATOR=" <|> ") AS ?AMLabel)
                       (GROUP_CONCAT(DISTINCT(?dbModel); separator=" <|> ") AS ?DBMODEL) (GROUP_CONCAT(DISTINCT(?dbmLabel); SEPARATOR=" <|> ") AS ?DBMLabel)
                       (GROUP_CONCAT(DISTINCT(?dModel); separator=" <|> ") AS ?DMODEL) (GROUP_CONCAT(DISTINCT(?dmLabel); SEPARATOR=" <|> ") AS ?DMLabel)
                       (GROUP_CONCAT(DISTINCT(?lbModel); separator=" <|> ") AS ?LBMODEL) (GROUP_CONCAT(DISTINCT(?lbmLabel); SEPARATOR=" <|> ") AS ?LBMLabel)
                       (GROUP_CONCAT(DISTINCT(?lModel); separator=" <|> ") AS ?LMODEL) (GROUP_CONCAT(DISTINCT(?lmLabel); SEPARATOR=" <|> ") AS ?LMLabel)
                       (GROUP_CONCAT(DISTINCT(?sModel); separator=" <|> ") AS ?SMODEL) (GROUP_CONCAT(DISTINCT(?smLabel); SEPARATOR=" <|> ") AS ?SMLabel)

                WHERE {{
                        BIND(:{0} AS ?t)
                        OPTIONAL {{ ?t :generalizedByModel ?gbModel.
                                    ?gbModel rdfs:label ?gbmLabel
                                    FILTER (lang(?gbmLabel) = 'en')}}
                        OPTIONAL {{ ?t :generalizesModel ?gModel.
                                    ?gModel rdfs:label ?gmLabel
                                    FILTER (lang(?gmLabel) = 'en')}}
                        OPTIONAL {{ ?t :approximatedByModel ?abModel.
                                    ?abModel rdfs:label ?abmLabel
                                    FILTER (lang(?abmLabel) = 'en')}}
                        OPTIONAL {{ ?t :approximatesModel ?aModel.
                                    ?aModel rdfs:label ?amLabel
                                    FILTER (lang(?amLabel) = 'en')}}
                        OPTIONAL {{ ?t :discretizedByModel ?dbModel.
                                    ?dbModel rdfs:label ?dbmLabel
                                    FILTER (lang(?dbmLabel) = 'en')}}
                        OPTIONAL {{ ?t :discretizesModel ?dModel.
                                    ?dModel rdfs:label ?dmLabel
                                    FILTER (lang(?dmLabel) = 'en')}}
                        OPTIONAL {{ ?t :linearizedByModel ?lbModel.
                                    ?lbModel rdfs:label ?lbmLabel
                                    FILTER (lang(?lbmLabel) = 'en')}}
                        OPTIONAL {{ ?t :linearizesModel ?lModel.
                                    ?lModel rdfs:label ?lmLabel
                                    FILTER (lang(?lmLabel) = 'en')}}
                        OPTIONAL {{ ?t :similarToModel ?sModel.
                                    ?sModel rdfs:label ?smLabel
                                    FILTER (lang(?smLabel) = 'en')}}
                     }}

                GROUP BY ?GBMODEL ?GBMLabel ?GMODEL ?GMLabel ?ABMODEL ?ABMLabel ?AMODEL ?AMLabel ?DBMODEL ?DBMLabel ?DMODEL ?DMLabel ?SMODEL ?LBMODEL ?LBMLabel ?LMODEL ?LMLabel ?SMLabel'''

query_mf =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
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
                               ?formula_elements ?formula ?quantity ?quantityLabel ?QC'''

query_mf2 =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?mf
                       (GROUP_CONCAT(DISTINCT(?gbFormula); separator=" <|> ") AS ?GBFORMULA) (GROUP_CONCAT(DISTINCT(?gbfLabel); SEPARATOR=" <|> ") AS ?GBFLabel)
                       (GROUP_CONCAT(DISTINCT(?gFormula); separator=" <|> ") AS ?GFORMULA) (GROUP_CONCAT(DISTINCT(?gfLabel); SEPARATOR=" <|> ") AS ?GFLabel)
                       (GROUP_CONCAT(DISTINCT(?abFormula); separator=" <|> ") AS ?ABFORMULA) (GROUP_CONCAT(DISTINCT(?abfLabel); SEPARATOR=" <|> ") AS ?ABFLabel)
                       (GROUP_CONCAT(DISTINCT(?aFormula); separator=" <|> ") AS ?AFORMULA) (GROUP_CONCAT(DISTINCT(?afLabel); SEPARATOR=" <|> ") AS ?AFLabel)
                       (GROUP_CONCAT(DISTINCT(?dbFormula); separator=" <|> ") AS ?DBFORMULA) (GROUP_CONCAT(DISTINCT(?dbfLabel); SEPARATOR=" <|> ") AS ?DBFLabel)
                       (GROUP_CONCAT(DISTINCT(?dFormula); separator=" <|> ") AS ?DFORMULA) (GROUP_CONCAT(DISTINCT(?dfLabel); SEPARATOR=" <|> ") AS ?DFLabel)
                       (GROUP_CONCAT(DISTINCT(?lbFormula); separator=" <|> ") AS ?LBFORMULA) (GROUP_CONCAT(DISTINCT(?lbfLabel); SEPARATOR=" <|> ") AS ?LBFLabel)
                       (GROUP_CONCAT(DISTINCT(?lFormula); separator=" <|> ") AS ?LFORMULA) (GROUP_CONCAT(DISTINCT(?lfLabel); SEPARATOR=" <|> ") AS ?LFLabel)
                       (GROUP_CONCAT(DISTINCT(?nbFormula); separator=" <|> ") AS ?NBFORMULA) (GROUP_CONCAT(DISTINCT(?nbfLabel); SEPARATOR=" <|> ") AS ?NBFLabel)
                       (GROUP_CONCAT(DISTINCT(?nFormula); separator=" <|> ") AS ?NFORMULA) (GROUP_CONCAT(DISTINCT(?nfLabel); SEPARATOR=" <|> ") AS ?NFLabel)
                       (GROUP_CONCAT(DISTINCT(?sFormula); separator=" <|> ") AS ?SFORMULA) (GROUP_CONCAT(DISTINCT(?sfLabel); SEPARATOR=" <|> ") AS ?SFLabel)

                WHERE {{
                        
                        VALUES ?mf {{{0}}}

                        OPTIONAL {{ ?mf :generalizedByFormulation ?gbFormula.
                                    ?gbFormula rdfs:label ?gbfLabel
                                    FILTER (lang(?gbfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :generalizesFormulation ?gFormula.
                                    ?gFormula rdfs:label ?gfLabel
                                    FILTER (lang(?gfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :approximatedByFormulation ?abFormula.
                                    ?abFormula rdfs:label ?abfLabel
                                    FILTER (lang(?abfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :approximatesFormulation ?aFormula.
                                    ?aFormula rdfs:label ?afLabel
                                    FILTER (lang(?afLabel) = 'en')}}
                        OPTIONAL {{ ?mf :discretizedByFormulation ?dbFormula.
                                    ?dbFormula rdfs:label ?dbfLabel
                                    FILTER (lang(?dbfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :discretizesFormulation ?dFormula.
                                    ?dFormula rdfs:label ?dfLabel
                                    FILTER (lang(?dfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :linearizedByFormulation ?lbFormula.
                                    ?lbFormula rdfs:label ?lbfLabel
                                    FILTER (lang(?lbfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :linearizesFormulation ?lFormula.
                                    ?lFormula rdfs:label ?lfLabel
                                    FILTER (lang(?lfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :nondimensionalizedByFormulation ?nbFormula.
                                    ?nbFormula rdfs:label ?nbfLabel
                                    FILTER (lang(?nbfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :nondimensionalizesFormulation ?nFormula.
                                    ?nFormula rdfs:label ?nfLabel
                                    FILTER (lang(?nfLabel) = 'en')}}
                        OPTIONAL {{ ?mf :similarToFormulation ?sFormula.
                                    ?sFormula rdfs:label ?sfLabel
                                    FILTER (lang(?sfLabel) = 'en')}}
                     }}

                GROUP BY ?mf ?GBFORMULA ?GBFLabel ?GFORMULA ?GFLabel ?ABFORMULA ?ABFLabel ?AFORMULA ?AFLabel ?DBFORMULA ?DBFLabel ?DFORMULA ?DFLabel ?LBFORMULA ?LBFLabel ?LFORMULA ?LFLabel 
                             ?NBFORMULA ?NBFLabel ?NFORMULA ?NFLabel ?SFORMULA ?SFLabel'''

query_pu =  '''PREFIX : <https://mardi4nfdi.de/mathmoddb#>
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

                      

                      
