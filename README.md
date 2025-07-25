# Vehicle Parking Management System

A minimal black and white web application for managing parking lots, parking spots, and vehicle reservations built with Flask.

## Features

### Admin Features

- **Dashboard**: View all parking lots, users, and statistics
- **Parking Lot Management**: Create, view, and delete parking lots
- **Spot Monitoring**: Real-time view of parking spot status (available/occupied)
- **User Management**: View all registered users
- **Visual Spot Grid**: Graphical representation of parking spots

### User Features

- **Registration/Login**: Secure user authentication
- **Dashboard**: View available parking lots and current reservations
- **Spot Booking**: Automatically allocate first available spot in selected lot
- **Spot Release**: Release parking spot and calculate cost
- **Cost Calculation**: Automatic billing based on parking duration

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Jinja2 Templates
- **Database**: SQLite
- **Authentication**: Session-based with SHA256 password hashing
- **UI Design**: Minimal black and white theme

## Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Fluxonide/MAD-I.git
   cd MAD-I
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## Default Login Credentials

### Admin Access

- **Username**: `admin`
- **Password**: `admin123`

### User Access

- Register a new account or use any registered user credentials

## Database Schema

### Users Table

- `id` (Primary Key)
- `username` (Unique)
- `password` (SHA256 hashed)
- `role` (admin/user)

### Parking Lots Table

- `id` (Primary Key)
- `prime_location_name`
- `price` (per hour in ₹)
- `address`
- `pin_code`
- `maximum_number_of_spots`

### Parking Spots Table

- `id` (Primary Key)
- `lot_id` (Foreign Key)
- `status` (A=Available, O=Occupied)

### Reservations Table

- `id` (Primary Key)
- `spot_id` (Foreign Key)
- `user_id` (Foreign Key)
- `parking_timestamp`
- `leaving_timestamp`
- `parking_cost`

## Application Flow

1. **Admin Workflow**:

   - Login with admin credentials
   - Create parking lots with specified number of spots
   - Monitor real-time spot occupancy
   - View user activity and statistics

2. **User Workflow**:
   - Register/Login to the system
   - Browse available parking lots
   - Book first available spot in chosen lot
   - Park vehicle (spot status changes to occupied)
   - Release spot when leaving (automatic cost calculation)

## Key Features Implementation

- **Automatic Spot Allocation**: Users cannot select specific spots; system allocates first available
- **Real-time Status Updates**: Spot status changes immediately upon booking/release
- **Cost Calculation**: Based on parking duration and hourly rates
- **Validation**: Prevents deletion of lots with occupied spots
- **Session Management**: Secure user sessions with role-based access

## File Structure

```
MAD-I/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   ├── index.html        # Landing page
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── admin_dashboard.html  # Admin dashboard
│   ├── user_dashboard.html   # User dashboard
│   └── view_lot.html     # Parking lot details
└── parking.db           # SQLite database (auto-created)
```

## Design Philosophy

- **Minimal UI**: Clean black and white interface
- **Responsive Design**: Works on desktop and mobile devices
- **User-Friendly**: Intuitive navigation and clear feedback
- **Secure**: Password hashing and session management
- **Efficient**: Automatic database creation and management

## Currency

All pricing is displayed in Indian Rupees (₹).

## Development Notes

- Database is created automatically on first run
- Admin user is created during database initialization
- All forms include basic validation
- Error messages and success notifications via Flask flash messages
- Debug mode enabled for development

## Future Enhancements

- Payment gateway integration
- Email notifications
- Advanced reporting and analytics
- Mobile app development
- Multi-level parking support

## License

This project is developed for educational purposes as part of the Modern Application Development course.

## Author

Developed as part of MAD-I project requirements.
