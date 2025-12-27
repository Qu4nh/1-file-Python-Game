import os
import hashlib
import requests
import time
from tqdm import tqdm

API_KEY = "" #API của virustotal
FOLDER_PATH = r"" #Path cần quét

VT_HEADERS = {
    "x-apikey": API_KEY
}

# Tính SHA256
def get_sha256(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

# Kiểm tra file có tồn tại trên VT chưa
def check_file_exists(sha256):
    url = f"https://www.virustotal.com/api/v3/files/{sha256}"
    r = requests.get(url, headers=VT_HEADERS)
    if r.status_code == 200:
        return r.json()
    return None

# Upload file nếu chưa có
def upload_file(filepath):
    url = "https://www.virustotal.com/api/v3/files"
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f)}
        r = requests.post(url, headers=VT_HEADERS, files=files)
        if r.status_code == 200:
            analysis_id = r.json()["data"]["id"]
            return get_scan_result(analysis_id)
    return None

# Lấy kết quả phân tích (sau khi upload)
def get_scan_result(analysis_id):
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    for _ in range(10):
        r = requests.get(url, headers=VT_HEADERS)
        if r.status_code == 200:
            result = r.json()
            status = result["data"]["attributes"]["status"]
            if status == "completed":
                return result
        time.sleep(5)
    return None

# Tóm tắt kết quả
def summarize_result(file, result):
    if "data" not in result:
        print(f"[ERROR] Không thể quét {file}")
        return
    stats = result["data"]["attributes"]["last_analysis_stats"]
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    harmless = stats.get("harmless", 0)
    total = sum(stats.values())

    if malicious > 0 or suspicious > 0:
        status = "❌ NGUY HIỂM"
    else:
        status = "✅ AN TOÀN"

    print(f"{file}: {status} (Malicious: {malicious}, Suspicious: {suspicious}, Harmless: {harmless}/{total})")

# Chạy kiểm tra toàn bộ folder
def scan_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for name in tqdm(files, desc="Scanning files"):
            path = os.path.join(root, name)
            try:
                sha256 = get_sha256(path)
                result = check_file_exists(sha256)
                if not result:
                    print(f"[UPLOAD] {name} chưa có trên VT. Đang upload...")
                    result = upload_file(path)
                summarize_result(name, result)
                time.sleep(15)  
            except Exception as e:
                print(f"[ERROR] {name}: {str(e)}")

# Bắt đầu
if __name__ == "__main__":
    scan_folder(FOLDER_PATH)
