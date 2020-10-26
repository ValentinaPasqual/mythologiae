# Here some queries on myth dataset, in particular on "WHAT" (works, citations and items) across the four layers

CQ1: Quali sono le categorie citate dalle Eneide di Virgilio?

```
SELECT ?categ (COUNT(ecrm:P67_refers_to) as ?n_assertion)
WHERE {
  graph ?assertion {<http://example.org/work/virgil-aeneis> ecrm:P67_refers_to ?categ}  
  graph myth:factual_data { ?categ a ecrm:E1_CRM_Entity. ?assertion a np:Assertion }
}  

GROUP BY ?categ ORDER BY DESC (?n_assertion) . 
```


| # |categ                                                                      |n_assertion|
|---|---------------------------------------------------------------------------|-----------|
|1  |http://example.org/categ/enea-nella-penisola-italica                       |12         |
|2  |http://example.org/categ/enea-abbandona-didone                             |6          |
|3  |http://example.org/categ/enea-negli-inferi                                 |5          |
|4  |http://example.org/categ/enea-verso-la-penisola-italica                    |5          |
|5  |http://example.org/categ/enea-contro-turno                                 |4          |
|6  |http://example.org/categ/enea-nei-campi-elisi                              |3          |
|7  |http://example.org/categ/enea-presenta-cupido-nei-panni-di-ascanio-a-didone|3          |
|8  |http://example.org/categ/enea-e-i-suoi-vengono-attaccati-dalle-arpie       |2          |
|9  |http://example.org/categ/enea-fugge-da-troia                               |2          |
|10 |http://example.org/categ/arianna-e-dioniso-sincontrano                     |1          |
|11 |http://example.org/categ/enea-e-didone-innamorati                          |1          |
|12 |http://example.org/categ/enea-e-i-sogni-rivelatori                         |1          |
|13 |http://example.org/categ/venere-e-anchise                                  |1          |


CQ2: Quali sono i passi delle Eneide che parlano di Enea nella penisola italica?  --> DA FINIRE

```
SELECT DISTINCT ?cit ?txEl  
WHERE {
  graph ?assertion {?cit ecrm:P67_refers_to <http://example.org/categ/enea-nella-penisola-italica>}  
  graph myth:factual_data {?categ a ecrm:E1_CRM_Entity. ?assertion a np:Assertion . 
   ?cit hucit:has_content ?txEl . 
    ?txStr hucit:is_canonical_structure_of <http://example.org/work/virgil-aeneis>; 
  			hucit:has_element ?txEl}
  }
  
  ```
  
  |cit                      |txEl                             |
|-------------------------|-----------------------------------|
|http://example.org/cit/11|http://example.org/str/V-604-699   |
|http://example.org/cit/20|http://example.org/str/VII-406-539 |
|http://example.org/cit/44|http://example.org/str/V-42-113    |
|http://example.org/cit/2 |http://example.org/str/V-362-484   |
|http://example.org/cit/15|http://example.org/str/XI-1-99     |
|http://example.org/cit/18|http://example.org/str/VII-195-204 |
|http://example.org/cit/22|http://example.org/str/VII-148-285 |
|http://example.org/cit/64|http://example.org/str/VII-25-36   |
|http://example.org/cit/19|http://example.org/str/VII-406-539 |
|http://example.org/cit/42|http://example.org/str/IX-25-175   |
|http://example.org/cit/40|http://example.org/str/VIII-560-584|

CQ3: Quali sono le 5 citazioni canoniche più citate nel dataset? E per ognuna di esse qual è la categoria che descrivono di più? 

  ```
SELECT DISTINCT ?cit ?label (COUNT(?cit) as ?n_cit) (MAX(?categ) as ?max_n_categ) 
WHERE { 
  graph ?assertion {?cit ecrm:P67_refers_to ?categ}
  graph myth:factual_data {?categ a ecrm:E1_CRM_Entity. ?assertion a np:Assertion . 
   ?cit hucit:has_content ?txEl; 
        rdfs:label ?label . 
    ?txStr hucit:is_canonical_structure_of ?work; 
  			hucit:has_element ?txEl}
  }

GROUP BY ?cit ?label ORDER BY DESC (?n_cit) 
LIMIT 5
 ```

|cit                      |label                              |n_cit|max_n_categ                                                   |
|-------------------------|-----------------------------------|-----|--------------------------------------------------------------|
|http://example.org/cit/20|Eneide,                            |328  |http://example.org/categ/vulcano                              |
|http://example.org/cit/27|Odissea, X                         |118  |http://example.org/categ/sfinge                               |
|http://example.org/cit/54|Publio Ovidio Nasone, Le Metamorfosi, VIII, vv. 176-177|43   |http://example.org/categ/arianna-tra-satiri-menadi-e-altre-figure-mitologiche|
|http://example.org/cit/61|Odissea, X, vv. 203-243            |28   |http://example.org/categ/ermes-aiuta-odisseo                  |
|http://example.org/cit/9 |Eneide                             |20   |http://example.org/categ/venere-e-anchise                     |

