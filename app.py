from flask import Flask, render_template, request, jsonify, send_file, request, redirect, url_for
from io import BytesIO
import pandas as pd
import sqlite3
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', selected_date='', no_data=False)

# Initialize database
def init_db_karyawan():
    with sqlite3.connect('karyawan.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS karyawan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                nik TEXT NOT NULL,
                jenis_kelamin TEXT NOT NULL,
                jabatan TEXT NOT NULL,
                departemen TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db_karyawan()

def get_karyawan_db_connection():
    conn = sqlite3.connect('karyawan.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_attendance_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, checkin_time, date FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True)
    
    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data)

@app.route('/export_all')
def export_all():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Export karyawan data
        karyawan_conn = get_karyawan_db_connection()
        df_karyawan = pd.read_sql_query('SELECT * FROM karyawan', karyawan_conn)
        df_karyawan.to_excel(writer, index=False, sheet_name='Karyawan Data')
        karyawan_conn.close()

        # Export attendance data
        attendance_conn = get_attendance_db_connection()
        df_attendance = pd.read_sql_query('SELECT * FROM attendance', attendance_conn)
        df_attendance.to_excel(writer, index=False, sheet_name='Attendance Data')
        attendance_conn.close()
    
    output.seek(0)
    return send_file(output, attachment_filename='all_data.xlsx', as_attachment=True)

@app.route('/dashboard')
def karyawan():
    karyawan_conn = get_karyawan_db_connection()
    karyawan_data = karyawan_conn.execute('SELECT * FROM karyawan').fetchall()
    karyawan_conn.close()

    attendance_conn = get_attendance_db_connection()
    attendance_data = attendance_conn.execute('SELECT * FROM attendance').fetchall()
    attendance_conn.close()

    # Combine karyawan and attendance data
    combined_data = []
    for karyawan in karyawan_data:
        attendances = [att for att in attendance_data if att['name'] == karyawan['name']]
        combined_data.append({
            'karyawan': karyawan,
            'attendances': attendances
        })

    return render_template('karyawan.html', combined_data=combined_data)

@app.route('/add', methods=['GET', 'POST'])
def add_karyawan():
    if request.method == 'POST':
        name = request.form['name']
        nik = request.form['nik']
        jenis_kelamin = request.form['jenis_kelamin']
        jabatan = request.form['jabatan']
        departemen = request.form['departemen']

        conn = get_karyawan_db_connection()
        conn.execute('''
            INSERT INTO karyawan (name, nik, jenis_kelamin, jabatan, departemen)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, nik, jenis_kelamin, jabatan, departemen))
        conn.commit()
        conn.close()
        return redirect(url_for('karyawan'))
    
    return render_template('add_karyawan.html')

@app.route('/edit_karyawan/<name>', methods=['GET'])
def edit_karyawan(name):
    conn = get_karyawan_db_connection()
    karyawan = conn.execute('SELECT * FROM karyawan WHERE name = ?', (name,)).fetchone()
    conn.close()
    
    if karyawan is None:
        return redirect(url_for('karyawan'))
    
    return render_template('edit_karyawan.html', karyawan=karyawan)

@app.route('/update_karyawan/<old_name>', methods=['POST'])
def update_karyawan(old_name):
    new_name = request.form['name']
    nik = request.form['nik']
    jenis_kelamin = request.form['jenis_kelamin']
    jabatan = request.form['jabatan']
    departemen = request.form['departemen']

    conn = get_karyawan_db_connection()
    conn.execute('''
        UPDATE karyawan
        SET name = ?, nik = ?, jenis_kelamin = ?, jabatan = ?, departemen = ?
        WHERE name = ?
    ''', (new_name, nik, jenis_kelamin, jabatan, departemen, old_name))
    conn.commit()
    conn.close()
    
    return redirect(url_for('karyawan'))


if __name__ == '__main__':
    app.run(debug=True)
