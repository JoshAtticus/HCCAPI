from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import hashlib # for flash codes
import zlib # for unlock codes

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

LOG_FILE = 'logs.json' # make sure you create the logs.json file before running api!

# predefined strings for flash code/v1 hashing
STD1_V1 = "5e8dd316726b0335"
STD2_V1 = "97b7bc6be525ab44"

# predefined strings for v2 hashing
CUSTOM_CRC32_TABLE = [
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x196c3671, 0x6e6b06e7, 0xfed41b76, 
	0x89d32be0, 0x10da7a5a, 0xfbd44c65, 0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 
	0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb, 0x4369e96a, 0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252, 
	0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b, 0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 
	0xdf60efc3, 0xa867df55, 0x316e8eef, 0x90bf1d91, 0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de, 
	0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7, 0x136c9856, 0xfa0f3d63, 0x8d080df5, 0x3b6e20c8, 
	0x4c69105e, 0xd56041e4, 0xa2677172, 0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b, 0x646ba8c0, 
	0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9, 0x45df5c75, 0xdcd60dcf, 0xabd13d59, 0x26d930ac, 
	0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0x706af48f, 0xe963a535, 
	0x9e6495a3, 0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988, 0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 
	0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0xb8bda50f, 0x2802b89e, 0x5f058808, 
	0xc60cd9b2, 0xb10be924, 0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d, 0x76dc4190, 0x4969474d, 
	0x3e6e77db, 0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 
	0x30b5ffe9, 0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0x03b6e20c, 0x74b1d29a, 
	0xead54739, 0x9dd277af, 0x04db2615, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01, 
	0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e, 0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457, 
	0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xe40ecf0b, 
	0x9309ff9d, 0x0a00ae27, 0x7d079eb1, 0xf00f9344, 0x4669be79, 0xcb61b38c, 0xbc66831a, 0x256fd2a0, 
	0x5268e236, 0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f, 0xc5ba3bbe, 0x68ddb3f8, 0x1fda836e, 
	0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777, 0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 
	0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45, 0xa00ae278, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04, 
	0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d, 0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 
	0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713, 0x346ed9fc, 0xad678846, 0xda60b8d0, 0x44042d73, 
	0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9, 0x5005713c, 0x270241aa, 0xbe0b1010, 0x01db7106, 0x98d220bc, 
	0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433, 0x7807c9a2, 0x0f00f934, 0x9609a88e, 
	0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f, 0x5edef90e, 0x29d9c998, 0xb0d09822, 
	0xc7d7a8b4, 0x59b33d17, 0xcdd70693, 0x54de5729, 0x23d967bf, 0xb3667a2e, 0xc4614ab8, 0x5d681b02, 
	0x2a6f2b94, 0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad, 0xedb88320, 
	0x9abfb3b6, 0x73dc1683, 0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8, 0x67dd4acc, 0xf9b9df6f, 
	0x8ebeeff9, 0x17b7be43, 0x60b08ed5, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb, 
	0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38, 0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21, 
	0x86d3d2d4, 0xf1d4e242, 0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661, 0xd06016f7, 0x2d02ef8d
]

# original algo for v1 imeis
def calculate_code_v1(imei, std):
    hash_str = md5_hash(imei + std)
    xor_result = xor_hash_bytes(hash_str)
    code = (xor_result[0] << 24) | (xor_result[1] << 16) | (xor_result[2] << 8) | xor_result[3]
    return str(code)

# use algo 1 for v2, may not work with some devices but works with mine!
def calculate_code_v2(imei, mode=0):
    imei_bytes = imei.encode('utf-8')
    
    crc = fake_crc32_huawei(imei_bytes) if mode == 201 else zlib.crc32(imei_bytes)
    
    crc = crc if crc >= 0 else crc + (1 << 32)
    
    nck = str(crc)[-8:].rjust(8, '9')
    
    if nck[0] == '0':
        nck = '9' + nck[1:]
    
    return nck

def fake_crc32_huawei(data):
    crc = 0xFFFFFFFF
    for byte in data:
        crc = CUSTOM_CRC32_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF

def algo_selector(imei, mode=1):
    x = 0
    for i in range(15):
        if mode == 201:
            x += ((ord(imei[i]) + i + 1) * ord(imei[i])) * (ord(imei[i]) + 313)
        else:
            x += (ord(imei[i]) + i + 1) * (i + 1)
    return x % 7

def calcv2(imei):
    algo_id = algo_selector(imei)
    return algo1(imei)
def log_usage(ip, imei, version):
    try:
        with open(LOG_FILE, 'r+') as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = {}

            if not isinstance(logs, dict):
                raise ValueError("Logs data is not a dictionary")

            if ip not in logs:
                logs[ip] = {"first_used": str(datetime.now()), "imei_logs": {}}

            logs[ip]["last_used"] = str(datetime.now())

            # Initialize or update the IMEI log entry
            if imei not in logs[ip]["imei_logs"]:
                logs[ip]["imei_logs"][imei] = {
                    "version": version,
                    "count": 1,
                    "last_requested": str(datetime.now())
                }
            else:
                logs[ip]["imei_logs"][imei]["count"] += 1
                logs[ip]["imei_logs"][imei]["last_requested"] = str(datetime.now())

            file.seek(0)
            json.dump(logs, file, indent=4)
            file.truncate()
    except Exception as e:
        print(f"An error occurred while logging usage: {e}")


# imei validation
def is_valid_imei(imei, version):
    if len(imei) != 15 or not imei.isdigit():
        return False

    if version == 2 and not imei.startswith("35"):
        return False

    sum = 0
    mul = 2
    for i in range(14):
        digit = int(imei[13-i])
        product = digit * mul
        sum += product // 10 + product % 10 
        mul = 1 if mul == 2 else 2 

    check_digit = (10 - (sum % 10)) % 10
    return check_digit == int(imei[-1])

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

def calculate_flash_code(imei, std):
    hash_str = md5_hash(imei + std)
    xor_result = xor_hash_bytes(hash_str)
    flash_code = (xor_result[0] << 24) | (xor_result[1] << 16) | (xor_result[2] << 8) | xor_result[3]
    return str(flash_code)  # Convert the flash code to a string before returning


# v1 unlock code api
@app.route('/api/v1/ucode', methods=['POST'])
def get_v1_unlock_code():
    data = request.get_json()
    imei = data.get('imei')
    
    if not is_valid_imei(imei, version=1):
        return jsonify({"error": "Invalid IMEI"}), 400
    
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    
    unlock_code = calculate_code_v1(imei, STD1_V1)
    return jsonify({"unlock_code": unlock_code})

# v2 unlock code api
@app.route('/api/v2/ucode', methods=['POST'])
def get_v2_unlock_code():
    data = request.get_json()
    imei = data.get('imei')
    
    if not is_valid_imei(imei, version=2):
        return jsonify({"error": "Invalid IMEI"}), 400
    
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    
    unlock_code = calculate_code_v2(imei)
    return jsonify({"unlock_code": unlock_code})

# flash code api
@app.route('/api/v2/fcode', methods=['POST'])
def get_v2_flash_code():
    data = request.get_json()
    imei = data.get('imei')
    
    if not is_valid_imei(imei, version=2):
        return jsonify({"error": "Invalid IMEI"}), 400
    
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    
    flash_code = calculate_code_v1(imei, STD2_V1)
    return jsonify({"flash_code": flash_code})

# all codes api v2
@app.route('/api/v2/all', methods=['POST'])
def get_all_codes_v2():
    data = request.get_json()
    imei = data.get('imei')

    if not is_valid_imei(imei, version=2):
        return jsonify({"error": "Invalid IMEI"}), 400

    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)
    
    unlock_code = calculate_code_v2(imei)
    
    flash_code = calculate_flash_code(imei, STD2_V1)
    
    flash_code_str = str(flash_code)
    
    return jsonify({
        "unlock_code": unlock_code,
        "flash_code": flash_code_str,
        "version": "2"
    })

# all codes api v1
@app.route('/api/v1/all', methods=['POST'])
def get_all_codes_v1():
    data = request.get_json()
    imei = data.get('imei')

    if not is_valid_imei(imei, version=1):
        return jsonify({"error": "Invalid IMEI"}), 400

    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    log_usage(ip, imei)

    unlock_code = calculate_code_v1(imei, STD1_V1)
    
    flash_code = calculate_flash_code(imei, STD2_V1)
    
    flash_code_str = str(flash_code)
    
    return jsonify({
        "unlock_code": unlock_code,
        "flash_code": flash_code_str,
        "version": "1"
    })


if __name__ == '__main__':
    app.run(debug=False)
