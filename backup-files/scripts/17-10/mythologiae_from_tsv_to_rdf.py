import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace, ConjunctiveGraph #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import re
import csv
import json
from mythologiae_cleaner import *
from entity_linking import *
from fonti_classiche import *

tsv_dataset='discarica/prova_19-08.tsv'
classiche_data = process_data(csv_classiche)

g = ConjunctiveGraph()

factual_data = URIRef("http://example.org/factual_data")

myth = Namespace('http://example.org/')
item = Namespace('http://example.org/item/')
work = Namespace('http://example.org/work/')
people = Namespace('http://example.org/person/')
citation = Namespace('http://example.org/cit/')
categ = Namespace('http://example.org/categ/')
can_str = Namespace('http://example.org/str/')
time = Namespace('http://example.org/time/')
place = Namespace('http://example.org/place/')
intact = Namespace('http://example.org/int-act/')
viaf = Namespace('http://viaf.org/viaf/')


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
wdp = Namespace('https://www.wikidata.org/wiki/Property:')

def process_data_tsv(source_csv_file_path):
    import csv
    data = list()
    with open(source_csv_file_path, 'r', encoding='utf-8') as test:
        processed_data = csv.DictReader(test, delimiter='\t')
        for x in processed_data:
            x = dict(x)
            data.append(x)
    return data

big_url = 'wpcsv-export-20200724150145-v2.xlsb.csv'

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
                g.get_context(assertion).add((item + URIRef(row['item_id'] + '-expression'), ecrm.P67_refers_to, (URIRef(categ + el['uri']))))
                if len(el) > 2: #quindi non contiene la chiave 'superclasse', ma solo uri e label
                    g.get_context(factual_data).add((URIRef(categ + el['superclasse']), RDF.type, ecrm.E1_CRM_Entity))
                    g.get_context(factual_data).add((URIRef(categ + el['uri']), ecrm.P67_refers_to, URIRef(categ + el['superclasse'])))

            if row['riscritture_letterarie'] != {}:
                for el2 in row['riscritture_letterarie']: # el2 = dizionario
                    if el2.get('work_uri') != None:
                        ######### da mettere a posto #####
                        g.get_context(factual_data).add((URIRef(work + el2.get('work_uri')), RDF.type, efrbroo.F1_Work))
                        if 'categoria' in el2.keys(): # caso di // DA METTERE A POSTO
                            g.get_context(assertion).add((work + URIRef(el2.get('work_uri')), ecrm.P67_refers_to, (categ + URIRef(el2['categoria']))))
                            g.get_context(assertion).add((item + URIRef(row['item_id'] + '-expression'), ecrm.P67_refers_to, (categ + URIRef(el2['categoria']))))
                        else:
                            g.get_context(assertion).add((work + URIRef(el2.get('work_uri')), ecrm.P67_refers_to, (categ + URIRef(el['uri']))))
                        ##################################
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), rdfs.label,  Literal(el2['work_label'], datatype=XSD.string)))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), ecrm.P2_has_type, (work + URIRef('riscritturaLetteraria'))))
                        #manca subwork_uri e subwork_label  --> che tanto non metto
                        if 'anno_uri' in el2.keys():
                            g.get_context(factual_data).add((URIRef(work + el2.get('work_uri') + '-conception'), ecrm.P4_has_time_span, (URIRef(time + el2['anno_uri']))))
                            g.get_context(factual_data).add((URIRef(time + el2.get('anno_uri')), rdfs.label, Literal(el2.get('anno_label'), datatype=XSD.string)))
                            g.get_context(factual_data).add((URIRef(time + el2.get('anno_uri')), ecrm.P82a_begin_of_the_begin, Literal(el2.get('anno_start'), datatype=XSD.date)))
                            g.get_context(factual_data).add((URIRef(time + el2.get('anno_uri')), ecrm.P82b_end_of_the_end, Literal(el2.get('anno_end'), datatype=XSD.date)))
                        for autore_uri_rl in list(set(el2['autore_uri'])):
                            g.get_context(factual_data).add((URIRef(people + autore_uri_rl), RDF.type, efrbroo.F10_Person))
                        for autore_label_rl in list(set(el2['autore_label'])):
                            if autore_label_rl != '' or autore_label_rl != None:
                                g.get_context(factual_data).add((URIRef(people + autore_uri_rl), rdfs.label, Literal(autore_label_rl, datatype=XSD.string)))
                                output_rl = reconciled_tsv_matcher('entity_linking/reconciled/l_au_rl-csv.tsv', 'l_au_rl', autore_label_rl)
                                if output_rl != [] and output_rl != None:
                                    g.get_context(factual_data).add((URIRef(people + autore_uri_rl), rdfs.label, Literal(output_rl[0], datatype=XSD.string)))
                                    g.get_context(factual_data).add((URIRef(people + autore_uri_rl), owl.sameAs, (URIRef(viaf + output_rl[1]))))
                                # produce triple di PersonaX con label_viaf e PersonaX owl:sameAs viaf_id
                            g.get_context(factual_data).add((URIRef(work + el2.get('work_uri') + '-conception'), RDF.type,  efrbroo.F27_Work_Conception))
                            g.get_context(factual_data).add((URIRef(work + el2.get('work_uri') + '-conception'), ecrm.P14_carried_out_by, (URIRef(people + autore_uri_rl))))

            if row['fonti_medievali_e_moderne'] != []:
                for el2 in row['fonti_medievali_e_moderne']:  # el2 = dizionario
                    if el2 != {}:
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), RDF.type, efrbroo.F1_Work))
                        if 'categoria' in el2.keys(): # caso di //
                            g.get_context(assertion).add((URIRef(work + el2['work_uri']), ecrm.P67_refers_to, (URIRef(categ + el2['categoria']))))
                            g.get_context(assertion).add((item + URIRef(row['item_id'] + '-expression'), ecrm.P67_refers_to, (URIRef(categ + el2['categoria']))))
                        else:
                            g.get_context(assertion).add((URIRef(work + el2['work_uri']), ecrm.P67_refers_to, (URIRef(categ + el['uri']))))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']), rdfs.label, Literal(el2['work_label'], datatype=XSD.string)))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri']),  ecrm.P2_has_type, (work + URIRef('fonteMedievaleOModerna'))))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-conception'), efrbroo.R16_initiated,(URIRef(work + el2['work_uri']))))
                        g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-conception'), RDF.type, efrbroo.F27_Work_Conception))
                        if 'anno_uri' in el2.keys():
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-conception'), ecrm.P4_has_time_span, (URIRef(time + el2['anno_uri']))))
                            g.get_context(factual_data).add((URIRef(time + el2.get('anno_uri')), rdfs.label, Literal(el2.get('anno_label'), datatype=XSD.string)))
                            g.get_context(factual_data).add((URIRef(time + el2.get('anno_uri')), ecrm.P82a_begin_of_the_begin, Literal(el2.get('anno_start'), datatype=XSD.date)))
                            g.get_context(factual_data).add((URIRef(time + el2.get('anno_uri')), ecrm.P82b_end_of_the_end, Literal(el2.get('anno_end'), datatype=XSD.date)))
                        # manca subwork_uri e subwork_label --> che tanto non metto
                        for autore_uri_fmm in list(set(el2['autore_uri'])):
                            g.get_context(factual_data).add((URIRef(people + autore_uri_fmm), RDF.type, efrbroo.F10_Person))
                            g.get_context(factual_data).add((URIRef(work + el2['work_uri'] + '-conception'), ecrm.P14_carried_out_by, (URIRef(people + autore_uri_fmm))))
                        for autore_label_fmm in list(set(el2['autore_label'])):
                            if autore_label_fmm != '' or autore_label_fmm != None:
                                g.get_context(factual_data).add((URIRef(people + autore_uri_fmm), rdfs.label, Literal(autore_label_fmm, datatype=XSD.string)))
                                output_mm = reconciled_tsv_matcher('entity_linking/reconciled/l_au_fmm-csv.tsv', 'l_au_fmm', autore_label_fmm)
                                if output_mm != [] and output_mm != None:
                                    g.get_context(factual_data).add((URIRef(people + autore_uri_fmm), rdfs.label, Literal(output_mm[0], datatype=XSD.string)))
                                    g.get_context(factual_data).add((URIRef(people + autore_uri_fmm), owl.sameAs, (URIRef(viaf + output_mm[1]))))

            if row['riscritture_cinematografiche'] != {}:
                for el3 in row['riscritture_cinematografiche']:
                    if 'categoria' in el3.keys(): # caso di //
                        if el3.get('work_uri') != None:
                            g.get_context(assertion).add((URIRef(work + el3.get('work_uri')), ecrm.P67_refers_to, (URIRef(categ + el3['categoria']))))
                            g.get_context(assertion).add((item + URIRef(row['item_id'] + '-expression'), ecrm.P67_refers_to, (URIRef(categ + el3['categoria']))))
                    else:
                        if el3.get('work_uri') != None:
                            g.get_context(assertion).add((URIRef(work + el3.get('work_uri')), ecrm.P67_refers_to, (URIRef(categ + el['uri']))))
                    if el3.get('titolo_film_uri'):
                        g.get_context(factual_data).add((URIRef(work + el3.get('titolo_film_uri')), RDF.type, efrbroo.F1_Work))
                        g.get_context(factual_data).add((URIRef(work + el3.get('titolo_film_uri')), rdfs.label, Literal(el3['titolo_film'], datatype=XSD.string)))
                        g.get_context(factual_data).add((URIRef(work + el3.get('titolo_film_uri')), ecrm.P2_has_type, (work + URIRef('riscritturaCinematografica'))))
                        g.get_context(factual_data).add((URIRef(work + el3.get('titolo_film_uri') + '-conception'), efrbroo.R16_initiated,(URIRef(work + el3['titolo_film_uri']))))
                        g.get_context(factual_data).add((URIRef(work + el3.get('titolo_film_uri') + '-conception'), RDF.type, efrbroo.F27_Work_Conception))
                    if 'anno_uri' in el3.keys():
                        if el3.get('titolo_film_uri') != None:
                            g.get_context(factual_data).add((URIRef(work + el3.get('titolo_film_uri') + '-conception'), ecrm.P4_has_time_span, (URIRef(time + el3['anno_uri']))))
                            g.get_context(factual_data).add((URIRef(time + el3.get('anno_uri')), rdfs.label, Literal(el3.get('anno_label'), datatype=XSD.string)))
                            g.get_context(factual_data).add((URIRef(time + el3.get('anno_uri')), ecrm.P82a_begin_of_the_begin, Literal(el3.get('anno_start'), datatype=XSD.date)))
                            g.get_context(factual_data).add((URIRef(time + el3.get('anno_uri')), ecrm.P82b_end_of_the_end, Literal(el3.get('anno_end'), datatype=XSD.date)))
                    # manca subwork_uri e subwork_label --> che tanto non metto
                    if el3.get('autore_uri') != None:
                        for autore_uri_rc in el3.get('autore_uri'):
                            g.get_context(factual_data).add((URIRef(work + el3['titolo_film_uri'] + '-conception'), ecrm.P14_carried_out_by, (URIRef(people + autore_uri_rc))))
                            g.get_context(factual_data).add((URIRef(people + autore_uri_rc), RDF.type, efrbroo.F10_Person))
                            g.get_context(factual_data).add((URIRef(people + autore_uri_rc), rdfs.label, Literal(el3.get('autore_label'), datatype=XSD.string)))
                    if el3.get('autore_label') != None:
                        if type(el3.get('autore_label')) == str:
                            if el3.get('autore_label') != '' or el3.get('autore_label') != None:
                                output_rc = reconciled_tsv_matcher('entity_linking/reconciled/l_au_rc-csv.tsv', 'l_au_rc',el3.get('autore_label'))
                                if output_rc != [] and output_rc != None:
                                    g.get_context(factual_data).add((URIRef(people + autore_uri_rc), rdfs.label, Literal(output_rc[0], datatype=XSD.string)))
                                    g.get_context(factual_data).add((URIRef(people + autore_uri_rc), owl.sameAs, (URIRef(viaf + output_rc[1]))))
                            # produce triple di PersonaX con label_viaf e PersonaX owl:sameAs viaf_id"""
                        if type(el3.get('autore_label')) == list:
                            for autore_label_rc in el3.get('autore_label'):
                                if type(el3.get('autore_label')) == str:
                                    if autore_label_rc != '' or autore_label_rc != None:
                                        g.get_context(factual_data).add((URIRef(people + autore_uri_rc), rdfs.label, Literal(autore_label_rc, datatype=XSD.string)))
                                        output_rc = reconciled_tsv_matcher('entity_linking/reconciled/l_au_rc-csv.tsv','l_au_rc', autore_label_rc)
                                        if output_rc != [] and output_rc != None:
                                            g.get_context(factual_data).add((URIRef(people + autore_uri_rc), rdfs.label,Literal(output_rc[0],datatype=XSD.string)))
                                            g.get_context(factual_data).add((URIRef(people + autore_uri_rc), owl.sameAs,(URIRef(viaf + output_rc[1]))))
                                    # produce triple di PersonaX con label_viaf e PersonaX owl:sameAs viaf_id"""


######################################################## FACTUAL DATA2 ###############################################################################################

            g.get_context(factual_data).add((item + URIRef(row['item_id']), RDF.type, efrbroo.F4_Manifestation_Singleton))
            if row['immagine_url'] != "":
                g.get_context(factual_data).add((item + URIRef(row['item_id']), schema.image,  Literal(row['immagine_url'], datatype=XSD.string)))
            if row.get('keywords') != []:
                for keyword in row['keywords']:
                    if keyword != "":
                        g.get_context(factual_data).add((item + URIRef(row['item_id']), dct.subject, Literal(keyword, datatype=XSD.string)))
            g.get_context(factual_data).add((item + URIRef(row['item_id']), dct.title, Literal(row.get('item_titolo'), datatype=XSD.string)))
            g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-creation'), RDF.type, efrbroo.F28_Expression_Creation))
            g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-creation'), efrbroo.R18_created, (item + URIRef(row['item_id']))))
            g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-creation'), efrbroo.R18_created, (item + URIRef(row['item_id'] + '-expression'))))
            g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-expression'), RDF.type, efrbroo.F2_Expression))
            # L'EXPRESSION del manif singleton VA NEL LIVELLO 0 O 1?????

            if row.get('item_autore') != [] and row.get('item_autore') != None:
                for diz_au in row.get('item_autore'):
                    g.get_context(factual_data).add((people + URIRef(diz_au.get('autore_uri')), RDF.type, efrbroo.F10_Person))
                    g.get_context(factual_data).add((people + URIRef(diz_au.get('autore_uri')), rdfs.label, Literal(diz_au.get('autore_label'), datatype=XSD.string)))
                    if diz_au.get('autore_label')!= '' or diz_au.get('autore_label') != None:
                        output_item = reconciled_tsv_matcher('entity_linking/reconciled/l_au_item-csv.tsv', 'l_au_item', diz_au.get('autore_label'))
                        if output_item != [] and output_item != None:
                            g.get_context(factual_data).add((people + URIRef(diz_au.get('autore_uri')), rdfs.label, Literal(output_item[0], datatype=XSD.string)))
                            g.get_context(factual_data).add((people + URIRef(diz_au.get('autore_uri')), owl.sameAs, (URIRef(viaf + output_item[1]))))
                    g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-creation'), ecrm.P14_carried_out_by, people + URIRef(diz_au.get('autore_uri'))))

            if row.get('item_data') != None:
                if row.get('item_data') != {}:
                    dy = row.get('item_data')
                    g.get_context(factual_data).add((URIRef(item + row['item_id'] + '-creation'), ecrm.P10_falls_within,(URIRef(time + dy.get('anno_uri')))))
                    g.get_context(factual_data).add((URIRef(time + row.get('item_data').get('anno_uri')), RDF.type, ecrm.E52_Time_Span))
                    # L'ONTO di P82a e P81b NON E' MAI ECRM!!!!!! MA 6.2.1 DI CIDOC
                    g.get_context(factual_data).add((URIRef(time + dy.get('anno_uri')), rdfs.label, Literal(dy.get('anno_label'), datatype=XSD.string)))
                    g.get_context(factual_data).add((URIRef(time + dy.get('anno_uri')), ecrm.P82a_begin_of_the_begin, Literal(dy.get('anno_start'), datatype=XSD.date)))
                    g.get_context(factual_data).add((URIRef(time + dy.get('anno_uri')), ecrm.P82b_end_of_the_end, Literal(dy.get('anno_end'), datatype=XSD.date)))
                    g.get_context(factual_data).add((URIRef(time + dy.get('anno_uri')),  ecrm.P2_has_type, (time + URIRef('anno'))))

            if row.get('item_periodo') != None:
                g.get_context(factual_data).add((time + URIRef(row.get('item_periodo')), RDF.type, ecrm.E4_Period))
                g.get_context(factual_data).add((time + URIRef(row.get('item_periodo')), owl.sameAs, URIRef(wdt + row.get('item_periodo_wdt'))))
                g.get_context(factual_data).add((time + URIRef(row.get('item_periodo')), rdfs.label, Literal(row.get('item_periodo_label'), datatype=XSD.string)))
                g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-creation'), ecrm.P10_falls_within, (time + URIRef(row.get('item_periodo')))))
                g.get_context(factual_data).add((time + URIRef(row.get('item_periodo')),  ecrm.P2_has_type, (time + URIRef('periodo'))))

            if row.get('item_secolo') != None:
                if row.get('item_secolo') != {}:
                    ds = row.get('item_secolo')
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')), RDF.type, ecrm.E52_Time_Span))  # NON PRENDE TIME-SPAN LOL
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')), owl.sameAs, URIRef(ds.get('item_secolo_wdt'))))
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')), rdfs.label, Literal(ds.get('item_secolo_label'), datatype=XSD.string)))
                    g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-creation'), ecrm.P10_falls_within, (time + URIRef(ds.get('item_secolo_uri')))))
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')),  ecrm.P2_has_type, (time + URIRef('secolo'))))
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')), owl.sameAs, URIRef(ds.get('item_secolo_wdt'))))
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')), ecrm.P82a_begin_of_the_begin, Literal(ds.get('secolo_start'),datatype=XSD.date)))
                    g.get_context(factual_data).add((time + URIRef(ds.get('item_secolo_uri')), ecrm.P82b_end_of_the_end,  Literal(ds.get('secolo_end'),datatype=XSD.date)))

            l_luoghi = process_data_tsv('entity_linking/reconciled/l_luoghi-csv.tsv')

            if row.get('item_collocazione_uri'):
                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), RDF.type, ecrm.E53_Place))
                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), rdfs.label, Literal(row.get('item_collocazione_label'), datatype=XSD.string)))
                g.get_context(factual_data).add((item + URIRef(row['item_id']), ecrm.P55_has_current_location, (place + URIRef(row.get('item_collocazione_uri')))))
                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), ecrm.P89_falls_within,(place + URIRef(row.get('item_citta_uri')))))
                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), ecrm.P2_has_type, (place + URIRef('collocazione'))))

            if row.get('item_citta_uri'):
                g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), RDF.type, ecrm.E53_Place))
                g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), rdfs.label,Literal(row.get('item_citta_label'), datatype=XSD.string)))
                g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')),  ecrm.P2_has_type, (place + URIRef('città'))))

            if row.get('item_collocazione_uri'):
                if row.get('item_collocazione_label') != None or row.get('item_collocazione_label') != '':
                    for dl in l_luoghi:
                        if row.get('item_collocazione_label') == dl.get('item_collocazione_label'):
                            if dl.get('wdt_label_collcaz'):
                                if dl.get('wdt_label_collcaz'):
                                    g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), rdfs.label, Literal(dl.get('wdt_label_collcaz'), datatype=XSD.string)))
                            if dl.get('wdt_P625_collocaz'):
                                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), wdp.P625, Literal(dl.get('wdt_P625_collocaz'), datatype=XSD.string)))
                            if dl.get('LOG_id_collocaz'):
                                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), owl.sameAs,(URIRef('https://id.loc.gov/authorities/names/' + dl.get('LOG_id_collocaz')))))
                            #if dl.get('ISNI_id_collocaz'):
                                #g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), owl.sameAs,(URIRef('http://www.isni.org/isni/' + dl.get('ISNI_id_collocaz')))))
                            if dl.get('wdt_id_collocaz'):
                                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')), owl.sameAs, URIRef('https://www.wikidata.org/wiki/' + dl.get('wdt_id_collocaz'))))
                            if dl.get('WorldCat_ID_collocaz'):
                                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')),owl.sameAs, URIRef('http://worldcat.org/identities/' + dl.get('WorldCat_ID_collocaz'))))
                            if dl.get('GeoNames_ID_collocaz'):
                                g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')),owl.sameAs, URIRef('http://sws.geonames.org/' + dl.get('GeoNames_ID_collocaz'))))
                        if row.get('item_citta_uri') != None:
                            if row.get('item_citta_label') == dl.get('item_citta_label'):
                                if dl.get('wdt_citta_label'):
                                    g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), rdfs.label,Literal(dl.get('wdt_citta_label'),datatype=XSD.string)))
                                if dl.get('wdt_P625_citta'):
                                    g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), wdp.P625,Literal(dl.get('wdt_P625_citta'),datatype=XSD.string)))
                                if dl.get('wdt_id_citta'):
                                    g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), owl.sameAs,URIRef('https://www.wikidata.org/wiki/' + dl.get('wdt_id_citta'))))
                                if dl.get('GeoNames_id_citta'):
                                        g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), owl.sameAs,URIRef('http://sws.geonames.org/' + dl.get('GeoNames_id_citta'))))
                                if dl.get('country'):
                                    g.get_context(factual_data).add((place + URIRef(uri_cleaner(dl.get('country'))),rdfs.label,Literal(dl.get('country'), datatype=XSD.string)))
                                    g.get_context(factual_data).add((place + URIRef(uri_cleaner(dl.get('country'))), RDF.type, ecrm.E53_Place))
                                    g.get_context(factual_data).add((place + URIRef(uri_cleaner(dl.get('country'))), ecrm.P2_has_type, (place + URIRef('nazione'))))
                                    g.get_context(factual_data).add((place + URIRef(row.get('item_citta_uri')), ecrm.P89_falls_within,(place + URIRef(uri_cleaner(dl.get('country'))))))
                                    g.get_context(factual_data).add((place + URIRef(row.get('item_collocazione_uri')),ecrm.P89_falls_within,(place + URIRef(uri_cleaner(dl.get('country'))))))

                                if dl.get('GeoNames_ID_country'):
                                    g.get_context(factual_data).add((place +URIRef(uri_cleaner(dl.get('country'))), owl.sameAs,URIRef('http://sws.geonames.org/' + dl.get('GeoNames_ID_country'))))

            if row.get('item_tipologia') != None:
                g.get_context(factual_data).add((time + URIRef(row.get('item_tipologia')), RDF.type, ecrm.P55_Type))
                # WDT NON FUNZIONA !!!!!!!!!!!!!!!!!!!!!!!!!  --> da vedere
                #g.get_context(factual_data).add((time + URIRef(row.get('item_tipologia')), owl.sameAs, URIRef(wdt + row.get('item_tipologia_wdt'))))
                g.get_context(factual_data).add((time + URIRef(row.get('item_tipologia')), rdfs.label,Literal(row.get('item_tipologia_label'), datatype=XSD.string)))
                g.get_context(factual_data).add((item + URIRef(row['item_id']), ecrm.P2_has_type, (item + URIRef(row.get('item_tipologia')))))

            if row.get('item_descrizione') != None:
                if row.get('item_descrizione') != "":
                    g.get_context(factual_data).add((item + URIRef(row['item_id'] + '-expression'), dct.description, Literal(row.get('item_descrizione'), datatype=XSD.string)))

            if row.get('item_note') != None:
                if row.get('item_note') != "":
                    g.get_context(factual_data).add((item + URIRef(row['item_id']), dct.note, Literal(row.get('item_note'), datatype=XSD.string)))

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

######################################################## ALTRA ROBA INUTILE IN FACTUAL DATA ###############################################################################################

            # CHE COS'è IL DHARC????
            g.get_context(factual_data).add((people + URIRef(row['post_autore_uri']), RDF.type, efrbroo.F10_Person))
            g.get_context(factual_data).add((URIRef(assertion), RDF.type, np.Assertion))
            g.get_context(factual_data).add((URIRef(provenance), RDF.type, np.Provenance))
            g.get_context(factual_data).add((URIRef(pubInfo), RDF.type, np.PublicationInfo))

######################################################## FACTUAL DATA E FONTI CLASSICHE ###############################################################################################



        for diz in reconciled_completed_works:
            if row['fonti_classiche_orig'] != '':
                string = row['fonti_classiche_orig'].lower()
                substring = diz['input_string'].lower()
                try:
                    if substring in string:
                        if string != '' and substring != '':
                            # DEFINIZIONE DELLE CITAZIONI + STRUTTURA TESTO
                            # passage ??
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), RDF.type, hucit.CanonicalCitation))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']),  ecrm.P2_has_type, (work + URIRef('fonteClassica'))))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), owl.sameAs, URIRef(diz['URN-CTS Citation'])))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), rdfs.label, Literal(diz.get('input_string').replace('; ', '').replace(';', '').replace(diz.get('passage'),'').replace('\"','').replace('  (trad. Luca Canali)', ''), datatype=XSD.string)))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), hucit.has_content,(citation + URIRef(diz['Text Element']))))
                            g.get_context(factual_data).add((citation + URIRef(diz['Text Element']), RDF.type,hucit.TextElement))  # forse ci vuole anche work all'inzio
                            g.get_context(factual_data).add((citation + URIRef(diz['Text Element']), hucit.is_canonical_structure_of, (can_str + URIRef(diz.get('Work URI')))))  # forse ci vuole anche work all'inzio
                            urn_cts_txt_el = diz.get('URN-CTS Citation').replace('http://data.perseus.org/citations/','').replace('.perseus-eng1', '')
                            g.get_context(factual_data).add((citation + URIRef(diz['Text Element']), ecrm.P1_is_identified_by,('http://example.org/' + URIRef(urn_cts_txt_el))))
                            # MANCA IL LIBRO
                            g.get_context(factual_data).add(
                                ('http://example.org/' + URIRef(urn_cts_txt_el), RDF.type, ecrm.E42_Identifier))
                            g.get_context(factual_data).add(('http://example.org/' + URIRef(urn_cts_txt_el), rdfs.label,Literal(diz.get(urn_cts_txt_el), datatype=XSD.string)))
                            g.get_context(factual_data).add(('http://example.org/' + URIRef(urn_cts_txt_el), ecrm.P2_has_type,('http://example.org/' + URIRef('CTS-URN'))))
                            g.get_context(factual_data).add((can_str + URIRef(diz.get('Work URI')), RDF.type, hucit.CanonicalTextStructure))
                            g.get_context(factual_data).add((can_str + URIRef(diz.get('Work URI')), hucit.has_element,(citation + URIRef(diz['Text Element']))))
                            g.get_context(factual_data).add((can_str + URIRef(diz.get('Work URI')),hucit.is_canonical_structure_of,(work + URIRef(diz.get('Work URI')))))

                            # DEFINIZIONE DEL WORK E DELLA SUA CREAZIONE con AUTORE

                            uri_work = diz.get('Work URI')
                            g.get_context(factual_data).add((work + URIRef(uri_work), RDF.type, efrbroo.F1_Work))
                            g.get_context(factual_data).add((work + URIRef(uri_work), owl.sameAs,
                                                             (viaf + URIRef(diz['VIAF ID Work']))))  # dove vanno le label??
                            g.get_context(factual_data).add(
                                (work + URIRef(uri_work), rdfs.label, Literal(diz.get('Label VIAF'), datatype=XSD.string)))
                            g.get_context(factual_data).add((work + URIRef(uri_work), owl.sameAs, URIRef(diz['URN-CTS Work'])))
                            g.get_context(factual_data).add((work + URIRef(uri_work), rdfs.label,
                                                             Literal(diz.get('Perseus Label Work'), datatype=XSD.string)))
                            g.get_context(factual_data).add(
                                (work + URIRef(uri_work) + '-conception', RDF.type, efrbroo.F27_Work_Conception))
                            g.get_context(factual_data).add(
                                (work + URIRef(uri_work) + '-conception', efrbroo.R16_initiated, (work + URIRef(uri_work))))
                            g.get_context(factual_data).add((people + URIRef(diz.get('Author URI')), ecrm.P14_carried_out_by,
                                                             (work + URIRef(uri_work) + '-conception')))
                            g.get_context(factual_data).add(
                                (people + URIRef(diz.get('Author URI')), RDF.type, efrbroo.F10_Person))
                            g.get_context(factual_data).add(
                                (people + URIRef(diz.get('Author URI')), owl.sameAs, (viaf + URIRef(diz['VIAF ID Author']))))
                            g.get_context(factual_data).add((people + URIRef(diz.get('Author URI')), rdfs.label,
                                                             Literal(diz.get('VIAF Label Author'), datatype=XSD.string)))
                        # PENSA SE METTERE L'URN CTS ANCHE ALL'AUTORE

                        ## ASSERZIONE - categorie
                            for cat in row.get('categoria'):
                                g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), ecrm.P67_refers_to, (categ + URIRef(cat.get('uri')))))

                    # HISTORIA AUGUSTA LOL

                except:
                    None

            if '//' in row.get('riscritture_letterarie'):
                n = 0
                for rl in row.get('riscritture_letterarie'):
                    if 'categoria' in rl.get('categoria'):
                        g.get_context(assertion + '-' + str(n+1)).add((URIRef(rl.get('work_uri')), ecrm.P67_refers_to,(URIRef(rl.get['categoria']))))


############################################################# OPINIONI DISCORDANTI ###########################################################################

            l = []
            l2 = []
            n = 0
            for rl in row.get('riscritture_letterarie'):
                if rl.get('categoria') != None:
                    l.append(rl.get('categoria'))
                    l2 = list(set(l))
            if l2 != []:
                for ll in l2:
                    n = n + 1
                    # if row.get('categoria') != None:
                    # for li in row.get('categoria'):
                    # if li.get('uri') != None:
                    # g.get_context(assertion + '-' + str(n)).add((URIRef(work + rl.get('work_uri')),ecrm.P67_refers_to,(URIRef(categ + li.get('uri')))))
                    # g.get_context(assertion + '-' + str(n)).add((URIRef(item + row.get('item_id')),ecrm.P67_refers_to,(URIRef(categ + li.get('uri')))))
                    for rl in row.get('riscritture_letterarie'):
                        if rl.get('categoria') == ll:
                            if rl.get('work_uri') != None:
                                if row.get('item_id') != None:
                                    g.get_context(assertion + '-' + str(n)).add((URIRef(work + rl.get('work_uri')),ecrm.P67_refers_to,(URIRef(categ + rl.get('categoria')))))
                                    g.get_context(assertion + '-' + str(n)).add((URIRef(item + row.get('item_id')),ecrm.P67_refers_to,(URIRef(categ + rl.get('categoria')))))

    print(g.serialize(format='trig').decode('UTF-8'))
    #g.serialize(destination='discarica/all-in-1-16-10c.trig', format='trig')
    #return factual_data, factual_data, assertion, provenance, publicationInfo, head

    # MANCA IDENTIFIER DI WORK!!!
    # OK # dct.type --> ecrm.p2
    # ID DI PERSON IN CONCEPTION E' SBAGLIATO !!!
    # OK # le riscritture letterarie hanno il refes to alla categoria???
    # gli uri di tutte le fonti tranne classici non sono perfetti --> forse dovrebbero rifarsi a viaf
    # tutti i work tranne clssiche--- manca l'allineamento con viaf
    # rivedi i work tranne classiche es: <http://example.org/work/giovanni-boccaccio-genealogie-deorum-gentilium-libri>
    # categoria classe --> superclassi in layer 0 o 1
    # OK # vedi in output cosa succede con i refers to work-categ riscritture letterarie
    # rivedi NI dei tipi --> forse ci vuole una specifica tipo: "tipoNazione"

#csv_writer(csv_creation(csv_intermedio(big_url)))
#assertion_creator(results)
#export_graph(g, results)
#factual_data_graph_simple_mode(results)

factual_data_graph(results)

