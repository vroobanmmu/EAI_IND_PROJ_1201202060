# Soy Joy

Soy Joy is an online platform for selling soy-based products. This Flask web application includes user registration, login, profile management, product catalog, reviews, shopping cart, and admin features. Data is stored in CSV files for easy prototyping.

## Features
- User registration and login
- Profile management & user dashboard
- Product catalog with search, reviews, and ratings
- Shopping cart and checkout
- Admin login, order management, inventory management
- Flash message feedback
- Responsive, modern design with Montserrat font, animations, and professional UI/UX

## Getting Started
1. Install dependencies: `pip install flask`
2. (Optional for desktop GUI) `pip install PyQt5`
3. Run the app: `python app.py`
4. Open your browser at `http://127.0.0.1:5000/`

## Project Structure
- `app.py` - Main Flask application
- `soyjoy_desktop_gui.py` - Desktop GUI launcher
- `templates/` - HTML templates
- `static/` - CSS and static files
- `users.csv` - User data storage
- `products.csv` - Product catalog
- `orders.csv` - Order data

## Next Steps
- Add product images to `/static/images/`
- Further enhance admin dashboard
- Add more interactivity with JavaScript if needed
