# 👾 ShadowRecon

![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Security](https://img.shields.io/badge/recon-OSINT-red)

A lightweight, high-speed passive reconnaissance and web intelligence gathering tool written in Python. ShadowRecon extracts critical server details, maps subdomains, visualizes DNS architecture, and generates active search intelligence vectors without making intrusive connections to the target infrastructure.

## 🚀 Features

- **Infrastructure Fingerprinting:** Extracts HTTP header insights, featuring modern TLS verification bypasses and firewall/CDN detection protocols.
- **Subdomain Mapping:** Queries high-availability public intelligence log sources to map unique exposed subdomains seamlessly.
- **DNS Intelligence Visualization:** Automatically enumerates and categorizes target domain DNS records including A, MX, NS, and TXT mapping.
- **Automated Intelligence Dorking:** Generates precise Google Dork links targeting configuration files, database backups, admin portals, and exposed sensitive documentation.
- **Clean HTML Reporting:** Compiles all captured operational insights into a standalone, dark-themed cyber reconnaissance static web report (`recon_report.html`).

## 🛠️ Installation & Setup

1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/fzirp/ShadowRecon.git
cd ShadowRecon
```
Install the required network dependencies:

```Bash
pip install -r requirements.txt
```
Run the reconnaissance engine:

```Bash
python shadow_recon.py
```
📊 Sample Output
The execution pipeline generates a professional standalone interactive summary dashboard tracking subdomains, raw DNS layers, technology stacks, and operational intelligence vectors.
