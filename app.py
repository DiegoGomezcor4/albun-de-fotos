from flask import Flask, render_template, request, redirect, url_for, Response, session, jsonify
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
PHOTOS_FILE = 'photos.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cargar la lista de fotos desde el archivo JSON
if os.path.exists(PHOTOS_FILE):
    with open(PHOTOS_FILE, 'r') as f:
        photos = json.load(f)
else:
    photos = []

# Credenciales
USERNAME = 'tu_usuario'
PASSWORD = 'tu_contraseña'

def check_auth(username, password):
    """Verifica si un nombre de usuario y contraseña son válidos."""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Envía una respuesta 401 para habilitar la autenticación básica."""
    return Response(
        'No autorizado', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        session['logged_in'] = True
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    logged_in = session.get('logged_in', False)
    return render_template('index.html', photos=photos, logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_auth(username, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Lógica para manejar la carga de múltiples archivos
        files = request.files.getlist('files[]')
        for file in files:
            if file:
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                photo = {
                    'id': len(photos),
                    'filename': filename,
                    'comment': '',
                    'likes': 0
                }
                photos.append(photo)
        with open(PHOTOS_FILE, 'w') as f:
            json.dump(photos, f)
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/edit/<int:photo_id>', methods=['GET', 'POST'])
@requires_auth
def edit(photo_id):
    global photos
    photo_to_edit = None
    for photo in photos:
        if photo['id'] == photo_id:
            photo_to_edit = photo
            break
    if request.method == 'POST':
        if photo_to_edit:
            photo_to_edit['comment'] = request.form['comment']
            with open(PHOTOS_FILE, 'w') as f:
                json.dump(photos, f)
        return redirect(url_for('index'))
    return render_template('edit.html', photo=photo_to_edit)

@app.route('/delete/<int:photo_id>', methods=['POST'])
@requires_auth
def delete(photo_id):
    global photos
    photo_to_delete = None
    for photo in photos:
        if photo['id'] == photo_id:
            photo_to_delete = photo
            break
    if photo_to_delete:
        photos.remove(photo_to_delete)
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo_to_delete['filename']))
        except FileNotFoundError:
            pass
        with open(PHOTOS_FILE, 'w') as f:
            json.dump(photos, f)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Photo not found'}), 404

@app.route('/like/<int:photo_id>', methods=['POST'])
def like_photo(photo_id):
    for photo in photos:
        if photo['id'] == photo_id:
            photo['likes'] += 1
            new_likes = photo['likes']
            break
    with open(PHOTOS_FILE, 'w') as f:
        json.dump(photos, f)
    return jsonify({'likes': new_likes})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))