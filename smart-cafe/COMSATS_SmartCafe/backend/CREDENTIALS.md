# Smart Cafe System - Login Credentials

## 🔐 Default Login Credentials

### 👤 Admin
- **Email:** `admin@cafe.com`
- **Password:** `admin123`
- **Role:** Admin
- **Access:** Full system access - manage orders, menu, users, reviews, notifications

### ⚖️ Food Authority
- **Email:** `authority@cafe.com`
- **Password:** `authority123`
- **Role:** Authority
- **Access:** View reviews, check prices, send warnings to admin

### 👥 User/Student
- Users can sign up with any email
- **Password Requirements:** Exactly 6 digits (e.g., `123456`)
- **Name Requirements:** Only alphabets (A-Z, a-z) - no numbers or special characters
- **Role:** Automatically assigned as "user" on signup
- **Access:** Order food, book tables, submit reviews, contact admin

## 📝 Notes

- All passwords are case-sensitive
- User passwords must be exactly 6 digits
- User names must contain only letters (spaces allowed)
- Admin and Authority credentials are pre-set in the database
- Users must sign up first before they can login
