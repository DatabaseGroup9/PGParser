#!/bin/env python
import re, io, os, csv, zipfile, codecs, subprocess, rdflib, logging
from geotext import GeoText
from collections import namedtuple

ARCHIVES_PATH = 'archive/root/zipfiles'
IS_DEBUG = False
USE_GEOTEXT = 'GEOTEXT'
USE_SPACY = 'SPACY'
BOOKS_CSV = 'books.csv'
CITIES_CSV = 'mentions.csv'

#Book class. Contains metadata, full text and list of cities when populated.
class PGBook:
	def __init__(self, bookID):
		self.bookID = bookID
		self.author = 'N/A'
		self.title = 'N/A'
		self.bookText = 'N/A'
		self.cities = []

	def prettyPrint(self):
		print(self.bookID)
		print('\t' + self.author)
		print('\t' + self.title)
		print(self.cities)
		print('-:_:-:-:_:-:-:_:-:-:_:-')

	def __str__(self):
		return str(self.bookID) + ': ' + str(self.title) + ', by ' + str(self.author)  + ".\ncities: " +  str(self.cities) 

#A named tuple for transport of CSV file pointers
FileTuple = namedtuple('FileTuple', ['books', 'cities'])


def traverseArchive(fileTuple):
	errorCount = 3000
	folderPath = 'archive/root/zipfiles'
	for fileName in os.listdir(folderPath):
		zipFilePath = folderPath + '/' + fileName
		with zipfile.ZipFile(zipFilePath, 'r') as archive:
			for innerFileName in archive.namelist():
				if innerFileName.endswith('.txt'):
					print(innerFileName)
					bookID = os.path.splitext(innerFileName)[0]
					try:
						#archive.testzip()
						#parseText(codecs.encode(archive.read(innerFileName), 'utf-8'))
						myBook = unzipAndParse(zipFilePath, innerFileName)
						appendCSV(myBook, fileTuple)
					except NotImplementedError:
						print("NotImplementedError. Possibly wrong compression, Trying System call")
						#unzipAndParse(zipFilePath ,innerFileName)
						errorCount += 1
					except IndexError:
						print('Unexpected first line.')
						errorCount += 10000
	print(str(errorCount) + ' archives could not be opened.')


def unzipAndParse(filePath, innerFile):
	bookID = os.path.splitext(innerFile)[0]
	myBook = PGBook(bookID)
	myBook.bookText = subprocess.check_output(['unzip', '-p', filePath, innerFile])
	myBook.cities = parseCities(myBook.bookText)
	myBook = getMetadataFromRDF(myBook)
	myBook.prettyPrint()
	return myBook
	#print(str(myBook))
	#parseText(bookID, subprocess.check_output(['unzip', '-p', filePath, innerFile]))


def tryParseMetadata(book):
	book.author = parseAuthor(book.bookText)
	book.title = parseTitle(book.bookText)
	return book


#DEPRECATED
def parseText(bookID, bookText):
	author = ''
	title = ''
	try:
		author = parseAuthor(bookText)
		title = parseTitle(bookText)
	except IndexError:
		print("Could not extract metadata from text...")

	printBookInfo(author, title, parseCities(bookText))


#DEPRECATED.
def parseAuthor(bookText):
	authorTitle = bookText.split('\n')[0].split(' of ', 1)[1]
	return authorTitle.split(', by ')[0]


#DEPRECATED.
def parseTitle(bookText):
	authorTitle = bookText.split('\n')[0].split(' of ', 1)[1]
	return authorTitle.split(', by ')[1]


#DEPRECATED
def printBookInfo(author, title, cities):
	print('\n' + author + " - " + title)
        print(cities)
        print('\n\n')


def parseCities(bookText, method=USE_SPACY):
	if method == USE_GEOTEXT:
		return parseCitiesGeoText(bookText)
	elif method == USE_SPACY:
		return parseCitiesGeoText(bookText)
	else:
		raise NotImplementedError('No such parsing method found')


def parseCitiesGeoText(bookText):
	return GeoText(bookText).cities


#NOT IMPLEMENTED
def parseCitiesSpacy():
	raise NotImplementedError('This function has not been implemented.')


def getMetadataFromRDF(book):
	if not isinstance(book, PGBook):
		raise TypeError('Argument(book) must be an instance of PGBook!')

	fileName = 'rdf-files/cache/epub/' + str(book.bookID) + '/pg' + str(book.bookID) + '.rdf'
	g = rdflib.Graph()
	
	try: #RDF file may not exist
		g.parse(fileName)
	except IOError:
		print('RDF archive for ' + book.bookID + ' not found. Has the whole archive been correctly decompressed?')
		print('Trying to parse metadata directly from book Text')
		return tryParseMetadata(book)


	for s, p, o in g:
		printFlag = False

		if '/pgterms/name' in p.encode('utf-8'):
			book.author = o.encode('utf-8')
			printFlag = True
		elif '/dc/terms/title' in str(p.encode('utf-8')):
			book.title = o.encode('utf-8')
			printFlag = True
			print(o.encode('utf-8'))

		if printFlag and IS_DEBUG and False:
			print('s: ' + s.encode('utf-8') + '\np:\t' + p.encode('utf-8') + '\no:\t\t' + o.encode('utf-8'))

	return book



def initCSV():
	bookHeader = ['bookID', 'author', 'title']
        with open(BOOKS_CSV, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(bookHeader)

	cityHeader = ['bookID', 'city']
        with open(CITIES_CSV, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(cityHeader)


def appendCSV(book, fileTuple):
	if not isinstance(book, PGBook):
                raise TypeError('Argument(book) must be an instance of PGBook!')

	bookFields = [book.bookID, book.author, book.title]
	bWriter = csv.writer(fileTuple.books)
	bWriter.writerow(bookFields)

	for city in book.cities:
		cityFields = [book.bookID, city]
        cWriter = csv.writer(fileTuple.cities)
		cWriter.writerow(cityFields)



#Start going over files:
initCSV()

with open(BOOKS_CSV, 'a') as booksFile, open(CITIES_CSV, 'a') as citiesFile:
	fileTuple = FileTuple(booksFile, citiesFile)
	traverseArchive(fileTuple)

#myBook = PGBook(1644)
#print(str(myBook))
#myBook = getMetadataFromRDF(PGBook(1644))
#print(str(myBook))

