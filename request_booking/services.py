import uuid
from gymkhana.models import Booking
from request_booking.models import Request

def create_bookings_for_cumulative(cumulative_request):
    individual_requests = Request.objects.filter(
        cumulative_request_id=cumulative_request.cumulative_request_id
    )

    for req in individual_requests:
        # Avoid duplicates
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
