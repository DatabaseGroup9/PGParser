echo 'Copying zipFileLinks.txt:';
scp root@$1:/root/zipfileLinks.txt zipfileLinks.txt;
echo 'Finished.\nCopying archive.tar:';
scp root@$1:/root/archive.tar archive.tar;
echo 'unzipping archive.tar'
unzip -n archive.tar
echo 'done fetching book data.';

echo 'Downloading RDF/XML files from Project Gutenberg...';
wget'https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.zip'
echo 'Unzipping RDF files...'
unzip -n rdf-files.tar.zip | tar -xvf rdf-files.tar --directory rdf-files
echo 'Done fetching RDF files!'

echo 'Downloading city locations from geobytes.com...'
wget http://www.geobytes.com/GeoWorldMap.zip
echo 'Unzipping city locations...'
unzip -j -n GeoWorldMap.zip
echo 'done fetching location data!'


