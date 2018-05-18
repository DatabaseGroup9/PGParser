./fetchFiles.sh
./install.sh
python3 PGParser.py --skip NUMBEROFFILESTOSKIP --take NUMBEROFFILESTOTAKE
./printHeadersAndZip.sh