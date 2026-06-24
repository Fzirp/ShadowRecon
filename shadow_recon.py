import requests
import json
import urllib3
import time
import ssl
from requests.adapters import HTTPAdapter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def get_server_details(target_domain):
    print(f"[*] Analyzing headers for: {target_domain}")
    try:
        url = f"https://www.{target_domain}"
        session = requests.Session()
        session.mount("https://", TLSAdapter())
        
        response = session.get(url, timeout=10, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        
        headers = response.headers
        server = headers.get("Server", "Unknown")
        powered_by = headers.get("X-Powered-By", "Unknown")
        security_policy = "Present" if "Content-Security-Policy" in headers else "Missing"
        
        print(f"[+] Server Technology: {server}")
        print(f"[+] Powered By: {powered_by}")
        print(f"[+] Content Security Policy: {security_policy}")
        
        return {"server": server, "powered_by": powered_by, "csp": security_policy}
    except Exception as e:
        print(f"[-] Error retrieving headers: {e}")
        return {"server": "Unknown", "powered_by": "Unknown", "csp": "Unknown"}

def find_subdomains(target_domain):
    print(f"[*] Extracting subdomains for: {target_domain}")
    subdomains = set()
    
    for attempt in range(2):
        try:
            url = f"https://crt.sh/?q=%.{target_domain}&output=json"
            response = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name = entry["name_value"]
                    for part in name.split("\n"):
                        if not part.startswith("*"):
                            subdomains.add(part.strip())
                break
        except Exception:
            if attempt < 1:
                time.sleep(2)
                
    if not subdomains:
        try:
            backup_url = f"https://api.hackertarget.com/hostsearch/?q={target_domain}"
            response = requests.get(backup_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200 and "error" not in response.text.lower():
                lines = response.text.split("\n")
                for line in lines:
                    if "," in line:
                        sub = line.split(",")[0]
                        subdomains.add(sub.strip())
        except Exception:
            pass

    if subdomains:
        print(f"[+] Successfully found {len(subdomains)} unique subdomains.")
        return sorted(list(subdomains))
    else:
        print("[-] Could not retrieve subdomains from public intelligence sources.")
        return []

def generate_google_dorks(target_domain):
    print(f"[*] Generating Google Dorking intelligence links for: {target_domain}")
    return {
        "Publicly Exposed Documents": f"https://www.google.com/search?q=site:{target_domain}+filetype:pdf+OR+filetype:doc+OR+filetype:docx+OR+filetype:xls+OR+filetype:xlsx",
        "Configuration & Backup Files": f"https://www.google.com/search?q=site:{target_domain}+filetype:sql+OR+filetype:env+OR+filetype:ini+OR+filetype:log+OR+filetype:bak",
        "Exposed Admin Panels": f"https://www.google.com/search?q=site:{target_domain}+inurl:admin+OR+inurl:login+OR+inurl:dashboard",
        "Directory Indexing Vulnerabilities": f"https://www.google.com/search?q=site:{target_domain}+intext:%22index+of+%22"
    }

def build_html_report(target_domain, infra, subs, dorks):
    print("[*] Building cyber reconnaissance HTML report...")
    
    subs_li = "".join([f"<li>{sub}</li>" for sub in subs])
    dorks_li = "".join([f"<li><strong>{k}:</strong> <a href='{v}' target='_blank'>Execute Dork Search</a></li>" for k, v in dorks.items()])
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>ShadowRecon Report - {target_domain}</title>
    <style>
        body {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }}
        h1 {{ color: #58a6ff; border-bottom: 1px solid #21262d; padding-bottom: 10px; }}
        h2 {{ color: #7ee787; margin-top: 30px; }}
        .box {{ background-color: #161b22; padding: 20px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 20px; }}
        ul {{ list-style-type: square; }}
        li {{ margin: 10px 0; }}
        a {{ color: #58a6ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .meta {{ color: #8b949e; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>SHADOWRECON INTELLIGENCE REPORT</h1>
    <p class="meta">Target Domain: <strong>{target_domain}</strong></p>
    
    <div class="box">
        <h2>Phase 1: Infrastructure & Tech Stack</h2>
        <p><strong>Server Architecture:</strong> {infra['server']}</p>
        <p><strong>Powered By Technology:</strong> {infra['powered_by']}</p>
        <p><strong>Content Security Policy (CSP):</strong> {infra['csp']}</p>
    </div>

    <div class="box">
        <h2>Phase 2: Discovered Subdomains ({len(subs)})</h2>
        <ul>{subs_li if subs else "<li>No subdomains found.</li>"}</ul>
    </div>

    <div class="box">
        <h2>Phase 3: Active Google Dorking Vectors</h2>
        <ul>{dorks_li}</ul>
    </div>
</body>
</html>
"""
    with open("recon_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[+] Report saved successfully as 'recon_report.html'.")

if __name__ == "__main__":
    print("==================================================")
    print("      SHADOWRECON - RECONNAISSANCE ENGINE         ")
    print("==================================================")
    
    target = input("[?] Enter target domain (e.g., github.com): ").strip()
    if target:
        target = target.replace("https://", "").replace("http://", "").replace("www.", "")
        
        print("\n--- PHASE 1: INFRASTRUCTURE ANALYSIS ---")
        infra_data = get_server_details(target)
        
        print("\n--- PHASE 2: SUBDOMAIN DISCOVERY ---")
        subdomain_list = find_subdomains(target)
        
        print("\n--- PHASE 3: GOOGLE DORKING AUTOMATION ---")
        dork_links = generate_google_dorks(target)
        
        print("\n--- PHASE 4: GENERATING REPORT ---")
        build_html_report(target, infra_data, subdomain_list, dork_links)
        
        print("\n==================================================")
        print("[+] Recon Session Completed Successfully.")
        print("==================================================")