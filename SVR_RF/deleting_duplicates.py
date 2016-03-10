#-------------------------------------------------------------------------------
# Name:        deleting_duplicates
# Purpose:     delete duplicates records from csv file
#
# Author:      Aparna
#
# Created:     11/07/2015

#-----------------------------
import csv

reader=csv.reader(open(r'D:\spatial_temporal analytics\Project\VGI\Naatuurkalender_all.csv', 'rU'))
writer=csv.writer(open(r'D:\spatial_temporal analytics\Project\VGI\VGI_cleaned_all.csv', 'w'))
entries = set()

for row in reader:
   key = (row[1],row[2], row[3],row[4], row[5],row[6],row[7],row[8], row[9],row[10],row[14], row[15]) # checks the required columms

   if key not in entries:
      writer.writerow(row)
      entries.add(key)
