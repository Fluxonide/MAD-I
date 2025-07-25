from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )''')
    
    # Parking lots table
    c.execute('''CREATE TABLE IF NOT EXISTS parking_lots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prime_location_name TEXT NOT NULL,
        price REAL NOT NULL,
        address TEXT NOT NULL,
        pin_code TEXT NOT NULL,
        maximum_number_of_spots INTEGER NOT NULL
    )''')
    
    # Parking spots table
    c.execute('''CREATE TABLE IF NOT EXISTS parking_spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lot_id INTEGER,
        status TEXT DEFAULT 'A',
        FOREIGN KEY (lot_id) REFERENCES parking_lots (id)
    )''')
    
    # Reservations table
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_id INTEGER,
        user_id INTEGER,
        parking_timestamp DATETIME,
        leaving_timestamp DATETIME,
        parking_cost REAL,
        FOREIGN KEY (spot_id) REFERENCES parking_spots (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Create admin user if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 ('admin', admin_password, 'admin'))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('parking.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and user[2] == hashlib.sha256(password.encode()).hexdigest():
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('parking.db')
        c = conn.cursor()
        
        # Check if username exists
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            flash('Username already exists')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashed_password, 'user'))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Get parking lots with spot counts
    c.execute('''SELECT pl.*, 
                 COALESCE(COUNT(ps.id), 0) as total_spots,
                 COALESCE(SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END), 0) as available_spots,
                 COALESCE(SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END), 0) as occupied_spots
                 FROM parking_lots pl
                 LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
                 GROUP BY pl.id''')
    lots = c.fetchall()
    
    # Get total users
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_users = c.fetchone()[0]
    
    conn.close()
    
    return render_template('admin_dashboard.html', lots=lots, total_users=total_users)

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Get available parking lots
    c.execute('''SELECT pl.*, 
                 COALESCE(COUNT(ps.id), 0) as total_spots,
                 COALESCE(SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END), 0) as available_spots
                 FROM parking_lots pl
                 LEFT JOIN parking_spots ps ON pl.id = ps.lot_id
                 GROUP BY pl.id
                 HAVING available_spots > 0''')
    available_lots = c.fetchall()
    
    # Get user's current reservations
    c.execute('''SELECT r.*, ps.id as spot_number, pl.prime_location_name
                 FROM reservations r
                 JOIN parking_spots ps ON r.spot_id = ps.id
                 JOIN parking_lots pl ON ps.lot_id = pl.id
                 WHERE r.user_id = ? AND r.leaving_timestamp IS NULL''',
              (session['user_id'],))
    current_reservations = c.fetchall()
    
    conn.close()
    
    return render_template('user_dashboard.html', 
                         available_lots=available_lots, 
                         current_reservations=current_reservations)

@app.route('/admin/create_lot', methods=['POST'])
def create_lot():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    location_name = request.form['location_name']
    price = float(request.form['price'])
    address = request.form['address']
    pin_code = request.form['pin_code']
    max_spots = int(request.form['max_spots'])
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Create parking lot
    c.execute('''INSERT INTO parking_lots 
                 (prime_location_name, price, address, pin_code, maximum_number_of_spots)
                 VALUES (?, ?, ?, ?, ?)''',
              (location_name, price, address, pin_code, max_spots))
    
    lot_id = c.lastrowid
    
    # Create parking spots for this lot
    for i in range(max_spots):
        c.execute("INSERT INTO parking_spots (lot_id, status) VALUES (?, 'A')",
                 (lot_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Parking lot "{location_name}" created with {max_spots} spots!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/lot/<int:lot_id>')
def view_lot(lot_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Get lot details
    c.execute("SELECT * FROM parking_lots WHERE id = ?", (lot_id,))
    lot = c.fetchone()
    
    # Get spots with reservation details
    c.execute('''SELECT ps.id, ps.status, u.username, r.parking_timestamp
                 FROM parking_spots ps
                 LEFT JOIN reservations r ON ps.id = r.spot_id AND r.leaving_timestamp IS NULL
                 LEFT JOIN users u ON r.user_id = u.id
                 WHERE ps.lot_id = ?
                 ORDER BY ps.id''', (lot_id,))
    spots = c.fetchall()
    
    conn.close()
    
    return render_template('view_lot.html', lot=lot, spots=spots)

@app.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Check if any spots are occupied
    c.execute("SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = 'O'", (lot_id,))
    occupied_count = c.fetchone()[0]
    
    if occupied_count > 0:
        flash('Cannot delete lot with occupied spots!')
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    # Delete spots first, then lot
    c.execute("DELETE FROM parking_spots WHERE lot_id = ?", (lot_id,))
    c.execute("DELETE FROM parking_lots WHERE id = ?", (lot_id,))
    
    conn.commit()
    conn.close()
    
    flash('Parking lot deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/user/book/<int:lot_id>')
def book_spot(lot_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Check if user already has a reservation
    c.execute("SELECT COUNT(*) FROM reservations WHERE user_id = ? AND leaving_timestamp IS NULL",
              (session['user_id'],))
    if c.fetchone()[0] > 0:
        flash('You already have an active reservation!')
        conn.close()
        return redirect(url_for('user_dashboard'))
    
    # Find first available spot in the lot
    c.execute("SELECT id FROM parking_spots WHERE lot_id = ? AND status = 'A' LIMIT 1",
              (lot_id,))
    spot = c.fetchone()
    
    if not spot:
        flash('No available spots in this lot!')
        conn.close()
        return redirect(url_for('user_dashboard'))
    
    spot_id = spot[0]
    
    # Create reservation and update spot status
    c.execute('''INSERT INTO reservations (spot_id, user_id, parking_timestamp)
                 VALUES (?, ?, ?)''',
              (spot_id, session['user_id'], datetime.now()))
    
    c.execute("UPDATE parking_spots SET status = 'O' WHERE id = ?", (spot_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Parking spot #{spot_id} booked successfully!')
    return redirect(url_for('user_dashboard'))

@app.route('/user/release/<int:reservation_id>')
def release_spot(reservation_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    
    # Get reservation details
    c.execute('''SELECT r.*, pl.price FROM reservations r
                 JOIN parking_spots ps ON r.spot_id = ps.id
                 JOIN parking_lots pl ON ps.lot_id = pl.id
                 WHERE r.id = ? AND r.user_id = ?''',
              (reservation_id, session['user_id']))
    reservation = c.fetchone()
    
    if not reservation:
        flash('Reservation not found!')
        conn.close()
        return redirect(url_for('user_dashboard'))
    
    # Calculate parking cost
    parking_start = datetime.strptime(reservation[3], '%Y-%m-%d %H:%M:%S.%f')
    parking_end = datetime.now()
    hours_parked = (parking_end - parking_start).total_seconds() / 3600
    cost = hours_parked * reservation[6]  # price from join
    
    # Update reservation and spot status
    c.execute('''UPDATE reservations 
                 SET leaving_timestamp = ?, parking_cost = ?
                 WHERE id = ?''',
              (parking_end, cost, reservation_id))
    
    c.execute("UPDATE parking_spots SET status = 'A' WHERE id = ?", (reservation[1],))
    
    conn.commit()
    conn.close()
    
    flash(f'Spot released! Total cost: ₹{cost:.2f}')
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)