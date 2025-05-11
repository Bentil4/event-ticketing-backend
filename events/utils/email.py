from django.core.mail import EmailMessage
import qrcode
from io import BytesIO

def send_ticket_email(ticket):
    # Generating QR code from ticket ID
    qr = qrcode.make(str(ticket.ticket_id))
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    subject = '🎟 Your Event Ticket'
    body = f"""
    Hi {ticket.owner_name},

    Thanks for your purchase. Your ticket ID is: {ticket.ticket_id}

    Show this QR code at the event entrance for validation.

    Regards,
    Event Team
    """
    email = EmailMessage(
        subject,
        body,
        to=[ticket.owner_email],
    )
    email.attach(f"ticket-{ticket.ticket_id}.png", buffer.read(), 'image/png')
    email.send()

    print("Sending ticket to:", ticket.owner_email)
    email.send()
    print("Ticket sent.")

