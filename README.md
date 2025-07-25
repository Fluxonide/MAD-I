# Vehicle Parking Management System

## Installation & Setup

1. Clone the repository

   ```bash
   git clone https://github.com/Fluxonide/MAD-I.git
   cd MAD-I
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application

   ```bash
   python app.py
   ```

4. Access at `http://localhost:5000`

Admin Login: username: `admin`, password: `admin123`

## File Structure

```
MAD-I/
├── app.py                    # Main Flask application
├── requirements.txt          # Dependencies
├── README.md                # Documentation
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Landing page
│   ├── login.html          # Login form
│   ├── register.html       # Registration form
│   ├── admin_dashboard.html # Admin dashboard
│   ├── user_dashboard.html  # User dashboard
│   └── view_lot.html       # Parking lot details
└── parking.db              # SQLite database (auto-created)
```
