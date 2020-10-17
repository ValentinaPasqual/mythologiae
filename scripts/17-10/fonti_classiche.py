import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace, ConjunctiveGraph #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import re
import csv
import json
from entity_linking import *
from mythologiae_cleaner import *

"""factual_data = URIRef("http://example.org/factual_data")
item = Namespace('http://example.org/item/')
work = Namespace('http://example.org/work/')
people = Namespace('http://example.org/person/')
categ = Namespace('http://example.org/categ/')
time = Namespace('http://example.org/time/')
place = Namespace('http://example.org/place/')
intact = Namespace('http://example.org/int-act/')
viaf = Namespace('http://viaf.org/viaf/')
citation = Namespace('http://example.org/cit/')
can_str = Namespace('http://example.org/str/')


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
g = ConjunctiveGraph()"""

big_url = 'wpcsv-export-20200724150145-v2.xlsb.csv'
results = csv_creation(csv_intermedio(big_url))

def romanToInt(rom):
    value = {
        'M': 1000,
        'D': 500,
        'C': 100,
        'L': 50,
        'X': 10,
        'V': 5,
        'I': 1
    }
    # Initialize previous character and answer
    p = 0
    ans = 0
    # Traverse through all characters
    n = len(rom)
    for i in range(n - 1, -1, -1):
        # If greater than or equal to previous,
        # add to answer
        if value[rom[i]] >= p:
            ans += value[rom[i]]
            # If smaller than previous
        else:
            ans -= value[rom[i]]
            # Update previous
        p = value[rom[i]]
    return ans

def canonical_citation_analizer(results):  # per didone + per lucrezia
    l, lwip, en, om = [], [], [], []
    for row in results:
        if row['fonti_classiche_orig']:
            if row['fonti_classiche_orig'] != '' or row['fonti_classiche_orig'] != 'ciao' or row['fonti_classiche_orig'] != 'dfgh':
                if "sec. d.C." not in row['fonti_classiche_orig'] or "sec. a.C." not in row['fonti_classiche_orig']:
                    if 'altre fonti su' not in row['fonti_classiche_orig'].lower():  # perchè vuol dire che c'è tipo 'ALTRE FONTI SU ENEA....'
                        lp = row['fonti_classiche_orig'].split('; ')
                        for ll in lp:
                            lp2 = ll.split(' - ')  # spezza in singoli bibliogr records
                            for el in lp2:
                                el2 = el.replace(';', '')
                                l.append(el2)
                    else:
                        m = re.search("; (.*):", row['fonti_classiche_orig'])    # QUI DOVREBBE ESSERCI LA PARTE SULLE ALTRE FONTI CHE PER ORA NON FACCIO BYE
                        gm = m.group(1) if m else None
                        lp3 = (row['fonti_classiche_orig']).split(gm)    # PER ORA AGGIUNGE SOLO LA PRIMA FONTE CLASSICA, TUTTO QUELLO DI ALTRE FONTI NON LO CONSIDERO PER ORA
                        l.append(lp3[0]) # il primo elemento lo aggiunge normale
                        afs = lp3[1].split('; ')
        #enea = list(set(en))
        ul = list(set(l))
        for entry in ul:
            df = {}
            df.update({'input_string': entry})  # STRINGA DI INPUT PER POI FARE IL MATCH CON IL CSV DI INPUT
            n_entry = entry.replace('”', '\"').replace('’', '\'').replace('“', '\"')
            try:
                match = re.search("\"(.*)\"", n_entry)
                wiw = match.group(1) if match else None
                if wiw != None:
                    df.update({'passage':wiw})   # STRINGA CHE CONTIENE IL PASSO TESTUALE DELLA REF BIB CANONICA
                ne2 = n_entry.replace(wiw, '').replace('vv. ', '').replace('vv.', '').replace("trad. Luca Canali", "") # ne2 è la stringa di input senza il 'passage' e senza 'vv'
            except:
                ne2 = n_entry
            l2 = ne2.split(', ')
            for e in l2:
                int_finder = re.findall(r'[0-9]+', e) # MANCA E SS.
                if 'odissea' in e.lower():
                    df.update({'author': 'Omero'})
                    df.update({'work': 'Odissea'})
                    l2.remove(e)
                if 'iliade' in e.lower():
                    df.update({'author': 'Omero'})
                    df.update({'work': 'Iliade'})
                    l2.remove(e)
                if 'eneide' in e.lower():
                    df.update({'author': 'Virgilio'})
                    df.update({'work': 'Eneide'})
                    l2.remove(e)
                if 'Historia Augusta.' in e.lower() or 'historia augusta' in e.lower():
                    df.update({'author': 'Sconosciuto'})
                    df.update({'work': 'Historia Augusta'})
                    l2.remove(e)
                else:
                    if len(l2) > 2:
                        author = re.sub('^ ', '', l2[0])
                        work = re.sub('^ ', '', l2[1])
                        df.update({'author': author})
                        df.update({'work': work})
                        l2.remove(l2[0])
                        l2.remove(l2[0])
            for xe in l2:
                int_finder2 = re.findall(r'[0-9]+', xe)
                if len(int_finder2) == 2:  # se lunghezza è 3 e ci sono numeri, quindi versi
                    df.update({'vv_start': int_finder2[0]})
                    df.update({'vv_end': int_finder2[1]})
                if len(int_finder2) == 1:
                    df.update({'vv': int_finder2[0]})
            for e2 in l2:
                int_finder2 = re.findall(r'[0-9]+', e2)
                if len(int_finder2) > 0:
                    l2.remove(e2)  # NON VA CREDO
            try:
                rn = romanToInt(l2[0])
                df.update({'n_book': rn})
                df.update({'rn_book': l2[0]})
            except:
                None
            if df['input_string'] != '':
                lwip.append(df)
    final_l = [dict(t) for t in {tuple(d.items()) for d in lwip}]
    return final_l

can_cit_list = canonical_citation_analizer(results)

def csv_writer(final_list_of_dicts):
    df = pd.DataFrame(final_list_of_dicts, columns=["input_string", "author", "work",
                                                    "n_book", "rn_book", "vv_start", "vv_end", "vv", "passage"])
    df.to_csv('discarica/fonti_classiche_interne.tsv', index=False, sep="\t", encoding='utf-8') #dovrei trovare il modo per mettere delimiter e formato

#csv_writer(can_cit_list)

######################################################################################################################




internal_cit_enriched = process_data_tsv("discarica/fonti_classiche_interne.tsv") # Da qui prendo tutte le citazioni con informazioni varie
reconciled = process_data_tsv("entity_linking/reconciled/classics_urn-cts_perseus-viaf.tsv") # qui ci sono work e autori riconciliati con viaf e perseus
# estraggo tutti gli autori e li riconcilio da internal_cit_enriched

def classic_authors_checking(internal_cit_enriched):
    l = []
    for x in internal_cit_enriched:
        l.append(x.get('author'))
    lf = [set(l)]
    print(lf)

#classic_authors_checking(internal_cit_enriched)

# Con data curator creo un dataset a mano che prenda tutti i work citati e li associ a perseus e viaf per
# avere le forme controllate della label
# con open-refine aggiungo i dati di viaf --> label regolarizzata ed id per persone e work


def matcher_internal_and_reconciled_values(internal, reconciled):
    for r in reconciled:
        rs = r['Label'].split(', ')
        for dic in internal:
            if rs[0] in dic['author'] and rs[1] in dic['work']: # in caso di omonimia non sbaglia
                dic.update(r)
    return internal

def uri_classiche_creator(internal_completed):
    var = 0
    for r in internal_completed:
        var = var + 1
        if r['vv_start'] != '' and r['vv_end'] != '' and r['n_book'] != '':  # X.10-12
            citation = str(r['URN-CTS Text'] + ':' + str(str(int(float(r['n_book']))) + '.' + r['vv_start'] + '-' + str(str(int(float(r['n_book']))) + '.' + r['vv_end'])))
            txt_element = r['rn_book'] + '-' + r['vv_start'] + '-' + r['vv_end']
        if r['vv'] != '' and r['n_book'] != '' and r['vv_start'] == '' and r['vv_end'] == '':  #X.10
            citation= str(r['URN-CTS Text'] + ':' + str(str(int(float(r['n_book']))) + '.' + r['vv']))
            txt_element = r['rn_book'] + '-' + r['vv']
        try:
            if r['vv_start'] != '' and r['vv_end'] != '' and r['n_book'] == '':   #10-12
                if r['URN-CTS Text'] != '' or r['URN-CTS Text'] != None:
                    citation = str(r['URN-CTS Text'] + ':' + r['vv_start'] + '-' + r['vv_end'])
                    txt_element = r['vv_start'] + '-' + r['vv_end']
        except:
            None
        if r['vv'] != '' and r['n_book'] == '':   #10
            citation = str(r['URN-CTS Text'] + ':' + r['vv'])
            txt_element = r['vv']
        if r['vv'] == '' and r['vv_start'] == '' and r['vv_end'] == '' and r['n_book'] != '':  # X
            n_book = str(int(float(r['n_book'])))
            citation = str(r['URN-CTS Text'] + ':' + n_book)
            txt_element = r['rn_book']
        # altrimenti non ha citazione e si parla solo di work
        urn_citation = citation.replace('/texts/', '/citations/')
        r.update({'URN-CTS Citation': urn_citation})
        r.update({'URI Citation': str(var)})
        r.update({'Text Element': txt_element})
        try:
            uri_work = uri_cleaner(r['Label VIAF']).replace('-43-b-c-17-a-d-or-18-a-d', '').replace('--', '-').replace(',', '').replace('-approximately-4-b-c-65-a-d', '')
            r.update({'Work URI':uri_work})
        except:
            None
        try:
            uri_author = uri_cleaner(r['VIAF Label Author']).replace('-43-b-c-17-a-d-or-18-a-d', '').replace('--', '-').replace(
                ',', '').replace('-approximately-4-b-c-65-a-d', '')
            r.update({'Author URI': uri_author})
        except:
            None
        #print(r)
    return internal_completed

reconciled_completed_works = matcher_internal_and_reconciled_values(internal_cit_enriched, reconciled)
uri_classiche_creator(reconciled_completed_works)



"""def matcher_full_work_and_input_csv(fullworks, inputcsv):
    for row in inputcsv:
        for diz in fullworks:
            if row['fonti_classiche_orig'] != '':
                string = row['fonti_classiche_orig'].lower()
                substring = diz['input_string'].lower()
                try:
                    if substring in string:
                        if string != '' and substring != '':
                            # DEFINIZIONE DELLE CITAZIONI + STRUTTURA TESTO
                            # passage ??
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), RDF.type, hucit.CanonicalCitation))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), owl.sameAs, URIRef(diz['URN-CTS Citation'])))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), rdfs.label, Literal(diz.get('input_string').replace('; ', '').replace(';', '').replace(diz.get('passage'), '').replace('\"', '').replace('  (trad. Luca Canali)', ''), datatype=XSD.string)))
                            g.get_context(factual_data).add((citation + URIRef(diz['URI Citation']), hucit.has_content, (citation + URIRef(diz['Text Element']))))
                            g.get_context(factual_data).add((citation + URIRef(diz['Text Element']), RDF.type, hucit.TextElement))  # forse ci vuole anche work all'inzio
                            urn_cts_txt_el = diz.get('URN-CTS Citation').replace('http://data.perseus.org/citations/', '').replace('.perseus-eng1', '')
                            g.get_context(factual_data).add((citation + URIRef(diz['Text Element']), ecrm.P1_is_identified_by, ('http://example.org/' + URIRef(urn_cts_txt_el))))
                            # MANCA IL LIBRO
                            g.get_context(factual_data).add(('http://example.org/' + URIRef(urn_cts_txt_el), RDF.type, ecrm.E42_Identifier))
                            g.get_context(factual_data).add(('http://example.org/' + URIRef(urn_cts_txt_el), rdfs.label, Literal(diz.get(urn_cts_txt_el), datatype=XSD.string)))
                            g.get_context(factual_data).add(('http://example.org/' + URIRef(urn_cts_txt_el), ecrm.P2_has_type, ('http://example.org/' + URIRef('CTS-URN'))))
                            g.get_context(factual_data).add((can_str + URIRef(diz.get('Work URI')), RDF.type, hucit.CanonicalTextStructure))
                            g.get_context(factual_data).add((can_str + URIRef(diz.get('Work URI')), hucit.has_element, citation + URIRef(diz['Text Element'])))
                            g.get_context(factual_data).add((can_str + URIRef(diz.get('Work URI')), hucit.is_canonical_structure_of, (work + URIRef(diz.get('Work URI')))))

                            # DEFINIZIONE DEL WORK E DELLA SUA CREAZIONE con AUTORE

                            uri_work = diz.get('Work URI')
                            g.get_context(factual_data).add((work + URIRef(uri_work), RDF.type, efrbroo.F1_Work))
                            g.get_context(factual_data).add((work + URIRef(uri_work), owl.sameAs, (viaf + URIRef(diz['VIAF ID Work'])))) # dove vanno le label??
                            g.get_context(factual_data).add((work + URIRef(uri_work), rdfs.label, Literal(diz.get('Label VIAF'), datatype=XSD.string)))
                            g.get_context(factual_data).add((work + URIRef(uri_work), owl.sameAs, URIRef(diz['URN-CTS Work'])))
                            g.get_context(factual_data).add((work + URIRef(uri_work), rdfs.label, Literal(diz.get('Perseus Label Work'), datatype=XSD.string)))
                            g.get_context(factual_data).add((work + URIRef(uri_work) + '-conception', RDF.type, efrbroo.F27_Work_Conception))
                            g.get_context(factual_data).add((work + URIRef(uri_work) + '-conception', efrbroo.R16_initiated, (work + URIRef(uri_work))))
                            g.get_context(factual_data).add((people + URIRef(diz.get('Author URI')), ecrm.P14_carried_out_by, (work + URIRef(uri_work) + '-conception')))
                            g.get_context(factual_data).add((people + URIRef(diz.get('Author URI')), RDF.type, efrbroo.F10_Person))
                            g.get_context(factual_data).add((people + URIRef(diz.get('Author URI')), owl.sameAs, (viaf + URIRef(diz['VIAF ID Author']))))
                            g.get_context(factual_data).add((people + URIRef(diz.get('Author URI')), rdfs.label, Literal(diz.get('VIAF Label Author'), datatype=XSD.string)))
                            # PENSA SE METTERE L'URN CTS ANCHE ALL'AUTORE

                        # HISTORIA AUGUSTA LOL

                except:
                    None

    print(g.serialize(format='trig').decode('UTF-8'))

matcher_full_work_and_input_csv(reconciled_completed_works, results)"""




