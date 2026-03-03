from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail


def send_order_confirmation_to_customer(order):
    """Send booking confirmation email to the customer."""
    try:
        msg = Message(
            subject=f'Booking Confirmed — Order #{order.id} | The Girlhub',
            recipients=[order.customer_email],
        )
        msg.html = render_template('email/order_confirmation.html', order=order)
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f'Failed to send customer email: {e}')


def send_order_notification_to_admin(order):
    """Send order notification email to the owner (parani867@gmail.com)."""
    try:
        owner_email = current_app.config.get('ADMIN_EMAIL', 'parani867@gmail.com')
        if not owner_email:
            return

        msg = Message(
            subject=f'New Order #{order.id} from {order.customer_name} | The Girlhub',
            recipients=[owner_email],
        )
        msg.html = render_template('email/order_notification.html', order=order)
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f'Failed to send owner email: {e}')

