cd data
for i in *.csv; do
	head -v -n 1 "$i";
	echo ""
done
cd ..
