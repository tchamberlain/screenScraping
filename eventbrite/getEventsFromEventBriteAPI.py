import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv

###############################################################
# HANDLE EVENT INFO HELPER FUNCTIONS
###############################################################

#____________________________________________________________
#INPUT: str -- date time string  '2016-06-25T11:00:00'
#OUTPUT: str -'18/12/2017' (dd/mm/yyyy)
def getDateStrFormat( dateTime ):
  convertFromDateTime = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S")
  ddmmyyy = datetime.strptime(str(convertFromDateTime), "%Y-%m-%d %H:%M:%S").strftime('%d/%m/%Y')
  return ddmmyyy
#____________________________________________________________
#INPUT: str -- date time string  '2016-06-25T11:00:00'
#OUTPUT: str -11:00 AM (TTTT pm)
def getTimeStrFormat( dateTime ):
  convertFromDateTime = datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S")
  TTTTpp = datetime.strptime(str(convertFromDateTime), "%Y-%m-%d %H:%M:%S").strftime('%I:%M %p')
  return TTTTpp

#____________________________________________________________
#INPUT: event object from eventBrite api
#OUTPUT: boolean - true if appropriate for teen 
def isAppropriateForYouth( event ):
  eventText = event['name']['text'].lower()
  badKeyWords = ['day party','whiskey','drunk','bar','alcohol', 'beer', 'cocktail', 'margarita', 'cigars','wine', 'crawl','booze', 'happy hour', 'brew']
  for word in badKeyWords: 
    if( word in eventText):
      return False
  return True

#____________________________________________________________
#INPUT: response from event brite api in json 
#OUTPUT: csv file with all of our events!
def pythonDatetoEventBriteDate( pythonDate ):
  arr = str(pythonDate).split(' ')
  eventBriteDate = arr[0]+'T'+arr[1].split('.')[0]
  return eventBriteDate

#____________________________________________________________
#INPUT: event object from eventBrite api, int -- maxCost of event
#OUTPUT: boolean - true if not expensive
def isNotExpensive( event, maxCost = 30 ):
  priceLimit = maxCost * 100
  priceLimit = 100000000000
  priceInfo = event['ticket_classes'][0]
  if 'cost' in priceInfo:
    priceValue = priceInfo['cost']['value']
    priceDisplay = priceInfo['cost']['display']
    if( priceValue > priceLimit ):
      return False
  else:
    return True 

###############################################################
# READ IN EVENTS FROM EVENTBRITE API
###############################################################

#____________________________________________________________
#INPUT: int-- approxNumEvents approx number of events wanted in csv, str -- startDate (dd/mm/yyyy), str - endDate (dd/mm/yyyy), boolean -- freeEventsOnly
#OUTPUT: csv file with all of our events!
def getEventsIntoCSV( startDate, endDate, freeEventsOnly = True, approxNumEvents = 1000):
  # first getting the number of pages in eventBrite's paginated response we need to get
  # there are 50 events per page
  numPages = int( approxNumEvents / 50 ) 
  
  # we need an extra price param if we only want free events
  if freeEventsOnly:
    priceParam = '&price=free'
  else:
    priceParam = ''

  for page in range( 1, numPages + 1 ):
    requestUrl = "https://www.eventbriteapi.com/v3/events/search/?venue.city=Chicago&sort_by=best&start_date.range_start="+ startDate + "&start_date.range_end=" + endDate + "&page=" + str(page) + "&expand=ticket_classes,venue,category,format" + priceParam
    # MAKING THE API REQUEST
    response = requests.get(
        requestUrl,
        headers = {
            "Authorization": "Bearer FLDGTAIYASFYNLR32RAT",
        },
        verify = True,  # Verify SSL certificate
    )
    response = response.json()
    # ensure our response has events
    if('events' not in response or len(response['events']) == 0):
      print '***************************************************************'
      print '---------> We got an error -- possibly requested too many events'
      print '----->API Response: ',response
      break
    # if it does, loop thru and record them in the csv
    else: 
      events = response['events']
      for event in events:
        # eventmust be appropriate and free or not-expensive
        if((freeEventsOnly or isNotExpensive( event )) and isAppropriateForYouth( event )):
          info = parseInfoIntoCSVFormat(event)
          # Event must return valid info, we receive None on error
          if info: 
            #write to csv
            writer.writerow(info)

#____________________________________________________________
#INPUT: response from event brite api in json 
#OUTPUT: array with each col in our csv, or None if there is an error
def parseInfoIntoCSVFormat( event ):
  #TITLE AND DESCRIPTION
  title = event['name']['text']
  description = event['description']['text']
  
  # DATE AND TIME
  dateTimeStart = event['start']['local'] # if you run this from not chicago, won't be local time!!
  dateTimeEnd = event['end']['local'] # if you run this from not chicago, won't be local time!!
  date = getDateStrFormat(dateTimeStart)
  endDate = getDateStrFormat(dateTimeEnd)
  startTime = getTimeStrFormat(dateTimeStart)
  endTime = getTimeStrFormat(dateTimeEnd)
  # NOTES: here, made the decision to only include first day of multi-day events, so start time can be shown
  # for the other days, we do not know the start time
  # consequently, end time is left blank (since it refers to end time on the last day of the event)
  if(date!=endDate): # if it is a multi-day event
    endTime = ''
  endTime = getTimeStrFormat(dateTimeEnd)
  
  # ADDRESS
  streetAddress = event['venue']['address']['address_1'] or ''
  city = event['venue']['address']['city'] or ''
  postal_code = event['venue']['address']['postal_code'] or ''
  region = event['venue']['address']['region'] or ''
  address = streetAddress +  ', ' + city + ', ' + region + ' ' + postal_code
  
  # SOURCE 
  source = event['url']

  # PRICE 
  priceInfo = event['ticket_classes'][0]
  if not priceInfo['free']:
    print '*************','name', title
  if 'cost' in priceInfo:
    print 'getting price?', priceInfo['cost']['display']
    free = 'false'
    price = priceInfo['cost']['display']
    print price
  else:  # if no cost info, event is free
    price = '$0.00'
    free = 'true'

  # ORIGDATETIME
  origDateTime = dateTimeStart

  #CATEGORY AND EVENT TYPE
  categoryInfo = event['category']
  typeInfo = event['format']
  if categoryInfo:
    category = categoryInfo['short_name']
  else:
    category = ''
  if typeInfo:
    eventType = typeInfo['short_name']
  else:
    eventType = ''
      
  # only return info if all info exists
  if title and description and date and startTime and origDateTime and source and price:
    if len(description) > 3 and len(title) > 2: # These can't just be 1 character
      # Make sure everything is in utf8
      title = title.encode('utf-8')
      description = description.encode('utf-8')
      return [title, description, date, startTime, endTime, origDateTime, source, price, free, category, eventType]
  else:
    return None

###############################################################
# OPEN CSV AND RUN FUNCTIONS
###############################################################

# open our final output file
writer = csv.writer(open('eventbriteEvents_limited.csv', 'wb'))

# make the header line
writer.writerow(["title","description","date","startTime","endTime","origDateTime","source","price","free","category","eventType"])

# grab date we want to get events for
# now 
# 2016-06-03 15:39:46.938028
startDate = pythonDatetoEventBriteDate( datetime.now() )
print(datetime.now())
endDate = pythonDatetoEventBriteDate( datetime.now() + relativedelta(months=4) )

# run function that will create our csv
getEventsIntoCSV(startDate, endDate, False, 1000);



