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


