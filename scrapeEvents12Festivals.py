import csv
import urllib2

###############################################################
# FIX DATE FORMATTING
###############################################################
# this is simply to get the correct index of a month for date parsing[]
allMonths = [['jan','01', 31], ['feb','02', 28], ['mar','03',31], ['apr','04', 30], ['may','05',31], ['june','06',30], ['july','07', 31], ['aug','08', 31], ['sept','09',30], ['oct','10',31], ['nov','11',30], ['dec','12',31]];
daysOfWeek = ['sun','mon','tues','wed','thurs','fri','sat']

#____________________________________________________________
#INPUT: str - day of week in full or abbreviated or w extr character 'mon ksdflksfs' 'Monday, ksfnwnek', 'Mon.'
#OUTPUT: int - orresponding string of length two ('02' for februrary), or none if no day found
def whichDayOfWeek(dayStr):
  dayStr = dayStr.lower()
  for day in daysOfWeek:
    if day in dayStr:
      return day
  return None

#____________________________________________________________
#INPUT: str - month in full or abbreviated
#OUTPUT: int - orresponding string of length two ('02' for februrary)
def getMM(month):
  month = month.lower()
  for monthTuple in allMonths:
    if monthTuple[0] in month:
      mm = monthTuple[1]
      return mm

#____________________________________________________________
#INPUT: str - month in full or abbreviated
#OUTPUT: int - number of days in that month
def getLastDayinMonth(month):
  month = month.lower()
  for monthTuple in allMonths:
    if monthTuple[0] in month:
      numDays = monthTuple[2]
      return numDays

#____________________________________________________________
#INPUT: str or int - a day of the month
#OUTPUT: str - day of the month in 2 digits, so '22' given 22 or '02' given '2'
def getDD(day):
  dayStr = str(day)
  if len(dayStr) < 2:
      dayStr = '0'+ dayStr
  return dayStr

#____________________________________________________________
#INPUT: str  - a time in the format 2:30 or 2
#OUTPUT: str - a time in the format 02:30 or 02:00
def getTTTT(time):
  # remove trailing space
  time = time.rstrip().lstrip()
  if len(time.split(':')[0]) == 1:
    time = '0' + time
  if ':' not in time:
    time = time + ':00'
  return time

#____________________________________________________________
#INPUT: three strs, '01', '12' '2017', or default year, '2016'
#OUTPUT: str -'01/12/2017'
def makeFormattedDate(dd, mm, year='2016'):
  return dd + '/' + mm + '/' + year

#____________________________________________________________
#INPUT: any string given by website (but with NO time info)
#OUTPUT: str or array of str-'01/12/2017' or  ['01/12/2017', '01/13/2017']
def formatDate( dateString ):
  # Remove any trailing spaces
  dateString = dateString.rstrip()
  
  # dealing w/ date in format 'April 24, 2016'
  if '-' not in dateString:
    #getting mm
    dd = dateString.split(' ')[1][:-1]+''
    dd = getDD(dd)
    #getting mm
    mm = getMM(dateString.lower())
    formattedDate = makeFormattedDate(dd, mm)
    return formattedDate
  
  # dealing dates in format: November 25 - 27, 2016
  elif len(dateString) <= 23 and len(dateString) >= 15 and len((dateString.split(' ')[3]).replace(',','')) < 3:
    #get month
    mm = getMM(dateString.lower())
    #get number of days to make dates for
    startDay = int(dateString.split(' ')[1])
    endDay = int(dateString.split(' ')[3][:-1]) #get rid of comma at end
    dateStrings = []
    for day in range(startDay, endDay+1):
      dd = getDD(day)
      dateStrings.append(makeFormattedDate(dd, mm))
    return dateStrings

  # dealing with dates in the format: September 30 - Oct. 31, 2016
  elif dateString.split(' ')[2] == '-':
    startDay = int(dateString.split(' ')[1])
    endDay = int(dateString.split(' ')[4][:-1]) #get rid of comma at end
    startMonth = dateString.split(' ')[0]
    endMonth = dateString.split(' ')[3]
    startMonthMM = getMM(startMonth)
    endMonthMM = getMM(endMonth)
    lastDayinStartMonth = getLastDayinMonth(startMonth)
    #starting values for while loop
    mm = startMonthMM
    day = startDay
    dateStrings = []
    # increment day until we reach the end day of the end month
    while(day <= endDay or mm != endMonthMM):
      dd = getDD(day)
      formattedDate = makeFormattedDate(dd, mm)
      dateStrings.append(formattedDate)
      if(mm == startMonthMM and day == lastDayinStartMonth):
        mm =  endMonthMM
        day = 1
      else:
        day += 1
    return  dateStrings
  else: # this other formatting is very rare -- ~ 5 events, for now removing these events
    return None

#____________________________________________________________
# INPUT: str - date in any format from our html
# OUPUT: dict -  {'startTime':'TT:TT','endTime':'TT:TT', 'date': 'dd/mm/yyyy'}
def handleDateAndTime( dateString ):
  #initialize the object we will return later
  dateTime = {'startTime':'', 'endTime':'', 'date': ''}

 # Remove any trailing spaces
  dateString = dateString.rstrip()
  
  #first check if the date mentions a day of the week-- if so , we want to eventually
  # send it to a function that will make entries for 'every tuesday' type of events
  if  whichDayOfWeek(dateString) is not None:
    return None
  #first check if there are parens, and if so, we handle info inside
  elif '('  in dateString:
    #We want to exclude events that are undated
    if 'undated' in dateString:
      return None
    # FOR NOW: also excluding events where the parens provide time info that ISNT start or end time
    elif 'p.m.' not in dateString and 'a.m.' not in dateString or 'begins' in dateString:
      return None
    else:
      # GET TIME
      timeString = dateString.split('(')[1][:-1]
      dateString = dateString.split('(')[0][:-1]
      time = formatTime(timeString)
      dateTime['startTime'] = time[0]
      dateTime['endTime'] = time[1]

  # GET DATE
  date = formatDate(dateString)
  dateTime['date'] = date
  return dateTime

#____________________________________________________________
# INPUT: time string in all formats given by website
# OUTPUT: [TT:TT, TT:TT]  arr of two strings, first is the  strt time
def formatTime( timeString ):
  # handling cases where just the start time is listed (8 a.m.)
  if 'to' not in timeString:
    timeNum = timeString.split(' ')[0]
    startTTTT = getTTTT(timeNum)
    if 'a.m.' in timeString:
      startTTTT += ' AM'
    else:
       startTTTT += ' PM'
    return [ startTTTT,'' ]
  # handling cases where both start  and time is listed (11 a.m. to 2 p.m.)
  # or 8 to 11 p.m.
  else: 
    startTimeNum = timeString.split('to')[0].split('a')[0].split('p')[0]
    endTimeNum = timeString.split('to')[1].split('a')[0].split('p')[0]
    startTTTT = getTTTT(startTimeNum)
    if 'a.m.' in timeString.split('to')[0]:
      startTTTT += ' AM'
    else:
       startTTTT += ' PM'
    endTTTT = getTTTT(endTimeNum)
    if 'a.m.' in timeString.split('to')[1]:
      endTTTT += ' AM'
    else:
       endTTTT += ' PM'
    return [ startTTTT,endTTTT ]


###############################################################
# READ IN EVENTS 
###############################################################
# open our final output file
writer = csv.writer(open('events12.csv', 'wb'))

# make the header line
writer.writerow(["title","description","date","startTime","endTime","origDateTime","source"])


# set up the  the url opener:
agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', agent)]

#we'll add each month to the base url, to get events for all months until the end of 2016 (starting from this month, April)
urlBase = 'http://www.events12.com/chicago/' 
source = 'http://www.events12.com/chicago/'
# starting from april since it's currently april
monthsToGetEventsFrom = ['april','may','june','july','august','september','october','november','december']

# Loop thru each month we want events from
for month in monthsToGetEventsFrom:
    # read the html for the given month and write all of the html to htmlContent.text
    url = urlBase + month + '/'
    html = opener.open(url)
    fullcode = html.read()
    htmlContent = open('htmlContent.txt', 'w')
    htmlContent.write(fullcode)
    #remove new line characters which we don't want to include
    fullcode = fullcode.replace('\n', '')
    # split code on event and store in events array
    events = fullcode.split('<div class="event">')

    for event in events:
        splitOnTitle = event.split('<p class="title">')
        if( len(splitOnTitle) >= 2 ):
            splitOnTitle = splitOnTitle[1].split('<p class="date">')
            title = splitOnTitle[0]
            splitOnDate = splitOnTitle[1].split('<p class="miles">')
            date = splitOnDate[0]
            splitOnDescription = splitOnDate[1].split('</p>')[1].split('</div>')
            #prevent the description from being replaced with an image
            if 'imagebox' not in splitOnDescription[0]:
                description = splitOnDescription[0]
            else:
                description = splitOnDescription[1]
            # get rid of the events that actually list multiple events
            # later, if we really want we could handle these individually
            if '<li>' not in description:
                # keeping the original date information to check for any errors in the future
                origDateTime = date
                dateTime = handleDateAndTime(date)
                # for certain events, the dates are mal-formatted, we won't include those
                # the dateTimes are coded as none
                if dateTime is not None:
                  date = dateTime['date']
                  startTime = dateTime['startTime']
                  endTime = dateTime['endTime']
                  # for certain events, the dates are mal-formatted, we won't include those
                  # the dates are coded as none
                  if date is not None:
                    if type(date) is str:
                      writer.writerow([title,description,date,startTime,endTime,origDateTime,source])
                    else: #in this case we have an array and we want an entry for each date in the array
                      for entry in date:
                        writer.writerow([title,description,entry,startTime,endTime,origDateTime,source])





