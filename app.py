from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import os
import json
from functools import wraps

app = Flask(__name__)
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
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html', photos=photos)

@app.route('/upload', methods=['GET', 'POST'])
@requires_auth
def upload():
    if request.method == 'POST':
        # Lógica para manejar la carga de archivos
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo = {
                'id': len(photos),
                'filename': filename,
                'comment': request.form.get('comment', ''),
                'likes': 0
            }
            photos.append(photo)
            with open(PHOTOS_FILE, 'w') as f:
                json.dump(photos, f)
        return redirect(url_for('index'))
    return render_template('upload.html')

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
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo_to_delete['filename']))
        with open(PHOTOS_FILE, 'w') as f:
            json.dump(photos, f)
    return redirect(url_for('index'))

@app.route('/like/<int:photo_id>', methods=['POST'])
def like_photo(photo_id):
    for photo in photos:
        if photo['id'] == photo_id:
            photo['likes'] += 1
            break
    with open(PHOTOS_FILE, 'w') as f:
        json.dump(photos, f)
    return jsonify({'likes': photo['likes']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))