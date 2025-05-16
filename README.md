# Volinux - Linux Memory Dump Analyzer

Volinux is a modern web-based platform for analyzing Linux memory dumps, combining powerful memory forensics capabilities with an intuitive user interface.

## 🚀 Features

- Modern, responsive web interface with multilingual support (EN/FR)
- Automatic Linux kernel version and distribution detection
- Execute various Volatility3 plugins for in-depth memory forensics
- Interactive results with filtering capabilities
- Docker-based deployment for easy setup

## 🔍 Supported Analysis Types

- **Bash History** (`linux.bash`) - View command history from bash sessions
- **Environment Variables** (`linux.envars`) - Examine environment variables
- **IP Addresses** (`linux.ip.Addr`) - List network address configurations
- **Network Interfaces** (`linux.ip.Link`) - Examine network interfaces
- **Boot Time Information** (`linux.boottime.Boottime`) - View system boot time
- **Files in Memory** (`linux.pagecache.Files`) - Examine cached files
- **Process List** (`linux.pslist.PsList`) - View running processes

## 🛠️ Tech Stack

### Frontend
- React 19.1.0
- Tailwind CSS 3.3.0
- Axios for API communication
- Modern JavaScript features and responsive design

### Backend
- Flask 3.0.0 (Python)
- Flask-CORS for cross-origin requests
- Volatility3 2.11.0 for memory forensics
- Gunicorn for production deployment

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/volinux.git
   cd volinux
   ```

2. Start the application using Docker Compose:

    ```bash
    docker-compose up
    ```

3. Access the application:
    - http://localhsot:3000

## 📋 Usage

1. Upload a Linux memory dump file via the web interface

2. The system will automatically detect the kernel version and distribution

3. Select one of the available plugins to analyze specific aspects of the memory dump

4. View and filter the detailed results in a new browser tab


## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact
For questions or support, please open an issue in the GitHub repository.
