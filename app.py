from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Admin credentials (in production, use proper authentication)
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "password123"  # Change this!

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            section TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    # Insert default admin if not exists
    cursor.execute('SELECT * FROM admin WHERE email = ?', ('admin@example.com',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', ('admin@example.com', 'password123'))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

# Public Routes
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        flash('Post not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('post.html', post=post)

# Admin Routes
@app.route('/admin')
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    email = request.form['email']
    password = request.form['password']
    username = request.form.get('username', '')  # username field for general users

    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM admin WHERE email = ? AND password = ?', (email, password)).fetchone()

    if admin:
        session['admin_logged_in'] = True
        session['admin_email'] = email
        flash('Login successful!', 'success')
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        # Save general user data if not already present
        user = conn.execute('SELECT * FROM users_data WHERE email = ?', (email,)).fetchone()
        if not user:
            if username:  # Only save if username is provided
                conn.execute('INSERT INTO users_data (username, email, password) VALUES (?, ?, ?)', (username, email, password))
                conn.commit()
                flash('Registered successfully as a general user.', 'success')
            else:
                flash('Username is required for general users.', 'error')
                conn.close()
                return redirect(url_for('admin_login'))
        else:
            flash('Logged in as a general user.', 'success')
        session['user_logged_in'] = True
        session['user_email'] = email
        conn.close()
        return redirect(url_for('index'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('user_logged_in', None)
    session.pop('admin_email', None)
    session.pop('user_email', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', posts=posts)

@app.route('/admin/create')
def admin_create():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    # Fetch sections from DB
    conn = get_db_connection()
    sections = [row['name'] for row in conn.execute('SELECT name FROM sections').fetchall()]
    conn.close()
    return render_template('admin_create.html', sections=sections)

@app.route('/admin/create', methods=['POST'])
def admin_create_post():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    title = request.form['title']
    content = request.form['content']
    section = request.form['section']
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"uploads/{filename}"
    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title, content, image_path, section) VALUES (?, ?, ?, ?)',
                 (title, content, image_path, section))
    conn.commit()
    conn.close()
    flash('Post created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit/<int:post_id>')
def admin_edit(post_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        flash('Post not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_edit.html', post=post)

@app.route('/admin/edit/<int:post_id>', methods=['POST'])
def admin_edit_post(post_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        flash('Post not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Handle image upload
    image_path = post['image_path']  # Keep existing image by default
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            # Delete old image if it exists
            if image_path:
                old_image_path = os.path.join('static', image_path)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"uploads/{filename}"
    
    conn.execute('UPDATE posts SET title = ?, content = ?, image_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                 (title, content, image_path, post_id))
    conn.commit()
    conn.close()
    
    flash('Post updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:post_id>')
def admin_delete(post_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        flash('Post not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Delete associated image
    if post['image_path']:
        image_path = os.path.join('static', post['image_path'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add', methods=['GET', 'POST'])
def add_admin():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO admin (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
            flash('New admin added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Admin with this email already exists.', 'error')
        finally:
            conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_admin.html')

@app.route('/admin/add_section', methods=['GET', 'POST'])
def add_section():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO sections (name) VALUES (?)', (name,))
            conn.commit()
            flash('Section added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Section already exists.', 'error')
        finally:
            conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_section.html')

@app.route('/blog')
def blog():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    sections = [row['name'] for row in conn.execute('SELECT name FROM sections').fetchall()]
    conn.close()
    return render_template('blog.html', posts=posts, sections=sections)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
