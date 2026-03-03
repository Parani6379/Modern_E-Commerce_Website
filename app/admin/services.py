import os
import json
import uuid
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import current_app
from app.extensions import db
from app.models import Product, Order, Expense, Category, User


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file):
    """Save a single uploaded file and return the filename."""
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


def save_product_images(files):
    """Save multiple product images and return list of filenames."""
    saved = []
    for f in files:
        filename = save_uploaded_file(f)
        if filename:
            saved.append(filename)
    return saved


def delete_file(filename):
    """Delete an uploaded file."""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)


def get_dashboard_stats():
    """Return aggregate statistics for the admin dashboard."""
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).filter(
        Order.status.in_(['paid', 'dispatched', 'delivered'])
    ).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_customers = User.query.filter_by(role='customer').count()
    profit = total_revenue - total_expenses

    # New status counts
    enquiry_orders = Order.query.filter_by(status='enquiry').count()
    ordered_orders = Order.query.filter_by(status='ordered').count()
    paid_orders = Order.query.filter_by(status='paid').count()
    dispatched_orders = Order.query.filter_by(status='dispatched').count()
    delivered_orders = Order.query.filter_by(status='delivered').count()
    pending_orders = enquiry_orders + ordered_orders  # Not yet paid

    return {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_customers': total_customers,
        'profit': profit,
        'enquiry_orders': enquiry_orders,
        'ordered_orders': ordered_orders,
        'paid_orders': paid_orders,
        'dispatched_orders': dispatched_orders,
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders,
    }


def get_monthly_revenue(year=None):
    """Return monthly revenue data for Chart.js."""
    if year is None:
        year = datetime.now(timezone.utc).year

    monthly = []
    for month in range(1, 13):
        rev = db.session.query(db.func.sum(Order.total_price)).filter(
            db.extract('year', Order.created_at) == year,
            db.extract('month', Order.created_at) == month,
            Order.status.in_(['paid', 'dispatched', 'delivered']),
        ).scalar() or 0
        monthly.append(round(rev, 2))
    return monthly


def get_monthly_expenses(year=None):
    """Return monthly expense data for Chart.js."""
    if year is None:
        year = datetime.now(timezone.utc).year

    monthly = []
    for month in range(1, 13):
        exp = db.session.query(db.func.sum(Expense.amount)).filter(
            db.extract('year', Expense.date) == year,
            db.extract('month', Expense.date) == month,
        ).scalar() or 0
        monthly.append(round(exp, 2))
    return monthly
