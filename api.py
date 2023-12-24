from flask import Flask, request, jsonify
import hashlib
import json
from datetime import datetime

app = Flask(__name__)

# Constants for predefined strings used in the hash
STD1 = "5e8dd316726b0335"
STD2 = "97b7bc6be525ab44"
LOG_FILE = 'logs.json'

def md5_hash(plaintext):
    return hashlib.md5(plaintext.encode('ascii')).hexdigest()

def xor_hash_bytes(md5_hash_str):
    xor_result = [0x00, 0x00, 0x00, 0x00]
    hash_bytes = [int(md5_hash_str[i:i+2], 16) for i in range(0, len(md5_hash_str), 2)]
    
    for i in range(4):
        for j in range(4):
            xor_result[j] ^= hash_bytes[i * 4 + j]
            
    xor_result[0] = (xor_result[0] & 1) | 2
    return xor_result

def calculate_code(imei, std):
    hash_str = md5_hash(imei + std)
    xor_result = xor_hash_bytes(hash_str)
    return (xor_result[0] << 24) | (xor_result[1] << 16) | (xor_result[2] << 8) | xor_result[3]

def log_usage(ip, imei):
    with open(LOG_FILE, 'r+') as file:
        try:
            logs = json.load(file)
        except json.JSONDecodeError:
            logs = {}
        
        if ip not in logs:
            logs[ip] = {"first_used": str(datetime.now()), "imeis": []}
        
        logs[ip]["last_used"] = str(datetime.now())
        if imei not in logs[ip]["imeis"]:
            logs[ip]["imeis"].append(imei)
        
        file.seek(0)
        json.dump(logs, file, indent=4)

def is_valid_imei(imei):
    if len(imei) != 15 or not imei.isdigit() or not imei.startswith("35"):
        return False

    sum = 0
    mul = 2
    for i in range(14):
        digit = int(imei[13-i])  # Get digit in reverse order
        product = digit * mul
        sum += product // 10 + product % 10  # Add sum of digits in product (same as adding digits for 10 or above)
        mul = 1 if mul == 2 else 2  # Alternate multiplier between 2 and 1

    check_digit = (10 - (sum % 10)) % 10
    return check_digit == int(imei[-1])

@app.route('/api/v1/ucode', methods=['POST'])
def get_unlock_code():
    data = request.get_json()
    imei = data.get('imei')

    # Validate the IMEI before proceeding
    if not is_valid_imei(imei):
        return jsonify({"error": "Invalid IMEI"}), 400
    
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    unlock_code = calculate_code(imei, STD1)
    return jsonify({"unlock_code": unlock_code})

@app.route('/api/v1/fcode', methods=['POST'])
def get_flash_code():
    data = request.get_json()
    imei = data.get('imei')

    # Validate the IMEI before proceeding
    if not is_valid_imei(imei):
        return jsonify({"error": "Invalid IMEI"}), 400
    
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    flash_code = calculate_code(imei, STD2)
    return jsonify({"flash_code": flash_code})

@app.route('/api/v1/all', methods=['POST'])
def get_all_codes():
    data = request.get_json()
    imei = data.get('imei')

    # Validate the IMEI before proceeding
    if not is_valid_imei(imei):
        return jsonify({"error": "Invalid IMEI"}), 400
    
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    
    unlock_code = calculate_code(imei, STD1)
    flash_code = calculate_code(imei, STD2)
    
    return jsonify({
        "unlock_code": unlock_code,
        "flash_code": flash_code
    })

if __name__ == '__main__':
    app.run(debug=False)
