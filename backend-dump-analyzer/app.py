from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
import logging
import re

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_profile(dump_path):
    try:
        logger.debug(f"Analyse du fichier dump: {dump_path}")
        
        # Exécuter la commande Volatility3 pour récupérer le profil
        cmd = [
            'vol',  # Utiliser la commande 'vol' directement
            '--remote-isf-url', 'https://github.com/Abyss-W4tcher/volatility3-symbols/raw/master/banners/banners.json',
            '-f', dump_path,
            'banners.Banners'
        ]
        
        logger.debug(f"Exécution de la commande: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logger.debug(f"Code de retour: {result.returncode}")
        logger.debug(f"Sortie standard: {result.stdout}")
        logger.debug(f"Erreur standard: {result.stderr}")
        
        if result.returncode != 0:
            return None, f"Erreur lors de l'exécution de Volatility3: {result.stderr}"
        
        # Analyser la sortie pour extraire les informations
        output = result.stdout
        for line in output.split('\n'):
            if 'Linux version' in line:
                # Extraire la version du noyau
                kernel_version = line.split('Linux version')[1].split()[0]
                
                # Extraire la distribution et sa version
                if 'Ubuntu' in line:
                    distro = 'Ubuntu'
                    # Chercher le motif #XXX~YY.YY
                    version_match = re.search(r'#\d+~(\d+\.\d+)', line)
                    if version_match:
                        distro_version = version_match.group(1)
                    else:
                        distro_version = 'Unknown'
                else:
                    distro = 'Unknown'
                    distro_version = 'Unknown'
                
                logger.debug(f"Version du noyau trouvée: {kernel_version}")
                logger.debug(f"Distribution trouvée: {distro} {distro_version}")
                
                return {
                    'kernel_version': kernel_version,
                    'distribution': distro,
                    'distro_version': distro_version,
                    'full_version': line.split('Linux version')[1].strip()
                }, None
        
        return None, "Version du noyau non trouvée dans la sortie"
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du dump: {str(e)}")
        return None, f"Erreur: {str(e)}"

def get_process_list(dump_path, command="linux.pslist"):
    try:
        logger.debug(f"Analyse des processus du dump: {dump_path}")
        
        # Exécuter la commande Volatility3 pour récupérer la liste des processus
        cmd = [
            'vol',
            '--remote-isf-url', 'https://github.com/Abyss-W4tcher/volatility3-symbols/raw/master/banners/banners.json',
            '-f', dump_path,
            command
        ]
        
        logger.debug(f"Exécution de la commande: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logger.debug(f"Code de retour: {result.returncode}")
        logger.debug(f"Sortie standard: {result.stdout}")
        logger.debug(f"Erreur standard: {result.stderr}")
        
        if result.returncode != 0:
            return None, f"Erreur lors de l'exécution de Volatility3: {result.stderr}"
        
        # Analyser la sortie en fonction de la commande
        if command == "linux.bash":
            commands = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 4:
                        commands.append({
                            'pid': parts[0],
                            'process': parts[1],
                            'time': ' '.join(parts[2:5]),
                            'command': ' '.join(parts[5:])
                        })
            return commands, None
        elif command == "linux.envars":
            envars = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 5:
                        envars.append({
                            'pid': parts[0],
                            'ppid': parts[1],
                            'comm': parts[2],
                            'key': parts[3],
                            'value': parts[4]
                        })
            return envars, None
        elif command == "linux.boottime.Boottime":
            boottime = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 2:
                        boottime.append({
                            'time_ns': parts[0],
                            'boot_time': ' '.join(parts[1:])
                        })
            return boottime, None
        elif command == "linux.pagecache.Files":
            files = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 3:
                        files.append({
                            'superblock_addr': parts[0],
                            'mount_point': parts[1],
                            'device': parts[2],
                            'inode_num': parts[3],
                            'inode_addr': parts[4],
                            'file_type': parts[5],
                            'inode_pages': parts[6],
                            'cached_pages': parts[7],
                            'file_mode': parts[8],
                            'access_time': parts[9:12],
                            'modification_time': parts[12:15],
                            'change_time': parts[15:18],
                            'file_path': ' '.join(parts[18:])
                        })
            return files, None
        elif command == "linux.pslist.PsList":
            processes = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 7:
                        processes.append({
                            'offset': parts[0],
                            'pid': parts[1],
                            'tid': parts[2],
                            'ppid': parts[3],
                            'comm': parts[4],
                            'creation_time': ' '.join(parts[5:8]),
                            'file_output': parts[8]
                        })
            return processes, None
        else:
            return None, "Commande non supportée"
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des processus: {str(e)}")
        return None, f"Erreur: {str(e)}"

@app.route('/upload_dump/', methods=['POST'])
def upload_dump():
    logger.debug("Requête POST reçue sur /upload_dump/")
    
    if 'file' not in request.files:
        logger.error("Aucun fichier dans la requête")
        return jsonify({'error': 'Aucun fichier n\'a été envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("Nom de fichier vide")
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    logger.debug(f"Fichier reçu: {file.filename}")
    
    try:
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            logger.debug(f"Fichier sauvegardé temporairement: {temp_file.name}")
            
            # Récupérer les informations du profil
            profile_info, error = get_profile(temp_file.name)
            if error:
                logger.error(f"Erreur lors de l'analyse: {error}")
                return jsonify({'error': error}), 400
            
            # Sauvegarder le chemin du fichier temporaire pour une utilisation ultérieure
            with open('last_dump_path.txt', 'w') as f:
                f.write(temp_file.name)
            
            if profile_info:
                # Sauvegarder les résultats dans last_analysis.json
                results = {
                    'os': 'Linux',
                    'kernel_version': profile_info['kernel_version'],
                    'distribution': profile_info['distribution'],
                    'distribution_version': profile_info['distro_version'],
                    'command': 'banners.Banners',
                    'output': []
                }
                
                with open('last_analysis.json', 'w') as f:
                    json.dump(results, f)
                
                logger.info(f"Informations trouvées: {profile_info}")
                return jsonify(profile_info)
            else:
                logger.error("Informations non trouvées")
                return jsonify({
                    'error': 'Informations non trouvées'
                }), 400
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier: {str(e)}")
        return jsonify({
            'error': f'Erreur lors du traitement du fichier : {str(e)}'
        }), 500

@app.route('/execute_plugin/<plugin_name>', methods=['GET'])
def execute_plugin(plugin_name):
    try:
        # Lire le chemin du dernier dump analysé
        with open('last_dump_path.txt', 'r') as f:
            dump_path = f.read().strip()
        
        # Exécuter le plugin spécifié
        output, error = get_process_list(dump_path, plugin_name)
        if error:
            return jsonify({'error': error}), 400
        
        # Mettre à jour last_analysis.json avec les nouveaux résultats
        with open('last_analysis.json', 'r') as f:
            results = json.load(f)
        
        results['command'] = plugin_name
        results['output'] = output
        
        with open('last_analysis.json', 'w') as f:
            json.dump(results, f)
        
        return jsonify({'success': True, 'output': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def show_results():
    try:
        with open('last_analysis.json', 'r') as f:
            results = json.load(f)
        
        command = results.get('command', '')
        output = results.get('output', [])
        
        # Générer le HTML en fonction de la commande
        if command == "linux.bash":
            html = generate_bash_html(output[1:])
        elif command == "linux.envars":
            html = generate_envars_html(output[1:])
        elif command == "linux.boottime.Boottime":
            html = generate_boottime_html(output[1:])
        elif command == "linux.pagecache.Files":
            html = generate_pagecache_files_html(output[1:])
        elif command == "linux.pslist.PsList":
            html = generate_pslist_html(output[1:])
        else:
            html = "<p>Format de sortie non supporté</p>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Résultats de l'analyse - {command}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .info {{
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #e9ecef;
                    border-radius: 4px;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Résultats de l'analyse - {command}</h1>
                <div class="info">
                    <p><strong>Système d'exploitation:</strong> {results.get('os', 'N/A')}</p>
                    <p><strong>Version du noyau:</strong> {results.get('kernel_version', 'N/A')}</p>
                    <p><strong>Distribution:</strong> {results.get('distribution', 'N/A')}</p>
                    <p><strong>Version de la distribution:</strong> {results.get('distribution_version', 'N/A')}</p>
                    <p><strong>Commande exécutée:</strong> {command}</p>
                </div>
                {html}
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Erreur: {str(e)}"
    
def generate_bash_html(commands):
    return f"""
    <table>
        <thead>
            <tr>
                <th>PID</th>
                <th>Process</th>
                <th>Time</th>
                <th>Command</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{c['pid']}</td>
                <td>{c['process']}</td>
                <td>{c['time']}</td>
                <td>{c['command']}</td>
            </tr>
            ''' for c in commands)}
        </tbody>
    </table>
    """

def generate_envars_html(envars):
    return f"""
    <table>
        <thead>
            <tr>
                <th>PID</th>
                <th>PPID</th>
                <th>COMM</th>
                <th>KEY</th>
                <th>VALUE</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{e['pid']}</td>
                <td>{e['ppid']}</td>
                <td>{e['comm']}</td>
                <td>{e['key']}</td>
                <td>{e['value']}</td>
            </tr>
            ''' for e in envars)}
        </tbody>
    </table>
    """

def generate_boottime_html(boottime):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Time NS</th>
                <th>Boot Time</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{b['time_ns']}</td>
                <td>{b['boot_time']}</td>
            </tr>
            ''' for b in boottime)}
        </tbody>
    </table>
    """

def generate_pagecache_files_html(files):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Superblock Address</th>
                <th>Mount Point</th>
                <th>Device</th>
                <th>Inode Number</th>
                <th>Inode Address</th>
                <th>File Type</th>
                <th>Inode Pages</th>
                <th>Cached Pages</th>
                <th>File Mode</th>
                <th>Access Time</th>
                <th>Modification Time</th>
                <th>Change Time</th>
                <th>File Path</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{f['superblock_addr']}</td>
                <td>{f['mount_point']}</td>
                <td>{f['device']}</td>
                <td>{f['inode_num']}</td>
                <td>{f['inode_addr']}</td>
                <td>{f['file_type']}</td>
                <td>{f['inode_pages']}</td>
                <td>{f['cached_pages']}</td>
                <td>{f['file_mode']}</td>
                <td>{' '.join(f['access_time'])}</td>
                <td>{' '.join(f['modification_time'])}</td>
                <td>{' '.join(f['change_time'])}</td>
                <td>{f['file_path']}</td>
            </tr>
            ''' for f in files)}
        </tbody>
    </table>
    """

def generate_pslist_html(processes):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Offset</th>
                <th>PID</th>
                <th>TID</th>
                <th>PPID</th>
                <th>Comm</th>
                <th>Creation Time</th>
                <th>File Output</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['offset']}</td>
                <td>{p['pid']}</td>
                <td>{p['tid']}</td>
                <td>{p['ppid']}</td>
                <td>{p['comm']}</td>
                <td>{p['creation_time']}</td>
                <td>{p['file_output']}</td>
            </tr>
            ''' for p in processes)}
        </tbody>
    </table>
    """
    return f"""
    <table>
        <thead>
            <tr>
                <th>Périphérique</th>
                <th>Point de montage</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{m['device']}</td>
                <td>{m['mountpoint']}</td>
                <td>{m['type']}</td>
            </tr>
            ''' for m in mounts)}
        </tbody>
    </table>
    """

if __name__ == '__main__':
    app.run(port=8000, debug=True) 