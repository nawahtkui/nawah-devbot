from flask import Flask, request, session, redirect, url_for, render_template_string, send_file, flash, abort
import sqlite3, os, csv, io
from dotenv import load_dotenv
from datetime import datetime

# إعداد البيئة
load_dotenv(os.path.join('config', '.env') if os.path.exists(os.path.join('config', '.env')) else '.env')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', '')
DB_PATH = os.getenv('DB_PATH', 'nawah_kyc.db')
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me')
PER_PAGE = 10

app = Flask(__name__)
app.secret_key = SECRET_KEY

# DB helpers
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()
    conn.close()

# تهيئة DB
execute_db('''CREATE TABLE IF NOT EXISTS kyc (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    national_id TEXT,
                    email TEXT,
                    timestamp_utc TEXT
                )''')

# Templates
LAYOUT = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Nawah KYC Dashboard</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:20px;}
table{border-collapse:collapse;width:100%;}
td,th{border:1px solid #ddd;padding:8px;}
th{background:#f2f2f2;}
a.button{display:inline-block;padding:6px 10px;background:#1976d2;color:#fff;text-decoration:none;border-radius:4px;}
form.inline{display:inline;}
.msg{color:green;}
.err{color:red;}
</style>
</head>
<body>
{% block body %}{% endblock %}
</body>
</html>
"""

INDEX = """
{% extends layout %}{% block body %}
{% if not session.get('admin') %}
<h3>Admin Login</h3>
<form method="post" action="{{ url_for('login') }}">
<input name="token" placeholder="Admin token" style="width:300px">
<button type="submit">Login</button>
</form>
{% else %}
<div style="margin-bottom:10px">
<a class="button" href="{{ url_for('export_csv') }}">Export CSV</a>
<a class="button" href="{{ url_for('logout') }}">Logout</a>
</div>
<table>
<tr><th>#</th><th>Full name</th><th>ID</th><th>Email</th><th>UTC</th><th>Actions</th></tr>
{% for r in rows %}
<tr>
<td>{{ loop.index + (page-1)*per_page }}</td>
<td>{{ r['full_name'] }}</td><td>{{ r['national_id'] }}</td><td>{{ r['email'] }}</td><td>{{ r['timestamp_utc'] }}</td>
<td>
<a href="{{ url_for('view_record', user_id=r['user_id']) }}">View</a> |
<form method="post" action="{{ url_for('delete_record', user_id=r['user_id']) }}" class="inline" onsubmit="return confirm('Delete this record?');">
<button type="submit">Delete</button>
</form>
</td>
</tr>
{% endfor %}
</table>
{% endif %}
{% endblock %}
"""

VIEW = """
{% extends layout %}{% block body %}
<h3>Record Details</h3>
<p><strong>Full name:</strong> {{ r['full_name'] }}</p>
<p><strong>ID:</strong> {{ r['national_id'] }}</p>
<p><strong>Email:</strong> {{ r['email'] }}</p>
<p><strong>User ID:</strong> {{ r['user_id'] }}</p>
<p><strong>UTC:</strong> {{ r['timestamp_utc'] }}</p>
<p><a href="{{ url_for('index') }}">Back</a></p>
{% endblock %}
"""

# Routes
@app.route('/', methods=['GET'])
def index():
    if not session.get('admin'):
        return render_template_string(INDEX, layout=LAYOUT)
    page = int(request.args.get('page',1))
    per_page = PER_PAGE
    offset = (page-1)*per_page
    rows = query_db('SELECT * FROM kyc ORDER BY timestamp_utc DESC LIMIT ? OFFSET ?', [per_page, offset])
    return render_template_string(INDEX, layout=LAYOUT, rows=rows, page=page, per_page=per_page)

@app.route('/login', methods=['POST'])
def login():
    token = request.form.get('token','').strip()
    if token == ADMIN_TOKEN:
        session['admin'] = True
        return redirect(url_for('index'))
    flash('Invalid admin token', 'error')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/record/<int:user_id>')
def view_record(user_id):
    if not session.get('admin'):
        return redirect(url_for('index'))
    r = query_db('SELECT * FROM kyc WHERE user_id=?', [user_id], one=True)
    if not r: abort(404)
    return render_template_string(VIEW, layout=LAYOUT, r=r)

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_record(user_id):
    if not session.get('admin'):
        return redirect(url_for('index'))
    execute_db('DELETE FROM kyc WHERE user_id=?', [user_id])
    flash('Record deleted')
    return redirect(url_for('index'))

@app.route('/export_csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('index'))
    rows = query_db('SELECT * FROM kyc ORDER BY timestamp_utc DESC')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['user_id','full_name','national_id','email','timestamp_utc'])
    for r in rows:
        writer.writerow([r['user_id'], r['full_name'], r['national_id'], r['email'], r['timestamp_utc']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     attachment_filename=f'kyc_export_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.csv')

if __name__ == '__main__':
    app.run(debug=True)
