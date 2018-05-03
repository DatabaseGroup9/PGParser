import csv

#import filenames
BOOKS_CSV = 'books.csv'
MENTIONS_CSV = 'mentions.csv'

#export filenames. 
#	authors.csv is a list of all the distinct author names found in books.csv
#	cities.csv is a list of all the distinct city names found in mentions.csv
CITIES_CSV = 'cities.csv'
AUTHORS_CSV = 'authors.csv'

PRINT_DIV = 20000

def exportCities():
	cities = set()
	progress = 0

	with open(MENTIONS_CSV) as mentionsFile:
		reader = csv.DictReader(mentionsFile)
		for row in reader:
			cities.add(row['city'].title())

			progress += 1
			printProgress(progress)

	citiesList = list(cities)
	print(citiesList)

	id = 0

	with open(CITIES_CSV, 'w') as citiesFile:
		w = csv.writer(citiesFile)
		w.writerow(['cityID', 'name'])
		for city in citiesList:
                        w.writerow([id, city])
			id += 1

	print(str(len(citiesList)) + ' records exported to ' + CITIES_CSV + ', out of ' + str(progress) + ' total lines.\n') 


def printProgress(progress):
	if progress % PRINT_DIV == 0:
		print 'Processed ' + str(progress) + ' records.\t\t\t\r',

def getSetFromCSVColumn(fileName, column):
	mySet = set()
	progress = 0

	with open(fileName) as csvFile:
                reader = csv.DictReader(csvFile)
                for row in reader:
                        mySet.add(row[column].title())

                        progress += 1
                        printProgress(progress)
	return mySet



def exportAuthors():
	authors = getSetFromCSVColumn(BOOKS_CSV, 'author')
        
        authorsList = list(authors)
        print(authorsList)
	
	id = 0

        with open(AUTHORS_CSV, 'w') as authorsFile:
                w = csv.writer(authorsFile)
		w.writerow(['authorID', 'name'])
                for name in authorsList:
			w.writerow([id, name])
			id += 1

        print(str(len(authorsList)) + ' records exported to ' + AUTHORS_CSV + '\n')



print('Exporting authors!\n')
exportAuthors()
print('Exporting cities!\n')
exportCities()

