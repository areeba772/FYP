# Smart Cafe System - Setup Instructions

## 🗄️ Database Setup

### Step 1: Create Database
Run the SQL file to create all tables:

```bash
mysql -u root -p < backend/database_schema.sql
```

Or manually run the SQL commands from `backend/database_schema.sql`

### Step 2: Verify Database Connection
Update the database credentials in `backend/app.py` if needed:
- Host: localhost
- User: root
- Password: areeba1012 (change if different)
- Database: smart_cafe_db

## 🚀 Backend Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Backend Server
```bash
python app.py
```

The server will run on `http://127.0.0.1:5000`

## 📋 Default Login Credentials

### Admin
- Email: admin@cafe.com
- Password: admin123

### Food Authority
- Email: authority@cafe.com
- Password: authority123

### User
- Users can sign up with any email
- Password must be exactly 6 digits
- Name must contain only alphabets

## 🎯 Features Implemented

### User Features
✅ Sign up with auto-assigned "user" role
✅ Login
✅ View menu
✅ Book table (8 AM - 5 PM only)
✅ Place dine-in order with table number and guests
✅ Payment through JazzCash
✅ View order status with real-time notifications
✅ Submit reviews and ratings
✅ Send messages/complaints to admin
✅ Receive admin replies

### Admin Features
✅ Login
✅ Dashboard with stats
✅ Monitor seating and orders
✅ Verify payment
✅ Update order status (sends notifications)
✅ View and reply to user messages
✅ Receive warnings from Food Authority

### Food Authority Features
✅ Login
✅ View customer reviews
✅ Check menu prices
✅ Send warning messages to admin

## 🎨 Design
- Consistent black and golden theme across all pages
- Same navbar and footer on all user pages
- Responsive design

## 📝 Important Notes

1. **Table Booking**: Only allowed between 8 AM - 5 PM
2. **Password Validation**: Must be exactly 6 digits for users
3. **Name Validation**: Must contain only alphabets
4. **Order Types**: Dine-in (requires table number and guests) or Takeaway
5. **Payment**: JazzCash requires transaction ID for verification

## 🔧 Troubleshooting

### Database Connection Error
- Check MySQL is running
- Verify credentials in `app.py`
- Ensure database `smart_cafe_db` exists

### Backend Not Starting
- Check if port 5000 is available
- Verify all dependencies are installed
- Check for syntax errors in `app.py`

### Frontend Not Connecting
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify API endpoints match in frontend code
