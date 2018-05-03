echo 'Copying zipFileLinks.txt:'
scp root@$1:/root/zipfileLinks.txt zipfileLinks.txt
echo 'Finished.\nCopying archive.tar:'
scp root@$1:/root/archive.tar archive.tar
echo 'done.'
