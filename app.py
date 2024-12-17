from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista para almacenar información de fotos
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
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/like/<int:photo_id>', methods=['POST'])
def like_photo(photo_id):
    if 0 <= photo_id < len(photos):
        photos[photo_id]['likes'] += 1  # Incrementa los "Me gusta"
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
