# Queries on places (where module)

NB: Spesso nelle query vengono presentati solo i primi 10 risualtati di ogni query per una questione di spazio

### CQ1: Quali sono gli item che si trovano a Londra? 

```
SELECT DISTINCT ?item
WHERE {graph myth:factual_data {?item ecrm:P55_has_current_location ?collocation. 
    ?collocation ecrm:P89_falls_within ?city . 
    ?city rdfs:label ?city_label }
FILTER regex(?city_label, "london", "i")
}
```
### CQ2: Quanti sono gli item che si trovano al Tate Modern?
```
SELECT DISTINCT ?item 
WHERE {graph myth:factual_data {?item ecrm:P55_has_current_location ?collocation. 
    ?collocation ecrm:P89_falls_within ?city.
    ?city rdfs:label ?city_label . 
    ?collocation rdfs:label ?coll_label }
  FILTER (regex(str(?coll_label),"tate", "i"))
  FILTER (regex(str(?city_label),"london|londra", "i"))
}
```

### CQ3: Qual è la keyword più usata in ogni stato? 
```
SELECT DISTINCT ?country_label (MAX(?keyword) AS ?max_k) 
WHERE {graph myth:factual_data {?item ecrm:P55_has_current_location ?collocation. 
    ?collocation ecrm:P89_falls_within ?country .
    ?country rdfs:label ?country_label ;
             ecrm:P2_has_type <http://example.org/place/nazione> .
  	?item dct:subject ?keyword}
}
GROUP BY ?country_label ORDER BY DESC (?max_k)
```

|country_label           |max_k          |
|------------------------|---------------|
|Italy                   |zucchi         |
|France                  |zoppo          |
|Germany                 |zeus-giove     |
|United Kingdom          |zeus-giove     |
|United States of America|zeus-era       |
|Spain                   |zeus-e-europa  |
|Belgium                 |zeus-e-danae   |
|Netherlands             |zeus-e-callisto|
|Australia               |zeus           |

[NB: Dalle keyword si presuppone che la rappresentazione più gettonata sia zeus]

### CQ4: Qual è la rappresentazione più gettonata per gli item di ogni stato? --> finire
```
SELECT DISTINCT ?country_label (MAX(?categ) AS ?max_cat) 
WHERE {
  graph myth:factual_data {?assertion a np:Assertion. ?item ecrm:P55_has_current_location ?collocation. 
    ?collocation ecrm:P89_falls_within ?country .
    ?country rdfs:label ?country_label ;
             ecrm:P2_has_type <http://example.org/place/nazione>}
  graph ?assertion {?itemExpr ecrm:P67_refers_to ?categ}
}
GROUP BY ?country_label ORDER BY DESC (?max_cat)
```
### CQ5: Qual è l'opera più citata in relazione agli item di ogni stato? 
```
SELECT DISTINCT ?country_label (MAX(?work) AS ?max_work) 
WHERE {
  graph myth:factual_data {?assertion a np:Assertion. ?item ecrm:P55_has_current_location ?collocation. 
    ?collocation ecrm:P89_falls_within ?country .
    ?country rdfs:label ?country_label ;
             ecrm:P2_has_type <http://example.org/place/nazione>}
  graph ?assertion {?itemExpr ecrm:P67_refers_to ?categ. ?work ecrm:P67_refers_to ?categ}
}
GROUP BY ?country_label ORDER BY DESC (?max_work)
LIMIT 1 
```

|country_label|max_work                                                        |
|-------------|----------------------------------------------------------------|
|Australia    |http://example.org/work/zingarelli-nicola-antonio-edipo-a-colono|
|Austria      |http://example.org/work/zingarelli-nicola-antonio-edipo-a-colono|
|Belgium      |http://example.org/work/zingarelli-nicola-antonio-edipo-a-colono|
|Brazil       |http://example.org/work/zingarelli-nicola-antonio-edipo-a-colono|
|Canada       |http://example.org/work/zingarelli-nicola-antonio-edipo-a-colono|

### CQ6: Qual è il paese con più item?
```
SELECT (COUNT(DISTINCT ?item) AS ?n_items) ?country
WHERE {
  graph myth:factual_data {?item ecrm:P55_has_current_location ?collocation. 
    ?collocation ecrm:P89_falls_within ?country.
	?country ecrm:P2_has_type "country"}
}
GROUP BY ?country ORDER BY DESC (?n_items)
```
