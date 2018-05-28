# PGParser
This is a Virtual Machine, that fetches the ~5GB downloaded Project Gutenberg book files and parses them to .csv.


### Steps:
1. Clone the repository PGParser.
2. Git Bash in PGParser directory: <br>
 sudo chmod 700 *<br>
2. execute "./runMe.sh > outerLog.txt 2>&1 &"<br>

The script runs for several hours and when completed the extracted datat saved in approximately 76 zip archives.
All output is logged in outerLog.txt

We then concatenate the files into one csv-file an upload to our [GitHub import repository](https://github.com/DatabaseGroup9/dataimport/tree/master/data).

to fetch the finished CSVs from the server, scp root@178.62.239.18:~/tmp/other/PGParser_proper/PGParser/data/data*.zip .
Usually however, formatting is done on the PGParser droplet, with the files in ./formatdata

This results in duplicate cities and authors, which will have to be cleaned up later in the process.

#### The parser script

[PGParser.py](https://github.com/DatabaseGroup9/PGParser/blob/master/PGParser.py) is the script that extracts the booktiltes, authors, cities and number of cities mentions in a book.

We have used the strategy to identify Capitalized text and running them through the python library Geotext to deterind if it's a city or not. This saves some time over running the entire corpus through geotext


## Instructions for old version:
### Steps:
1. Clone the repository PGParser.
2. Get the IP address 178.62.99.117.
3. Git Bash in PGParser directory: <br>
`./ fetch Files.sh [ip_address]` <br>
_This downloads archives.tar and zipfilelinks.txt_
4. Download rdm archives from Gutenberg and unzips it. (5G disk space)
5. Run Python script: <br>
`docker build -t pgparser` <br>
`docker run -v $PWD/../:/data/ -it pgparser`

> Docker container runs parserarchive.py first there deriveCSV.py here we could have different python scripts for the different databases. 

### FILES:
- _parserarchive.py_ - extracts the cities into ine csv file(books.csv, mentions.csv)
- _derivecsv.py_ - creates the other csv files to  be used for imports stuff
