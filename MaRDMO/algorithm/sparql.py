queryProviderAL = {
                 'AL': '''PREFIX : <https://mardi4nfdi.de/mathalgodb/0.1#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>                             
                          
                          SELECT DISTINCT ?id ?label ?quote
                          WHERE {
                                 ?idraw a :algorithm .
                                 BIND(STRAFTER(STR(?idraw), "#") AS ?id)
                                 OPTIONAL {?idraw rdfs:label ?labelraw .}
                                 BIND(COALESCE(?labelraw, "No Label Provided!") AS ?label)
                                 OPTIONAL {?idraw rdfs:comment ?quoteraw.}
                                 BIND(COALESCE(?quoteraw, "No Description Provided!") AS ?quote)
                                }
                          GROUP BY ?id ?label ?quote''',

                 'PU': '''PREFIX : <https://mardi4nfdi.de/mathalgodb/0.1#>
                          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>                             
                          
                          SELECT DISTINCT ?id ?label ?quote
                          WHERE {
                                 ?idraw a :publication .
                                 BIND(STRAFTER(STR(?idraw), "#") AS ?id)
                                 OPTIONAL {?idraw rdfs:label ?labelraw .}
                                 BIND(COALESCE(?labelraw, "No Label Provided!") AS ?label)
                                 OPTIONAL {?idraw rdfs:comment ?quoteraw.}
                                 BIND(COALESCE(?quoteraw, "No Description Provided!") AS ?quote)
                                }
                          GROUP BY ?id ?label ?quote'''

}