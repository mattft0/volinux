from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
import logging
import re
import pdfkit

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dictionnaire de traductions
translations = {
    'en': {
        'title': 'Analysis Results - {command}',
        'os': 'Operating System',
        'kernel_version': 'Kernel Version',
        'distribution': 'Distribution',
        'distribution_version': 'Distribution Version',
        'executed_command': 'Executed Command',
        'pid': 'PID',
        'process': 'Process',
        'time': 'Time',
        'command': 'Command',
        'ppid': 'PPID',
        'comm': 'COMM',
        'key': 'KEY',
        'value': 'VALUE',
        'time_ns': 'Time NS',
        'boot_time': 'Boot Time',
        'superblock_addr': 'Superblock Address',
        'mount_point': 'Mount Point',
        'device': 'Device',
        'inode_num': 'Inode Number',
        'inode_addr': 'Inode Address',
        'file_type': 'File Type',
        'inode_pages': 'Inode Pages',
        'cached_pages': 'Cached Pages',
        'file_mode': 'File Mode',
        'access_time': 'Access Time',
        'modification_time': 'Modification Time',
        'change_time': 'Change Time',
        'file_path': 'File Path',
        'offset': 'Offset',
        'tid': 'TID',
        'creation_time': 'Creation Time',
        'file_output': 'File Output',
        'switch_to_fr': 'Switch to French',
        'switch_to_en': 'Switch to English',
        'netns': 'NetNS',
        'index': 'Index',
        'interface': 'Interface',
        'mac': 'MAC Address',
        'promiscuous': 'Promiscuous',
        'ip': 'IP Address',
        'prefix': 'Prefix',
        'scope': 'Scope',
        'type': 'Type',
        'state': 'State',
        'module': 'Module',
        'codesize': 'Code Size',
        'taints': 'Taints',
        'arguments': 'Arguments',
        'fileoutput': 'File Output',
        'name': 'Name',
        'loadaddress': 'Load Address',
        'path': 'Path',
        'mountpoint': 'Mount Point',
        'device': 'Device',
        'inodenum': 'Inode Number',
        'inodeaddr': 'Inode Address',
        'filetype': 'File Type',
        'inodepages': 'Inode Pages',
        'cachedpages': 'Cached Pages',
        'filemode': 'File Mode',
        'accesstime': 'Access Time',
        'modificationtime': 'Modification Time',
        'changetime': 'Change Time',
        'filepath': 'File Path',
        'inodesize': 'Inode Size',
        'recovered': 'Recovered',
        'args': 'Arguments',
        'address': 'Address',
        'handleraddr': 'Handler Address',
        'handlersymb': 'Handler Symbol',
        'name': 'Name',
        'address': 'Address',
        'handleraddr': 'Handler Address',
        'handlersymb': 'Handler Symbol',
        'name': 'Name',
        'download_pdf': 'Download as PDF'
    },
    'fr': {
        'title': 'Résultats de l\'analyse - {command}',
        'os': 'Système d\'exploitation',
        'kernel_version': 'Version du noyau',
        'distribution': 'Distribution',
        'distribution_version': 'Version de la distribution',
        'executed_command': 'Commande exécutée',
        'pid': 'PID',
        'process': 'Processus',
        'time': 'Heure',
        'command': 'Commande',
        'ppid': 'PPID',
        'comm': 'COMM',
        'key': 'CLÉ',
        'value': 'VALEUR',
        'time_ns': 'Temps NS',
        'boot_time': 'Temps de démarrage',
        'superblock_addr': 'Adresse Superblock',
        'mount_point': 'Point de montage',
        'device': 'Périphérique',
        'inode_num': 'Numéro Inode',
        'inode_addr': 'Adresse Inode',
        'file_type': 'Type de fichier',
        'inode_pages': 'Pages Inode',
        'cached_pages': 'Pages en cache',
        'file_mode': 'Mode fichier',
        'access_time': 'Heure d\'accès',
        'modification_time': 'Heure de modification',
        'change_time': 'Heure de changement',
        'file_path': 'Chemin du fichier',
        'offset': 'Offset',
        'tid': 'TID',
        'netns': 'NetNS',
        'index': 'Index',
        'interface': 'Interface',
        'mac': 'Adresse MAC',
        'promiscuous': 'Promiscuité',
        'ip': 'Adresse IP',
        'prefix': 'Préfixe',
        'scope': 'Portée',
        'type': 'Type',
        'state': 'État',    
        'creation_time': 'Heure de création',
        'file_output': 'Sortie fichier',
        'switch_to_fr': 'Passer en français',
        'switch_to_en': 'Passer en anglais',
        'download_pdf': 'Télécharger en PDF'
    }
}

def get_profile(dump_path):
    try:
        logger.debug(f"Analyse du fichier dump: {dump_path}")
        
        # Exécuter la commande Volatility3 pour récupérer le profil
        cmd = [
            'python3', '/opt/volatility3/vol.py',  # Utiliser la commande 'vol' directement
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
            'python3', '/opt/volatility3/vol.py',
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
        elif command == "linux.ip.Addr":
            ip_addresses = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    # Create a base structure with default values
                    entry = {
                        'netns': 'N/A',
                        'index': 'N/A',
                        'interface': 'N/A',
                        'mac': 'N/A',
                        'promiscuous': 'N/A',
                        'ip': 'N/A',
                        'prefix': 'N/A',
                        'scope': 'N/A',
                        'type': 'N/A',
                        'state': 'N/A'
                    }
                    
                    # Fill in values from the line if they exist
                    if len(parts) > 0: entry['netns'] = parts[0]
                    if len(parts) > 1: entry['index'] = parts[1]
                    if len(parts) > 2: entry['interface'] = parts[2]
                    if len(parts) > 3: entry['mac'] = parts[3]
                    if len(parts) > 4: entry['promiscuous'] = parts[4]
                    if len(parts) > 5: entry['ip'] = parts[5]
                    if len(parts) > 6: entry['prefix'] = parts[6]
                    if len(parts) > 7: entry['scope'] = parts[7]
                    if len(parts) > 8: entry['type'] = parts[8]
                    if len(parts) > 9: entry['state'] = parts[9]
                    
                    # Only add non-empty lines with at least an interface name
                    if len(parts) >= 3:
                        ip_addresses.append(entry)
            return ip_addresses, None
        elif command == "linux.check_syscall.Check_syscall":
            syscalls = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 5:
                        syscalls.append({
                            'address': parts[0],
                            'name': parts[1],
                            'index': parts[2],
                            'handleraddr': parts[3],
                            'handlersymb': parts[4]
                        })
            return syscalls, None
        elif command == "linux.elfs.Elfs":
            elfs = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 6:
                        elfs.append({
                            'pid': parts[0],
                            'process': parts[1],
                            'start': parts[2],
                            'end': parts[3],
                            'filepath': parts[4],
                            'fileoutput': parts[5]
                        })
            return elfs, None
        elif command == "linux.hidden_modules.Hidden_modules":
            hidden_modules = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 6:
                        hidden_modules.append({
                            'offset': parts[0],
                            'module': parts[1],
                            'codesize': parts[2],
                            'taints': parts[3],
                            'arguments': parts[4],
                            'fileoutput': parts[5]
                        })
            return hidden_modules, None
        elif command == "linux.library_list.LibraryList":
            libraries = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 4:
                        libraries.append({
                            'name': parts[0],
                            'pid': parts[1],
                            'loadaddress': parts[2],
                            'path': parts[3]
                        })
            return libraries, None
        elif command == "linux.pagecache.RecoverFs":
            recover_fs = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 15:
                        recover_fs.append({
                            'blockaddr': parts[0],
                            'mountpoint': parts[1],
                            'device': parts[2],
                            'inodenum': parts[3],
                            'inodeaddr': parts[4],
                            'filetype': parts[5],
                            'inodepages': parts[6],
                            'cachedpages': parts[7],
                            'filemode': parts[8],
                            'accesstime': parts[9:12],
                            'modificationtime': parts[12:15],
                            'changetime': parts[15:18],
                            'filepath': parts[18],
                            'inodesize': parts[19],
                            'recovered': parts[20]
                        })
            return recover_fs, None
        elif command == "linux.psaux.PsAux":
            psaux = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Volatility'):
                    parts = line.split()
                    if len(parts) >= 4:
                        psaux.append({
                            'pid': parts[0],
                            'ppid': parts[1],
                            'comm': parts[2],
                            'args': parts[3]
                        })
            return psaux, None
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
        lang = request.args.get('lang', 'en')
        t = translations[lang]
        
        # Générer le HTML en fonction de la commande
        if command == "linux.bash":
            html = generate_bash_html(output[1:], t)
        elif command == "linux.envars":
            html = generate_envars_html(output[1:], t)
        elif command == "linux.boottime.Boottime":
            html = generate_boottime_html(output[1:], t)
        elif command == "linux.pagecache.Files":
            html = generate_pagecache_files_html(output[1:], t)
        elif command == "linux.pslist.PsList":
            html = generate_pslist_html(output[1:], t)
        elif command == "linux.ip.Addr":
            html = generate_ipaddr_html(output[1:], t)
        elif command == "linux.check_syscall.Check_syscall":
            html = generate_check_syscall_html(output[1:], t)
        elif command == "linux.elfs.Elfs":
            html = generate_elfs_html(output[1:], t)
        elif command == "linux.hidden_modules.Hidden_modules":
            html = generate_hidden_modules_html(output[1:], t)
        elif command == "linux.library_list.LibraryList":
            html = generate_library_list_html(output[1:], t)
        elif command == "linux.pagecache.RecoverFs":
            html = generate_recover_fs_html(output[1:], t)
        elif command == "linux.psaux.PsAux":
            html = generate_psaux_html(output[1:], t)
        else:
            html = "<p>Format de sortie non supporté</p>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@100..900&display=swap" rel="stylesheet">
            <title>{t['title'].format(command=command)}</title>
            <style>
                body {{
                    font-family: 'Lexend', sans-serif;
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
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                h1 {{
                    color: #333;
                    margin: 0;
                }}
                .language-switch {{
                    margin-left: 20px;
                }}
                .language-switch button {{
                    padding: 8px 16px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background-color 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .language-switch button:hover {{
                    background-color: #0056b3;
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
                .filter-row {{
                    background-color: #f8f9fa;
                }}
                .filter-row input {{
                    width: 100%;
                    padding: 4px;
                    margin: 2px 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }}
                .filter-row input:focus {{
                    outline: none;
                    border-color: #007bff;
                    box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
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
                .button-container {{
                    margin-top: 20px;
                    text-align: right;
                    margin-bottom: 20px;
                }}
                .download-button {{
                    padding: 10px 20px;
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    text-decoration: none;
                    display: inline-block;
                }}
                .download-button:hover {{
                    background-color: #218838;
                }}
            </style>
            <script>
                function filterTable(tableId) {{
                    const table = document.getElementById(tableId);
                    const filters = table.getElementsByClassName('filter-input');
                    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

                    for (let i = 0; i < rows.length; i++) {{
                        let showRow = true;
                        for (let j = 0; j < filters.length; j++) {{
                            const filterValue = filters[j].value.toLowerCase();
                            const cellValue = rows[i].getElementsByTagName('td')[j].textContent.toLowerCase();
                            if (!cellValue.includes(filterValue)) {{
                                showRow = false;
                                break;
                            }}
                        }}
                        rows[i].style.display = showRow ? '' : 'none';
                    }}
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{t['title'].format(command=command)}</h1>
                    <div class="language-switch">
                        <a href="?lang={'fr' if lang == 'en' else 'en'}">
                            <button>{t['switch_to_fr'] if lang == 'en' else t['switch_to_en']}</button>
                        </a>
                    </div>
                </div>
                <div class="button-container">
                    <a href="/download_pdf?lang={lang}" class="download-button">
                        {t.get('download_pdf', 'Download as PDF')}
                    </a>
                </div>
                <div class="info">
                    <p><strong>{t['os']}:</strong> {results.get('os', 'N/A')}</p>
                    <p><strong>{t['kernel_version']}:</strong> {results.get('kernel_version', 'N/A')}</p>
                    <p><strong>{t['distribution']}:</strong> {results.get('distribution', 'N/A')}</p>
                    <p><strong>{t['distribution_version']}:</strong> {results.get('distribution_version', 'N/A')}</p>
                    <p><strong>{t['executed_command']}:</strong> {command}</p>
                </div>
                {html}
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"
    
@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    try:
        with open('last_analysis.json', 'r') as f:
            results = json.load(f)
        
        command = results.get('command', '')
        output = results.get('output', [])
        lang = request.args.get('lang', 'en')
        t = translations[lang]
        
        # Générer le HTML spécifique pour PDF (sans les filtres)
        if command == "linux.bash":
            html = generate_bash_html_pdf(output[1:], t)
        elif command == "linux.envars":
            html = generate_envars_html_pdf(output[1:], t)
        elif command == "linux.boottime.Boottime":
            html = generate_boottime_html_pdf(output[1:], t)
        elif command == "linux.pagecache.Files":
            html = generate_pagecache_files_html_pdf(output[1:], t)
        elif command == "linux.pslist.PsList":
            html = generate_pslist_html_pdf(output[1:], t)
        elif command == "linux.ip.Addr":
            html = generate_ipaddr_html_pdf(output[1:], t)
        elif command == "linux.check_syscall.Check_syscall":
            html = generate_check_syscall_html_pdf(output[1:], t)
        elif command == "linux.elfs.Elfs":
            html = generate_elfs_html_pdf(output[1:], t)
        elif command == "linux.hidden_modules.Hidden_modules":
            html = generate_hidden_modules_html_pdf(output[1:], t)
        elif command == "linux.library_list.LibraryList":
            html = generate_library_list_html_pdf(output[1:], t)
        elif command == "linux.pagecache.RecoverFs":
            html = generate_recover_fs_html_pdf(output[1:], t)
        elif command == "linux.psaux.PsAux":
            html = generate_psaux_html_pdf(output[1:], t)
        else:
            html = "<p>Format de sortie non supporté</p>"
        
        # Créer le HTML complet
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{t['title'].format(command=command)}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 10px; /* Réduire la taille de police pour les tableaux */
                }}
                th, td {{
                    padding: 6px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                .info {{
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #e9ecef;
                    border-radius: 4px;
                }}
                h1 {{
                    font-size: 18px;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <div>
                <h1>{t['title'].format(command=command)}</h1>
                <div class="info">
                    <p><strong>{t['os']}:</strong> {results.get('os', 'N/A')}</p>
                    <p><strong>{t['kernel_version']}:</strong> {results.get('kernel_version', 'N/A')}</p>
                    <p><strong>{t['distribution']}:</strong> {results.get('distribution', 'N/A')}</p>
                    <p><strong>{t['distribution_version']}:</strong> {results.get('distribution_version', 'N/A')}</p>
                    <p><strong>{t['executed_command']}:</strong> {command}</p>
                </div>
                {html}
            </div>
        </body>
        </html>
        """
        
        # Créer un fichier temporaire pour le PDF
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        pdf_path = temp_file.name
        temp_file.close()
        
        # Générer le PDF à partir du HTML
        pdfkit_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.5in',
            'margin-bottom': '0.75in',
            'margin-left': '0.5in',
            'encoding': 'UTF-8',
            'no-outline': None,
            'orientation': 'Landscape'  # Format paysage pour inclure plus de colonnes
        }
        
        # Utiliser une configuration explicite pour spécifier le chemin de wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        
        pdfkit.from_string(full_html, pdf_path, options=pdfkit_options, configuration=config)
        
        # Envoyer le fichier PDF
        filename = f"volinux_analysis_{command.replace('.', '_')}.pdf"
        return send_file(pdf_path, as_attachment=True, download_name=filename, mimetype='application/pdf')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_bash_html(commands, t):
    return f"""
    <table id="bash-table">
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['process']}</th>
                <th>{t['time']}</th>
                <th>{t['command']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('bash-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('bash-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('bash-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('bash-table')" placeholder="Filter..."></th>
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

def generate_envars_html(envars, t):
    return f"""
    <table id="envars-table">
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['ppid']}</th>
                <th>{t['comm']}</th>
                <th>{t['key']}</th>
                <th>{t['value']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('envars-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('envars-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('envars-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('envars-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('envars-table')" placeholder="Filter..."></th>
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

def generate_ipaddr_html(ip_addresses, t):
    return f"""
    <table id="ipaddr-table">
        <thead>
            <tr>
                <th>{t['netns']}</th>
                <th>{t['index']}</th>
                <th>{t['interface']}</th>
                <th>{t['mac']}</th>
                <th>{t['promiscuous']}</th>
                <th>{t['ip']}</th>
                <th>{t['prefix']}</th>
                <th>{t['scope']}</th>
                <th>{t['type']}</th>
                <th>{t['state']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('ipaddr-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{i['netns']}</td>
                <td>{i['index']}</td>
                <td>{i['interface']}</td>
                <td>{i['mac']}</td>
                <td>{i['promiscuous']}</td>
                <td>{i['ip']}</td>
                <td>{i['prefix']}</td>
                <td>{i['scope']}</td>
                <td>{i['type']}</td>
                <td>{i['state']}</td>
            </tr>
            ''' for i in ip_addresses)}
        </tbody>
    </table>
    """

def generate_boottime_html(boottime, t):
    return f"""
    <table id="boottime-table">
        <thead>
            <tr>
                <th>{t['time_ns']}</th>
                <th>{t['boot_time']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('boottime-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('boottime-table')" placeholder="Filter..."></th>
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

def generate_pagecache_files_html(files, t):
    return f"""
    <table id="pagecache-table">
        <thead>
            <tr>
                <th>{t['superblock_addr']}</th>
                <th>{t['mount_point']}</th>
                <th>{t['device']}</th>
                <th>{t['inode_num']}</th>
                <th>{t['inode_addr']}</th>
                <th>{t['file_type']}</th>
                <th>{t['inode_pages']}</th>
                <th>{t['cached_pages']}</th>
                <th>{t['file_mode']}</th>
                <th>{t['access_time']}</th>
                <th>{t['modification_time']}</th>
                <th>{t['change_time']}</th>
                <th>{t['file_path']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pagecache-table')" placeholder="Filter..."></th>
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

def generate_pslist_html(processes, t):
    return f"""
    <table id="pslist-table">
        <thead>
            <tr>
                <th>{t['offset']}</th>
                <th>{t['pid']}</th>
                <th>{t['tid']}</th>
                <th>{t['ppid']}</th>
                <th>{t['comm']}</th>
                <th>{t['creation_time']}</th>
                <th>{t['file_output']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('pslist-table')" placeholder="Filter..."></th>
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

def generate_check_syscall_html(syscall, t):
    return f"""
    <table id="syscall-table">
        <thead>
            <tr>
                <th>{t['address']}</th>
                <th>{t['name']}</th>
                <th>{t['index']}</th>
                <th>{t['handleraddr']}</th>
                <th>{t['handlersymb']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('syscall-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('syscall-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('syscall-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('syscall-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('syscall-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['address']}</td>
                <td>{p['name']}</td>
                <td>{p['index']}</td>
                <td>{p['handleraddr']}</td>
                <td>{p['handlersymb']}</td>
            </tr>
            ''' for p in syscall)}
        </tbody>
    </table>
    """

def generate_elfs_html(elfs, t):
    return f"""
    <table id="elfs-table">
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['process']}</th>
                <th>{t['start']}</th>
                <th>{t['end']}</th>
                <th>{t['filepath']}</th>
                <th>{t['fileoutput']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('elfs-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('elfs-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('elfs-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('elfs-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('elfs-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('elfs-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['pid']}</td>
                <td>{p['process']}</td>
                <td>{p['start']}</td>
                <td>{p['end']}</td>
                <td>{p['filepath']}</td>
                <td>{p['fileoutput']}</td>
            </tr>
            ''' for p in elfs)}
        </tbody>
    </table>
    """

def generate_hidden_modules_html(hiddenmodules, t):
    return f"""
    <table id="hiddenmodules-table">
        <thead>
            <tr>
                <th>{t['offset']}</th>
                <th>{t['module']}</th>
                <th>{t['codesize']}</th>
                <th>{t['taints']}</th>
                <th>{t['arguments']}</th>
                <th>{t['fileoutput']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('hiddenmodules-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('hiddenmodules-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('hiddenmodules-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('hiddenmodules-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('hiddenmodules-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('hiddenmodules-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['offset']}</td>
                <td>{p['module']}</td>
                <td>{p['codesize']}</td>
                <td>{p['taints']}</td>
                <td>{p['arguments']}</td>
                <td>{p['fileoutput']}</td>
            </tr>
            ''' for p in hiddenmodules)}
        </tbody>
    </table>
    """

def generate_library_list_html(library, t):
    return f"""
    <table id="library-table">
        <thead>
            <tr>
                <th>{t['name']}</th>
                <th>{t['pid']}</th>
                <th>{t['loadaddress']}</th>
                <th>{t['path']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['name']}</td>
                <td>{p['pid']}</td>
                <td>{p['loadaddress']}</td>
                <td>{p['path']}</td>
            </tr>
            ''' for p in library)}
        </tbody>
    </table>
    """

def generate_recover_fs_html(library, t):
    return f"""
    <table id="library-table">
        <thead>
            <tr>
                <th>{t['blockaddr']}</th>
                <th>{t['mountpoint']}</th>
                <th>{t['device']}</th>
                <th>{t['inodenum']}</th>
                <th>{t['inodeaddr']}</th>
                <th>{t['filetype']}</th>
                <th>{t['inodepages']}</th>
                <th>{t['cachedpages']}</th>
                <th>{t['filemode']}</th>
                <th>{t['accesstime']}</th>
                <th>{t['modificationtime']}</th>
                <th>{t['changetime']}</th>
                <th>{t['filepath']}</th>
                <th>{t['inodesize']}</th>
                <th>{t['recovered']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('library-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['blockaddr']}</td>
                <td>{p['mountpoint']}</td>
                <td>{p['device']}</td>
                <td>{p['inodenum']}</td>
                <td>{p['inodeaddr']}</td>
                <td>{p['filetype']}</td>
                <td>{p['inodepages']}</td>
                <td>{p['cachedpages']}</td>
                <td>{p['filemode']}</td>
                <td>{' '.join(p['accesstime'])}</td>
                <td>{' '.join(p['modificationtime'])}</td>
                <td>{' '.join(p['changetime'])}</td>
                <td>{p['filepath']}</td>
                <td>{p['inodesize']}</td>
                <td>{p['recovered']}</td>
            </tr>
            ''' for p in library)}
        </tbody>
    </table>
    """

def generate_psaux_html(psaux, t):
    return f"""
    <table id="psaux-table">
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['ppid']}</th>
                <th>{t['comm']}</th>
                <th>{t['args']}</th>
            </tr>
            <tr class="filter-row">
                <th><input type="text" class="filter-input" onkeyup="filterTable('psaux-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('psaux-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('psaux-table')" placeholder="Filter..."></th>
                <th><input type="text" class="filter-input" onkeyup="filterTable('psaux-table')" placeholder="Filter..."></th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['pid']}</td>
                <td>{p['ppid']}</td>
                <td>{p['comm']}</td>
                <td>{p['args']}</td>
            </tr>
            ''' for p in psaux)}
        </tbody>
    </table>
    """

def generate_ipaddr_html_pdf(ip_addresses, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['netns']}</th>
                <th>{t['index']}</th>
                <th>{t['interface']}</th>
                <th>{t['mac']}</th>
                <th>{t['promiscuous']}</th>
                <th>{t['ip']}</th>
                <th>{t['prefix']}</th>
                <th>{t['scope']}</th>
                <th>{t['type']}</th>
                <th>{t['state']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{i['netns']}</td>
                <td>{i['index']}</td>
                <td>{i['interface']}</td>
                <td>{i['mac']}</td>
                <td>{i['promiscuous']}</td>
                <td>{i['ip']}</td>
                <td>{i['prefix']}</td>
                <td>{i['scope']}</td>
                <td>{i['type']}</td>
                <td>{i['state']}</td>
            </tr>
            ''' for i in ip_addresses)}
        </tbody>
    </table>
    """

def generate_bash_html_pdf(commands, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['process']}</th>
                <th>{t['time']}</th>
                <th>{t['command']}</th>
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

def generate_envars_html_pdf(envars, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['ppid']}</th>
                <th>{t['comm']}</th>
                <th>{t['key']}</th>
                <th>{t['value']}</th>
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

def generate_boottime_html_pdf(boottime, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['time_ns']}</th>
                <th>{t['boot_time']}</th>
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

def generate_pagecache_files_html_pdf(files, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['superblock_addr']}</th>
                <th>{t['mount_point']}</th>
                <th>{t['device']}</th>
                <th>{t['inode_num']}</th>
                <th>{t['inode_addr']}</th>
                <th>{t['file_type']}</th>
                <th>{t['inode_pages']}</th>
                <th>{t['cached_pages']}</th>
                <th>{t['file_mode']}</th>
                <th>{t['access_time']}</th>
                <th>{t['modification_time']}</th>
                <th>{t['change_time']}</th>
                <th>{t['file_path']}</th>
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

def generate_pslist_html_pdf(processes, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['offset']}</th>
                <th>{t['pid']}</th>
                <th>{t['tid']}</th>
                <th>{t['ppid']}</th>
                <th>{t['comm']}</th>
                <th>{t['creation_time']}</th>
                <th>{t['file_output']}</th>
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

def generate_check_syscall_html_pdf(syscall, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['address']}</th>
                <th>{t['name']}</th>
                <th>{t['index']}</th>
                <th>{t['handleraddr']}</th>
                <th>{t['handlersymb']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['address']}</td>
                <td>{p['name']}</td>
                <td>{p['index']}</td>
                <td>{p['handleraddr']}</td>
                <td>{p['handlersymb']}</td>
            </tr>
            ''' for p in syscall)}
        </tbody>
    </table>
    """

def generate_elfs_html_pdf(elfs, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['process']}</th>
                <th>{t['start']}</th>
                <th>{t['end']}</th>
                <th>{t['filepath']}</th>
                <th>{t['fileoutput']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['pid']}</td>
                <td>{p['process']}</td>
                <td>{p['start']}</td>
                <td>{p['end']}</td>
                <td>{p['filepath']}</td>
                <td>{p['fileoutput']}</td>
            </tr>
            ''' for p in elfs)}
        </tbody>
    </table>
    """

def generate_hidden_modules_html_pdf(hiddenmodules, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['offset']}</th>
                <th>{t['module']}</th>
                <th>{t['codesize']}</th>
                <th>{t['taints']}</th>
                <th>{t['arguments']}</th>
                <th>{t['fileoutput']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['offset']}</td>
                <td>{p['module']}</td>
                <td>{p['codesize']}</td>
                <td>{p['taints']}</td>
                <td>{p['arguments']}</td>
                <td>{p['fileoutput']}</td>
            </tr>
            ''' for p in hiddenmodules)}
        </tbody>
    </table>
    """

def generate_library_list_html_pdf(library, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['name']}</th>
                <th>{t['pid']}</th>
                <th>{t['loadaddress']}</th>
                <th>{t['path']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['name']}</td>
                <td>{p['pid']}</td>
                <td>{p['loadaddress']}</td>
                <td>{p['path']}</td>
            </tr>
            ''' for p in library)}
        </tbody>
    </table>
    """

def generate_recover_fs_html_pdf(library, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['blockaddr']}</th>
                <th>{t['mountpoint']}</th>
                <th>{t['device']}</th>
                <th>{t['inodenum']}</th>
                <th>{t['inodeaddr']}</th>
                <th>{t['filetype']}</th>
                <th>{t['inodepages']}</th>
                <th>{t['cachedpages']}</th>
                <th>{t['filemode']}</th>
                <th>{t['accesstime']}</th>
                <th>{t['modificationtime']}</th>
                <th>{t['changetime']}</th>
                <th>{t['filepath']}</th>
                <th>{t['inodesize']}</th>
                <th>{t['recovered']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['blockaddr']}</td>
                <td>{p['mountpoint']}</td>
                <td>{p['device']}</td>
                <td>{p['inodenum']}</td>
                <td>{p['inodeaddr']}</td>
                <td>{p['filetype']}</td>
                <td>{p['inodepages']}</td>
                <td>{p['cachedpages']}</td>
                <td>{p['filemode']}</td>
                <td>{' '.join(p['accesstime'])}</td>
                <td>{' '.join(p['modificationtime'])}</td>
                <td>{' '.join(p['changetime'])}</td>
                <td>{p['filepath']}</td>
                <td>{p['inodesize']}</td>
                <td>{p['recovered']}</td>
            </tr>
            ''' for p in library)}
        </tbody>
    </table>
    """

def generate_psaux_html_pdf(psaux, t):
    return f"""
    <table>
        <thead>
            <tr>
                <th>{t['pid']}</th>
                <th>{t['ppid']}</th>
                <th>{t['comm']}</th>
                <th>{t['args']}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{p['pid']}</td>
                <td>{p['ppid']}</td>
                <td>{p['comm']}</td>
                <td>{p['args']}</td>
            </tr>
            ''' for p in psaux)}
        </tbody>
    </table>
    """

if __name__ == '__main__':
    app.run(port=8000, debug=True)