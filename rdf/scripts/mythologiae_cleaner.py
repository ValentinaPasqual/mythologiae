import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import re
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

import csv
import json

url='Toyset_Mythologiae.tsv'
big_url = 'wpcsv-export-20200724150145.csv'

################################################################################################################################################################
########################################################################### CSV PARSERS ########################################################################
################################################################################################################################################################

def process_data(source_csv_file_path):
    import csv
    data = list()
    with open(source_csv_file_path, 'r', encoding='utf-8') as test:
        processed_data = csv.DictReader(test, delimiter=';')
        for x in processed_data:
            x = dict(x)
            data.append(x)
    return data

def process_data_tsv(source_csv_file_path):
    import csv
    data = list()
    with open(source_csv_file_path, 'r', encoding='utf-8') as test:
        processed_data = csv.DictReader(test, delimiter='\t')
        for x in processed_data:
            x = dict(x)
            data.append(x)
    return data


def utf8_encoding(data):
    lista = list()
    for row in data:
        string = str()
        dizionario = {}
        for k,v in row.items():
            if '\xa0' in v:
                string = v.replace('\xa0', '')
                dizionario.update({k:string.lstrip(' ')})
            elif '\n' in v:
                string = v.replace('\n', '')
                dizionario.update({k:string.lstrip(' ')})
            elif '\'' in v:
                string = v.replace('\'', '')
                dizionario.update({k: string.lstrip(' ')})
            elif '\t' in v:
                string = v.replace('\t', '')
                dizionario.update({k: string.lstrip(' ')})
        lista.append(dizionario)
    return (lista)

def uri_cleaner(string):
    string3, string4 = str(), str()
    string2 = string.replace(' ', '-').replace(':', '-').lower()
    if '--' in string2:
        string3 = string2.replace('--', '-')
    else:
        string3 = string2
    if len(string3) > 0:
        if '-' in string3[0]:
            string4 = string3[1:]
        else:
            string4 = string3
    return string4


def sort_of_dicts_cleaner(string):
    print(string)
    lista1 = []
    if string != None:
        lista1 = string.split('\"')
    if lista1 != []:
        return lista1[1]
    else:
        m = str()
        return m


################################################################################################################################################################
####################################################################### CHECK LIST CREATORS ####################################################################
################################################################################################################################################################


def periods_list(data): # serve per vedere se ci sono inconsistenze nei dati e per cercare a mano poi i codici su Getty
    lista = []
    for row in data:
        if type(row['periodo']) != float:
            lista.append(row['periodo'])
            lista= list(set(lista))
    print (sorted(lista)) # fa una lista di valori unici

def typology_list(data): # serve per vedere se ci sono inconsistenze nei dati e per cercare a mano poi i codici su Getty
    lista = []
    for row in data:
        if type(row['tipologia']) != float:
            lista.append(row['tipologia'])
            lista= list(set(lista))
    print(sorted(lista)) # fa una lista di valori unici

def collocation_list(data):  # serve per vedere se ci sono inconsistenze nei dati e per cercare a mano poi i codici su WIKIDATA
    lista = []
    for row in data:
        if type(row['collocazione']) != float:
            lista.append(row['collocazione'])
            lista= list(set(lista))
    print(sorted(lista)) # fa una lista di valori unici

def item_author_list(data):
    lista = []
    for row in data:
        if type(row['cf_Autore']) != float:
            lista.append(row['cf_Autore'])
            lista = list(set(lista))
    return sorted(lista)

def lista_fonti_per_autore(data, colum_name):
    diz = {}
    new_dict = {}
    new_list = {}
    for row in data:
        if type(row[colum_name]) == str:
            str1 = row[colum_name].replace('\"', '')
            str2 = str1.replace('\'', '')
            lista_fonti = str2.split(',')
        if lista_fonti[0] not in diz:
            diz.update({lista_fonti[0]: []})
        else:
            for key, value in diz.items():
                if lista_fonti[0] in key:
                    stringa = ",".join(lista_fonti[1:len(lista_fonti)])
                    value.append(stringa)
    for k,v in diz.items():
        new_list = list(set(v))
        new_dict.update({k:new_list})
    #for x,y in new_dict.items():
        #print (x,y)
    return new_dict

################################################################################################################################################################
###########################################################################  CLEANER ###########################################################################
################################################################################################################################################################

def collocation_cleaner(collocation_column):
    if collocation_column != '':
        lista = collocation_column.split(', ')
        museum_name = lista[0]
        return museum_name

def collocation_city_cleaner(collocation_column):
    museum_city = str()
    if collocation_column != '':
        lista = collocation_column.split(', ')
        if len(lista) > 1:
            museum_city = lista[1]
        return museum_city

def uri_category_cleaner(categoria_column):
    new_categoria_column = str()
    lista2 = []
    if categoria_column != '':
        if ',' in categoria_column:
            lista = categoria_column.split(', ')
            for x in lista:
                string = x.replace(' ', '-').replace(',', '-').replace('.', '-').replace(':', '-').replace('~','-').replace('(', '-').replace(')', '-').lower()

                lista2.append(string)
        else:
            new_categoria_column = (categoria_column).replace(' ', '-').replace(',', '-').replace('.', '-').replace(':', '-').replace('~','-').replace('(', '-').replace(')', '-').lower()
    try:
        for element in new_categoria_column:
            element.replace('--', '-')
    except:
        for element in lista2:
            element.replace('--', '-')
    #print(new_categoria_column, lista2)
    return new_categoria_column or lista2

def new_category_cleaner(categoria_column):
    lista1, lista2, lista_finale = [], [], []
    if categoria_column != '':
        try:
            lista1= categoria_column.split(',')
            for x in lista1:
                diz = {}
                lista2 = x.split(':')
                uri = lista2[0]
                label = lista2[1]
                if '~' in uri:
                    lista_superflua = lista2[0].split('~')
                    superclasse = lista_superflua[0]
                    diz.update({'uri':lista_superflua[1]})
                    diz.update({'label':label})
                    diz.update({'superclasse':superclasse})
                else:
                    diz.update({'uri': uri})
                    diz.update({'label': label})
            lista_finale.append(diz)
            #print('LISTA FINALE', lista_finale, categoria_column)
        except:
            print('PROBABILE ERRORE IN CSV INPUT: tx_category', categoria_column)
    return (lista_finale)



def keywords_cleaner(keyword_column):
    new_categoria_column = str()
    lista2 = []
    if keyword_column != ' ':
        if ', ' in keyword_column:
            lista = keyword_column.split(', ')
            for x in lista:
                string = x.replace(' ', '-').lower()
                string2 = string.replace('.', '')
                lista2.append(string2)
        elif ',' in keyword_column:
            if ', ' in keyword_column:
                lista = keyword_column.split(', ')
                for x in lista:
                    string = x.replace(' ', '-').lower()
                    string2 = string.replace('.', '')
                    lista2.append(string2)
        else:
            new_categoria_column = keyword_column.replace(' ', '-').replace('.', '').lower()
    #print(new_categoria_column, lista2)
    return new_categoria_column or lista2

def uri_periodo_cleaner(periodo_column):
    new_categoria_column = str()
    if periodo_column != '':
        new_categoria_column = periodo_column.replace(' - ', '-').replace(' ', '-').replace('à','a').replace('Ã ', 'a').lower()
    return (new_categoria_column)


def wdt_periodo(period_column):
    dictionary = {'Arte greca - Età classica':'Q16064885', 'Arte greca - Età arcaica':'Q3624131',
        'Arte romana - Età imperiale':'Q2277', 'Arte romana': 'Q3354732', 'Arte medievale':'Q3624153', "Arte etrusco-italica":'Q830331', 'Arte greca - Età micenea' : 'Q181264',
        'Arte greca - Età ellenistica' : 'Q428995', 'Arte romana - Età Repubblicana' : '', 'Arte contemporanea':'Q186030', 'Arte moderna':'Q38166'}

    for k,v in dictionary.items():
        try:
            if period_column == k :
                return str(v)
        except:
            v = ""
            return str(v)

def uri_tipologia_cleaner(tipologia_column):
    new_categoria_column = str()
    if tipologia_column != '':
        new_categoria_column = tipologia_column.replace(' - ', '-').replace(' ', '-').replace('à','a').replace('Ã ', 'a').lower()
    return (new_categoria_column)

def wdt_tipologia(tipologia_column):
    dictionary = {'Disegno':'Q1228609', 'Pittura':'Q1231896', 'Pittura vascolare':'Q4102418', 'Arti minori':'Q631931', 'Scultura':'Q11634'}
    for k,v in dictionary.items():
        for k, v in dictionary.items():
            try:
                if period_column == k:
                    return str(v)
            except:
                v = ""
                return str(v)


def century_comparer(row):
    new_dict = {}
    lista = process_data_tsv('wdt_query_results_folder/query_secoli.tsv')
    if row['cf_secolo'] != '':
        for dictionary in lista:
            if row['cf_secolo'].lower() == dictionary['label'].lower():
                new_dict.update({'item_secolo_wdt': dictionary['x']})
                new_dict.update({'item_secolo_label': dictionary['label']})
    return new_dict

def cinema_cleaner(row):
    string = str()
    lista1, lista2, movie_year_list, lista3, lista4, = [], [], [], [], []
    lista_finale = []
    lista_numeri = ['1','2','3','4','5','6','7','8','9']
    lista = row['cf_riscritture_cinematografiche'].split('. ')
    for x in lista:
        dictionary = {}
        lista1 = x.split(' ')
        for n in lista_numeri:
            year = str()
            for el in lista1:
                if n in el:
                    year = el.replace('.', '').replace('(', '').replace(' (', '').replace(')', '')
                    dictionary.update({'anno_film' : year})
                    movie_year_list.append(year)
        for y in movie_year_list:
            if y in x:
                string = x.replace(y, '')
                lista3.append(string)
        for element in lista3:
            lista2 = element.split(', ')
            if len(lista2) == 2:
                dictionary.update({'titolo_film': lista2[0]})
                dictionary.update({'titolo_film_uri': str(uri_cleaner(lista2[0]).lower() + '-' + year)})
            elif len(lista2) > 2:
                lista_uri_autori = []
                if ' e ' in lista2[0]:
                    lista4 = lista2[0].split(' e ')
                    dictionary.update({'autore_film_label': lista4})
                    for ele in lista4:
                        lista_uri_autori.append(uri_cleaner(ele))
                    dictionary.update({'autore_film_uri': list(set(lista_uri_autori))})
                else:
                    dictionary.update({'autore_film_label': lista2[0]}) # pattern autore, titolo, anno
                    lista_uri_autori.append(uri_cleaner(lista2[0]))
                    dictionary.update({'autore_film_uri': list(set(lista_uri_autori))})

                dictionary.update({'titolo_film': lista2[1]})
                dictionary.update({'titolo_film_uri': str(uri_cleaner(lista2[1]).lower() + '-' + year)})
        lista_finale.append(dictionary)
    return lista_finale

def fonti_medievali_moderne_riscr_let_cleaner(row):
    lista_finale = []
    lista_farlocca, lista_farlocca2 = [], []
    year = ""
    work = ""
    new_row = str()
    if row != '':
        if 'vv.' or 'v.' in row:
            new_row = row.replace('vv.', 'vv').replace('v.', 'v')
        lista0 = new_row.split('. ')
        for element in lista0:
            dizionario_finale = {}
            authors_list, authors_uri_list = [], [],
            try:
                element2 = Divina_Commedia_replacer(element)
            except:
                element = element2
            lista = element2.split(', ')
            for x in lista:
                if '(' and ')' in x:
                    try:
                        year = (x.split(' (')[1]).replace(') ', '').replace('.', '').replace('(', '').replace(')', '')
                        work = (x.split(' (')[0]).replace(') ', '').replace('.', '')
                    except:
                        print("MANCA L\'ANNO")
            try:
                if len(lista) > 1:
                    try:
                        author_string = str()
                        author_string = lista[0].replace("\'", '').replace("\"", "")
                        autore = author_string.split(' e ')
                        for au in autore:
                            authors_list.append(au)
                            authors_uri_list.append(uri_cleaner(au))
                        dizionario_finale.update({'autore_label': authors_list})
                        dizionario_finale.update({'autore_uri': authors_uri_list})#ANCHE SE C'è UN SOLO ELEMENTO NELLA LISTA, FA UNA LISTA LO STESSO
                    except:
                        dizionario_finale.update({'autore_label': lista[0].replace("\'", '').replace("\"", "")})
                    if work != "":
                        dizionario_finale.update({'work_label': (work.replace("\'", '')).replace("\"", "")})
                    else:
                        dizionario_finale.update({'work_label': (lista[1].replace("\'", '')).replace("\"", "")})
                if len(lista) > 2:
                    dizionario_finale.update({'subwork_label': (lista[2].replace("\'",'')).replace("\"","")})
                    if year != "":
                        dizionario_finale.update({'anno': year.replace("\'",'').replace("\'","")}) # si perdono un po' di dati tipo versi etc, ma secondo me non ci interessa
            except:
                print('AN ERROR OCCURRED IN CLEANING FONTI MEDIEVALI')
            if len(dizionario_finale) > 0:
                try:
                    dizionario_finale.update({'work_uri': uri_cleaner(authors_list[0]) + '-' + uri_cleaner(dizionario_finale['work_label'])})
                    dizionario_finale.update({'subwork_uri': uri_cleaner(authors_list[0]) + '-' + uri_cleaner(dizionario_finale['work_label']) + '-' + uri_cleaner(dizionario_finale['subwork_label'])})
                except:
                    dizionario_finale.update({'work_uri': uri_cleaner(authors_list[0]) + '-' + uri_cleaner(dizionario_finale['work_label'])})
            lista_finale.append(dizionario_finale)
    return lista_finale

def Divina_Commedia_replacer(row):
    lista_nomi = ['Inferno', 'inferno', 'Paradiso', 'paradiso', 'purgatorio', 'Purgatorio']
    new_row = str()
    for x in lista_nomi:
        if x in row:
            lista_row = row.split(x)
            new_row = str(lista_row[0] + 'Divina Commedia') + str(lista_row[1])
        else:
            new_row = row
    return new_row


################################################################################################################################################################
###########################################################################  CSV CREATORS ######################################################################
################################################################################################################################################################

def csv_creation(list_of_dictionaries):
    lista_finale = []
    x = 0
    for row in list_of_dictionaries:
        if 'post' in row['wp_post_type']:
            x = x + 1
            dizionario_finale = {}
            dizionario_finale.update({'item_id': str(x)})
            # titolo
            dizionario_finale.update({'item_autore': row['cf_Autore']})
            #   AGGIUNGI ITEM_AUTORE_ID
            dizionario_finale.update({'item_descrizione': row['cf_descrizione']})
            #if row['cf_descrizione'] != '':
                #dizionario_finale.update({'item_descrizione_lang': '@it'}) #farlocchio, ma tanto sono tutti ita
            if row['cf_periodo'] != '':
                dizionario_finale.update({'item_periodo': sort_of_dicts_cleaner(uri_periodo_cleaner(row['cf_periodo']))})
                dizionario_finale.update({'item_periodo_wdt': wdt_periodo(sort_of_dicts_cleaner(row['cf_periodo']))})
                dizionario_finale.update({'item_periodo_label': sort_of_dicts_cleaner(row['cf_periodo'])})
            results_secoli = century_comparer(row)
            if results_secoli != {}:
                dizionario_finale.update({'item_secolo_wdt': results_secoli['item_secolo_wdt']})
                dizionario_finale.update({'item_secolo_label': results_secoli['item_secolo_label']})
            #data
            if row['cf_tipologia_del_manufatto'] != '':
                dizionario_finale.update({'item_tipologia': sort_of_dicts_cleaner(uri_periodo_cleaner(row['cf_tipologia_del_manufatto']))})
                dizionario_finale.update({'item_tipologia_wdt': wdt_periodo(sort_of_dicts_cleaner(row['cf_tipologia_del_manufatto']))})
                dizionario_finale.update({'item_tipologia_label': sort_of_dicts_cleaner(row['cf_tipologia_del_manufatto'])})
            dizionario_finale.update({'item_collocazione': collocation_cleaner(row['cf_Collocazione'])})
            dizionario_finale.update({'item_citta': collocation_city_cleaner(row['cf_Collocazione'])})
            #note #fonti_classiche
            lista_riscr_lett = fonti_medievali_moderne_riscr_let_cleaner(row['cf_riscritture_letterarie'])
            if len(lista_riscr_lett) > 0:
                if lista_riscr_lett != [{}]:
                    dizionario_finale.update({'riscritture_letterarie': lista_riscr_lett})
            else:
                dizionario_finale.update({'riscritture_letterarie': ""})
            lista_fonti_mediev = fonti_medievali_moderne_riscr_let_cleaner(row['cf_fonti_medievali_e_moderne'])
            if len(lista_fonti_mediev) > 0:
                if lista_fonti_mediev != [{}]:
                    dizionario_finale.update({'fonti_medievali_e_moderne': lista_fonti_mediev})
            else:
                dizionario_finale.update({'fonti_medievali_e_moderne': ""})
            lista_film = cinema_cleaner(row)
            if lista_film != [{}]:
                dizionario_finale.update({'riscritture_cinematografiche': lista_film})
            else:
                dizionario_finale.update({'riscritture_cinematografiche': ''})
            dizionario_finale.update({'categoria' : new_category_cleaner(row['tx_category'])}) #lista o stringa a seconda del n' delle categorie
            dizionario_finale.update({'item_link_esterno': row['cf_collegamento_link_esterno']})
            dizionario_finale.update({'keywords': keywords_cleaner(row['tx_post_tag'])}) # fa delle liste a caso boh
        lista_finale.append(dizionario_finale)
        print(dizionario_finale)
    return lista_finale


def csv_writer(final_list_of_dicts):
    df = pd.DataFrame(final_list_of_dicts, columns=["item_id", 'item_autore', 'item_descrizione',
                                                    'item_periodo', 'item_periodo_wdt', 'item_periodo_label', 'item_secolo_wdt', 'item_secolo_label',
                                                    'item_tipologia','item_tipologia_wdt', 'item_tipologia_label',
                                                    'item_collocazione', 'item_citta', 'anno_film','autore_film', 'titolo_film', 'categoria',
                                                    'item_link_esterno',"fonti_medievali_e_moderne", "riscritture_letterarie", "riscritture_cinematografiche", 'keywords'])
    df.to_csv('discarica/prova_19-08.tsv', index=False, sep="\t", encoding='utf-8') #dovrei trovare il modo per mettere delimiter e formato


#csv_writer(csv_creation(url))



def csv_intermedio(dataset_url):
    final_list = []
    data = process_data(dataset_url) #devo trovare il modo di togliere \t e spazi
    for row in data:
        if 'post' in row['wp_post_type']: #solo se lo status del post è quello di post e non di revisione
            new_dict = {}
            new_dict.update({'wp_post_title' : row['wp_post_title']})
            new_dict.update({'wp_post_date' : row['wp_post_date']})
            new_dict.update({'wp_post_modified':row['wp_post_modified']})
            new_dict.update({'wp_post_status': row['wp_post_status']})
            new_dict.update({'wp_post_type' : row['wp_post_type']})
            new_dict.update({'wp_post_author' : row['wp_post_author']})
            #new_dict.update({'G2:wp_post_title': row['wp_post_title']}) #C'è 2 VOLTE O PARE A ME???
            new_dict.update({'tx_category' : row['tx_category']})
            new_dict.update({'tx_post_tag' : row['tx_post_tag']})
            new_dict.update({'cf_Autore' : row['cf_Autore']})   # FATTO
            new_dict.update({'cf_Data' : row['cf_Data']})
            new_dict.update({'cf_Collocazione' : row['cf_Collocazione']})
            new_dict.update({'cf_note' : row['cf_note']})
            new_dict.update({'cf_secolo': row['cf_secolo']})
            new_dict.update({'cf_periodo' : row['cf_periodo']})
            new_dict.update({'cf_tipologia_del_manufatto' : row['cf_tipologia_del_manufatto']})
            new_dict.update({'cf_collegamento_link_esterno' : row['cf_collegamento_link_esterno']})
            new_dict.update({'cf_fonti_letterarie' : row['cf_fonti_letterarie']})
            new_dict.update({'cf_descrizione' : row['cf_descrizione']}) #fatto
            new_dict.update({'cf_fonti_medievali_e_moderne' : row['cf_fonti_medievali_e_moderne']})
            new_dict.update({'cf_riscritture_letterarie': row['cf_riscritture_letterarie']})
            new_dict.update({'cf_riscritture_cinematografiche' : row['cf_riscritture_cinematografiche']})
            if new_dict != {}:
                final_list.append(new_dict)
    return final_list

def printer(data):
    for x in data:
        print(x)

def wikidata_queries(lista):
    lista2 = []
    print(lista)
    for elem in lista:
        try:
            if ',' in elem:
                lista_prov = elem.split(', ')
                x = str(lista_prov[1] + ' ' + lista_prov[0])
            else:
                x = elem
        except:
            x = elem
        try:  #devo comunque levare spazi e \t
            sparql_query = """
            SELECT ?s ?sLabel ?viaf_id
            WHERE {
              ?s wdt:P31 wd:Q5 ;
                wdt:P214 ?viaf_id. 
            FILTER regex(?sLabel, """ + '\'' + x + '\'' + """, 'i'). } """
            res = return_sparql_query_results(sparql_query)
            #lista2.append(res)
            print(res)
        except:
            print(x + ' non va')



#printer(item_author_list(csv_intermedio(big_url)))
#csv_writer(csv_creation(csv_intermedio(big_url)))


#wikidata_queries(item_author_list(csv_intermedio(big_url)))







#lista_fonti_per_autore(utf8_encoding(process_data('Toyset_Mythologiae.tsv')), 'Fonti letterarie classiche')
#utf8_encoding(process_data('Toyset_Mythologiae.tsv'))

