


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
SLOT_START = 9
SLOT_DURATION = 0.5

# date in YYYY-MM-DD format
# every day has 12 slots of 1 hr each starting from 8 am

def checkDate(date: str):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# def getAvailableSlots(venue_id, start_date, end_date):
#     if not checkDate(start_date) or not checkDate(end_date):
#         raise ValueError("Invalid dates")  # raises error to the callee

#     # get from database
#     slots_booked = db.getBookedSlotsFromDB(venue_id, start_date, end_date)  # ✅ Fetch as dict
#     json_array = []
#     booking_dict = {}
#     start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
#     end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
#     iterator_date = start_date

#     while iterator_date <= end_date:
#         booking_dict[iterator_date] = [True for _ in range(SLOT_NUM)]
#         iterator_date += datetime.timedelta(days=1)

#     for row in slots_booked:
#         for i in range(float(row['duration'])): 
#             print("DATE: ",row['date'])
#             print("time:", row['time']) # ✅ Use dict keys instead of tuple indexing
#             booking_dict[row['date']][row['time'] + i - SLOT_START] = False

#     # convert dictionary to array which can be handled by a template
#     for key, value in booking_dict.items():
#         json_array.append(
#             {
#                 'date': key.strftime("%d-%m-%Y"),
#                 # **{f"{i + SLOT_START}": value[i] for i in range(SLOT_NUM)}
#                 **{str(SLOT_START + i * SLOT_DURATION): value[i] for i in range(SLOT_NUM)}

#             }
#         )

#     return json_array


import datetime

# Constants (make sure they match your real config)
SLOT_START = 8          # 8 AM
SLOT_NUM = 20           # Total slots per day
SLOT_DURATION = 0.5     # Each slot is 30 minutes

def getAvailableSlots(venue_id, start_date, end_date):
    if not checkDate(start_date) or not checkDate(end_date):
        raise ValueError("Invalid dates")

    slots_booked = db.getBookedSlotsFromDB(venue_id, start_date, end_date)
    json_array = {}
    booking_dict = {}

    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    iterator_date = start_date_obj

    # Initialize availability: True = available
    while iterator_date <= end_date_obj:
        booking_dict[iterator_date] = [True for _ in range(SLOT_NUM)]
        iterator_date += datetime.timedelta(days=1)

    # Mark booked slots
    for row in slots_booked:
        duration = float(row['duration'])  # e.g., 1.5 hours
        start_time = float(row['time'])    # e.g., 9.5 for 9:30 AM
        booking_date = row['date']         # assumed to be a datetime.date object

        # Convert fractional time to slot index
        start_slot_index = int(round((start_time - SLOT_START) / SLOT_DURATION))
        slots_count = int(duration / SLOT_DURATION)

        for i in range(slots_count):
            slot_index = start_slot_index + i
            if 0 <= slot_index < SLOT_NUM:
                booking_dict[booking_date][slot_index] = False

    # Prepare final output
    for key, value in booking_dict.items():
        json_array[key.strftime("%d-%m-%Y")] = {
            str(SLOT_START + i * SLOT_DURATION): value[i] for i in range(SLOT_NUM)
        }

    return json_array




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

def forwardRequestToGymkhana(req_id, user_id):
    try:
        print('in services : booking_service : forwardRequestToGymkhana()')
        print('user id : ',user_id)
        print('req id : ',req_id)
        req_id = req_id.replace('-','')
        print('req id : ',req_id)

        res = db.forwardRequestToGymkhanaFromDB(req_id, user_id)
    except Exception as e:
        raise e
    
    return True

def getForwardRequests(user_id):
    try:
        json_array=[]
        res = db.getForwardRequestsFromDB(user_id)
        for row in res:
            json_array.append(
                {
                    'RequestID': row['request_id'],
                    'user_name': row['user__name'],
                    'venue_name': row['venue__venue_name'],
                    'date': row['date'],
                    'time': row['time'],
                    'duration': row['duration'],
                    'event_details': row['event_details']
                }
            )

    except Exception as e:
        raise e
    
    return json_array

def declineForwardRequest(req_id, user_id):
    try:
        res = db.declineForwardRequestFromDB(req_id, user_id)
    except Exception as e:
        raise e
    
    return True

# def getUnavailableSlots(venue_name, date):
#     try:
#         print("DATE:", date)
#         res = db.getBookedSlotsFromDB1(venue_name, date)
#         json_array=[]
#         for row in res:
#             print("row from data base:" ,row)
#             for i in range(row['duration']):
#                 json_array.append(str(row['time']+i)+":00")

#     except Exception as e:
#         raise e
    
#     return json_array

def getUnavailableSlots(venue_name, date):
    try:
        print("DATE:", date)
        res = db.getBookedSlotsFromDB1(venue_name, date)
        json_array = []

        for row in res:
            print("row from data base:", row)
            start_time = float(row['time'])
            duration = float(row['duration'])

            slots = int(duration * 2)  # multiply by 2 for half-hour steps
            for i in range(slots):
                json_array.append(round(start_time + i * 0.5, 2))  # round to avoid floating-point issues

    except Exception as e:
        raise e

    return json_array

