from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import tempfile

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_kernel_version(dump_path):
    try:
        # Utiliser strings pour extraire le contenu du fichier
        result = subprocess.run(['strings', dump_path], capture_output=True, text=True)
        
        # Chercher la version du noyau dans la sortie
        for line in result.stdout.split('\n'):
            if 'Linux version' in line:
                # Extraire la version du noyau
                version = line.split('Linux version ')[1].split()[0]
                return version
        return None
    except Exception as e:
        print(f"Erreur lors de l'extraction de la version : {str(e)}")
        return None

@app.route('/upload_dump/', methods=['POST'])
def upload_dump():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier n\'a été envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    try:
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            kernel_version = extract_kernel_version(temp_file.name)
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_file.name)
            
            if kernel_version:
                return jsonify({
                    'kernel_version': kernel_version
                })
            else:
                return jsonify({
                    'error': 'Version du noyau non trouvée dans le dump'
                }), 400
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors du traitement du fichier : {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True) 