from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

PRODUCTS_CSV = 'products.csv'
ORDERS_CSV = 'orders.csv'
REVIEWS_CSV = 'reviews.csv'
USERS_CSV = 'users.csv'
LOGIN_LOGS_CSV = 'login_logs.csv'

# Helper to load products from CSV
def load_products():
    products = []
    if os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                products.append(row)
    return products

# Helper to save order to CSV
def save_order(username, cart):
    with open(ORDERS_CSV, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in cart:
            writer.writerow([username, item['id'], item['name'], item['quantity'], item['price']])

# Helper to load reviews
def load_reviews():
    reviews = []
    if os.path.exists(REVIEWS_CSV):
        with open(REVIEWS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                reviews.append(row)
    return reviews

# Helper to save review
def save_review(product_id, user, text, rating):
    file_exists = os.path.exists(REVIEWS_CSV)
    with open(REVIEWS_CSV, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['product_id', 'user', 'text', 'rating']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'product_id': product_id, 'user': user, 'text': text, 'rating': rating})

# Helper to load users
def load_users():
    users = []
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    return users

# Helper to update user profile
def update_user_profile(username, full_name):
    users = load_users()
    for user in users:
        if user['username'] == username:
            user['full_name'] = full_name
    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['full_name', 'username', 'email', 'password']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)

# Helper to log login attempts
def log_login(username, role):
    file_exists = os.path.exists(LOGIN_LOGS_CSV)
    with open(LOGIN_LOGS_CSV, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['username', 'role', 'login_time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'username': username, 'role': role, 'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

# Helper to log admin activities
def log_admin_activity(username, action, detail):
    file_exists = os.path.exists(LOGIN_LOGS_CSV)
    with open(LOGIN_LOGS_CSV, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['username', 'role', 'login_time', 'action', 'detail']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'username': username, 'role': 'admin', 'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'action': action, 'detail': detail})

# Routes
@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Validation
        if not full_name or not username or not email or not password:
            flash('All fields are required!', 'error')
            return render_template('register.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'error')
            return render_template('register.html')
        if '@' not in email or '.' not in email:
            flash('Invalid email format!', 'error')
            return render_template('register.html')
        users = load_users()
        for user in users:
            if user['username'] == username:
                flash('Username already exists!', 'error')
                return render_template('register.html')
        file_exists = os.path.exists(USERS_CSV)
        with open(USERS_CSV, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['full_name', 'username', 'email', 'password']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({'full_name': full_name, 'username': username, 'email': email, 'password': password})
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Admin login (unified credentials)
        if username == 'a01' and password == 'a01@1234':
            session.clear()
            session['admin'] = True
            session['username'] = 'a01'
            log_login('a01', 'admin')
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        # User login
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session.clear()
                session['username'] = username
                log_login(username, 'user')
                flash('Login successful!', 'success')
                return redirect(url_for('user_home'))
        flash('Invalid credentials!', 'error')
    return render_template('login.html')

@app.route('/user-home')
def user_home():
    if 'username' not in session or session.get('admin'):
        return redirect(url_for('login'))
    return render_template('user_home.html')

@app.route('/user-profile')
def user_profile():
    if 'username' not in session or session.get('admin'):
        return redirect(url_for('login'))
    username = session['username']
    users = load_users()
    user = next((u for u in users if u['username'] == username), None)
    full_name = user['full_name'] if user else ''
    email = user['email'] if user else ''
    # Load orders
    orders = []
    if os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    orders.append({'name': row[2], 'quantity': row[3], 'price': row[4], 'date': row[5] if len(row) > 5 else ''})
    favorites = []
    return render_template('profile.html', full_name=full_name, username=username, email=email, orders=orders, favorites=favorites)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'username' in session and not session.get('admin'):
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == session['username']:
                user['full_name'] = full_name
                user['email'] = email
                if password:
                    user['password'] = password
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['full_name', 'username', 'email', 'password']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
        flash('Profile updated!', 'success')
    return redirect(url_for('user_profile'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/order', methods=['GET'])
def order():
    if 'username' not in session or session.get('admin'):
        return redirect(url_for('login'))
    products = load_products()
    query = request.args.get('q', '').lower()
    if query:
        products = [p for p in products if query in p['name'].lower() or query in p['description'].lower()]
    return render_template('products.html', products=products, query=query)

@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('order'))
    reviews = [r for r in load_reviews() if r['product_id'] == product_id]
    product['reviews'] = reviews
    return render_template('product_detail.html', product=product)

@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'username' not in session or session.get('admin'):
        return redirect(url_for('login'))
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('order'))
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] = str(int(item['quantity']) + quantity)
            break
    else:
        cart.append({'id': product['id'], 'name': product['name'], 'quantity': str(quantity), 'price': product['price']})
    session['cart'] = cart
    flash('Added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'username' not in session or session.get('admin'):
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    total = sum(float(item['price']) * int(item['quantity']) for item in cart)
    return render_template('cart.html', cart=cart, total=round(total, 2))

@app.route('/remove-from-cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'username' not in session or session.get('admin'):
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'username' not in session or session.get('admin'):
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    # Save order with timestamp
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(ORDERS_CSV, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in cart:
            writer.writerow([session['username'], item['id'], item['name'], item['quantity'], item['price'], now])
    session['cart'] = []
    flash('Order placed successfully!', 'success')
    return render_template('receipt.html', username=session['username'], cart=cart, total=sum(float(i['price'])*int(i['quantity']) for i in cart), order_time=now)

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    logs = []
    if os.path.exists(LOGIN_LOGS_CSV):
        with open(LOGIN_LOGS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    log = {'username': row[0], 'role': row[1], 'login_time': row[2]}
                    if len(row) > 3:
                        log['action'] = row[3]
                        log['detail'] = row[4] if len(row) > 4 else ''
                    logs.append(log)
    admin_logs = [log for log in logs if log['role'] == 'admin' and not log.get('action')]
    admin_activities = [log for log in logs if log['role'] == 'admin' and log.get('action')]
    return render_template('admin_login.html', admin_logs=admin_logs, admin_activities=admin_activities)

@app.route('/admin/orders')
def admin_orders():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    all_orders = []
    if os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                all_orders.append({'username': row[0], 'product_id': row[1], 'name': row[2], 'quantity': row[3], 'price': row[4], 'date': row[5] if len(row) > 5 else ''})
    return render_template('orders.html', orders=all_orders)

@app.route('/admin/inventory')
def admin_inventory():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    products = load_products()
    return render_template('products.html', products=products, query=None, admin=True)

@app.route('/admin/user-activity')
def admin_user_activity():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    activities = []
    if os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                activities.append({'type': 'Order', 'username': row[0], 'detail': f"Ordered {row[3]} x {row[2]}", 'date': row[5] if len(row) > 5 else ''})
    if os.path.exists(REVIEWS_CSV):
        with open(REVIEWS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                activities.append({'type': 'Review', 'username': row['user'], 'detail': f"Reviewed product {row['product_id']}: {row['text']} (Rating: {row['rating']})", 'date': ''})
    if os.path.exists(LOGIN_LOGS_CSV):
        with open(LOGIN_LOGS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['role'] == 'user':
                    activities.append({'type': 'Login', 'username': row['username'], 'detail': f"Logged in as user", 'date': row['login_time']})
    activities = sorted(activities, key=lambda x: x['date'], reverse=True)
    return render_template('user_activity.html', activities=activities)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['admin_username']
        password = request.form['admin_password']
        if username == 'a01' and password == 'a01@1234':
            session.clear()
            session['admin'] = True
            session['username'] = 'a01'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')
    return render_template('admin_login.html')

@app.route('/product/<product_id>/review', methods=['POST'])
def add_review(product_id):
    if 'username' not in session or session.get('admin'):
        flash('Please log in to review.', 'error')
        return redirect(url_for('login'))
    review_text = request.form.get('review')
    rating = request.form.get('rating')
    if not review_text or not rating:
        flash('Review and rating required.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    save_review(product_id, session['username'], review_text, rating)
    flash('Review submitted!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        products = load_products()
        new_id = str(max([int(p['id']) for p in products] + [0]) + 1)
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        image = request.form['image']
        with open(PRODUCTS_CSV, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'name', 'description', 'price', 'category', 'image']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if os.stat(PRODUCTS_CSV).st_size == 0:
                writer.writeheader()
            writer.writerow({'id': new_id, 'name': name, 'description': description, 'price': price, 'category': category, 'image': image})
        log_admin_activity(session.get('username', 'admin'), 'add_product', f"Added product {name} (ID: {new_id})")
        flash('Product added!', 'success')
        return redirect(url_for('admin_inventory'))
    return render_template('add_product.html')

@app.route('/admin/edit-product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('admin_inventory'))
    if request.method == 'POST':
        old_name = product['name']
        product['name'] = request.form['name']
        product['description'] = request.form['description']
        product['price'] = request.form['price']
        product['category'] = request.form['category']
        product['image'] = request.form['image']
        # Save all products back
        with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'name', 'description', 'price', 'category', 'image']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        log_admin_activity(session.get('username', 'admin'), 'edit_product', f"Edited product {product['name']} (ID: {product_id})")
        flash('Product updated!', 'success')
        return redirect(url_for('admin_inventory'))
    return render_template('edit_product.html', product=product)

@app.route('/admin/delete-product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    products = load_products()
    deleted_name = None
    for p in products:
        if p['id'] == product_id:
            deleted_name = p['name']
    products = [p for p in products if p['id'] != product_id]
    with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'name', 'description', 'price', 'category', 'image']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    if deleted_name:
        log_admin_activity(session.get('username', 'admin'), 'delete_product', f"Deleted product {deleted_name} (ID: {product_id})")
    flash('Product deleted!', 'success')
    return redirect(url_for('admin_inventory'))

@app.route('/api/order-status/<username>')
def api_order_status(username):
    orders = []
    if os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username:
                    orders.append({
                        'name': row[2],
                        'quantity': row[3],
                        'price': row[4],
                        'date': row[5] if len(row) > 5 else ''
                    })
    return jsonify({'orders': orders})

@app.route('/api/admin/inventory', methods=['GET'])
def api_admin_inventory():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    products = load_products()
    return jsonify({'products': products})

@app.route('/api/admin/inventory/add', methods=['POST'])
def api_add_product():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    products = load_products()
    new_id = str(max([int(p['id']) for p in products] + [0]) + 1)
    new_product = {
        'id': new_id,
        'name': data.get('name', ''),
        'price': data.get('price', ''),
        'stock': data.get('stock', ''),
        'image': data.get('image', '')
    }
    products.append(new_product)
    with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'name', 'price', 'stock', 'image']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    log_admin_activity(session.get('username', 'admin'), 'add_product', f"Added product {new_product['name']} (ID: {new_id})")
    return jsonify({'success': True, 'product': new_product})

@app.route('/api/admin/inventory/edit/<product_id>', methods=['POST'])
def api_edit_product(product_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    products = load_products()
    found = False
    for p in products:
        if p['id'] == product_id:
            p['name'] = data.get('name', p['name'])
            p['price'] = data.get('price', p['price'])
            p['stock'] = data.get('stock', p.get('stock', ''))
            p['image'] = data.get('image', p.get('image', ''))
            found = True
            log_admin_activity(session.get('username', 'admin'), 'edit_product', f"Edited product {p['name']} (ID: {product_id})")
    if not found:
        return jsonify({'error': 'Product not found'}), 404
    with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'name', 'price', 'stock', 'image']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    return jsonify({'success': True})

@app.route('/api/admin/inventory/delete/<product_id>', methods=['POST'])
def api_delete_product(product_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    products = load_products()
    deleted_name = None
    for p in products:
        if p['id'] == product_id:
            deleted_name = p['name']
    products = [p for p in products if p['id'] != product_id]
    with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'name', 'price', 'stock', 'image']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    if deleted_name:
        log_admin_activity(session.get('username', 'admin'), 'delete_product', f"Deleted product {deleted_name} (ID: {product_id})")
    return jsonify({'success': True})

@app.route('/api/admin/dashboard')
def api_admin_dashboard():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    logs = []
    if os.path.exists(LOGIN_LOGS_CSV):
        with open(LOGIN_LOGS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    log = {'username': row[0], 'role': row[1], 'login_time': row[2]}
                    if len(row) > 3:
                        log['action'] = row[3]
                        log['detail'] = row[4] if len(row) > 4 else ''
                    logs.append(log)
    admin_logs = [log for log in logs if log['role'] == 'admin' and not log.get('action')]
    admin_activities = [log for log in logs if log['role'] == 'admin' and log.get('action')]
    return jsonify({'admin_logs': admin_logs, 'admin_activities': admin_activities})

@app.route('/api/admin/orders')
def api_admin_orders():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_orders = []
    if os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                all_orders.append({'username': row[0], 'product_id': row[1], 'name': row[2], 'quantity': row[3], 'price': row[4], 'date': row[5] if len(row) > 5 else ''})
    return jsonify({'orders': all_orders})

@app.route('/api/admin/user-activity')
def api_admin_user_activity():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    activities = []
    if os.path.exists(ORDERS_CSV):
        with open(ORDERS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                activities.append({'type': 'Order', 'username': row[0], 'detail': f"Ordered {row[3]} x {row[2]}", 'date': row[5] if len(row) > 5 else ''})
    if os.path.exists(REVIEWS_CSV):
        with open(REVIEWS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                activities.append({'type': 'Review', 'username': row['user'], 'detail': f"Reviewed product {row['product_id']}: {row['text']} (Rating: {row['rating']})", 'date': ''})
    if os.path.exists(LOGIN_LOGS_CSV):
        with open(LOGIN_LOGS_CSV, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['role'] == 'user':
                    activities.append({'type': 'Login', 'username': row['username'], 'detail': f"Logged in as user", 'date': row['login_time']})
    activities = sorted(activities, key=lambda x: x['date'], reverse=True)
    return jsonify({'activities': activities})

if __name__ == '__main__':
    app.run(debug=True)
