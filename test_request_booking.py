import sys
sys.path.insert(0, r'c:\Users\nehar\Web Dev\VenueBookingSystem')
import venue_admin.views as v
print('views module:', v.__file__)
print('has request_booking', hasattr(v, 'request_booking'))
print('request_booking attr:', v.request_booking)
