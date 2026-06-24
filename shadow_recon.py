#!/usr/bin/env python3
import requests
import json
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_server_details(target_domain):
    print(f"[*] Analyzing headers for: {target_domain}")
    headers_to_check = ["Server", "X-Powered-By", "Content-Security-Policy"]
    
    # Strategy 1: Try standard HTTPS first
    try:
        url = f"https://www.{target_domain}"
        response = requests.get(url, timeout=8, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        res_headers = response.headers
        server = res_headers.get("Server", "Unknown")
        powered_by = res_headers.get("X-Powered-By", "Unknown")
        csp = "Present" if "Content-Security-Policy" in res_headers else "Missing"
        print(f"[+] Server Technology: {server}")
        return {"server": server, "powered_by": powered_by, "csp": csp}
    except Exception:
        # Strategy 2: Fallback to HTTP if SSL/TLS handshakes fail
        try:
            url = f"http://www.{target_domain}"
            response = requests.get(url, timeout=8, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            res_headers = response.headers
            server = res_headers.get("Server", "Unknown")
            powered_by = res_headers.get("X-Powered-By", "Unknown")
            csp = "Present" if "Content-Security-Policy" in res_headers else "Missing"
            print(f"[+] Server Technology (via HTTP Fallback): {server}")
            return {"server": server, "powered_by": powered_by, "csp": csp}
        except Exception as e:
            print(f"[-] Infrastructure analysis failed completely: {e}")
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

def get_dns_records(target_domain):
    print(f"[*] Querying DNS records via HackerTarget for: {target_domain}")
    dns_results = {}
    try:
        url = f"https://api.hackertarget.com/dnslookup/?q={target_domain}"
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200 and "error" not in response.text.lower():
            lines = response.text.split("\n")
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    # Categorize by common record types (A, MX, TXT, NS)
                    r_type = "UNKNOWN"
                    for t in ["A", "MX", "TXT", "NS", "CNAME", "AAAA"]:
                        if t in parts or (t == "A" and any(c.isdigit() for c in parts[-1]) and len(parts)==2):
                            r_type = t
                            break
                    if r_type not in dns_results:
                        dns_results[r_type] = []
                    dns_results[r_type].append(line.strip())
            
            for r_type, records in dns_results.items():
                print(f"[+] Found {len(records)} {r_type} record(s).")
            return dns_results
    except Exception as e:
        print(f"[-] Error querying DNS records: {e}")
    
    print("[-] No public DNS records captured.")
    return {}

def generate_google_dorks(target_domain):
    print(f"[*] Generating Google Dorking intelligence links for: {target_domain}")
    return {
        "Publicly Exposed Documents": f"https://www.google.com/search?q=site:{target_domain}+filetype:pdf+OR+filetype:doc+OR+filetype:docx+OR+filetype:xls+OR+filetype:xlsx",
        "Configuration & Backup Files": f"https://www.google.com/search?q=site:{target_domain}+filetype:sql+OR+filetype:env+OR+filetype:ini+OR+filetype:log+OR+filetype:bak",
        "Exposed Admin Panels": f"https://www.google.com/search?q=site:{target_domain}+inurl:admin+OR+inurl:login+OR+inurl:dashboard",
        "Directory Indexing Vulnerabilities": f"https://www.google.com/search?q=site:{target_domain}+intext:%22index+of+%22"
    }

def build_html_report(target_domain, infra, subs, dns, dorks):
    print("[*] Building cyber reconnaissance HTML report...")
    
    subs_li = "".join([f"<li>{sub}</li>" for sub in subs])
    dorks_li = "".join([f"<li><strong>{k}:</strong> <a href='{v}' target='_blank'>Execute Dork Search</a></li>" for k, v in dorks.items()])
    
    dns_html = ""
    if dns:
        for r_type, records in dns.items():
            dns_html += f"<h3>{r_type} Records</h3><ul>"
            for rec in records:
                dns_html += f"<li><code>{rec}</code></li>"
            dns_html += "</ul>"
    else:
        dns_html = "<p>No DNS records captured.</p>"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>ShadowRecon Report - {target_domain}</title>
    <style>
        body {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }}
        h1 {{ color: #58a6ff; border-bottom: 1px solid #21262d; padding-bottom: 10px; }}
        h2 {{ color: #7ee787; margin-top: 30px; border-bottom: 1px solid #30363d; padding-bottom: 5px; }}
        h3 {{ color: #ff79c6; margin-top: 15px; font-size: 16px; }}
        .box {{ background-color: #161b22; padding: 20px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 20px; }}
        ul {{ list-style-type: square; }}
        li {{ margin: 8px 0; }}
        a {{ color: #58a6ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .meta {{ color: #8b949e; font-size: 14px; }}
        code {{ background-color: #21262d; padding: 3px 6px; border-radius: 4px; font-family: monospace; color: #ff7b72; }}
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
        <h2>Phase 3: DNS Intelligence Visualization</h2>
        {dns_html}
    </div>

    <div class="box">
        <h2>Phase 4: Active Google Dorking Vectors</h2>
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
        
        print("\n--- PHASE 3: DNS VISUALIZATION ---")
        dns_data = get_dns_records(target)
        
        print("\n--- PHASE 4: GOOGLE DORKING AUTOMATION ---")
        dork_links = generate_google_dorks(target)
        
        print("\n--- PHASE 5: GENERATING REPORT ---")
        build_html_report(target, infra_data, subdomain_list, dns_data, dork_links)
        
        print("\n==================================================")
        print("[+] Recon Session Completed Successfully.")
        print("==================================================")
