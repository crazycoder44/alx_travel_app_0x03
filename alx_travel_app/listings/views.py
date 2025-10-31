# listings/views.py
import uuid
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, status, permissions
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Listings.
    Provides CRUD operations: list, create, retrieve, update, delete.
    """
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Bookings.
    Provides CRUD operations: list, create, retrieve, update, delete.
    """
    queryset = Booking.objects.all().order_by('-created_at')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Save the booking instance
        booking = serializer.save()

        # Prepare email content
        user_email = booking.user.email if booking.user else None
        if user_email:
            booking_details = (
                f"Booking ID: {booking.id}\n"
                f"Destination: {booking.destination}\n"
                f"Date: {booking.date}\n"
                f"Status: {booking.status}\n"
                f"Created at: {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Trigger Celery background task
            send_booking_confirmation_email.delay(user_email, booking_details)

CHAPA_BASE_URL = "https://api.chapa.co/v1"

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request):
    """
    Initiates payment with Chapa API
    """
    booking_id = request.data.get("booking_id")
    amount = request.data.get("amount")
    user = request.user

    try:
        booking = Booking.objects.get(booking_id=booking_id, user_id=user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Generate unique transaction reference
    tx_ref = f"CHAPA-{uuid.uuid4().hex[:10]}"

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": user.email,
        "first_name": user.first_name or "Guest",
        "last_name": user.last_name or "User",
        "tx_ref": tx_ref,
        "callback_url": request.build_absolute_uri(f"/api/payments/verify/{tx_ref}/"),
        "return_url": request.build_absolute_uri(f"/api/payments/verify/{tx_ref}/"),
        "customization[title]": "Booking Payment",
        "customization[description]": "Payment for property booking",
    }

    response = requests.post(f"{CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {})
        checkout_url = data.get("checkout_url")

        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            user=user,
            amount=amount,
            transaction_reference=tx_ref,
            chapa_tx_ref=data.get("tx_ref"),
            status='pending'
        )

        return Response({
            "payment_id": str(payment.payment_id),
            "checkout_url": checkout_url,
            "tx_ref": tx_ref,
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Failed to initiate payment", "details": response.json()}, status=response.status_code)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_payment(request, tx_ref):
    """
    Verifies payment with Chapa API
    """
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }

    response = requests.get(f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}", headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {})
        status_code = data.get("status")

        try:
            payment = Payment.objects.get(transaction_reference=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if status_code == "success":
            payment.status = "completed"
            payment.booking.status = "confirmed"
            payment.booking.save()
            payment.save()
            # Optionally trigger Celery email task here
        else:
            payment.status = "failed"
            payment.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Verification failed", "details": response.json()}, status=response.status_code)
