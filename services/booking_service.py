# """
# Handles logic of the person making request for booking
# includes external as well as internal users
# version: 0.1
# Developed by: Kaustubh Kharat
# Month-Year: 2-2025
# """

# from services import db
# import datetime

# SLOT_NUM      = 12
# SLOT_START    = 8
# SLOT_DURATION = 1

# # date in YYYY-MM-DD format
# # every day has 12 slots of 1 hr each starting from 8 am

# def checkDate(date:str):
#     try:
#         test_date=datetime.datetime.strptime(date, "%Y-%m-%d")
#     except ValueError as e:
#         return False
#     return True

# def getAvailableSlots(venue_id, start_date, end_date):
#     if not checkDate(start_date) or not checkDate(end_date):
#         raise ValueError("Invalid dates") # raises error to the callee
#     # get from database
#     slots_booked  = db.getBookedSlotsFromDB(venue_id, start_date, end_date) # date is handled by database
#     json_array    = []
#     booking_dict  = {}
#     start_date    = datetime.strptime(start_date, "%Y-%m-%d").date()
#     end_date      = datetime.strptime(end_date,   "%Y-%m-%d").date()
#     iterator_date = start_date

#     while iterator_date <= end_date:
#         booking_dict[iterator_date]  = [True for _ in range(SLOT_NUM)]
#         iterator_date               += datetime.timedelta(days=1)

#     for row in slots_booked:
#         # assuming all the booking errors are handled by the request slot method
#         # all entries in the database are consistent
#         for i in range(row.duration):
#             booking_dict[row.date][row.time+i]=False

#     # convert dictionary to array which can be handled by a template
#     for key, value in booking_dict.items():
#         json_array.append(
#             {
#                 'date':key.strftime("%d-%m-%Y"),
#                 **{f"{i+SLOT_START}":value[i] for i in range(SLOT_NUM)}
#             }
#         )

#     return json_array

# def requestSlot(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
#     if not checkDate(date):
#         raise ValueError("Invalid Date")
#     if time + duration > SLOT_START + SLOT_NUM*SLOT_DURATION:
#         raise ValueError("Invalid Duration")
#     # query database
#     try:
#         res=db.requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need) # implemented in db
#     except ValueError:
#         raise ValueError("Venue Doesn't Exist")
#     return res

# def cancelRequest(req_id):
#     try:
#         res=db.cancelRequestFromDB(req_id) # implemented in db
#     except ValueError:
#         raise ValueError("Request Doesn't Exist")
#     return True

# def getVenueDetails(venue_id):
#     try:
#         res=db.getVenueDetailsFromDB(venue_id) # implemented in db
#     except ValueError:
#         raise ValueError("Venue Doesn't Exist")
#     if res == None:
#         raise ValueError("Venue Doesn't Exist")
#     json_array=[]
#     for row in res:
#         json_array.append(
#             {
#                 'Name'        :row.venue_name,
#                 'Photo_URL'   :row.photo_url,
#                 'Address'     :row.address,
#                 'Facilites'   :row.facilities,
#                 'Description' :row.description
#             }
#         )

#     return json_array

# def getVenues(limit):
#     if limit < 0:
#         raise ValueError("Invalid limit")
#     try:
#         # limit logic is handled by db
#         res=db.getVenuesFromDB(limit) #implemented in db
#     except Exception as e:
#         raise e  # Handle or log error properly

#     json_array = []
#     # 
#     for row in res:
#         print(row)
#         print('----')
#         json_array.append(
#             {
#                 # 'Name'      :row.venue_name,
#                 'Name'      : row['venue_name'],
#                 'Facilites' :row['facilities'],
#                 'Photo_URL' :row['photo_url']
#             }
#         )
#     return json_array

# def getUserRequests(user_id):
#     try:
#         res=getUserRequestsFromDB(user_id)
#     except Exception as e:
#         raise e  # Handle or log error properly

#     json_array = []
#     for row in res:
#         json_array.append(
#             {
#                 'RequestID' :row.request_id,
#                 'Date'      :row.date,
#                 'VenueName' :row.venue_name,
#                 'Time'      :row.time,
#                 'Duration'  :row.duration * SLOT_DURATION,
#                 'Status'    :row.status
#             }
#         )
#     return json_array


"""
Handles logic of the person making request for booking
includes external as well as internal users
version: 0.1
Developed by: Kaustubh Kharat
Month-Year: 2-2025
"""

from services import db
import datetime

SLOT_NUM = 12
SLOT_START = 8
SLOT_DURATION = 1

# date in YYYY-MM-DD format
# every day has 12 slots of 1 hr each starting from 8 am

def checkDate(date: str):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def getAvailableSlots(venue_id, start_date, end_date):
    if not checkDate(start_date) or not checkDate(end_date):
        raise ValueError("Invalid dates")  # raises error to the callee

    # get from database
    slots_booked = db.getBookedSlotsFromDB(venue_id, start_date, end_date)  # ✅ Fetch as dict
    json_array = []
    booking_dict = {}
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    iterator_date = start_date

    while iterator_date <= end_date:
        booking_dict[iterator_date] = [True for _ in range(SLOT_NUM)]
        iterator_date += datetime.timedelta(days=1)

    for row in slots_booked:
        for i in range(row['duration']):  # ✅ Use dict keys instead of tuple indexing
            booking_dict[row['date']][row['time'] + i] = False

    # convert dictionary to array which can be handled by a template
    for key, value in booking_dict.items():
        json_array.append(
            {
                'date': key.strftime("%d-%m-%Y"),
                **{f"{i + SLOT_START}": value[i] for i in range(SLOT_NUM)}
            }
        )

    return json_array

# def requestSlot(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
#     if not checkDate(date):
#         raise ValueError("Invalid Date")
#     if time + duration > SLOT_START + SLOT_NUM * SLOT_DURATION:
#         raise ValueError("Invalid Duration")

#     try:
#         res = db.requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need)  # ✅ Query DB
#     except ValueError:
#         raise ValueError("Venue Doesn't Exist")
#     return res

import uuid

def requestSlot(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
    if not checkDate(date):
        raise ValueError("Invalid Date")
    if time + duration > SLOT_START + SLOT_NUM * SLOT_DURATION:
        raise ValueError("Invalid Duration")

    try:
        res = db.requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need)  # ✅ Query DB
    except ValueError:
        raise ValueError("Venue Doesn't Exist")
    return res

def cancelRequest(req_id):
    try:
        db.cancelRequestFromDB(req_id)  # ✅ Query DB
    except ValueError:
        raise ValueError("Request Doesn't Exist")
    return True

def getVenueDetails(venue_id):
    print('entered')
    print(venue_id)
    try:
        res = db.getVenueDetailsFromDB(venue_id)  # ✅ Fetch as dict
    except ValueError:
        raise ValueError("Venue Doesn't Exist")

    if not res:
        raise ValueError("Venue Doesn't Exist")

    json_array = []
    for row in res:
        json_array.append(
            {
                'Name': row['venue_name'],  # ✅ Use dictionary key
                'Photo_URL': row['photo_url'],
                'Address': row['address'],
                'Facilities': row['facilities'],
                'Description': row['description']
            }
        )
        print('---')

    return json_array

def getVenues(limit):
    if limit < 0:
        raise ValueError("Invalid limit")
    
    try:
        res = db.getVenuesFromDB(limit)  # ✅ Fetch as dict
    except Exception as e:
        raise e

    json_array = []
    
    for row in res:
        json_array.append(
            {
                'Name': row['venue_name'],  # ✅ Use dictionary keys
                'Facilities': row['facilities'],
                'Photo_URL': row['photo_url']
            }
        )
    return json_array

def getUserRequests(user_id):
    try:
        res = db.getUserRequestsFromDB(user_id)  # ✅ Fetch as dict
    except Exception as e:
        raise e

    json_array = []
    for row in res:
        json_array.append(
            {
                'RequestID': row['request_id'],  # ✅ Use dictionary keys
                'Date': row['date'],
                'VenueName': row['venue_name'],
                'Time': row['time'],
                'Duration': row['duration'] * SLOT_DURATION,
                'Status': row['status']
            }
        )
    return json_array
