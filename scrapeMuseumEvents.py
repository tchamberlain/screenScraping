###############################################################
# GENERATE MUSEUM EVENT ENTRIES
###############################################################

import csv
import datetime

#____________________________________________________________
#INPUT: str - start date "02/05/2016", str - end date "02/05/2016"
#OUTPUT: csv entries
def createCsv(startDate, endDate):
  # open our final OUTPUT file
  writer = csv.writer(open('onceAWeekEvents_safetyToolEvents_formatted.csv', 'wb'))

  # make the header line
  writer.writerow(["title","description","date","startTime","endTime","origDateTime",'address',"source"])

  # open our INPUT file -- since we are reading in from a txt file
  reader = csv.reader(open('../onceAWeekEvents_safetyToolEvents.txt', 'rU'), dialect=csv.excel_tab)
  
  # Hack to skip the first line which is a header
  i = 0

  # Loop thru each line in the csv
  for row in reader:
    if i:
      dayOfWeekInt = getDayOfWeekInt(row[2])
      datesArr = makeOnceAWeekDateArr(dayOfWeekInt, startDate, endDate)
      for date in datesArr:
        writer.writerow([row[0],row[1],date,row[5],row[6],row[2],row[4],row[3]])
    i+=1


###############################################################
# GENERATE ONCE A WEEK EVENT ENTRIES
###############################################################

#____________________________________________________________
# INPUT: int day of the week (0-6), string start date('"11/01/2016"'), string - enddate('"11/01/2016"')
# OUTPUT: array of date strings [ "11/01/2016", "11/01/2016" ]
def makeOnceAWeekDateArr(dayOfWeek, startDate, endDate):
  # while current date is less than final date, increment days by one day
  # if date is the day of week we want, record the info in the csv
  currDate =  datetime.datetime.strptime(startDate, "%d/%m/%Y")
  endDate =  datetime.datetime.strptime(endDate, "%d/%m/%Y")
  datesToAdd = []
  while(currDate <= endDate):
    if currDate.weekday() == dayOfWeek-1:
      formattedDate = currDate.strftime("%d/%m/%Y")
      datesToAdd.append(formattedDate)
    currDate = currDate + datetime.timedelta(days=1)
  return datesToAdd
 
#____________________________________________________________
#INPUT: str - day of week in full or abbreviated or w extr character 'mon ksdflksfs' 'Monday, ksfnwnek', 'Mon.'
#OUTPUT: int - 0-6
def getDayOfWeekInt(dayStr):
  daysOfWeek = [['sun',0],['mon',1],['tues',2],['wed',3],['thurs',4],['fri',5],['sat',6]]
  dayStr = dayStr.lower()
  for dayArr in daysOfWeek:
    if dayArr[0] in dayStr:
      return dayArr[1]
  return None

# Create csv with entries for between these dates
createCsv("02/05/2016","31/12/2016")



