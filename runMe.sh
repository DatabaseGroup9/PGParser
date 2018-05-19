./fetchFiles.sh
./install.sh
stepValue=500
for i in {0..37500..500}
	do
		echo "Clearing files."
		> data/headers.txt 
		> data/authors.csv
		> data/wrote.csv
		> data/books.csv
		> data/mentioned.csv
		> data/cities.csv
		> data/log.txt
		echo "Taking $stepValue books, starting from $i"
		python3 PGParser.py --skip $i --take $stepValue #> data/log.txt 2> data/err.txt
		./printHeadersAndZip.sh
		echo "Zipping: "
		zip -j data/data$i-$stepValue.zip data/headers.txt data/authors.csv data/wrote.csv data/books.csv data/mentioned.csv data/cities.csv data/log.txt
	done

