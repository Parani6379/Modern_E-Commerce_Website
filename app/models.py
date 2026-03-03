from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager
import json


# ── User loader for Flask-Login ──────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── USER ─────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin | customer
    phone = db.Column(db.String(20), default='')
    address = db.Column(db.Text, default='')
    avatar = db.Column(db.String(256), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    product_requests = db.relationship('ProductRequest', backref='requester', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


# ── CATEGORY ─────────────────────────────────────────────
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    products = db.relationship('Product', backref='category', lazy='dynamic',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'


# ── PRODUCT ──────────────────────────────────────────────
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    images = db.Column(db.Text, default='[]')  # JSON list of filenames
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # ── Dress-specific fields ─────────────────────────────
    dress_type = db.Column(db.String(10), default='')       # 'adult' | 'child' | ''
    size_prices = db.Column(db.Text, default='{}')           # JSON: {"S": 500, "M": 600, ...}
    age_prices = db.Column(db.Text, default='{}')            # JSON: {"1-3": 400, "4-6": 500, ...}

    orders = db.relationship('Order', backref='product', lazy='dynamic',
                             cascade='all, delete-orphan')

    def get_images(self):
        try:
            return json.loads(self.images)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_images(self, image_list):
        self.images = json.dumps(image_list)

    def get_size_prices(self):
        try:
            return json.loads(self.size_prices)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_size_prices(self, prices):
        self.size_prices = json.dumps(prices)

    def get_age_prices(self):
        try:
            return json.loads(self.age_prices)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_age_prices(self, prices):
        self.age_prices = json.dumps(prices)

    @property
    def is_dress(self):
        """Check if this product belongs to a 'Dress' category."""
        return self.category and self.category.name.lower() == 'dress'

    @property
    def primary_image(self):
        imgs = self.get_images()
        return imgs[0] if imgs else None

    def __repr__(self):
        return f'<Product {self.name}>'


# ── ORDER ────────────────────────────────────────────────
# Status flow: enquiry → ordered → paid → dispatched → delivered
ORDER_STATUSES = ['enquiry', 'ordered', 'paid', 'dispatched', 'delivered']


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)

    # Customer details captured at booking time
    customer_name = db.Column(db.String(150), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    customer_instagram = db.Column(db.String(100), default='')  # Instagram ID (optional)
    preferences = db.Column(db.Text, default='')
    reference_image = db.Column(db.String(256), default='')

    # Status: enquiry → ordered → paid → dispatched → delivered
    status = db.Column(db.String(20), nullable=False, default='enquiry')
    tracking_id = db.Column(db.String(100), default='')
    total_price = db.Column(db.Float, nullable=False, default=0.0)

    # Dress selection (if applicable)
    selected_size = db.Column(db.String(10), default='')
    selected_age_group = db.Column(db.String(20), default='')

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    @property
    def status_color(self):
        return {
            'enquiry': 'yellow',
            'ordered': 'blue',
            'paid': 'indigo',
            'dispatched': 'purple',
            'delivered': 'green',
        }.get(self.status, 'gray')

    @property
    def is_locked(self):
        return self.status == 'delivered'

    def can_advance_to(self, new_status):
        """Check if the order can advance to the given status."""
        if self.is_locked:
            return False
        if new_status not in ORDER_STATUSES:
            return False
        current_idx = ORDER_STATUSES.index(self.status) if self.status in ORDER_STATUSES else -1
        new_idx = ORDER_STATUSES.index(new_status)
        return new_idx == current_idx + 1

    def __repr__(self):
        return f'<Order #{self.id} — {self.status}>'


# ── PRODUCT REQUEST ──────────────────────────────────────
class ProductRequest(db.Model):
    __tablename__ = 'product_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), default='')
    image = db.Column(db.String(256), default='')
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<ProductRequest #{self.id} by {self.customer_name}>'


# ── EXPENSE ──────────────────────────────────────────────
class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(100), default='General')
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Expense {self.title} — ₹{self.amount}>'


# ── SITE SETTINGS (key-value store) ──────────────────────
class SiteSetting(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, default='')

    @classmethod
    def get(cls, key, default=''):
        """Get a setting value by key."""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value):
        """Set a setting value by key (create or update)."""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

    def __repr__(self):
        return f'<SiteSetting {self.key}={self.value}>'
