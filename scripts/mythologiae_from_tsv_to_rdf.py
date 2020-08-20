import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import re
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

import csv
import json
from mythologiae_cleaner import *

tsv_dataset='discarica/prova_19-08.tsv'


factual_data = Graph()
factual_data2 = Graph()
item = Namespace('http://example.org/item/')
work = Namespace('http://example.org/work/')
people = Namespace('http://example.org/person/')
citations = Namespace('http://example.org/cit')
categ = Namespace('http://example.org/categ/')
time = Namespace('http://example.org/time/')

schema = Namespace('http://schema.org/')
owl = Namespace('http://www.w3.org/2002/07/owl#')
dct = Namespace ('http://purl.org/dc/terms/')
frbr = Namespace('http://purl.org/spar/frbr/')
np = Namespace ('http://www.nanopub.org/nschema#')
my_graphs = Namespace('http://example.com/grafi')
fabio = Namespace('http://purl.org/spar/fabio')
hucit = Namespace('http://purl.org/net/hucit/')
ecrm = Namespace('http://erlangen-crm.org/current/')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
efrbroo = Namespace('http://erlangen-crm.org/efrbroo/')
wdt = Namespace('https://www.wikidata.org/wiki/')

"""def factual_data_graph(df):
    for index, row in df.iterrows():
        for key,value in fonti_classiche_cleaner(row).items():  #RDF FONTI CLASSICHE (SOLO ELEMENTI UNICI)
            factual_data.add((URIRef(key), RDF.type, frbr.Work))
            factual_data.add((URIRef(key), frbr.creator, URIRef(value)))
            factual_data.add((URIRef(value), RDF.type, frbr.Person))
        for key,value in riscritture_letterarie_cleaner(row).items():  #RDF FONTI CLASSICHE (SOLO ELEMENTI UNICI)
            factual_data.add((URIRef(key), RDF.type, frbr.Work))
            factual_data.add((URIRef(key), frbr.creator, URIRef(value)))
            factual_data.add((URIRef(value), RDF.type, frbr.Person)) 

    print(factual_data.serialize(format='trig').decode('UTF-8'))"""

def process_data_tsv(source_csv_file_path):
    import csv
    data = list()
    with open(source_csv_file_path, 'r', encoding='utf-8') as test:
        processed_data = csv.DictReader(test, delimiter='\t')
        for x in processed_data:
            x = dict(x)
            data.append(x)
    return data

big_url = 'wpcsv-export-20200724150145.csv'

results = csv_creation(csv_intermedio(big_url))

def factual_data_graph(results):
    for row in results:
        if row != []:
            for el in row['categoria']: #ogni el è un dizionario
                factual_data.add((URIRef(categ + el['uri']), RDF.type, ecrm.E1_CRM_Entity))
                factual_data.add((URIRef(categ + el['uri']), rdfs.label, Literal(el['label'], datatype=XSD.string)))
                if len(el) > 2: #quindi non contiene la chiave 'superclasse', ma solo uri e label
                    factual_data.add((URIRef(categ + el['superclasse']), RDF.type, ecrm.E1_CRM_Entity))
                    factual_data.add((URIRef(categ + el['uri']), ecrm.P67_refers_to, URIRef(categ + el['superclasse'])))
            if row['riscritture_letterarie'] != {}:
                for el2 in row['riscritture_letterarie']: # el2 = dizionario
                    try:
                        factual_data.add((URIRef(work + el2['work_uri']), RDF.type, efrbroo.F1_Work))
                        factual_data.add((URIRef(work + el2['work_uri']), rdfs.label,  Literal(el2['work_label'], datatype=XSD.string)))
                        #manca subwork_uri e subwork_label
                        for autore_uri in el2['autore_uri']:
                            factual_data.add((URIRef(work + autore_uri), RDF.type, efrbroo.F10_Person))
                            factual_data.add((URIRef(work + el2['work_uri']), rdfs.label, (URIRef(work + autore_uri))))
                            factual_data.add((URIRef(work + el2['work_uri'] + '-wc'), RDF.type,  efrbroo.F27_Work_Conception))
                            factual_data.add((URIRef(work + el2['work_uri'] + '-wc'), ecrm.P14_carried_out_by, (URIRef(work + autore_uri))))
                            factual_data.add((URIRef(work + el2['work_uri'] + '-wc'), efrbroo.R16_initiated, (URIRef(work + el2['work_uri']))))
                            # manca il link tra work uri e work label
                            # manca la data !!!!
                    except:
                        print('Mi sa che manca qualcosa in riscritture letterarie')
            if row['fonti_medievali_e_moderne'] != {}:
                for el2 in row['fonti_medievali_e_moderne']:  # el2 = dizionario
                    try:
                        factual_data.add((URIRef(work + el2['work_uri']), RDF.type, efrbroo.F1_Work))
                        factual_data.add((URIRef(work + el2['work_uri']), rdfs.label,
                                          Literal(el2['work_label'], datatype=XSD.string)))
                        # manca subwork_uri e subwork_label
                        # manca la data !!!!
                        for autore_uri in el2['autore_uri']:
                            factual_data.add((URIRef(work + autore_uri), RDF.type, efrbroo.F10_Person))
                            factual_data.add((URIRef(work + el2['work_uri'] + '-wc'), RDF.type, efrbroo.F27_Work_Conception))
                            factual_data.add((URIRef(work + el2['work_uri'] + '-wc'), ecrm.P14_carried_out_by,
                                              (URIRef(work + autore_uri))))
                            factual_data.add((URIRef(work + el2['work_uri'] + '-wc'), efrbroo.R16_initiated,
                                              (URIRef(work + el2['work_uri']))))
                            # manca il link tra autore uri e autore label
                            # manca la data !!!!
                    except:
                        print('Mi sa che manca qualcosa in fonti medievali e moderne')
            if row['riscritture_cinematografiche'] != {}:
                for el3 in row['riscritture_cinematografiche']:
                    try:
                        factual_data.add((URIRef(work + el3['titolo_film_uri']), RDF.type, efrbroo.F1_Work))
                        factual_data.add((URIRef(work + el3['titolo_film_uri']), rdfs.label, Literal(el3['titolo_film'], datatype=XSD.string)))
                        # manca la data !!!!
                        # manca autore_uri + autore label
                        # manca work conception
                    except:
                        print('Alc nol va in CINEMA')

    print(factual_data.serialize(format='trig').decode('UTF-8'))
    factual_data.serialize(destination='discarica/rdf_liv0_works.trig', format='trig')
    return factual_data

def factual_data_graph_simple_mode(results):
    for row in results:
        factual_data2.add((item + URIRef(row['item_id']), RDF.type, efrbroo.F4_Manifestation_Singleton))
        # L'EXPRESSION del manif singleton VA NEL LIVELLO 0 O 1?????
        if row.get('item_periodo') != None:
            factual_data2.add((time + URIRef(row.get('item_periodo')), RDF.type, ecrm.E4_Period))
            factual_data2.add((time + URIRef(row.get('item_periodo')), owl.sameAs, URIRef(wdt + row.get('item_periodo_wdt'))))
            factual_data2.add((time + URIRef(row.get('item_periodo')), rdfs.label, Literal(row.get('item_periodo_label'), datatype=XSD.string)))
        if row.get('item_tipologia') != None:
            factual_data2.add((time + URIRef(row.get('item_tipologia')), RDF.type, ecrm.P55_Type))
            # WDT NON FUNZIONA !!!!!!!!!!!!!!!!!!!!!!!!!
            #factual_data.add((time + URIRef(row.get('item_tipologia')), owl.sameAs, URIRef(wdt + row.get('item_tipologia_wdt'))))
            factual_data2.add((time + URIRef(row.get('item_tipologia')), rdfs.label,Literal(row.get('item_tipologia_label'), datatype=XSD.string)))


    print(factual_data2.serialize(format='trig').decode('UTF-8'))
    factual_data2.serialize(destination='discarica/rdf_liv0_base.trig', format='trig')
    return factual_data2


factual_data_graph_simple_mode(results)
factual_data_graph(results)




