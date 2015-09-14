#!/bin/bash
cd /Users/rainstar/scrapyProject/ndmctsgh
LIMIT=40
dept1=10
dept2=9
dept3=4
dept4=17
NOW=$(date +"%m-%d-%Y")
MYT=$(date +"%T")
for ((a=1; a <= LIMIT ; a++))
do
   if [ $a -gt 23 ]
   then
      b=3
   elif [ $a -gt 19 ]
   then
      b=2
   elif [ $a -gt 10 ] 
   then
      b=1
   else
      b=0
   fi
   rm -f export.json
   /Library/Frameworks/Python.framework/Versions/2.7/bin/scrapy crawl -a i=$a -a j=$b -a z=1 ndmctsgh   
   mv export.json export-$a-2.json
   sleep 5
   size=`cat export-$a-2.json | wc -c`
   if (( $size < 3 )) 
   then
       scrapy crawl -a i=$a -a j=$b -a z=1 ndmctsgh   
       mv export.json export-$a-2.json
       sleep 5
   fi
   if (( $size < 3 )) 
   then
       rm export-$a-2.json
   fi
done

cat export-*-2.json >> t-$NOW-$MYT.json
