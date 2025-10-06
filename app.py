#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'sales_report_secret_key_2024'

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database file path
DATABASE = 'sales_customers.db'

# Palestinian governorates
GOVERNORATES = [
    'رام الله',
    'نابلس', 
    'جنين',
    'طولكرم',
    'قلقيلية',
    'سلفيت',
    'طوباس',
    'أريحا',
    'بيت لحم',
    'الخليل'
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            governorate TEXT NOT NULL,
            company_name TEXT NOT NULL,
            address TEXT,
            contact_person TEXT,
            mobile1 TEXT,
            mobile2 TEXT,
            phone TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create communication_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS communication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            communication_details TEXT NOT NULL,
            log_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Create customer_files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_description TEXT,
            file_size INTEGER,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Main page showing governorates"""
    # Get customer count for each governorate
    conn = get_db_connection()
    governorate_stats = {}
    
    for gov in GOVERNORATES:
        count = conn.execute(
            'SELECT COUNT(*) as count FROM customers WHERE governorate = ?', 
            (gov,)
        ).fetchone()['count']
        governorate_stats[gov] = count
    
    conn.close()
    return render_template('index.html', 
                         governorates=GOVERNORATES, 
                         stats=governorate_stats)

@app.route('/governorate/<governorate>')
def governorate_customers(governorate):
    """Show customers for a specific governorate"""
    if governorate not in GOVERNORATES:
        flash('محافظة غير صحيحة', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    customers = conn.execute('''
        SELECT c.*, 
               COUNT(cl.id) as communication_count,
               MAX(cl.log_date) as last_communication
        FROM customers c
        LEFT JOIN communication_logs cl ON c.id = cl.customer_id
        WHERE c.governorate = ?
        GROUP BY c.id
        ORDER BY c.last_updated DESC
    ''', (governorate,)).fetchall()
    
    conn.close()
    return render_template('governorate_customers.html', 
                         governorate=governorate, 
                         customers=customers)

@app.route('/add_customer/<governorate>')
def add_customer_form(governorate):
    """Show form to add new customer"""
    if governorate not in GOVERNORATES:
        flash('محافظة غير صحيحة', 'error')
        return redirect(url_for('index'))
    
    return render_template('add_customer.html', governorate=governorate)

@app.route('/add_customer/<governorate>', methods=['POST'])
def add_customer(governorate):
    """Add new customer"""
    if governorate not in GOVERNORATES:
        flash('محافظة غير صحيحة', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    company_name = request.form.get('company_name', '').strip()
    address = request.form.get('address', '').strip()
    contact_person = request.form.get('contact_person', '').strip()
    mobile1 = request.form.get('mobile1', '').strip()
    mobile2 = request.form.get('mobile2', '').strip()
    phone = request.form.get('phone', '').strip()
    communication_details = request.form.get('communication_details', '').strip()
    
    # Validation
    if not company_name:
        flash('اسم الشركة/المحل مطلوب', 'error')
        return render_template('add_customer.html', governorate=governorate)
    
    # Insert customer
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO customers (governorate, company_name, address, contact_person, 
                             mobile1, mobile2, phone, created_date, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (governorate, company_name, address, contact_person, mobile1, mobile2, 
          phone, datetime.now(), datetime.now()))
    
    customer_id = cursor.lastrowid
    
    # Add initial communication log if provided
    if communication_details:
        cursor.execute('''
            INSERT INTO communication_logs (customer_id, communication_details, log_date)
            VALUES (?, ?, ?)
        ''', (customer_id, communication_details, datetime.now()))
    
    conn.commit()
    conn.close()
    
    flash('تم إضافة العميل بنجاح', 'success')
    return redirect(url_for('governorate_customers', governorate=governorate))

@app.route('/customer/<int:customer_id>')
def customer_details(customer_id):
    """Show customer details and communication history"""
    conn = get_db_connection()
    
    # Get customer info
    customer = conn.execute(
        'SELECT * FROM customers WHERE id = ?', 
        (customer_id,)
    ).fetchone()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    # Get communication logs
    communications = conn.execute('''
        SELECT * FROM communication_logs 
        WHERE customer_id = ? 
        ORDER BY log_date DESC
    ''', (customer_id,)).fetchall()
    
    # Get customer files
    files = conn.execute('''
        SELECT * FROM customer_files 
        WHERE customer_id = ? 
        ORDER BY upload_date DESC
    ''', (customer_id,)).fetchall()
    
    conn.close()
    return render_template('customer_details.html', 
                         customer=customer, 
                         communications=communications,
                         files=files)

@app.route('/edit_customer/<int:customer_id>')
def edit_customer_form(customer_id):
    """Show form to edit customer"""
    conn = get_db_connection()
    customer = conn.execute(
        'SELECT * FROM customers WHERE id = ?', 
        (customer_id,)
    ).fetchone()
    conn.close()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/edit_customer/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    """Update customer information"""
    conn = get_db_connection()
    customer = conn.execute(
        'SELECT * FROM customers WHERE id = ?', 
        (customer_id,)
    ).fetchone()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    company_name = request.form.get('company_name', '').strip()
    address = request.form.get('address', '').strip()
    contact_person = request.form.get('contact_person', '').strip()
    mobile1 = request.form.get('mobile1', '').strip()
    mobile2 = request.form.get('mobile2', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # Validation
    if not company_name:
        flash('اسم الشركة/المحل مطلوب', 'error')
        return render_template('edit_customer.html', customer=customer)
    
    # Update customer
    conn.execute('''
        UPDATE customers 
        SET company_name = ?, address = ?, contact_person = ?, 
            mobile1 = ?, mobile2 = ?, phone = ?, last_updated = ?
        WHERE id = ?
    ''', (company_name, address, contact_person, mobile1, mobile2, 
          phone, datetime.now(), customer_id))
    
    conn.commit()
    conn.close()
    
    flash('تم تحديث بيانات العميل بنجاح', 'success')
    return redirect(url_for('customer_details', customer_id=customer_id))

@app.route('/add_communication/<int:customer_id>')
def add_communication_form(customer_id):
    """Show form to add communication log"""
    conn = get_db_connection()
    customer = conn.execute(
        'SELECT * FROM customers WHERE id = ?', 
        (customer_id,)
    ).fetchone()
    conn.close()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    return render_template('add_communication.html', customer=customer)

@app.route('/add_communication/<int:customer_id>', methods=['POST'])
def add_communication(customer_id):
    """Add new communication log"""
    conn = get_db_connection()
    customer = conn.execute(
        'SELECT * FROM customers WHERE id = ?', 
        (customer_id,)
    ).fetchone()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    communication_details = request.form.get('communication_details', '').strip()
    
    if not communication_details:
        flash('تفاصيل التواصل مطلوبة', 'error')
        return render_template('add_communication.html', customer=customer)
    
    # Add communication log
    conn.execute('''
        INSERT INTO communication_logs (customer_id, communication_details, log_date)
        VALUES (?, ?, ?)
    ''', (customer_id, communication_details, datetime.now()))
    
    # Update customer's last_updated
    conn.execute('''
        UPDATE customers SET last_updated = ? WHERE id = ?
    ''', (datetime.now(), customer_id))
    
    conn.commit()
    conn.close()
    
    flash('تم إضافة تقرير التواصل بنجاح', 'success')
    return redirect(url_for('customer_details', customer_id=customer_id))

@app.route('/search')
def search():
    """Search customers"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    customers = conn.execute('''
        SELECT c.*, 
               COUNT(cl.id) as communication_count,
               MAX(cl.log_date) as last_communication
        FROM customers c
        LEFT JOIN communication_logs cl ON c.id = cl.customer_id
        WHERE c.company_name LIKE ? OR c.contact_person LIKE ? OR c.address LIKE ?
        GROUP BY c.id
        ORDER BY c.last_updated DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    return render_template('search_results.html', 
                         customers=customers, 
                         query=query)

@app.route('/statistics')
def statistics():
    """Show statistics dashboard"""
    conn = get_db_connection()
    
    # Total customers
    total_customers = conn.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']
    
    # Customers by governorate
    gov_stats = []
    for gov in GOVERNORATES:
        count = conn.execute(
            'SELECT COUNT(*) as count FROM customers WHERE governorate = ?', 
            (gov,)
        ).fetchone()['count']
        gov_stats.append({'governorate': gov, 'count': count})
    
    # Recent communications
    recent_communications = conn.execute('''
        SELECT c.company_name, c.governorate, cl.communication_details, cl.log_date
        FROM communication_logs cl
        JOIN customers c ON cl.customer_id = c.id
        ORDER BY cl.log_date DESC
        LIMIT 10
    ''').fetchall()
    
    # Most active customers
    active_customers = conn.execute('''
        SELECT c.company_name, c.governorate, COUNT(cl.id) as communication_count
        FROM customers c
        LEFT JOIN communication_logs cl ON c.id = cl.customer_id
        GROUP BY c.id
        ORDER BY communication_count DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('statistics.html',
                         total_customers=total_customers,
                         gov_stats=gov_stats,
                         recent_communications=recent_communications,
                         active_customers=active_customers)

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)



@app.route('/upload_file/<int:customer_id>')
def upload_file_form(customer_id):
    """Show file upload form"""
    conn = get_db_connection()
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    conn.close()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    return render_template('upload_file.html', customer=customer)

@app.route('/upload_file/<int:customer_id>', methods=['POST'])
def upload_file(customer_id):
    """Handle file upload"""
    conn = get_db_connection()
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    
    if not customer:
        flash('العميل غير موجود', 'error')
        return redirect(url_for('index'))
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'error')
        return redirect(url_for('upload_file_form', customer_id=customer_id))
    
    file = request.files['file']
    file_description = request.form.get('file_description', '').strip()
    
    # Check if file is selected
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'error')
        return redirect(url_for('upload_file_form', customer_id=customer_id))
    
    # Check file extension
    if not allowed_file(file.filename):
        flash('نوع الملف غير مسموح. الأنواع المسموحة: ' + ', '.join(ALLOWED_EXTENSIONS), 'error')
        return redirect(url_for('upload_file_form', customer_id=customer_id))
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{customer_id}_{timestamp}_{original_filename}"
    
    try:
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Save file info to database
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer_files (customer_id, filename, original_filename, 
                                      file_description, file_size, upload_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, filename, original_filename, file_description, 
              file_size, datetime.now()))
        
        conn.commit()
        flash('تم تحميل الملف بنجاح', 'success')
        
    except Exception as e:
        flash(f'حدث خطأ أثناء تحميل الملف: {str(e)}', 'error')
    
    finally:
        conn.close()
    
    return redirect(url_for('customer_details', customer_id=customer_id))

@app.route('/download_file/<int:file_id>')
def download_file(file_id):
    """Download customer file"""
    conn = get_db_connection()
    file_info = conn.execute('''
        SELECT * FROM customer_files WHERE id = ?
    ''', (file_id,)).fetchone()
    conn.close()
    
    if not file_info:
        flash('الملف غير موجود', 'error')
        return redirect(url_for('index'))
    
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], 
                                 file_info['filename'], 
                                 as_attachment=True,
                                 download_name=file_info['original_filename'])
    except FileNotFoundError:
        flash('الملف غير موجود على الخادم', 'error')
        return redirect(url_for('customer_details', customer_id=file_info['customer_id']))

@app.route('/delete_file/<int:file_id>')
def delete_file(file_id):
    """Delete customer file"""
    conn = get_db_connection()
    file_info = conn.execute('''
        SELECT * FROM customer_files WHERE id = ?
    ''', (file_id,)).fetchone()
    
    if not file_info:
        flash('الملف غير موجود', 'error')
        return redirect(url_for('index'))
    
    customer_id = file_info['customer_id']
    
    try:
        # Delete file from filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customer_files WHERE id = ?', (file_id,))
        conn.commit()
        
        flash('تم حذف الملف بنجاح', 'success')
        
    except Exception as e:
        flash(f'حدث خطأ أثناء حذف الملف: {str(e)}', 'error')
    
    finally:
        conn.close()
    
    return redirect(url_for('customer_details', customer_id=customer_id))

