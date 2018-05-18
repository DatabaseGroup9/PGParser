#!/bin/env python
import re, io, os, csv, zipfile, codecs, subprocess, rdflib, logging, nltk, re, pprint
from collections import Counter
from shutil import copy
from geotext import GeoText
from nltk import word_tokenize, sent_tokenize

import argparse, sys

parser=argparse.ArgumentParser()

parser.add_argument('--skip', help='How many books to skip? [positive int]')
parser.add_argument('--take', help='How many books to parse, starting from --skip? [positive int]')
__arguments=parser.parse_args()

# nltk.download('words')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')

ARCHIVES_PATH = 'data/archive.full/root/zipfiles'
RDF_PATH = 'data/rdf-files/cache/epub/'
IS_DEBUG = False
USE_GEOTEXT = 'GEOTEXT'
USE_NLTK = 'NLTK'

AUTHORS_CSV = 'data/authors.csv'
WROTE_CSV = 'data/wrote.csv'
BOOKS_CSV = 'data/books.csv'
MENTIONED_CSV = 'data/mentioned.csv'
CITIES_CSV = 'data/cities.csv'

GEOCITIES_CSV = 'data/cities1000.txt'



__books = {}
__cities = {}
__authors = {}
__authorsCount = 0
__wrotes = {}
__mentioneds = {}

WHICH_PARSER = USE_GEOTEXT

#Book class. Contains metadata, full text and list of cities when populated.
class PGAuthor:
    def __init__(self, name):
        self.authorID = -1
        self.fullName = name
        self.title = ''
        self.firstName = ''
        self.surname = ''
        self.parseName()
        
    def parseName(self):
        if ',' in self.fullName:
            names = self.fullName.split(',', 1)
            self.firstName = names[1].strip()
            self.surName = names[0].strip()
            
            if ',' in names[1]:
                names = names[1].split(',', 1)
                self.title = names[1].strip()
                self.firstName = names[0].strip()
        else:
            names = self.fullName.split(' ', 1)
            self.firstName = names[0].strip()
            self.surName = names[1].strip()
    
    def getKey(self):
        return self.firstName + "" + self.surName

    def __str__(self):
        return str(self.authorID) + '\n\t' + self.fullName + ' --> ' + self.firstName + ' ' + self.surName + ' ' + self.title 
        
        
class PGCity:
    def __init__(self, cityID, name, lat, lon):
        self.cityID = cityID
        self.name = name
        self.lat = lat
        self.lon = lon
    
    def getKey(self):
        return self.cityID
    
    def __str__(self):
        return self.cityID + '\n\t' + self.name + '\n\t' + str(self.lat) + ", " + str(self.lon)

class PGMentioned:
    def __init__(self, bookID, cityID, count):
        self.bookID = bookID
        self.cityID = cityID
        self.count = count
        #self.shortString = shortString
    
    def getKey(self):
        return self.bookID + "" + self.cityID
    
    def __str__(self):
        return "m: " + str(self.bookID) + ", " + str(self.cityID) + "\t(count: " + str(self.count) + ")"
        
class PGWrote:
    def __init__(self, authorID, bookID):
        self.authorID = authorID
        self.bookID = bookID
    
    def getKey(self):
        return str(self.authorID) + "" + self.bookID
    
    def __str__(self):
        return str(self.authorID) + '\t' + self.bookID 
    
class PGBook:
    def __init__(self, bookID):
        self.bookID = bookID
        self.title = 'N/A'
        self.bookText = 'N/A'

    def prettyPrint(self):
        print(self)

    def getKey(self):
        return self.bookID
        
    def __str__(self):
        return self.bookID + '\n\t' + self.title + '\n' 


        
def traverseArchive():
    errorCount = 0
    folderPath = ARCHIVES_PATH
    
    for fileName in handleSkipTake(os.listdir(folderPath)):
        zipFilePath = folderPath + '/' + fileName
        with zipfile.ZipFile(zipFilePath, 'r') as archive:
            for innerFileName in archive.namelist():
                if innerFileName.endswith('.txt'):
                    print(innerFileName)
                    bookID = os.path.splitext(innerFileName)[0]
                    error = False
                    try:
                        #archive.testzip()
                        #parseText(codecs.encode(archive.read(innerFileName), 'utf-8'))
                        myBook = unzipAndParse(zipFilePath, innerFileName)
                        addBook(myBook)
                        
                    except NotImplementedError:
                        print("NotImplementedError. Possibly wrong compression, Trying System call")
                        #unzipAndParse(zipFilePath ,innerFileName)
                        error = True
                        errorCount += 1
                    except IndexError:
                        print('Unexpected first line.')
                        error = True
                        errorCount += 1
                    
                    if error:
                        copy(zipFilePath, "data/failed/" + fileName)
                        
    print(str(errorCount) + ' archives could not be opened.')

def handleSkipTake(list):
    skip = int(__arguments.skip)
    take = int(__arguments.take)
    
    if int(__arguments.skip) > 0:
        list = list[skip:]
        
    if take > 0:
        list = list[:take]
    
    
    return list
    
def unzipAndParse(filePath, innerFile):
    bookID = os.path.splitext(innerFile)[0]
    myBook = PGBook(bookID)
    myBook = getMetadataFromRDF(myBook)
    myBook.bookText = str(subprocess.check_output(['unzip', '-p', filePath, innerFile]))
    myBook = removeHeader(myBook)
    print(myBook.title)
    parseCities(myBook)
    myBook.prettyPrint()
    return myBook

        
        
def getMetadataFromRDF(book):
    if not isinstance(book, PGBook):
        raise TypeError('Argument(book) must be an instance of PGBook!')

    fileName = RDF_PATH + str(book.bookID) + '/pg' + str(book.bookID) + '.rdf'
    g = rdflib.Graph()

    try: #RDF file may not exist
        g.parse(fileName)
    except IOError:
        print('RDF archive for ' + book.bookID + ' not found. Has the whole archive been correctly decompressed?')
        print('Trying to parse metadata directly from book Text')
        #return tryParseMetadata(book)
    
    #DO WE HAVE A BIRTHDAY TO SEPARATE AUTHORS BY?
    

    for s, p, o in g:
        printFlag = False

        if '/pgterms/name' in str(p):
            author = addAuthor(PGAuthor(str(o)))
            print(author)
            
            addWrote(author.authorID, book.bookID)

        elif '/dc/terms/title' in str(p):
            book.title = str(o)

    return book

def removeHeader(book):
    #TODO IMPLEMENT HEADER REMOVAL?
    return book
    
    
def parseCities(book):
    if WHICH_PARSER == USE_GEOTEXT:
        return parseCitiesGeoText(book)
    if WHICH_PARSER == USE_NLTK:
        return parseCitiesNLTK(book)
    
def parseCitiesGeoText(book):
    global __cities
    global __mentioneds
    
    counter = Counter(GeoText(book.bookText).cities)
    for cityName in counter:
        count = counter[cityName]
        geoCity = pgCityFromFile(cityName)
        
        if not geoCity is None and len(cityName) > 3:
            addCity(book, geoCity, count)
            

def addCity(book, geoCity, count):
    mentioned = PGMentioned(book.bookID, geoCity.cityID, count)
    __mentioneds[mentioned.getKey()] = mentioned
    __cities[geoCity.getKey()] = geoCity
    
def parseCitiesNLTK(book):
    if not isinstance(book, PGBook):
        raise TypeError('Argument(book) must be an instance of PGBook!')
        
    if book.title == 'N/A' or book.bookText == 'N/A':
        raise AttributeError('Title and bookText must be filled out!')
        
    tokens = word_tokenize(book.bookText)
    sentences = sent_tokenize(book.bookText)
    
    tree = [nltk.ne_chunk(tSentence) for tSentence in ie_preprocess(book.bookText)]
    
    getPlacesFromTree(tree)
    
    #for token in filter(lambda s: s.istitle(), tokens):
        #print(token)
        
    return book
    
    
def getPlacesFromTree(tree):
    for subtree in tree:
        for t in subtree.subtrees():
            if t.label() == 'NE':
                for u in t:
                    print(u)

                    
def pgCityFromFile(cityName):
    
    for city in __geoCities:
        if city['name'] == cityName or city['asciiname'] == cityName:
            return PGCity(city['geonameid'], city['name'], city['latitude'], city['longitude'])
    
    return None

                    
#BORROWED FROM https://www.nltk.org/book/ch07.html
def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def addBook(book):
    if not isinstance(book, PGBook):
        raise TypeError('Argument(book) must be an instance of PGAuthor!')
    
    global __books
    
    __books[book.getKey()] = book
    
    
    
def addAuthor(author):
    if not isinstance(author, PGAuthor):
        raise TypeError('Argument(book) must be an instance of PGAuthor!')
    
    global __authors
    global __authorsCount
    
    
    if not author.getKey() in __authors:
        __authorsCount += 1
        author.authorID = __authorsCount
        __authors[author.getKey()] = author
    else:
    
        author.authorID = __authors[author.getKey()].authorID
    
    return author
  
def addWrote(authorID, bookID):
    global __wrotes
    
    wrote = PGWrote(authorID, bookID)
    __wrotes[wrote.getKey()] = wrote
  
def getGeoCities():
    with open(GEOCITIES_CSV, 'rt', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', fieldnames=['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude','longitude', 'feature class', 'feature code', 'country code', 'cc2', 'admin1 code', 'admin2code', 'admin3 code', 'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date'])
        
        return sorted(list(reader), key=lambda row: int(row['population']), reverse=True)

        
def exportAll():
    exportCSVs()
    #exportCSV(BOOKS_CSV, sorted(__books, key=lambda k: __books[k].bookID), ['bookID', 'title'])
    
    #exportCSV(MENTIONED_CSV, sorted(__mentioneds ), ['bookID', 'cityID', 'count'])
    
    #exportCSV(CITIES_CSV, sorted(__cities, key=lambda k: int(__cities[k].cityID)), ['cityID', 'name', 'lat', 'lon'])
    
    #exportCSV(AUTHORS_CSV, sorted(__books, key=lambda k: __books[k].bookID), ['authorID', 'fullName', 'firstName', 'surName', 'title'])
    
    #exportCSV(WROTE_CSV, sorted(__books, key=lambda k: __books[k].bookID), ['authorID', 'bookID'])
    
    
    
##Would be nice if this could be generic   
# def exportCSV(filename, myDict, fieldNames):
    # with open(filename, 'w', newline='') as csvfile:
        # writer = csv.writer(csvfile, delimiter=',')
        # writer.writerow(fieldNames)
        
        # for key in myDict:
            # item = myDict[key]
            # writer.writerow([item.__dict__[field] for field in fieldNames])
        
def escapeEncode(list):
	return [str(val).encode('unicode_escape').decode('ASCII') for val in list]
		
def exportCSVs():
    with open(BOOKS_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['bookID', 'title'])
        for key in sorted(__books, key=lambda k: __books[k].bookID):
            book = __books[key]
            writer.writerow(escapeEncode([book.bookID, book.title]))
        
    with open(MENTIONED_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['bookID', 'cityID', 'count'])
        for key in sorted(__mentioneds ):
            mentioned = __mentioneds[key]
            writer.writerow(escapeEncode([mentioned.bookID, mentioned.cityID, mentioned.count]))
            
    with open(CITIES_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['cityID', 'name', 'lat', 'lon'])
        for key in sorted(__cities, key=lambda k: int(__cities[k].cityID)):
            city = __cities[key]
            writer.writerow(escapeEncode([city.cityID, city.name, city.lat, city.lon]))
    
    with open(AUTHORS_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['authorID', 'fullName', 'firstName', 'surName', 'title'])
        for key in sorted(__authors, key=lambda k: __authors[k].authorID):
            author = __authors[key]
            writer.writerow(escapeEncode([author.authorID, author.fullName, author.firstName, author.surName, author.title]))
            
    with open(WROTE_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['authorID', 'bookID'])
        for key in sorted(__wrotes, key=lambda k: (__wrotes[k].authorID, __wrotes[k].bookID)):
            wrote = __wrotes[key]
            writer.writerow(escapeEncode([wrote.authorID, wrote.bookID]))
    
    # for mention in sorted(__mentioneds ):
        # print(__mentioneds[mention])

    # for city in sorted(__cities, key=lambda k: int(__cities[k].cityID)):
        # print(__cities[city])
        
    # for author in sorted(__authors, key=lambda k: __authors[k].authorID):
        # print(__authors[author])
        
    # for wrote in sorted(__wrotes, key=lambda k: (__wrotes[k].authorID, __wrotes[k].bookID)):
        # print(__wrotes[wrote])
        
    # for book in sorted(__books, key=lambda k: __books[k].bookID):
        # print(__books[book])
        

        

#Populating list of cities
__geoCities = getGeoCities()        


##Main program      
traverseArchive()

exportAll()
