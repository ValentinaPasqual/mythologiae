import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace, ConjunctiveGraph #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import re
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

import csv
import json
from mythologiae_cleaner import *

tsv_dataset='discarica/prova_19-08.tsv'
classiche_data = process_data(csv_classiche)

g = ConjunctiveGraph()

factual_data = URIRef("http://example.org/factual_data")
factual_data2 = URIRef("http://example.org/factual_data2")



item = Namespace('http://example.org/item/')
work = Namespace('http://example.org/work/')
people = Namespace('http://example.org/person/')
citations = Namespace('http://example.org/cit')
categ = Namespace('http://example.org/categ/')
time = Namespace('http://example.org/time/')
place = Namespace('http://example.org/place/')
intact = Namespace('http://example.org/int-act/')


owl = Namespace('http://www.w3.org/2002/07/owl#')
dct = Namespace ('http://purl.org/dc/terms/')
frbr = Namespace('http://purl.org/spar/frbr/')
np = Namespace ('http://www.nanopub.org/nschema#')
my_graphs = Namespace('http://example.com/grafi')
fabio = Namespace('http://purl.org/spar/fabio')
hucit = Namespace('http://purl.org/net/hucit#')
ecrm = Namespace('http://erlangen-crm.org/current/')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
efrbroo = Namespace('http://erlangen-crm.org/efrbroo/')
wdt = Namespace('https://www.wikidata.org/wiki/')
prov = Namespace('http://www.w3.org/ns/prov#')
schema = Namespace('http://schema.org/')
hico = Namespace('http://purl.org/emmedi/hico/')

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
    x = 0
    for row in results:
        if row != []:


######################################################## ASSERTIONS ###############################################################################################

            stringa = str(x + 1)
            assertion = URIRef("http://example.org/assertion" + stringa)
            x = x + 1

######################################################## FACTUAL DATA ###############################################################################################

            for el in row['categoria']: #ogni el è un dizionario
                g.get_context(factual_data).add((URIRef(categ + el['uri']), RDF.type, ecrm.E1_CRM_Entity))
                g.get_context(factual_data).add((URIRef(categ + el['uri']), rdfs.label, Literal(el['label'], datatype=XSD.string)))
                g.get_context(assertion).add((item + URIRef(row['item_id'] + '-expression'), ecrm.P67_refers_to, (URIRef(categ + el['uri'])))) #NUOVO
                if len(el) > 2: #quindi non contiene la chiave 'superclasse', ma solo uri e label
                    g.get_context(factual_data).add((URIRef(categ + el['superclasse']), RDF.type, ecrm.E1_CRM_Entity))
                    g.get_context(factual_data).add((URIRef(categ + el['uri']), ecrm.P67_refers_to, URIRef(categ + el['superclasse'])))

            if row['riscritture_letterarie'] != {}:
                for el2 in row['riscritture_letterarie']: # el2 = dizionario
                    try:
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), RDF.type, efrbroo.F1_Work))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), rdfs.label,  Literal(el2['work_label'], datatype=XSD.string)))
                        #manca subwork_uri e subwork_label
                        for autore_uri in el2['autore_uri']:
                            g.get_context(factual_data).add((URIRef(people + autore_uri), RDF.type, efrbroo.F10_Person))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri']), rdfs.label, (URIRef(people + autore_uri))))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-wc'), RDF.type,  efrbroo.F27_Work_Conception))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-wc'), ecrm.P14_carried_out_by, (URIRef(people + autore_uri))))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-wc'), efrbroo.R16_initiated, (URIRef(work + el2['work_uri']))))
                            # manca il link tra work uri e work label
                            # manca la data !!!!
                    except:
                        print('Mi sa che manca qualcosa in riscritture letterarie')
            if row['fonti_medievali_e_moderne'] != {}:
                for el2 in row['fonti_medievali_e_moderne']:  # el2 = dizionario
                    try:
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), RDF.type, efrbroo.F1_Work))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), rdfs.label,
                                          Literal(el2['work_label'], datatype=XSD.string)))
                        # manca subwork_uri e subwork_label
                        # manca la data !!!!
                        for autore_uri in el2['autore_uri']:
                            g.get_context(factual_data).add((URIRef(people + autore_uri), RDF.type, efrbroo.F10_Person))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-wc'), RDF.type, efrbroo.F27_Work_Conception))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-wc'), ecrm.P14_carried_out_by,
                                              (URIRef(people + autore_uri))))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-wc'), efrbroo.R16_initiated,
                                              (URIRef(work + el2['work_uri']))))
                            # manca il link tra autore uri e autore label
                            # manca la data !!!!
                    except:
                        print('Mi sa che manca qualcosa in fonti medievali e moderne')
            if row['riscritture_cinematografiche'] != {}:
                for el3 in row['riscritture_cinematografiche']:
                    try:
                        g.get_context(factual_data).add((URIRef(work + el3['titolo_film_uri']), RDF.type, efrbroo.F1_Work))
                        g.get_context(factual_data).add((URIRef(work + el3['titolo_film_uri']), rdfs.label, Literal(el3['titolo_film'], datatype=XSD.string)))
                        # manca la data !!!!
                        # manca autore_uri + autore label
                        # manca work conception
                    except:
                        print('Alc nol va in CINEMA')

    #print(factual_data.serialize(format='trig').decode('UTF-8'))
    #factual_data.serialize(destination='discarica/rdf_liv0_works.trig', format='trig')

        ######################################################## FACTUAL DATA2 ###############################################################################################

        g.get_context(factual_data2).add((item + URIRef(row['item_id']), RDF.type, efrbroo.F4_Manifestation_Singleton))
        if row['immagine_url'] != "":
            g.get_context(factual_data2).add((item + URIRef(row['item_id']), schema.image,  Literal(row['immagine_url'], datatype=XSD.string)))
        if row.get('keywords') != []:
            for keyword in row['keywords']:
                g.get_context(factual_data2).add((item + URIRef(row['item_id']), dct.subject, Literal(keyword, datatype=XSD.string)))
        g.get_context(factual_data2).add((item + URIRef(row['item_id']), dct.title, Literal(row.get('item_titolo'), datatype=XSD.string)))
        g.get_context(factual_data2).add((item + URIRef(row['item_id'] + '-creation'), RDF.type, efrbroo.F28_Expression_Creation))
        g.get_context(factual_data2).add((item + URIRef(row['item_id'] + '-expression'), RDF.type, efrbroo.F2_Expression))
        # L'EXPRESSION del manif singleton VA NEL LIVELLO 0 O 1?????

        if row.get('item_autore') != []:
            for diz in row.get('item_autore'):
                g.get_context(factual_data2).add((people + URIRef(diz.get('autore_uri')), RDF.type, efrbroo.F10_Person))
                g.get_context(factual_data2).add((people + URIRef(diz.get('autore_uri')), rdfs.label, Literal(diz.get('autore_label'), datatype=XSD.string)))
                g.get_context(factual_data2).add((item + URIRef(row['item_id'] + '-creation'), ecrm.P14_carried_out_by, people + URIRef(diz.get('autore_uri'))))
                # MANCA WDT DELLA PERSONA

        if row.get('item_periodo') != None:
            g.get_context(factual_data2).add((time + URIRef(row.get('item_periodo')), RDF.type, ecrm.E4_Period))
            g.get_context(factual_data2).add((time + URIRef(row.get('item_periodo')), owl.sameAs, URIRef(wdt + row.get('item_periodo_wdt'))))
            g.get_context(factual_data2).add((time + URIRef(row.get('item_periodo')), rdfs.label, Literal(row.get('item_periodo_label'), datatype=XSD.string)))
            g.get_context(factual_data2).add((item + URIRef(row['item_id'] + '-creation'), ecrm.P10_falls_within, (time + URIRef(row.get('item_periodo')))))
        if row.get('item_secolo') != None:
            if row.get('item_secolo') != "":
                for diz in row.get('item_secolo'):
                    if diz != {}:
                        g.get_context(factual_data2).add((time + URIRef(diz.get('item_secolo_uri')), RDF.type, ecrm.E52_Time_Span))  # NON PRENDE TIME-SPAN LOL
                        g.get_context(factual_data2).add((time + URIRef(diz.get('item_secolo_uri')), owl.sameAs, URIRef(diz.get('item_secolo_wdt'))))
                        g.get_context(factual_data2).add((time + URIRef(diz.get('item_secolo_uri')), rdfs.label, Literal(diz.get('item_secolo_label'), datatype=XSD.string)))
                        g.get_context(factual_data2).add((item + URIRef(row['item_id'] + '-creation'), ecrm.P10_falls_within, (time + URIRef(diz.get('item_secolo_uri')))))

        if row.get('item_collocazione_uri') != None:
            g.get_context(factual_data2).add((place + URIRef(row.get('item_collocazione_uri')), RDF.type, ecrm.E53_Place))
            g.get_context(factual_data2).add((place + URIRef(row.get('item_collocazione_uri')), rdfs.label, Literal(row.get('item_collocazione_label'), datatype=XSD.string)))
            g.get_context(factual_data2).add((item + URIRef(row['item_id']), ecrm.P55_has_current_location, (place + URIRef(row.get('item_collocazione_uri')))))

        if row.get('item_citta_uri') != None:
            g.get_context(factual_data2).add((place + URIRef(row.get('item_citta_uri')), RDF.type, ecrm.E53_Place))
            g.get_context(factual_data2).add((place + URIRef(row.get('item_citta_uri')), rdfs.label, Literal(row.get('item_citta_label'), datatype=XSD.string)))
            g.get_context(factual_data2).add((place + URIRef(row.get('item_collocazione_uri')), ecrm.P89_falls_within,(place + URIRef(row.get('item_citta_uri')))))

        if row.get('item_tipologia') != None:
            g.get_context(factual_data2).add((time + URIRef(row.get('item_tipologia')), RDF.type, ecrm.P55_Type))
            # WDT NON FUNZIONA !!!!!!!!!!!!!!!!!!!!!!!!!
            #g.get_context(factual_data).add((time + URIRef(row.get('item_tipologia')), owl.sameAs, URIRef(wdt + row.get('item_tipologia_wdt'))))
            g.get_context(factual_data2).add((time + URIRef(row.get('item_tipologia')), rdfs.label,Literal(row.get('item_tipologia_label'), datatype=XSD.string)))
            g.get_context(factual_data2).add((item + URIRef(row['item_id']), ecrm.P2_has_type, (time + URIRef(row.get('item_tipologia')))))

    #print(g.serialize(format='trig').decode('UTF-8'))
    #g.serialize(destination='discarica/rdf_liv0_base_24-08.trig', format='trig')

######################################################## PROVENANCE ###############################################################################################

        provenance = URIRef("http://example.org/provenance" + stringa)
        g.get_context(provenance).add((URIRef(intact + stringa), RDF.type, prov.InterpretationAct))
        g.get_context(provenance).add((URIRef("http://example.org/assertion" + stringa), prov.wasGeneratedAtTime, Literal(row['post_data'], datatype=XSD.dateTime)))
        g.get_context(provenance).add((URIRef("http://example.org/assertion" + stringa), prov.wasGeneratedBy, (URIRef(intact + stringa))))
        g.get_context(provenance).add((URIRef(intact + stringa), prov.wasAttributedTo, (people + URIRef(row['post_autore_uri']))))
        g.get_context(provenance).add((URIRef(intact + stringa), hico.hasInterpretationCriterion, Literal('hermeneutic-analysis', datatype=XSD.string)))
        g.get_context(provenance).add((URIRef(intact + stringa), hico.hasInterpretationType, Literal('iconographic-approach', datatype=XSD.string)))


######################################################## PUB INFO ###############################################################################################

        pubInfo = URIRef("http://example.org/pubInfo" + stringa)
        g.get_context(pubInfo).add((URIRef('http://example.org/np-' + stringa), prov.wasAttributedTo, (URIRef(people + 'dharc'))))  #RIVEDI BENE COSA SCRIVERE
        g.get_context(pubInfo).add((URIRef('http://example.org/np-' + stringa), prov.wasGeneratedAtTime, Literal('2020-08-24-09:00', datatype=XSD.dateTime)))

######################################################## NP HEAD ###############################################################################################

        head = URIRef("http://example.org/head" + stringa)
        g.get_context(head).add((URIRef('http://example.org/np-' + stringa), RDF.type, np.Nanopublication))
        g.get_context(head).add((URIRef('http://example.org/np-' + stringa), np.hasAssertion, (URIRef("http://example.org/assertion" + stringa))))
        g.get_context(head).add((URIRef('http://example.org/np-' + stringa), np.hasProvenance, (URIRef("http://example.org/provenance" + stringa))))
        g.get_context(head).add((URIRef('http://example.org/np-' + stringa), np.hasPublicationInfo, (URIRef("http://example.org/pubInfo" + stringa))))
        # MANCANO PER TUTTE E 3 TIPO assertio-1 a np:Assertion --> DOVE LO METTO????

######################################################## ALTRA ROBA INUTILE IN FACTUAL DATA ###############################################################################################

        # CHE COS'è IL DHARC????
        g.get_context(provenance).add((people + URIRef(row['post_autore_uri']), RDF.type, efrbroo.F10_Person))


######################################################## FACTUAL DATA E FONTI CLASSICHE ###############################################################################################


        for diz_tsv in row['fonti_classiche']: # fonti classiche del tsv di partenza
            for diz_cl in classiche_data:  # CSV processato con risultati query
                for result in result_preparer_fonti_classiche:  # lista di diz con work, autor e cts
                    if diz_tsv['author'] in result['author']:
                        if diz_tsv['work'] in result['work']:
                            if diz_cl['work'] == result['cts']:
                                # MANCA CHE OGNUNO DI QUESTI WORKS SI RIFERISCE AD UNA O PIù CATEGRIE
                                g.get_context(factual_data).add((URIRef(diz_cl['work']), RDF.type, efrbroo.F1_Work))
                                g.get_context(factual_data).add((URIRef(diz_cl['work']), rdfs.label, Literal(diz_cl['work_label'], datatype=XSD.dateTime)))
                                g.get_context(factual_data).add((URIRef(diz_cl['work']), efrbroo.P102_has_title, (URIRef(diz_cl['title']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['title']), RDF.type, efrbroo.E35_Title))
                                g.get_context(factual_data).add((URIRef(diz_cl['title']), rdfs.label,  Literal(diz_cl['title_label'], datatype=XSD.dateTime)))
                                g.get_context(factual_data).add((URIRef(diz_cl['work']), ecrm.P1_is_identified_by , (URIRef(diz_cl['work_urn_cts']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['work_urn_cts']), ecrm.P2_has_type , (URIRef(diz_cl['work_urn_cts_type']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['work_urn_cts']), rdfs.label , (URIRef(diz_cl['work_urn_cts_uri_label']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['work_urn_cts']), RDF.type , ecrm.E42_Identifier))
                                g.get_context(factual_data).add((URIRef(diz_cl['work_conception']), efrbroo.R16_initiated ,(URIRef(diz_cl['work_urn_cts']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['work_conception']), RDF.type, efrbroo.F27_Work_Conception))
                                g.get_context(factual_data).add((URIRef(diz_cl['person']), RDF.type, efrbroo.F10_Person))
                                g.get_context(factual_data).add((URIRef(diz_cl['person']), efrbroo.P14i_performed, (URIRef(diz_cl['work_conception']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['person']), ecrm.P1_is_identified_by, (URIRef(diz_cl['person_urn_cts']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['person']), ecrm.P1_is_identified_by, (URIRef(diz_cl['name']))))
                                g.get_context(factual_data).add((URIRef(diz_cl['person_urn_cts']), RDF.type, ecrm.E42_Identifier))
                                g.get_context(factual_data).add((URIRef(diz_cl['name']), RDF.type, efrbroo.F12_Name))
                                g.get_context(factual_data).add((URIRef(diz_cl['name']), rdfs.label,  Literal(diz_cl['name_label'], datatype=XSD.dateTime)))
                                g.get_context(factual_data).add((URIRef(diz_cl['person_urn_cts']), rdfs.label,  Literal(diz_cl['person_urn_cts_label'], datatype=XSD.dateTime)))
                                g.get_context(factual_data).add((URIRef(diz_cl['person_urn_cts']), ecrm.P2_has_type , (URIRef(diz_cl['person_urn_cts_type']))))

    print(g.serialize(format='trig').decode('UTF-8'))
    g.serialize(destination='discarica/grafo_wip_27-08.trig', format='trig')
    return factual_data, factual_data2, assertion



#csv_writer(csv_creation(csv_intermedio(big_url)))

#assertion_creator(results)
#export_graph(g, results)
#factual_data_graph_simple_mode(results)

factual_data_graph(results)

