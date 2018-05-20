# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
import csv
 
 
def main():

    inputfile = sys.argv[1]
    finalfile = sys.argv[2]
    o= open(finalfile,"w+")
    i = 0
    with open(inputfile, 'r') as reader:
        read = csv.reader(reader)
        for row in read :
            #print(row[1]) 
            finalrow= [];
            for col in row:
                col = bytearray(col, 'UTF-8').decode('latin-1')
                col = col.replace("\\xc9", "É") # hexadecimal 
                col = col.replace("\\xe7", "ç") # hexadecimal
                col = col.replace("\\xe9", "é") # hexadecimal 
                col = col.replace("\\xeb", "ë") # hexadecimal 
                col = col.replace("\\xf3", "ó") # hexadecimal 
                col = col.replace("\\xe1", "á") # hexadecimal 
                
                col = col.replace("\\xf8", "ø") # hexadecimal 
                col = col.replace("\\u017", "ž") # hexadecimal
                col = col.replace("\\u0301", "́́`") # hexadecimal
                col = col.replace("\\u0142", "ł") # hexadecimal
                col = col.replace("\\xed", "í") # hexadecimal
                
                col = col.replace("\\xe8", "è") # hexadecimal 
                col = col.replace("\\xfc", "ü") # hexadecimal 
                col = col.replace("\\xde", "Þ") #     Þ
                col = col.replace("\\xe3", "ã") # hexadecimal
                col = col.replace("\\xf6", "a") # hexadecimal
                col = col.replace("\\xef", "ï") # hexadecimal   
                col = col.replace("\\u0100", "Ā") # hexadecimal 
                col = col.replace("\\xf1", "ñ") # hexadecimal
                col = col.replace("\\xc1", "Á") # hexadecimal
                #print(row[1])
                #print (a[0])
                finalrow.append(col)
            str1 = ', '.join(finalrow)+"\n"

            
            o.write (str1) 
	print(finalfile + "has been formatted")			
		
    o.close() 

if __name__ == "__main__":
    main() 