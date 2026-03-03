from flask import render_template, redirect, url_for, flash, request, Response, make_response
from flask_login import login_required, current_user
from app.customer import customer_bp
from app.customer.services import create_order, get_customer_orders
from app.models import Product, Category, ProductRequest, SiteSetting
from app.admin.services import save_uploaded_file
from app.extensions import db
from flask import current_app


@customer_bp.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category', 0, type=int)

    query = Product.query.filter_by(is_active=True)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.order_by(Product.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get('PRODUCTS_PER_PAGE', 12),
        error_out=False
    )
    categories = Category.query.order_by(Category.name).all()
    instagram_url = SiteSetting.get('instagram_url', '')
    return render_template('customer/home.html',
                           products=products, categories=categories,
                           search=search, category_id=category_id,
                           instagram_url=instagram_url)


@customer_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    return render_template('customer/product_detail.html',
                           product=product, related=related)


@customer_bp.route('/book/<int:product_id>', methods=['GET', 'POST'])
@login_required
def booking(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Validate required fields
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not all([name, email, phone, address]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('customer/booking.html', product=product)

        # Validate dress selection if applicable
        selected_size = request.form.get('selected_size', '').strip()
        selected_age_group = request.form.get('selected_age_group', '').strip()

        if product.is_dress:
            if product.dress_type == 'adult' and not selected_size:
                flash('Please select a size for this dress.', 'danger')
                return render_template('customer/booking.html', product=product)
            if product.dress_type == 'child' and not selected_age_group:
                flash('Please select an age group for this dress.', 'danger')
                return render_template('customer/booking.html', product=product)

        reference_file = request.files.get('reference_image')
        order = create_order(current_user, product, request.form, reference_file)

        # Try to send emails (non-blocking if mail not configured)
        try:
            from app.email.mail_service import (
                send_order_confirmation_to_customer,
                send_order_notification_to_admin
            )
            send_order_confirmation_to_customer(order)
            send_order_notification_to_admin(order)
        except Exception:
            pass  # Emails are optional -- don't break booking flow

        # Show confirmation popup instead of redirect
        return render_template('customer/booking.html',
                               product=product,
                               show_popup=True,
                               order_id=order.id)

    return render_template('customer/booking.html', product=product)


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    orders = get_customer_orders(current_user.id)
    return render_template('customer/dashboard.html', orders=orders)


# ══════════════════════════════════════════════════════════
#  PRODUCT REQUEST
# ══════════════════════════════════════════════════════════
@customer_bp.route('/product-request', methods=['GET', 'POST'])
@login_required
def product_request():
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        if not description:
            flash('Please provide a description of the product you are looking for.', 'danger')
            return render_template('customer/product_request.html')

        image_filename = ''
        image_file = request.files.get('sample_image')
        if image_file and image_file.filename:
            image_filename = save_uploaded_file(image_file) or ''

        pr = ProductRequest(
            customer_id=current_user.id,
            customer_name=current_user.username,
            customer_email=current_user.email,
            customer_phone=current_user.phone or '',
            image=image_filename,
            description=description,
        )
        db.session.add(pr)
        db.session.commit()
        flash('Your product request has been submitted! We will get back to you soon.', 'success')
        return redirect(url_for('customer.home'))

    return render_template('customer/product_request.html')


# ══════════════════════════════════════════════════════════
#  SEO: robots.txt & sitemap.xml
# ══════════════════════════════════════════════════════════
@customer_bp.route('/robots.txt')
def robots():
    sitemap_url = url_for('customer.sitemap', _external=True)
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /auth/
Sitemap: {sitemap_url}
"""
    return Response(content, mimetype='text/plain')


@customer_bp.route('/sitemap.xml')
def sitemap():
    from datetime import datetime
    pages = []
    base = request.host_url.rstrip('/')

    # Static pages
    pages.append({'loc': base + '/', 'priority': '1.0', 'changefreq': 'daily'})

    # All active products
    products = Product.query.filter_by(is_active=True).all()
    for p in products:
        pages.append({
            'loc': base + url_for('customer.product_detail', product_id=p.id),
            'priority': '0.8',
            'changefreq': 'weekly',
            'lastmod': p.updated_at.strftime('%Y-%m-%d') if p.updated_at else ''
        })

    # All categories
    categories = Category.query.all()
    for c in categories:
        pages.append({
            'loc': base + url_for('customer.home', category=c.id),
            'priority': '0.6',
            'changefreq': 'weekly'
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        if page.get('lastmod'):
            xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page.get("changefreq", "weekly")}</changefreq>\n'
        xml += f'    <priority>{page.get("priority", "0.5")}</priority>\n'
        xml += '  </url>\n'
    xml += '</urlset>'

    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response
