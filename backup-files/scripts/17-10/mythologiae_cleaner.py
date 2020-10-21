import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import re
import unidecode
import csv
import json

url='Toyset_Mythologiae.tsv'
big_url = 'wpcsv-export-20200724150145-v2.xlsb.csv'
csv_classiche = 'query_results_hucitkb/combine.csv'

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
    string3, string4, string5 = str(), str(), str()
    if string != None:
        string2 = string.replace(' - ', '-').replace(' ', '-').replace(':', '-').replace('.','-').replace('\"', '').replace('\'','').replace('.', '').replace('|', '-').replace('/', '-').lower()
        if '--' in string2:
            string3 = string2.replace('--', '-')
        else:
            string3 = string2
        if len(string3) > 0:
            if '-' in string3[0]:
                string4 = string3[1:]
            else:
                string4 = string3
            if '-' in string4[len(string4)-1]:
                string5 = string4[:len(string4)-1]
            else:
                string5 = string4
    string6 = unidecode.unidecode(string5)
    return string6

def sort_of_dicts_cleaner(string):
    lista1 = []
    if string != None:
        lista1 = string.split('\"')
    if len(lista1) > 2:
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

def lista_fonti_per_autore(colum_name):
    new_list, lista = [],[]
    new_dict = {}
    str2 = str()
    if type(colum_name) == str:
        if colum_name != "":
            str1 = colum_name.replace('\"', '')
            str_a = re.sub("([\(\[]).*?([\)\]])", "", str1) #per togliere le () e il loro contenuto !!!
            str0 = str_a.replace('\'', '')
            if ' ' in str0[len(str0)-1]: #per togliere lo spazio alla fine della stringa
                str2 = str0[:len(str0)-1]
            else:
                str2 = str0
            if ' e ' in str2:
                lista = str2.split(' e ')
                for el in lista:
                    str_uri = str()
                    new_dict = {}
                    str_uri = uri_cleaner(el).replace(',', '').replace('--', '-') # type lista di n elementi
                    str_label = el.replace(',', '')
                    new_dict.update({'autore_uri' : str_uri})
                    new_dict.update({'autore_label': str_label})
                    new_list.append(new_dict)
            else:
                str_uri = uri_cleaner(str2).replace(',', '').replace('--', '-')  # type lista di 1 elemento
                str_label = str2.replace(',', '')
                new_dict.update({'autore_uri': str_uri})
                new_dict.update({'autore_label': str_label})
                new_list.append(new_dict)
    return new_list


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
                    lista_finale.append(diz)
                else:
                    diz.update({'uri': uri})
                    diz.update({'label': label})
                    lista_finale.append(diz)
        except:
            print('PROBABILE ERRORE IN CSV INPUT: tx_category', categoria_column)
    return (lista_finale)



def keywords_cleaner(keyword_column):
    new_categoria_column = str()
    lista2, lista3 = [], []
    if keyword_column != ' ':
        if ',' in keyword_column:
            lista = keyword_column.split(',')
            for x in lista:
                lista2 = x.split(':')
                lista3.append(lista2[0])
        else:
            lista2 = keyword_column.split(':')
            lista3.append(lista2[0])
    return lista3

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



def timespans_definer(string1):
    dictionary = {}
    year, start_anno, end_anno = str(), str(), str()
    string = string1.replace(" a.C.", "").replace("ca.", "").replace("ca ", "").replace(" ca", "").replace(' circa', "") \
        .replace('circa ', "").replace(" a.C", "").replace(' d.C.', "").replace(' a.c.', "").replace(' a.c. ', "") \
        .replace('a.c. ', "").replace('a.c.', "").replace('a.C.', "").replace('cir', "").replace(' cir', "")
    # "prima del....", "dopo del ....." che famo???
    if 'sec' not in string1.lower():  # se c'è il secolo non lo considero
        if '>' not in string1:  # che non sia il caso di '>1530' e caso del: "dopoil1510"
            if 'a.c' not in string1.lower():  # se è a.C. allora cambia il calcolo della data
                if '-' in string or '–' in string: # se il formato è 'xx-xx',cioè è un timespan
                    timespan = string.split('-')
                    if len(timespan) > 1:
                        start_anno = timespan[0].replace(" ", "") + '-01-01'
                        end_anno = timespan[1].replace(" ", "") + '-12-31'
                    if len(start_anno) == 10:
                        dictionary.update({'anno_start': start_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_start': '0' + start_anno.replace(" ", "")})
                    if len(end_anno) == 10:
                        dictionary.update({'anno_end': end_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_end': '0' + end_anno.replace(" ", "")})
                    dictionary.update({'anno_label': string.replace(" ", "")})
                    dictionary.update({'anno_uri': uri_cleaner(string).replace(" ", "")})
                else:
                    start_anno = string.replace(" ", "") + '-01-01' # se il formato è solo la data, cioè timespan di un anno
                    end_anno = string.replace(" ", "") + '-12-31'
                    dictionary.update({'anno_label': string.replace(" ", "")})
                    dictionary.update({'anno_uri': uri_cleaner(string).replace(" ", "")})
                    if len(start_anno) == 10:
                        dictionary.update({'anno_start': start_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_start': '0' + start_anno.replace(" ", "")})
                    if len(end_anno) == 10:
                        dictionary.update({'anno_end': end_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_end': '0' + end_anno.replace(" ", "")})
            else:  # d.C altro calcolo della data   ------> !!!!!!!!!!A.C.!!!!!!!!!!!!!
                if '-' in string or '–' in string:
                    timespan = string.split('-')
                    if len(timespan) > 1:
                        start_anno = timespan[0].replace(" ", "") + '-01-01'
                        end_anno = timespan[1].replace(" ", "") + '-12-31'
                    dictionary.update({'anno_label': string.replace(" ", "") + ' a.C.'})
                    dictionary.update({'anno_uri': uri_cleaner(string).replace(" ", "") + 'a-c'})
                    if len(start_anno) == 10:
                        dictionary.update({'anno_start': '-' + start_anno.replace("-", "")})
                    else:
                        dictionary.update({'anno_start': '-0' + start_anno.replace(" ", "")})
                    if len(end_anno) == 10:
                        dictionary.update({'anno_end': end_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_end': '-0' + end_anno.replace(" ", "")})
                else:
                    start_anno = string.replace(" ", "") + '01-01'
                    end_anno = string.replace(" ", "") + '-12-31'
                    dictionary.update({'anno_label': string.replace(" ", "") + ' a.C.'})
                    dictionary.update({'anno_uri': uri_cleaner(string).replace(" ", "") + 'a-c'})
                    if len(start_anno) == 10:
                        dictionary.update({'anno_start': start_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_start': '-0' + start_anno.replace(" ", "")})
                    if len(end_anno) == 10:
                        dictionary.update({'anno_end': end_anno.replace(" ", "")})
                    else:
                        dictionary.update({'anno_end': '-0' + end_anno.replace(" ", "")})
    return dictionary


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


def century_comparer(column_name):
    final_list = []
    secolo_start = {}
    new_dict = {}
    lista = process_data_tsv('wdt_query_results_folder/query_secoli.tsv')
    lista_di_secoli = column_name.split(";")
    for element in lista_di_secoli:
        if column_name != None:
            if column_name != '':
                if 'secolo' in element:
                    clean_string = sort_of_dicts_cleaner(element)
                    for dictionary in lista:
                        if dictionary['label'] != None:
                            if clean_string.lower() == dictionary['label'].lower():
                                new_dict.update({'item_secolo_wdt': dictionary['x']})
                                new_dict.update({'item_secolo_label': dictionary['label']})
                                nr = dictionary['label'].split(' ')
                                if 'a.c' in dictionary['label'].lower():
                                    secolo_start = '-' + str(romanToInt(nr[0]) * 100) + '-01-01'
                                    secolo_end = '-' + str(romanToInt(nr[0]) * 100 - 99) + '-12-31'
                                    if len(secolo_start) == 10:
                                        new_dict.update({'secolo_start': secolo_start})
                                    else:
                                        new_dict.update({'secolo_start': '0' + secolo_start})
                                    if len(secolo_end) == 10:
                                        new_dict.update({'secolo_end': secolo_end})
                                    else:
                                        new_dict.update({'secolo_end': '0' + secolo_end})
                                else:
                                    secolo_start = str(romanToInt(nr[0]) * 100 - 100) + '-01-01'
                                    secolo_end = str(romanToInt(nr[0]) * 100 - 1) + '-12-31'
                                    if len(secolo_start) == 10:
                                        new_dict.update({'secolo_start': secolo_start})
                                    else:
                                        new_dict.update({'secolo_start': '0' + secolo_start})
                                    if len(secolo_end) == 10:
                                        new_dict.update({'secolo_end': secolo_end})
                                    else:
                                        new_dict.update({'secolo_end': '0' + secolo_end})
                                stringa_uri = uri_cleaner(dictionary['label'])
                                if '-' in stringa_uri[len(stringa_uri) - 1]:  # per togliere lo spazio alla fine della stringa
                                    str2 = stringa_uri[:len(stringa_uri) - 1]
                                    new_dict.update({'item_secolo_uri': str2})
                                else:
                                    new_dict.update({'item_secolo_uri': stringa_uri})
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
                    dictionary.update(timespans_definer(year))
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
                    dictionary.update({'autore_label': lista4})
                    for ele in lista4:
                        lista_uri_autori.append(uri_cleaner(ele))
                    dictionary.update({'autore_uri': list(set(lista_uri_autori))})
                else:
                    dictionary.update({'autore_label': lista2[0]}) # pattern autore, titolo, anno
                    lista_uri_autori.append(uri_cleaner(lista2[0]))
                    dictionary.update({'autore_uri': list(set(lista_uri_autori))})

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
                if '(' in x or '(' in x:
                    year = x[x.find("(")+1:x.find(")")]
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
                            dizionario_finale.update({'autore_uri': authors_uri_list}) #ANCHE SE C'è UN SOLO ELEMENTO NELLA LISTA, FA UNA LISTA LO STESSO
                        except:
                            dizionario_finale.update({'autore_label': lista[0].replace("\'", '').replace("\"", "")})
                        if work != "":
                            dizionario_finale.update({'work_label': (work.replace("\'", '')).replace("\"", "").replace('(' + year + ')', "")})
                        else:
                            dizionario_finale.update({'work_label': (lista[1].replace("\'", '')).replace("\"", "").replace('(' + year + ')', "")})
                    if len(lista) > 2:
                        dizionario_finale.update({'subwork_label': (lista[2].replace("\'",'')).replace("\"","")})
                        if year != "":
                            dizionario_finale.update(timespans_definer(year)) # si perdono un po' di dati tipo versi etc, ma secondo me non ci interessa
                except:
                    print('AN ERROR OCCURRED IN CLEANING FONTI MEDIEVALI', row)
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

def post_dateTime_converter(row):
    string1 = row.replace('/', '-')
    string2 = string1.replace(' ', '-')
    return string2


################################################################################################################################################################
###########################################################################  KB HUCIT #########################################################################
################################################################################################################################################################

def cleaner_fonti_classiche(row):
    string, stri2, stri0 = str(), str(), str()
    new_list, lista1, lista2 = [], [], []
    lista_n_romani = [' X', 'II', ' I ', ' V ', 'III' 'VI', 'XV', 'VII', 'III', 'IV', 'IX', 'XI', 'IV', 'VIII', 'IX',
                      'IV']
    new_dict = {}
    if row != None:
        if row != '':
            if 'eneide' in row[0:6].lower():
                string = 'Virgilio, ' + row
            elif 'Odissea' in row[0:7]:
                string = 'Omero, ' + row
            else:
                string = row
            if ' - ' in string:
                lista1 = string.split(' - ')
            elif ';' in string:
                lista1 = string.split('; ')
            else:
                lista1.append(string)
            for element in lista1:
                if 'altre fonti su ' not in element.lower():
                    lista = element.split(', ')
                    if len(lista) > 1:
                        new_dict = {'author': lista[0]}
                        for n in lista_n_romani:
                            if n in lista[1]:
                                lista2 = lista[1].split(n)
                                stri = lista2[0].replace('X', '').replace('V', '').replace('VII', '')
                                if len(stri) > 1:
                                    if ' ' in stri[len(stri) - 1]:
                                        stri0 = stri[:len(stri) - 1]
                                    else:
                                        stri0 = stri
                                    if ' ' in stri0[0]:
                                        stri2 = stri0[1:]
                                    else:
                                        stri2 = stri0
                                new_dict.update({'work': stri2.replace(';', '')})
                        if 'work' not in new_dict:
                            stinghetta = lista[1].replace(n, '')
                            new_dict.update({'work': stinghetta.replace(';', '')})
                if 'author' in new_dict.keys():
                    new_list.append(new_dict)
    return new_list


def classiche_aggregator(row): #richiama la funzione precedente, è richiamata nel csv_creator
    new_list = []
    if '//' in row:
        l = row.split('// ')
        for el in l:
            lista_prov = []
            l2 = el.split(': ')
            lista_prov = cleaner_fonti_classiche(l2[1])
            for d in lista_prov:
                d.update({'categoria': uri_cleaner(l2[0].replace('Per ', ''))})
                new_list.append(d)
    else:
        new_list = cleaner_fonti_classiche(row)
    return new_list

def fonti_mediev_riscr_let_aggregator(row): #richiama la funzione precedente, è richiamata nel csv_creator
    new_list = []
    if '//' in row:
        l = row.split('// ')
        for el in l:
            lista_prov = []
            l2 = el.split(': ')
            lista_prov = fonti_medievali_moderne_riscr_let_cleaner(l2[1])
            for d in lista_prov:
                d.update({'categoria': uri_cleaner(l2[0].replace('Per ', ''))})
                new_list.append(d)
    else:
        new_list = fonti_medievali_moderne_riscr_let_cleaner(row)
    return new_list


def preparer_fonti_classiche(results):
    new_list, final_list = [], []
    for row in results:
        if row != []:
            if row['fonti_classiche'] != '':
                for dictionary in row['fonti_classiche']:
                    new_list.append(dictionary)
    for diz in new_list:
        if diz not in final_list:
            final_list.append(diz)
    return final_list

#preparer_fonti_classiche(results)


result_preparer_fonti_classiche = [{'author': 'Omero', 'work': 'Odissea', 'cts':'http://purl.org/hucit/kb/works/2816'},
                                   {'author': 'Omero', 'work': 'Iliade' , 'cts':'http://purl.org/hucit/kb/works/2815'},
                                   {'author': 'Publio Ovidio Nasone', 'work': 'Le Metamorfosi', 'cts':'http://purl.org/hucit/kb/works/1161'}, {'author': 'Ovidio', 'work': 'Metamorfosi' , 'cts':'http://purl.org/hucit/kb/works/1161'}, {'author': 'Publio Ovidio Nasone', 'work': 'Metamorfosi' , 'cts':'http://purl.org/hucit/kb/works/1161'}, {'author': 'Ovidio', 'work': 'Metamorfosi ' , 'cts':'http://purl.org/hucit/kb/works/1161'}, {'author': ' Ovidio', 'work': 'Metamorfosi', 'cts':'http://purl.org/hucit/kb/works/1161'},
                                   {'author': 'Ovidio', 'work': 'Fasti', 'cts':'http://purl.org/hucit/kb/works/1162'},
                                   {'author': 'Ovidio', 'work': 'Heroides (epistola', 'cts':'http://purl.org/hucit/kb/works/1157'}, {'author': 'Ovidio', 'work': 'Heroides', 'cts':'http://purl.org/hucit/kb/works/1157'}, {'author': 'Ovidio', 'work': 'Epistulae heroidum', 'cts':'http://purl.org/hucit/kb/works/1157'},
                                   {'author': 'Euripide', 'work': 'Medea', 'cts': 'http://purl.org/hucit/kb/works/2301'},
                                   {'author': 'Euripide', 'work': 'Reso', 'cts':'http://purl.org/hucit/kb/works/2304'}, {'author': 'Euripide', 'work': 'Reso ', 'cts':'http://purl.org/hucit/kb/works/2304'},
                                   {'author': 'Euripide', 'work': 'Le Fenicie', 'cts':'http://purl.org/hucit/kb/works/2303'},
                                   {'author': 'Seneca', 'work': 'Medea', 'cts':'http://purl.org/hucit/kb/works/2301'},
                                   {'author': 'Sofocle', 'work': 'Edipo a Colono', 'cts':'http://purl.org/hucit/kb/works/3899'},
                                   {'author': 'Sofocle', 'work': 'Antigone', 'cts': 'http://purl.org/hucit/kb/works/3897'} ,
                                   {'author': 'Sofocle', 'work': 'Edipo Re', 'cts':'http://purl.org/hucit/kb/works/3900'}, {'author': 'Sofocle', 'work': 'Edipo re ', 'cts':'http://purl.org/hucit/kb/works/3900'}, {'author': 'Sofocle', 'work': 'Edipo re ', 'cts':'http://purl.org/hucit/kb/works/3900'},
                                   {'author': 'Virgilio', 'work': 'Eneide', 'cts':'http://purl.org/hucit/kb/works/1413'}, {'author': 'Virgilio', 'work': 'Eneide 337-396', 'cts':'http://purl.org/hucit/kb/works/1413'}, {'author': ' Eneide II 721-724 "Detto così', 'work': 'distendo sulle larghe spalle e sul collo reclino una coperta', 'cts': 'http://purl.org/hucit/kb/works/1413'},
                                   {'author': 'Pseudo-Apollodoro', 'work': 'Biblioteca', 'cts': 'http://purl.org/hucit/kb/works/9087'}, {'author': 'Apollodoro', 'work': 'Biblioteca', 'cts':'http://purl.org/hucit/kb/works/9087'}, {'author': 'Apollodoro', 'work': 'Biblioteca I', 'cts':'http://purl.org/hucit/kb/works/9087'},
                                   {'author': 'Igino', 'work': 'Fabulae', 'cts':'http://purl.org/hucit/kb/works/1067'},
                                   {'author': 'Quinto Smirneo', 'work': 'Posthomerica', 'cts':'http://purl.org/hucit/kb/works/3852'}, {'author': 'Quinto Smirneo', 'work': 'Posthomerica', 'cts':'http://purl.org/hucit/kb/works/3852'},
                                   {'author': 'Silio Italico', 'work': 'Punica', 'cts':'http://purl.org/hucit/kb/works/1310'},
                                   {'author': 'Venere descrive Didone; Eneide IV 584-705; Ovidio', 'work': 'Epistulae heroidum Ovidio', 'cts': 'http://purl.org/hucit/kb/works/1157'},
                                   {'author': 'Apollonio Rodio', 'work': 'Le argonautiche I', 'cts':'http://purl.org/hucit/kb/works/1557'}, {'author': 'Apollonio Rodio', 'work': 'Le argonautiche', 'cts':'http://purl.org/hucit/kb/works/1557'},
                                   {'author': 'Erodoto', 'work': 'Storie', 'cts':'http://purl.org/hucit/kb/works/2691'}]


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
            dizionario_finale.update({'post_autore_uri': uri_cleaner(row['wp_post_author'])})
            dizionario_finale.update({'post_autore_label': row['wp_post_author']})
            dizionario_finale.update({'post_data': post_dateTime_converter(row['wp_post_date'])})
            dizionario_finale.update({'item_titolo': row['wp_post_title']})
            dizionario_finale.update({'item_autore': lista_fonti_per_autore(row['cf_Autore'])})
            dizionario_finale.update({'item_descrizione': row['cf_descrizione']})

            if row['cf_Data']:
                dizionario_finale.update({'item_data': timespans_definer(row['cf_Data'])})

            if row['cf_periodo'] != '':
                dizionario_finale.update({'item_periodo': sort_of_dicts_cleaner(uri_periodo_cleaner(row['cf_periodo']))})
                dizionario_finale.update({'item_periodo_wdt': wdt_periodo(sort_of_dicts_cleaner(row['cf_periodo']))})
                dizionario_finale.update({'item_periodo_label': sort_of_dicts_cleaner(row['cf_periodo'])})

            if row['cf_secolo'] != '':
                if row['cf_secolo'] != None:
                    dizionario_finale.update({'item_secolo': century_comparer(row['cf_secolo'])})

            if row['cf_tipologia_del_manufatto'] != '':
                dizionario_finale.update({'item_tipologia': sort_of_dicts_cleaner(uri_periodo_cleaner(row['cf_tipologia_del_manufatto']))})
                dizionario_finale.update({'item_tipologia_wdt': wdt_periodo(sort_of_dicts_cleaner(row['cf_tipologia_del_manufatto']))})
                dizionario_finale.update({'item_tipologia_label': sort_of_dicts_cleaner(row['cf_tipologia_del_manufatto'])})

            dizionario_finale.update({'item_collocazione_label': collocation_cleaner(row['cf_Collocazione'])})
            if dizionario_finale['item_collocazione_label'] != None:
                if dizionario_finale['item_collocazione_label'] != '':
                    dizionario_finale.update({'item_collocazione_uri': uri_cleaner(dizionario_finale['item_collocazione_label'])})

            dizionario_finale.update({'item_citta_label': collocation_city_cleaner(row['cf_Collocazione'])})
            if dizionario_finale['item_collocazione_label'] != None:
                dizionario_finale.update({'item_citta_uri': uri_cleaner(dizionario_finale['item_citta_label'])})

            dizionario_finale.update({'item_note': (row['cf_note']).replace('\"', "")})

            fonti_classiche = classiche_aggregator(row['cf_fonti_letterarie'])
            if fonti_classiche != []:
                dizionario_finale.update({'fonti_classiche': fonti_classiche})
            else:
                dizionario_finale.update({'fonti_classiche': ''})
            if row['cf_fonti_letterarie']:
                dizionario_finale.update({'fonti_classiche_orig': row['cf_fonti_letterarie']})
            else:
                dizionario_finale.update({'fonti_classiche_orig': ""})
            lista_riscr_lett = fonti_mediev_riscr_let_aggregator(row['cf_riscritture_letterarie'])
            if len(lista_riscr_lett) > 0:
                if lista_riscr_lett != [{}]:
                    dizionario_finale.update({'riscritture_letterarie': lista_riscr_lett})
            else:
                dizionario_finale.update({'riscritture_letterarie': ""})
            lista_fonti_mediev = fonti_mediev_riscr_let_aggregator(row['cf_fonti_medievali_e_moderne'])
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

            dizionario_finale.update({'categoria' : new_category_cleaner(row['tx_category'])}) #RIVEDIIIII lista o stringa a seconda del n' delle categorie
            dizionario_finale.update({'item_link_esterno': row['cf_collegamento_link_esterno']})
            dizionario_finale.update({'keywords': keywords_cleaner(row['tx_post_tag'])}) # fa delle liste a caso boh

            if row['fi_thumbnail'] != None:
                dizionario_finale.update({'immagine_url': row['fi_thumbnail']})
        lista_finale.append(dizionario_finale)
    return lista_finale


def csv_writer(final_list_of_dicts):
    df = pd.DataFrame(final_list_of_dicts, columns=["item_id", 'post_autore_uri', 'post_autore_label', 'post_data', 'item_titolo', 'item_autore', 'item_descrizione',
                                                    'item_data', 'item_periodo', 'item_periodo_wdt', 'item_periodo_label', 'item_secolo',
                                                    'item_tipologia','item_tipologia_wdt', 'item_tipologia_label', 'item_note'
                                                    'item_collocazione_label', 'item_collocazione_uri', 'item_citta_uri', 'item_citta_label',
                                                    'anno_film','autore_film', 'titolo_film', 'categoria',
                                                    'item_link_esterno', 'fonti_classiche', "fonti_classiche_orig", "fonti_medievali_e_moderne",
                                                    "riscritture_letterarie", "riscritture_cinematografiche", 'keywords', 'immagine_url'])
    df.to_csv('discarica/tsv_intermedio_17-09.tsv', index=False, sep="\t", encoding='utf-8') #dovrei trovare il modo per mettere delimiter e formato


def csv_intermedio(dataset_url):
    final_list = []
    data = process_data(dataset_url) #devo trovare il modo di togliere \t e spazi
    for row in data:
        if row.get('wp_post_type') != None:
            if 'post' in row.get('wp_post_type'): #solo se lo status del post è quello di post e non di revisione
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
                new_dict.update({'cf_Data' : row['cf_Data']})
                new_dict.update({'cf_secolo': row['cf_secolo']})
                new_dict.update({'cf_periodo' : row['cf_periodo']})
                new_dict.update({'cf_tipologia_del_manufatto' : row['cf_tipologia_del_manufatto']})
                new_dict.update({'cf_collegamento_link_esterno' : row['cf_collegamento_link_esterno']})
                new_dict.update({'cf_fonti_letterarie' : row['cf_fonti_letterarie']})
                new_dict.update({'cf_descrizione' : row['cf_descrizione']}) #fatto
                new_dict.update({'cf_fonti_medievali_e_moderne' : row['cf_fonti_medievali_e_moderne']})
                new_dict.update({'cf_riscritture_letterarie': row['cf_riscritture_letterarie']})
                new_dict.update({'cf_riscritture_cinematografiche' : row['cf_riscritture_cinematografiche']})
                new_dict.update({'fi_thumbnail' : row['fi_thumbnail']})
                if new_dict != {}:
                    final_list.append(new_dict)
    #for x in final_list:
        #for k,v in x.items():
            #if k == 'cf_riscritture_letterarie' or k == 'cf_fonti_letterarie' or k == 'cf_fonti_medievali_e_moderne':
                #if '//' in v:
                    #print('r', x)
    return final_list



def printer(data):
    for x in data:
        print(x)


csv_writer(csv_creation(csv_intermedio(big_url))) # per stampare il tsv intermedio

#printer(item_author_list(csv_intermedio(big_url)))
#wikidata_queries(item_author_list(csv_intermedio(big_url)))
#lista_fonti_per_autore(utf8_encoding(process_data('Toyset_Mythologiae.tsv')), 'Fonti letterarie classiche')
#utf8_encoding(process_data('Toyset_Mythologiae.tsv'))









