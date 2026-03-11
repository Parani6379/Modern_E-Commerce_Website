# 🌸 The Ecom — Owner's Guide

Welcome to **The Ecom**! This guide will help you manage your online store.

---

## 👑 How to Create an Admin Account

If you don't have an admin account yet, you can create one easily using the terminal:

1. Open your terminal in the project folder
2. Run the command: `flask create-admin`
3. Enter your desired **username**, **email**, and **password** when prompted
4. Your admin account is now ready to use!

---

## 🔑 How to Log In

1. Open your website in a browser
2. Click **Login** (top-right corner)
3. Enter your **email** and **password**
4. Click **Sign In**
5. You'll see the **Admin Panel** since you're the owner

---

## 📦 How to Add a Category

You must create categories first before adding products.

1. Go to **Admin Panel → Categories** (left sidebar)
2. Type the category name (e.g. "Saree", "Dress", "Jewellery")
3. Click **Add Category**
4. Your category is now ready for products!

> 💡 **Tip:** If you delete a category, all products under it will also be deleted automatically.

---

## 🛍️ How to Add a Product

1. Go to **Admin Panel → Products** (left sidebar)
2. Click the **+ Add Product** button
3. Fill in the details:
   - **Product Name** — Give it a clear name
   - **Description** — Describe the product
   - **Base Price** — Set the price in ₹
   - **Stock** — How many are available
   - **Category** — Select a category from the dropdown
   - **Images** — Upload product photos (drag & drop or click)
4. Click **Add Product**

### 👗 Adding a Dress Product

If you select the **"Dress"** category, extra options will appear:

- **Adult Dress** → Set prices for each size (S, M, L, XL)
- **Child Dress** → Add age groups and set a price for each (e.g. Age 1-3: ₹300, Age 4-6: ₹400)

---

## 📋 How to Manage Orders

When a customer books a product, it appears in your orders.

### Order Status Flow

Every order goes through **5 steps** in this exact order:

| Step | Status | Meaning |
|------|--------|---------|
| 1 | **Enquiry** | Customer has placed the order (new) |
| 2 | **Ordered** | You've confirmed the order |
| 3 | **Paid** | Customer has made the payment |
| 4 | **Dispatched** | Product has been shipped (you'll enter a Tracking ID) |
| 5 | **Delivered** | Customer has received the product ✅ |

### How to Update an Order

1. Go to **Admin Panel → Orders**
2. Click **View** on any order
3. You'll see the current status and a button to advance to the next step
4. Click the **"Advance to..."** button
5. When advancing to **Dispatched**, you'll need to enter a **Tracking ID**
6. Once **Delivered**, the order is locked — no more changes

### How to Create a Manual Order

1. Go to **Admin Panel → Orders**
2. Click the **+ New Order** button
3. Fill in the customer's name, email, phone, and address
4. Select the product and enter the amount
5. Click **Create Order**

---

## 📨 Product Requests from Customers

If a customer can't find what they're looking for, they can submit a **Product Request** with a description and image.

1. Go to **Admin Panel → Product Requests** (left sidebar)
2. You'll see all requests with customer details and images
3. Use this to understand what your customers want!

---

## 👥 How to Manage Users

1. Go to **Admin Panel → Users** (left sidebar)
2. You can see all registered customers with their:
   - Name, email, phone
   - Role (Admin or Customer)
   - Join date & total orders
3. Use the **Search bar** to find specific users
4. Click **Delete** to remove a user (this also deletes their orders)

> ⚠️ You cannot delete your own admin account.

---

## 📊 Dashboard Overview

The **Dashboard** (home page of admin panel) gives you a quick summary:

- **Total Orders** — All orders received
- **Paid Orders** — Confirmed payments
- **Pending** — Orders waiting for action
- **Delivered** — Successfully completed
- **Revenue** — Total earnings from paid/dispatched/delivered orders
- **Charts** — Visual breakdown of revenue and expenses by month

---

## 💰 How to Track Expenses

1. Go to **Admin Panel → Expenses** (left sidebar)
2. Click **+ Add Expense**
3. Enter the title, amount, category, date, and notes
4. Click **Save** — it's now tracked in your dashboard charts

---

## 📸 Instagram Link

1. Go to **Admin Panel → Settings** (left sidebar)
2. Scroll to **Site Settings**
3. Paste your Instagram profile URL
4. Click **Save Changes**
5. The "Follow us on Instagram" button on the home page will link to your profile

---

## ⚙️ How to Update Your Profile

1. Go to **Admin Panel → Settings**
2. Update your username, email, phone, or address
3. Change your **password** (leave blank to keep current one)
4. Click on your **avatar** to upload a new profile photo
5. Click **Save Changes**

---

## 📧 Email Notifications

When a customer places an order:
- ✉️ The **customer** receives a booking confirmation email
- ✉️ **You (the owner)** receive a notification email with order details

---

## 🎨 For Customers — What They Can Do

Your customers can:
- 🏠 **Browse products** on the home page with search & category filters
- 📄 **View product details** with image gallery and descriptions
- 🛒 **Book a product** by filling in their details
- 📊 **Track their orders** in "My Orders" with a visual progress bar
- 📨 **Request a product** if something they want isn't available
- 📱 **Follow you on Instagram** via the button on the home page

---

## ❓ Quick FAQ

**Q: How do I start fresh?**
A: Delete all categories from Admin → Categories. This will remove all products and their orders too.

**Q: Can customers see admin pages?**
A: No. Only the owner (admin) can access the admin panel. Customers see only the store.

**Q: What happens when stock runs out?**
A: Products with 0 stock show as "Sold Out" and customers cannot book them.

**Q: Can I edit a product after adding it?**
A: Yes! Go to Admin → Products and click the **Edit** button on any product.

---

Made with ❤️ for **The Girlhub**
