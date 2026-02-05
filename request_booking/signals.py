"""
Django Signals for Automatic Booking Creation

This module contains signals that automatically create Booking entries
when Request or CumulativeRequest objects are approved.

Place this file in your request_booking app directory.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
import uuid
import logging

from request_booking.models import Request, CumulativeRequest
from gymkhana.models import Booking

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Request)
def track_request_status_change(sender, instance, **kwargs):
    """
    Track status changes for Request objects.
    This runs before the Request is saved.
    """
    if instance.pk:  # Only for existing objects (updates)
        try:
            old_instance = Request.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Request.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Request)
def create_booking_on_approval(sender, instance, created, **kwargs):
    """
    Automatically create a Booking entry when a Request is approved.
    
    This signal fires after a Request is saved. It checks if:
    1. The status changed to 'approved'
    2. A Booking doesn't already exist for this Request
    
    If both conditions are met, it creates a new Booking entry.
    """
    # Only proceed if this is an update (not a new creation)
    if created:
        return
    
    # Get the old status (set by pre_save signal)
    old_status = getattr(instance, '_old_status', None)
    
    # Check if status changed to 'approved'
    if instance.status == 'approved' and old_status != 'approved':
        logger.info(f"Request {instance.request_id} approved - creating booking")
        
        # Check if booking already exists
        if Booking.objects.filter(request=instance).exists():
            logger.info(f"Booking already exists for Request {instance.request_id}")
            return
        
        try:
            with transaction.atomic():
                # Create the booking
                booking = Booking.objects.create(
                    booking_id=uuid.uuid4(),
                    request=instance,
                    user=instance.user,
                    venue=instance.venue,
                    date=instance.date,
                    time=float(instance.time),
                    duration=float(instance.duration),
                    event_details=instance.event_details or "",
                    msg=getattr(instance, 'msg', '') or "",
                    status='active',
                    reason_for_approval=f"Auto-created from approved request {instance.request_id}"
                )
                
                logger.info(f"Successfully created Booking {booking.booking_id} for Request {instance.request_id}")
                
        except Exception as e:
            logger.error(f"Error creating booking for Request {instance.request_id}: {str(e)}")
            # Don't raise the exception - let the request approval succeed even if booking creation fails
            # You can add additional error handling here if needed


@receiver(pre_save, sender=CumulativeRequest)
def track_cumulative_request_status_change(sender, instance, **kwargs):
    """
    Track status changes for CumulativeRequest objects.
    This runs before the CumulativeRequest is saved.
    """
    if instance.pk:  # Only for existing objects (updates)
        try:
            old_instance = CumulativeRequest.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except CumulativeRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=CumulativeRequest)
def create_bookings_for_cumulative_approval(sender, instance, created, **kwargs):
    """
    Automatically create Booking entries for all related Requests
    when a CumulativeRequest is approved.
    
    This signal fires after a CumulativeRequest is saved. It:
    1. Checks if the status changed to 'approved'
    2. Finds all related Request objects
    3. Creates Booking entries for each Request that doesn't have one
    """
    # Only proceed if this is an update (not a new creation)
    if created:
        return
    
    # Get the old status (set by pre_save signal)
    old_status = getattr(instance, '_old_status', None)
    
    # Check if status changed to 'approved'
    if instance.status == 'approved' and old_status != 'approved':
        logger.info(f"CumulativeRequest {instance.cumulative_request_id} approved - creating bookings")
        
        # Find all related Request objects
        related_requests = Request.objects.filter(
            cumulative_request_id=instance.cumulative_request_id
        )
        
        bookings_created = 0
        bookings_skipped = 0
        
        for req in related_requests:
            # Check if booking already exists
            if Booking.objects.filter(request=req).exists():
                bookings_skipped += 1
                continue
            
            try:
                with transaction.atomic():
                    # Create the booking
                    booking = Booking.objects.create(
                        booking_id=uuid.uuid4(),
                        request=req,
                        user=req.user,
                        venue=req.venue,
                        date=req.date,
                        time=float(req.time),
                        duration=float(req.duration),
                        event_details=req.event_details or "",
                        msg=getattr(req, 'msg', '') or "",
                        status='active',
                        reason_for_approval=f"Auto-created from approved cumulative request {instance.cumulative_request_id}"
                    )
                    
                    # Update the Request status to approved
                    req.status = 'approved'
                    req.save()
                    
                    bookings_created += 1
                    logger.info(f"Created Booking {booking.booking_id} for Request {req.request_id}")
                    
            except Exception as e:
                logger.error(f"Error creating booking for Request {req.request_id}: {str(e)}")
                # Continue with next request even if this one fails
                continue
        
        logger.info(
            f"Cumulative approval complete: {bookings_created} bookings created, "
            f"{bookings_skipped} skipped (already existed)"
        )


# Optional: Signal to sync booking cancellations
@receiver(post_save, sender=Request)
def sync_booking_cancellation(sender, instance, created, **kwargs):
    """
    When a Request is cancelled, also cancel the associated Booking.
    """
    if created:
        return
    
    old_status = getattr(instance, '_old_status', None)
    
    # Check if status changed to a cancelled state
    if instance.status in ['cancelled', 'user-cancelled', 'rejected'] and old_status not in ['cancelled', 'user-cancelled', 'rejected']:
        try:
            booking = Booking.objects.get(request=instance)
            if booking.status not in ['cancelled', 'user-cancelled']:
                booking.status = instance.status
                booking.msg = getattr(instance, 'reasons', '') or booking.msg
                booking.save()
                logger.info(f"Synced cancellation: Booking {booking.booking_id} status updated to {instance.status}")
        except Booking.DoesNotExist:
            # No booking exists, nothing to sync
            pass
        except Exception as e:
            logger.error(f"Error syncing booking cancellation for Request {instance.request_id}: {str(e)}")