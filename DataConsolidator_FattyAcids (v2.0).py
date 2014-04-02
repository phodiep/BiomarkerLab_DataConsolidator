##-----------------------------------------------------------------------
##  DataConsolidator_FattyAcids.py
##  Purpose: Consolidate the raw data from the csv files
##           exported by checmstation after integrations
##           of the peaks of interest
##  Written in Python 2.7.3
##  Written by:   Pho Diep (10/29/2012)
##  Last Updated: Pho Diep (11/21/2012)
##  Update Log: (11/9/12) update order of data printed
##              (11/21/12)updated so no longer need to enter report type
##                        and opens file after consolidation
##------------------------------------------------------------------------

import os
import time
import re
import csv

#==========================================================================
def cleanCSV(csvData):
  """removes all " <space> newLine from csv file and splits lines at \r"""
  
  tmpData = re.sub('"|\n| ','',str(csvData)) #remove all " and <spaces> and newLine using Regular Expressions (re) ... must 'import re'
  tmpLine = tmpData.split('\r')     #split string into list - spliting at \r
  return tmpLine

#==========================================================================
def convertCSVType(csvFile):
  """Opens csv File decodes 'UTF-16'and returns 'ASCII' encoded data csvFile = file to be opened"""
  
  decodeData = csvFile.read().decode('UTF-16')            #decode UTF-16
  encodeData = decodeData.encode('ASCII','replace')       #encode ASCII

  return encodeData

#==========================================================================
def getCSVdata(csvData,sampleDict,keyName,reportType):
  """converts csv file data to tuple for each entry"""
  
  tmpSample = cleanCSV(csvData)
  tmpData = ()

  for row in tmpSample:
    tmpRow = row.split(',')
    tmpData += tmpRow,

  tmpDataMapped = map(None,*cleanInfo(tmpData,keyName)) #transposes the data horizontally
  
  if keyName == 'column':
    #rename header and create 1 row of data
    
    dataMapped = ['','']

    peakNames = list(tmpDataMapped[0])
    peakArea = list(tmpDataMapped[1])
    peakData = list(tmpDataMapped[2])

    listIS = findIS(tmpDataMapped[0])
    
    tmpSumArea = [getSum(tmpDataMapped[1],listIS)]
    tmpSumQuant = [getSum(tmpDataMapped[2],listIS)]
    tmpPerc = getPercent(tmpDataMapped[1],listIS)
 
    if reportType == 'Quant':

      #add Calculated Percentage
      dataMapped[0] = ['Calculated Percentage'] + peakNames
      dataMapped[1] = [''] + tmpPerc
      
      #add Quantitative data
      dataMapped[0] += ['Quant (ug/ml)'] + peakNames + ['Total Quant (ug/ml)']
      dataMapped[1] += [''] + peakData + tmpSumQuant

    elif reportType == 'Report':
      #add Percentage
      dataMapped[0] = ['Percentage'] + peakNames
      dataMapped[1] = [''] + peakData

    #add AreaCount
    dataMapped[0] += ['AreaCount'] + peakNames + ['Total Area Count']
    dataMapped[1] += [''] + peakArea + tmpSumArea

    tmpDataMapped[0],tmpDataMapped[1] = dataMapped[0], dataMapped[1]
         
  tmpCount = 0
  for i in tmpDataMapped:
    tmpCount += 1
    if tmpCount >=4:
      break
    else:
      tmpName = keyName + str(tmpCount)
      sampleDict[tmpName] = tuple(i)

  return sampleDict

#==========================================================================
def findIS(tmpList):
  """find internal standard in peaks... returns a list of IS indexes"""
  listIS = list()

  for i in tmpList:
    if 'i' in i.lower() and 's' in i.lower():
      listIS.append(tmpList.index(i))

  return listIS

#==========================================================================
def getSum(tmpList,tmpIS):
  """ returns sum of list, not including IS """
  tmpSum = 0.0

  for i in tmpList:
    if i != '' and i != '-' and tmpList.index(i) not in tmpIS:
      tmpSum += float(i)
    else:
      continue

  return tmpSum

#==========================================================================
def getPercent(tmpList,tmpIS):
  """ returns list of percentages, including IS (will sum to more than 100perc)"""
  tmpSum = getSum(tmpList,tmpIS)
  percList = []

  for i in tmpList:
    if i == '' or i == '-':
      percList += i,
    else:
      percList += str((float(i)/tmpSum)*100),

  return percList

#==========================================================================
def cleanInfo(tmpData,keyName):
  """only keep columns of interest to study  - return as tuple"""

  dataToReturn = ()

  if keyName == 'info':
    listToKeep1 = ('SampleName','Acq.Instrument','Acq.Method')
    listToKeep2 = 'DataFile'
    
    for i in tmpData:
      try:
        if i[0] in listToKeep1:
          dataToReturn += (i[0],i[1]),

        if i[0] == listToKeep2:
          dataToReturn += (i[0],i[2]),
      except:
        continue

  if keyName == 'column':
    for i in tmpData:
      try:
        dataToReturn += ("'"+i[7],i[2],i[4]),
      except:
        continue
      
  return dataToReturn

#==========================================================================
def combineInfoData(info1,info2,column1,column2):
  """combine header and data by line"""
  
  dataToReturn ={}

  dataToReturn['header']= info1 + column1
  dataToReturn['data']= info2 + column2

  return dataToReturn

#==========================================================================
def osWalkSorted(path):
  tmpPathList = []

  for i in os.walk(path): tmpPathList.append(i) #pull out and sort tuple of pathways to ensure files are read in acending order
  tmpPathList.sort()
  
  return tmpPathList

#==========================================================================

print """
==============================================
              DATA CONSOLIDATOR
                 Fatty Acids

                 Version 2.0
            Last updated 11.21.2012

==============================================
   Written By: Pho Diep (phodiep@gmail.com)

          Written in Python 2.7.3
         Packaged using Py2Exe 0.6.9

----------------------------------------------
"""
directions = 'n'
directions = raw_input('Do you want directions? (y/n) \n')
if directions.lower() == 'y':
  print """
---------------------------------------------------------------------
Directions:

  **Important - for Quantitative Report,
      make sure internal standard has "IS" in peak name.
      Example:   13:0 IS    or    IS 13:0

      if it does not have "IS" in name, it will be treated
      like a peak of interest
           
1. Place the rawdata folder into the following path:
   P:\\XSONG\\Laboratory\\PLData\\rawdata\\

2. User will then be asked for "Folder Name".
   This is the name of the folder placed above.

   Example: '091312PD'

3. The consolidated "raw_data.csv" file will be placed inside
   the same rawdata folder.

   Example: P:\\XSONG\\Laboratory\\PLData\\rawdata\\091312PD\\raw_data.csv
---------------------------------------------------------------------
  """

finalResults = ()
finalResultsReport = ()
finalResultsQuant = ()
fileDate = ''

pDrivePath = 'P:\\XSONG\\Laboratory\\PLData\\rawdata\\'

#prompt user for folder name
fileDate = str(raw_input('\nEnter Folder Name \n'))

path = pDrivePath + fileDate

#check for null user input
if fileDate == '':
  print '\nPlease enter a valid folder name.'
  raw_input('\nPress ENTER to close application')
  
#check for non-existent folder
elif not os.path.isdir(pDrivePath + fileDate):
  print '\nThis folder does not exist.'
  raw_input('\nPress ENTER to close application')
  
#else... folder exists... so run
else:
  startTime = time.time()
  print '\nPlease wait while data is being consolidated........ \n'

  fileWriteTo = path + '\\' + 'raw_data.csv'

  for (path,dirs,files) in osWalkSorted(path):
    tmpList = files
    tmpListLower = []
    tmpPath = path
    sampleResultsReport = {}
    sampleResultsQuant = {}

    for item in tmpList:
      tmpListLower += item.lower(),

    if 'report00.csv' in tmpListLower and 'report01.csv' in tmpListLower:
      with open(path+'\\REPORT00.CSV',"rb") as csvFile:
        csvSample = convertCSVType(csvFile)                        #convert to readable format
        sampleResultsReport = getCSVdata(csvSample,sampleResultsReport,'info','Report')  #convert csv to list

      with open(path+'\\REPORT01.CSV',"rb") as csvFile:
        csvSample = convertCSVType(csvFile)                        #convert to readable format
        sampleResultsReport = getCSVdata(csvSample,sampleResultsReport,'column','Report')  #convert csv to list

      sampleResultsReport = combineInfoData(sampleResultsReport['info1'],sampleResultsReport['info2'],sampleResultsReport['column1'],sampleResultsReport['column2'])
      finalResultsReport += sampleResultsReport,


    if 'quant00.csv' in tmpListLower and 'quant01.csv' in tmpListLower:
      with open(path+'\\QUANT00.CSV',"rb") as csvFile:
        csvSample = convertCSVType(csvFile)                        #convert to readable format
        sampleResultsQuant = getCSVdata(csvSample,sampleResultsReport,'info','Quant')  #convert csv to list

      with open(path+'\\QUANT01.CSV',"rb") as csvFile:
        csvSample = convertCSVType(csvFile)                        #convert to readable format
        sampleResultsQuant = getCSVdata(csvSample,sampleResultsReport,'column','Quant')  #convert csv to list
      
      
      sampleResultsQuant = combineInfoData(sampleResultsQuant['info1'],sampleResultsQuant['info2'],sampleResultsQuant['column1'],sampleResultsQuant['column2'])
      finalResultsQuant += sampleResultsQuant,

  #---combine reports if necessary---
  if finalResultsReport != () and finalResultsQuant != ():
    finalResults = finalResultsReport + finalResultsQuant
  elif finalResultsReport != ():
    finalResults = finalResultsReport
  elif finalResultsQuant != ():
    finalResults = finalResultsQuant


  #---write to CSV file---
  #if no data found don't print report
  if finalResults == ():
    print '\nThere were no results to consolidate!\n'

  #else print report
  else:
    with open(fileWriteTo, 'wb') as csvfile:
      csvwriter = csv.writer(csvfile)
      columnCount = 0
      for sample in finalResults:
        if columnCount != len(sample['header']):
          columnCount = len(sample['header'])
          
          csvwriter.writerow('')
          csvwriter.writerow(sample['header'])
          csvwriter.writerow(sample['data'])

        else:
          csvwriter.writerow(sample['data'])
      print '\nConsolidated Report has been saved here:'
      print fileWriteTo + '\n'
      print 'Total time for data consolidation: ' + str(time.time() - startTime) + ' seconds'
      
    raw_input('\nPress ENTER to close application and open the consolidated report in Excel')
    os.startfile(fileWriteTo, 'open')
