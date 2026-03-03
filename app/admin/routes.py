import json
from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.admin.services import (
    get_dashboard_stats, get_monthly_revenue, get_monthly_expenses,
    save_product_images, save_uploaded_file, delete_file, allowed_file
)
from app.extensions import db
from app.models import Product, Category, Order, Expense, User, ProductRequest, ORDER_STATUSES


# ── Decorator: admin-only ─────────────────────────────────
def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════
@admin_bp.route('/')
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    revenue_data = get_monthly_revenue()
    expense_data = get_monthly_expenses()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           stats=stats,
                           revenue_data=revenue_data,
                           expense_data=expense_data,
                           recent_orders=recent_orders)


# ══════════════════════════════════════════════════════════
#  PRODUCTS
# ══════════════════════════════════════════════════════════
@admin_bp.route('/products')
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category', 0, type=int)

    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/products.html',
                           products=products, categories=categories,
                           search=search, category_id=category_id)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def product_add():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        stock = request.form.get('stock', 0, type=int)
        category_id = request.form.get('category_id', type=int) or None

        if not name:
            flash('Product name is required.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        images = save_product_images(request.files.getlist('images'))

        product = Product(
            name=name, description=description,
            price=price, stock=stock, category_id=category_id
        )
        product.set_images(images)

        # ── Dress-specific fields ─────────────────────────
        dress_type = request.form.get('dress_type', '').strip()
        if dress_type in ('adult', 'child'):
            product.dress_type = dress_type
            if dress_type == 'adult':
                sizes = ['S', 'M', 'L', 'XL']
                size_prices = {}
                for s in sizes:
                    p = request.form.get(f'size_price_{s}', 0, type=float)
                    if p > 0:
                        size_prices[s] = p
                product.set_size_prices(size_prices)
                product.set_age_prices({})
            else:  # child
                age_groups = request.form.getlist('age_group_name')
                age_prices_vals = request.form.getlist('age_group_price')
                age_prices = {}
                for ag, ap in zip(age_groups, age_prices_vals):
                    ag = ag.strip()
                    try:
                        ap = float(ap)
                    except (ValueError, TypeError):
                        ap = 0
                    if ag and ap > 0:
                        age_prices[ag] = ap
                product.set_age_prices(age_prices)
                product.set_size_prices({})
        else:
            product.dress_type = ''

        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=None)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.price = request.form.get('price', 0, type=float)
        product.stock = request.form.get('stock', 0, type=int)
        product.category_id = request.form.get('category_id', type=int) or None

        # Handle new images
        new_files = request.files.getlist('images')
        if new_files and new_files[0].filename:
            new_images = save_product_images(new_files)
            existing = product.get_images()
            product.set_images(existing + new_images)

        # Handle removed images
        removed = request.form.getlist('remove_images')
        if removed:
            current_imgs = product.get_images()
            for img in removed:
                if img in current_imgs:
                    current_imgs.remove(img)
                    delete_file(img)
            product.set_images(current_imgs)

        # ── Dress-specific fields ─────────────────────────
        dress_type = request.form.get('dress_type', '').strip()
        if dress_type in ('adult', 'child'):
            product.dress_type = dress_type
            if dress_type == 'adult':
                sizes = ['S', 'M', 'L', 'XL']
                size_prices = {}
                for s in sizes:
                    p = request.form.get(f'size_price_{s}', 0, type=float)
                    if p > 0:
                        size_prices[s] = p
                product.set_size_prices(size_prices)
                product.set_age_prices({})
            else:  # child
                age_groups = request.form.getlist('age_group_name')
                age_prices_vals = request.form.getlist('age_group_price')
                age_prices = {}
                for ag, ap in zip(age_groups, age_prices_vals):
                    ag = ag.strip()
                    try:
                        ap = float(ap)
                    except (ValueError, TypeError):
                        ap = 0
                    if ag and ap > 0:
                        age_prices[ag] = ap
                product.set_age_prices(age_prices)
                product.set_size_prices({})
        else:
            product.dress_type = ''
            product.set_size_prices({})
            product.set_age_prices({})

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=product)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    # Delete images from disk
    for img in product.get_images():
        delete_file(img)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.products'))


# ══════════════════════════════════════════════════════════
#  CATEGORIES
# ══════════════════════════════════════════════════════════
@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            if Category.query.filter_by(name=name).first():
                flash('Category already exists.', 'warning')
            else:
                db.session.add(Category(name=name))
                db.session.commit()
                flash('Category added!', 'success')
        else:
            flash('Category name is required.', 'danger')
    cats = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@admin_required
def category_delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))


# ══════════════════════════════════════════════════════════
#  ORDERS
# ══════════════════════════════════════════════════════════
@admin_bp.route('/orders')
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False)
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order, statuses=ORDER_STATUSES)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status', '').strip()

    # Block if order is already delivered
    if order.is_locked:
        flash('This order is delivered and locked. No further changes allowed.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    # Validate the new status transition
    if not order.can_advance_to(new_status):
        flash(f'Invalid status transition. Orders must follow the sequence: Enquiry -> Ordered -> Paid -> Dispatched -> Delivered.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    # Require tracking ID for dispatched
    if new_status == 'dispatched':
        tracking_id = request.form.get('tracking_id', '').strip()
        if not tracking_id:
            flash('Tracking ID is required before marking as Dispatched.', 'danger')
            return redirect(url_for('admin.order_detail', order_id=order.id))
        order.tracking_id = tracking_id

    order.status = new_status
    db.session.commit()
    flash(f'Order #{order.id} status updated to {new_status.title()}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))


# ── Admin Manual Order Entry ─────────────────────────────
@admin_bp.route('/orders/add', methods=['GET', 'POST'])
@admin_required
def order_add():
    products_list = Product.query.filter_by(is_active=True).order_by(Product.name).all()

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        customer_address = request.form.get('customer_address', '').strip()
        product_id = request.form.get('product_id', type=int)
        amount = request.form.get('amount', 0, type=float)
        preferences = request.form.get('preferences', '').strip()

        if not all([customer_name, customer_email, customer_phone]):
            flash('Customer name, email, and phone are required.', 'danger')
            return render_template('admin/order_form.html', products=products_list)

        # Use the admin user as the customer_id for manual orders
        order = Order(
            customer_id=current_user.id,
            product_id=product_id if product_id else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_address=customer_address,
            preferences=preferences,
            total_price=amount,
            status='enquiry',
        )
        db.session.add(order)
        db.session.commit()
        flash(f'Manual order #{order.id} created successfully!', 'success')
        return redirect(url_for('admin.orders'))

    return render_template('admin/order_form.html', products=products_list)


# ══════════════════════════════════════════════════════════
#  PRODUCT REQUESTS
# ══════════════════════════════════════════════════════════
@admin_bp.route('/product-requests')
@admin_required
def product_requests():
    page = request.args.get('page', 1, type=int)
    requests_list = ProductRequest.query.order_by(
        ProductRequest.created_at.desc()
    ).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/product_requests.html', requests=requests_list)


# ══════════════════════════════════════════════════════════
#  EXPENSES
# ══════════════════════════════════════════════════════════
@admin_bp.route('/expenses')
@admin_required
def expenses():
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=15, error_out=False)
    total = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    return render_template('admin/expenses.html', expenses=expenses, total=total)


@admin_bp.route('/expenses/add', methods=['GET', 'POST'])
@admin_required
def expense_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount = request.form.get('amount', 0, type=float)
        category = request.form.get('category', 'General').strip()
        date_str = request.form.get('date', '')
        notes = request.form.get('notes', '').strip()

        if not title:
            flash('Expense title is required.', 'danger')
            return render_template('admin/expense_form.html', expense=None)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now(timezone.utc).date()
        except ValueError:
            date = datetime.now(timezone.utc).date()

        expense = Expense(title=title, amount=amount, category=category, date=date, notes=notes)
        db.session.add(expense)
        db.session.commit()
        flash('Expense added!', 'success')
        return redirect(url_for('admin.expenses'))

    return render_template('admin/expense_form.html', expense=None)


@admin_bp.route('/expenses/edit/<int:expense_id>', methods=['GET', 'POST'])
@admin_required
def expense_edit(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if request.method == 'POST':
        expense.title = request.form.get('title', '').strip()
        expense.amount = request.form.get('amount', 0, type=float)
        expense.category = request.form.get('category', 'General').strip()
        date_str = request.form.get('date', '')
        expense.notes = request.form.get('notes', '').strip()

        try:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else expense.date
        except ValueError:
            pass

        db.session.commit()
        flash('Expense updated!', 'success')
        return redirect(url_for('admin.expenses'))

    return render_template('admin/expense_form.html', expense=expense)


@admin_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@admin_required
def expense_delete(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('admin.expenses'))


# ══════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    from app.models import SiteSetting

    if request.method == 'POST':
        current_user.username = request.form.get('username', current_user.username).strip()
        current_user.email = request.form.get('email', current_user.email).strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.address = request.form.get('address', '').strip()

        new_password = request.form.get('new_password', '').strip()
        if new_password:
            current_user.set_password(new_password)

        avatar = request.files.get('avatar')
        if avatar and avatar.filename:
            filename = save_uploaded_file(avatar)
            if filename:
                if current_user.avatar:
                    delete_file(current_user.avatar)
                current_user.avatar = filename

        # Save site-wide settings
        instagram_url = request.form.get('instagram_url', '').strip()
        SiteSetting.set('instagram_url', instagram_url)

        db.session.commit()
        flash('Settings updated!', 'success')
        return redirect(url_for('admin.settings'))

    instagram_url = SiteSetting.get('instagram_url', '')
    return render_template('admin/settings.html', instagram_url=instagram_url)


# ══════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ══════════════════════════════════════════════════════════
@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.phone.ilike(f'%{search}%'),
            )
        )

    users_list = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users_list, search=search)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))

    username = user.username

    # Delete user's orders first
    Order.query.filter_by(customer_id=user.id).delete()
    # Delete user's product requests
    ProductRequest.query.filter_by(customer_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" has been deleted.', 'success')
    return redirect(url_for('admin.users'))
