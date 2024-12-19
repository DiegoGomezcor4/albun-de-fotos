from flask import Flask, render_template, request, redirect, url_for
import os
import json

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

@app.route('/')
def index():
    return render_template('index.html', photos=photos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        comment = request.form.get('comment', '')

        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Guardar información de la foto
            photos.append({'filename': filename, 'comment': comment, 'likes': 0})

            # Guardar la lista de fotos en el archivo JSON
            with open(PHOTOS_FILE, 'w') as f:
                json.dump(photos, f)

            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/like/<int:photo_id>', methods=['POST'])
def like_photo(photo_id):
    if 0 <= photo_id < len(photos):
        photos[photo_id]['likes'] += 1  # Incrementa los "Me gusta"

        # Guardar la lista de fotos en el archivo JSON
        with open(PHOTOS_FILE, 'w') as f:
            json.dump(photos, f)

    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)