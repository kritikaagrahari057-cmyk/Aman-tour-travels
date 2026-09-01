from flask import Flask, render_template, request, session, redirect, url_for, flash
import requests
import os
from dotenv import load_dotenv

# .env file se secret data nikalne ke liye
load_dotenv()

# Flask app start kiya
app = Flask(__name__)
# Session secure rakhne ke liye secret key
app.secret_key = "my_super_secret_travel_key" 

# FastAPI backend ka address
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ==========================================
# 1. HOME ROUTE
# ==========================================
@app.route('/')
def home():
    # Website ka main page dikhayega
    return render_template('home.html') 

# ==========================================
# 2. LOGIN ROUTE
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jab user login form submit karega
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Backend API ka link
            api_login_url = f"{API_URL}/auth/login"
            data = {"email": email, "password": password}
            
            # FastAPI ko data bheja
            response = requests.post(api_login_url, json=data)

            if response.status_code == 200:
                token_data = response.json()
                
                # Token aur user details session me save kiye
                session['access_token'] = token_data.get('access_token')
                session['full_name'] = token_data.get('full_name')
                session['email'] = email 
                
                flash("Login successful!", "success")
                
                # Agar admin hai toh admin page pe bhejo
                if email.lower() == "aman@gmail.com":
                    return redirect(url_for('admin_dashboard'))
                # Normal user ko customer page pe bhejo
                else:
                    return redirect(url_for('customer_dashboard')) 
                    
            else:
                flash("Invalid email or password", "danger")
        except Exception as e:
            flash(f"Could not connect to backend: {e}", "danger")

    # Agar normal page open kiya hai toh form dikhao
    return render_template('login.html')

# ==========================================
# 3. REGISTER ROUTE
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Jab naya user form bharega
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        try:
            api_register_url = f"{API_URL}/auth/register"
            user_data = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "password": password
            }
            
            # FastAPI ko naye user ka data bheja
            response = requests.post(api_register_url, json=user_data)

            if response.status_code == 200:
                flash("Account created successfully! Please login.", "success")
                # Signup ke baad login page par bhejo
                return redirect(url_for('login')) 
            else:
                error_message = response.json().get('detail', 'Registration failed')
                flash(error_message, "danger")
        except Exception as e:
            flash("Could not connect to backend server.", "danger")

    return render_template('register.html')

# ==========================================
# 4. SECURE DASHBOARD ROUTES
# ==========================================

# ==========================================
# CUSTOMER LIST ROUTE (For Admin)
# ==========================================
@app.route('/customers')
def customers():
    # Security check: Sirf login kiya hua admin hi isey dekh sake
    if 'access_token' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))
    
    # -------------------------------------------------------------
    # 🚀 DUMMY DATA (Jab tak backend API ready nahi hoti, tab tak 
    # ye data page par cards dikhayega taaki design test ho sake)
    # -------------------------------------------------------------
    dummy_customers = [
        {"id": "AT-101", "full_name": "Rahul Sharma", "email": "rahul@example.com", "phone": "9876543210"},
        {"id": "AT-102", "full_name": "Kritika Patel", "email": "k@gmail.com", "phone": "8765432109"},
        {"id": "AT-103", "full_name": "Aman", "email": "aman@gmail.com", "phone": ""}, # Phone missing case test
        {"id": "AT-104", "full_name": "", "email": "unknown@example.com", "phone": "9998887776"} # Name missing case test
    ]
        
    # Yahan humne 'customer=dummy_customers' pass kiya hai, 
    # jisse HTML file ka {% for item in customer %} chal padega!
    return render_template('customer_list.html', customer=dummy_customers)

# Admin Dashboard Route
@app.route('/admin-dashboard')
def admin_dashboard():
    # Bina login ke admin page pe aane se rokne ke liye check
    if 'access_token' not in session:
        flash("Please login to access the admin panel.", "warning")
        return redirect(url_for('login'))
        
    return render_template('admin_dashboard.html')

# ==========================================
# 5. LOGOUT ROUTE
# ==========================================
@app.route('/logout')
def logout():
    # Session ka saara data delete kar do (Logout)
    session.clear() 
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

# Server start karne ka code
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)