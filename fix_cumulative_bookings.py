from gymkhana.models import Booking
from request_booking.models import Request, CumulativeRequest
import uuid

bookings_created = 0

approved_cumulatives = CumulativeRequest.objects.filter(status='approved')

for cumulative_req in approved_cumulatives:
    individual_requests = Request.objects.filter(
        cumulative_request_id=cumulative_req.cumulative_request_id
    )

    for req in individual_requests:
        if Booking.objects.filter(
            request=req,
            venue=req.venue,
            date=req.date,
            time=req.time
        ).exists():
            continue

        Booking.objects.create(
            booking_id=uuid.uuid4(),
            request=req,
            user=req.user,
            venue=req.venue,
            date=req.date,
            time=float(req.time),
            duration=float(req.duration),
            event_details=req.event_details,
            msg=req.msg if hasattr(req, "msg") else "",
            status="active",
            reason_for_approval="Approved via cumulative booking"
        )

        bookings_created += 1

print("Bookings created:", bookings_created)
print("Total bookings now:", Booking.objects.count())
