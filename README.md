# Flask Blog Application
[go live](https://journal-by-gourab.onrender.com/)

A modern, full-featured blog platform built with Flask.  
It offers a clean interface for readers and a secure, powerful dashboard for administrators.  
Includes image uploads, responsive design, and easy content management.

---

## 🚀 Features

### 📰 For Readers
- Beautiful, modern blog interface
- Fully responsive (mobile, tablet, desktop)
- Browse all blog posts by section (Technology, Travel, Books, etc.)
- View posts with featured images and formatted content
- Automatic image optimization and graceful fallback

### 🔑 For Users
- Login/Signup with email, username, and password
- Access the "Blog" section after login to browse categorized posts

### 🛡️ For Administrators
- Secure admin login system (email & password)
- Dashboard with blog statistics (total posts, with images, etc.)
- Create, edit, and delete blog posts with rich content and images
- Assign posts to custom sections (categories)
- Add new sections directly from the dashboard
- Add new admin users
- Image upload with preview and validation
- Auto-save for post forms (prevents data loss)
- Keyboard shortcuts for productivity

### ⚙️ Technical Features
- SQLite database for easy setup and portability
- Image upload with validation and security
- Bootstrap 5 for responsive, modern UI
- Custom CSS for enhanced look and feel
- JavaScript enhancements (auto-save, image preview, form validation, animations)
- Error handling and user feedback with flash messages

---

## 📁 File Structure

```
blog-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── blog.db                # SQLite database (created automatically)
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── blog.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_create.html
│   ├── admin_edit.html
│   ├── add_admin.html
│   └── add_section.html
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   ├── js/
│   │   └── script.js      # JavaScript functionality
│   └── uploads/           # Uploaded images (created automatically)
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### 2. Clone or Download
Download or clone this repository and organize the files as shown above.

### 3. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv blog_env

# Activate virtual environment
# On Windows:
blog_env\Scripts\activate
# On macOS/Linux:
source blog_env/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```
The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## ✨ Usage

- **Home:** View latest posts and blog statistics.
- **Login/Signup:** Use the "Login/Signup" option in the navbar to log in as admin or register as a user.
- **Admin Dashboard:** Admins can manage posts, sections, and other admins.
- **Blog:** Logged-in users can browse all posts by section.
- **Image Upload:** Add images to posts with live preview and validation.
- **Auto-save:** Your post drafts are auto-saved in the browser until published.

---

## 📝 Customization

- **Change Admin Credentials:** Default admin is `admin@example.com` / `password123`. Change this in `init_db()` in `app.py`.
- **Add/Remove Sections:** Use the "Add Section" button in the admin dashboard.
- **Styling:** Modify `static/css/style.css` for custom styles.

---

## 📄 License

This project is for educational and personal use.  
Feel free to modify and extend it for your own projects!

---
