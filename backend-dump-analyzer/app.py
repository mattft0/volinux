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
        if command == "linux.pslist":
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
                            'creation_time': parts[5],
                            'file_output': parts[6]
                        })
            return processes, None
        elif command == "linux.pstree":
            processes = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 4:
                        processes.append({
                            'pid': parts[0],
                            'ppid': parts[1],
                            'name': parts[2],
                            'tree': parts[3]
                        })
            return processes, None
        elif command == "linux.lsof":
            files = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 4:
                        files.append({
                            'pid': parts[0],
                            'fd': parts[1],
                            'path': parts[2],
                            'type': parts[3]
                        })
            return files, None
        elif command == "linux.netstat":
            connections = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 6:
                        connections.append({
                            'pid': parts[0],
                            'protocol': parts[1],
                            'local_addr': parts[2],
                            'remote_addr': parts[3],
                            'state': parts[4],
                            'process': parts[5]
                        })
            return connections, None
        elif command == "linux.bash":
            commands = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 3:
                        commands.append({
                            'pid': parts[0],
                            'time': parts[1],
                            'command': ' '.join(parts[2:])
                        })
            return commands, None
        elif command == "linux.check_modules":
            modules = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 3:
                        modules.append({
                            'name': parts[0],
                            'size': parts[1],
                            'path': parts[2]
                        })
            return modules, None
        elif command == "linux.check_syscall":
            syscalls = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 2:
                        syscalls.append({
                            'address': parts[0],
                            'name': parts[1]
                        })
            return syscalls, None
        elif command == "linux.check_tty":
            ttys = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 3:
                        ttys.append({
                            'name': parts[0],
                            'pid': parts[1],
                            'command': ' '.join(parts[2:])
                        })
            return ttys, None
        elif command == "linux.elfs":
            elfs = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 2:
                        elfs.append({
                            'path': parts[0],
                            'type': parts[1]
                        })
            return elfs, None
        elif command == "linux.mount":
            mounts = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 3:
                        mounts.append({
                            'device': parts[0],
                            'mountpoint': parts[1],
                            'type': parts[2]
                        })
            return mounts, None
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
            
            # Récupérer la liste des processus
            processes, process_error = get_process_list(temp_file.name)
            if process_error:
                logger.error(f"Erreur lors de l'analyse des processus: {process_error}")
                return jsonify({'error': process_error}), 400
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_file.name)
            logger.debug("Fichier temporaire supprimé")
            
            if profile_info:
                # Sauvegarder les résultats dans last_analysis.json
                results = {
                    'os': 'Linux',
                    'kernel_version': profile_info['kernel_version'],
                    'distribution': profile_info['distribution'],
                    'distribution_version': profile_info['distro_version'],
                    'command': 'linux.pslist',
                    'output': processes
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

@app.route('/results', methods=['GET'])
def show_results():
    try:
        with open('last_analysis.json', 'r') as f:
            results = json.load(f)
        
        command = results.get('command', 'linux.pslist')
        output = results.get('output', [])
        
        # Générer le HTML en fonction de la commande
        if command == "linux.pslist":
            html = generate_pslist_html(output)
        elif command == "linux.pstree":
            html = generate_pstree_html(output)
        elif command == "linux.lsof":
            html = generate_lsof_html(output)
        elif command == "linux.netstat":
            html = generate_netstat_html(output)
        elif command == "linux.bash":
            html = generate_bash_html(output)
        elif command == "linux.check_modules":
            html = generate_modules_html(output)
        elif command == "linux.check_syscall":
            html = generate_syscall_html(output)
        elif command == "linux.check_tty":
            html = generate_tty_html(output)
        elif command == "linux.elfs":
            html = generate_elfs_html(output)
        elif command == "linux.mount":
            html = generate_mount_html(output)
        else:
            html = "<p>Format de sortie non supporté</p>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Résultats de l'analyse</title>
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Résultats de l'analyse</h1>
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

def generate_pslist_html(processes):
    return f"""
    <table>
        <thead>
            <tr>
                <th>OFFSET (V)</th>
                <th>PID</th>
                <th>TID</th>
                <th>PPID</th>
                <th>COMM</th>
                <th>CREATION TIME</th>
                <th>File output</th>
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

def generate_pstree_html(processes):
    return f"""
    <table>
        <thead>
            <tr>
                <th>PID</th>
                <th>PPID</th>
                <th>Nom</th>
                <th>Arbre</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['pid']}</td>
                <td>{p['ppid']}</td>
                <td>{p['name']}</td>
                <td>{p['tree']}</td>
            </tr>
            ''' for p in processes)}
        </tbody>
    </table>
    """

def generate_lsof_html(files):
    return f"""
    <table>
        <thead>
            <tr>
                <th>PID</th>
                <th>FD</th>
                <th>Chemin</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{f['pid']}</td>
                <td>{f['fd']}</td>
                <td>{f['path']}</td>
                <td>{f['type']}</td>
            </tr>
            ''' for f in files)}
        </tbody>
    </table>
    """

def generate_netstat_html(connections):
    return f"""
    <table>
        <thead>
            <tr>
                <th>PID</th>
                <th>Protocole</th>
                <th>Adresse locale</th>
                <th>Adresse distante</th>
                <th>État</th>
                <th>Processus</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{c['pid']}</td>
                <td>{c['protocol']}</td>
                <td>{c['local_addr']}</td>
                <td>{c['remote_addr']}</td>
                <td>{c['state']}</td>
                <td>{c['process']}</td>
            </tr>
            ''' for c in connections)}
        </tbody>
    </table>
    """

def generate_bash_html(commands):
    return f"""
    <table>
        <thead>
            <tr>
                <th>PID</th>
                <th>Heure</th>
                <th>Commande</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{c['pid']}</td>
                <td>{c['time']}</td>
                <td>{c['command']}</td>
            </tr>
            ''' for c in commands)}
        </tbody>
    </table>
    """

def generate_modules_html(modules):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>Taille</th>
                <th>Chemin</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{m['name']}</td>
                <td>{m['size']}</td>
                <td>{m['path']}</td>
            </tr>
            ''' for m in modules)}
        </tbody>
    </table>
    """

def generate_syscall_html(syscalls):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Adresse</th>
                <th>Nom</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{s['address']}</td>
                <td>{s['name']}</td>
            </tr>
            ''' for s in syscalls)}
        </tbody>
    </table>
    """

def generate_tty_html(ttys):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>PID</th>
                <th>Commande</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{t['name']}</td>
                <td>{t['pid']}</td>
                <td>{t['command']}</td>
            </tr>
            ''' for t in ttys)}
        </tbody>
    </table>
    """

def generate_elfs_html(elfs):
    return f"""
    <table>
        <thead>
            <tr>
                <th>Chemin</th>
                <th>Type</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{e['path']}</td>
                <td>{e['type']}</td>
            </tr>
            ''' for e in elfs)}
        </tbody>
    </table>
    """

def generate_mount_html(mounts):
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