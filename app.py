import os
import uuid

from flask import Flask, request, session, g, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

from models import get_db, query_db

APP_SECRET = 'dev-secret-for-demo'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = None  # None = permitir cualquier extensión para el demo

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar carpeta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    if ALLOWED_EXTENSIONS is None:
        return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html', title='Flask IDOR demo')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html', title='Login')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        display_name = request.form.get('name') or ''
        uploaded = request.files.get('file')
        if uploaded and uploaded.filename != '' and allowed_file(uploaded.filename):
            orig_filename = secure_filename(uploaded.filename)
            unique_name = f"{uuid.uuid4().hex}_{orig_filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            uploaded.save(save_path)

            db = get_db()
            db.execute(
                'INSERT INTO files (name, filename, content_type, user_id) VALUES (?, ?, ?, ?)',
                (display_name or orig_filename, unique_name, uploaded.mimetype or 'application/octet-stream',
                 session['user_id'])
            )
            db.commit()
            return redirect(url_for('myfiles'))
        else:
            return 'No file or invalid file', 400
    return render_template('upload.html', title='Upload file')


@app.route('/myfiles')
def myfiles():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    q_user_id = request.args.get('user_id', type=int)
    target_user_id = q_user_id if q_user_id is not None else session['user_id']

    files = query_db('SELECT id, name FROM files WHERE user_id = ?', (target_user_id,))
    return render_template('myfiles.html', title=f'Files for user {target_user_id}', files=files)



# ---------- Vulnerable endpoint ----------
@app.route('/file')
def file_vulnerable():
    file_id = request.args.get('id', type=int)
    if not file_id:
        return 'Missing id parameter', 400
    row = query_db('SELECT id, name, filename, content_type, user_id FROM files WHERE id = ?', (file_id,), one=True)
    if not row:
        return 'Not found', 404
    filename_on_disk = row['filename']
    if not filename_on_disk:
        return 'File not available', 404

    resp = send_from_directory(app.config['UPLOAD_FOLDER'], filename_on_disk, as_attachment=True)
    display_name = row['name'] or filename_on_disk
    resp.headers['Content-Disposition'] = f'attachment; filename="{display_name}"'
    return resp

# ---------- Secure endpoint ----------
@app.route('/file_secure')
def file_secure():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    file_id = request.args.get('id', type=int)
    if not file_id:
        return 'Missing id parameter', 400
    row = query_db('SELECT id, name, filename, content_type, user_id FROM files WHERE id = ?', (file_id,), one=True)
    if not row:
        return 'Not found', 404
    if row['user_id'] != session['user_id']:
        return 'Forbidden: you do not own this file', 403

    filename_on_disk = row['filename']
    if not filename_on_disk:
        return 'File not available', 404

    resp = send_from_directory(app.config['UPLOAD_FOLDER'], filename_on_disk, as_attachment=True)
    display_name = row['name'] or filename_on_disk
    resp.headers['Content-Disposition'] = f'attachment; filename="{display_name}"'
    return resp


if __name__ == '__main__':
    app.run(debug=True)
