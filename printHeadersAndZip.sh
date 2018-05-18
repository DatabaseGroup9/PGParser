cd data
fileList="authors.csv wrote.csv books.csv mentioned.csv cities.csv"
 > headers.txt
for i in ${fileList}; do
	head -v -n 1 "$i" >> headers.txt;
	{ echo -n "Entries: ";  tail -n +2 "$i" | wc -l; } >> headers.txt;
	echo "" | tail -f >> headers.txt;
done
cat headers.txt
echo "Zipping: "
zip data.zip headers.txt authors.csv wrote.csv books.csv mentioned.csv cities.csv
cd ..
