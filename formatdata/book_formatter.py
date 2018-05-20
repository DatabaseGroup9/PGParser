# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
import csv
import re


def main():


	inputfile = sys.argv[1]
	tempfile = "./tmp.csv"
	finalfile = sys.argv[3]

	w= open(tempfile,"w+")
	print(tempfile)
	with open(inputfile) as f:
		read_data = f.read()
		read_data = read_data.strip()
		replaced = "|".join(read_data.split("\\n"))
		replaced = "|".join(replaced.split("\\r"))
		replaced = "".join(replaced.split(u"\u2014"))
		replaced = "|".join(replaced.split("||"))
		#replaced = re.sub('||', '|', replaced)

		#replaced = re.sub('[A-Z]','|', read_data)

		w.write(replaced)
	w.close()
	f.closed
	o= open(finalfile,"w+")
	 
	import csv
	i = 0
	with open(tempfile, 'r') as reader:
		read = csv.reader(reader)
		
		for row in read :
			if i == 0:
				print (row[1])
				o.write (', '.join(row)+",short_title"+"\n") 
			if i>0:
				#print(row[1]) 
				row[1] = row[1].replace("\\u2014", "-") # hexadecimal
				row[1] = row[1].replace("\\xc9", "É") # hexadecimal 
				row[1] = row[1].replace("\\xe7", "ç") # hexadecimal
				row[1] = row[1].replace("\\xe9", "é") # hexadecimal 
				row[1] = row[1].replace("\\xeb", "ë") # hexadecimal 
				row[1] = row[1].replace("\\xf3", "ó") # hexadecimal 
				row[1] = row[1].replace("\\xe1", "á") # hexadecimal 
				
				row[1] = row[1].replace("\\xf8", "ø") # hexadecimal 
				row[1] = row[1].replace("\\u017", "ž") # hexadecimal
				row[1] = row[1].replace("\\u0301", "́́`") # hexadecimal
				row[1] = row[1].replace("\\u0142", "ł") # hexadecimal
				row[1] = row[1].replace("\\xed", "í") # hexadecimal
				
				row[1] = row[1].replace("\\xe8", "è") # hexadecimal 
				row[1] = row[1].replace("\\xfc", "ü") # hexadecimal 
				row[1] = row[1].replace("\\xde", "Þ") # 	Þ
				row[1] = row[1].replace("\\xe3", "ã") # hexadecimal
				row[1] = row[1].replace("\\xf6", "a") # hexadecimal
				row[1] = row[1].replace("\\xef", "ï") # hexadecimal   
				row[1] = row[1].replace("\\u0100", "Ā") # hexadecimal 
				row[1] = row[1].replace("\\xf1", "ñ") # hexadecimal
				row[1] = row[1].replace("\\xc1", "Á") # hexadecimal
				a = row[1].split('|')
				#print(row[1])
				#print (a[0])
				str1 = ', '.join(row)+","+a[0]+"\n"
				str1 = bytearray(str1, 'UTF-8').decode('latin-1')
				print(str1)
				o.write (str1) 

			i += 1
				  
	o.close() 

if __name__ == "__main__":
    main() 