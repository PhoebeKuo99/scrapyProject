#!/bin/bash

cd /Users/rainstar/scrapyProject/ndmctsgh

LIMIT=50
dept1=11
dept2=9
dept3=6
dept4=24
NOW=$(date +"%m-%d-%Y")
MYT=$(date +"%T")
for ((a=1; a <= LIMIT ; a++))
do
   if [ $a -gt 26 ]
   then
      b=3
   elif [ $a -gt 20 ]
   then
      b=2
   elif [ $a -gt 11 ] 
   then
      b=1
   else
      b=0
   fi
   rm -f export.json
   /Library/Frameworks/Python.framework/Versions/2.7/bin/scrapy crawl -a i=$a -a j=$b -a z=0 ndmctsgh   
   mv export.json export-$a-1.json
   sleep 5
   size=`cat export-$a-1.json | wc -c`
   if (( $size < 3 )) 
   then
       /Library/Frameworks/Python.framework/Versions/2.7/bin/scrapy crawl -a i=$a -a j=$b -a z=0 ndmctsgh 
       mv export.json export-$a-1.json
       sleep 5
   fi
   if (( $size < 3 )) 
   then
       rm export-$a-1.json
   fi
done

cat export-*-1.json >> n-$NOW-$MYT.json
