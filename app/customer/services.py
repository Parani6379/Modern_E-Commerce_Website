from app.extensions import db
from app.models import Order
from app.admin.services import save_uploaded_file


def create_order(customer, product, form_data, reference_file=None):
    """Create a new order from booking form data."""
    reference_image = ''
    if reference_file and reference_file.filename:
        reference_image = save_uploaded_file(reference_file) or ''

    # Determine correct price based on dress selection
    total_price = product.price
    selected_size = form_data.get('selected_size', '').strip()
    selected_age_group = form_data.get('selected_age_group', '').strip()

    if product.is_dress:
        if product.dress_type == 'adult' and selected_size:
            size_prices = product.get_size_prices()
            if selected_size in size_prices:
                total_price = size_prices[selected_size]
        elif product.dress_type == 'child' and selected_age_group:
            age_prices = product.get_age_prices()
            if selected_age_group in age_prices:
                total_price = age_prices[selected_age_group]

    order = Order(
        customer_id=customer.id,
        product_id=product.id,
        customer_name=form_data.get('name', '').strip(),
        customer_email=form_data.get('email', '').strip(),
        customer_phone=form_data.get('phone', '').strip(),
        customer_address=form_data.get('address', '').strip(),
        customer_instagram=form_data.get('instagram_id', '').strip(),
        preferences=form_data.get('preferences', '').strip(),
        reference_image=reference_image,
        total_price=total_price,
        selected_size=selected_size,
        selected_age_group=selected_age_group,
        status='enquiry',
    )
    db.session.add(order)
    db.session.commit()
    return order


def get_customer_orders(customer_id):
    """Return all orders for a customer, newest first."""
    return Order.query.filter_by(customer_id=customer_id)\
        .order_by(Order.created_at.desc()).all()
