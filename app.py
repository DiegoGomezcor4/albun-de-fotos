from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Cambia esto por una clave más segura
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegúrate de que la carpeta de uploads exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ruta principal
@app.route('/')
def index():
    # Obtener todas las imágenes de la carpeta uploads
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=images)

# Ruta para subir imágenes
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Verifica si se subió un archivo
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('El archivo no tiene nombre')
            return redirect(request.url)
        
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Imagen subida exitosamente')
            return redirect(url_for('index'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
