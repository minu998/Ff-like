from flask import Flask, request, jsonify
import asyncio
import httpx
import base64
import binascii
import json
import logging
import warnings
import requests
import time
import aiohttp  # Fixed import
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson, ParseDict
from google.protobuf.message import DecodeError
from urllib3.exceptions import InsecureRequestWarning

# Protobuf imports
import like_pb2
import like_count_pb2
import uid_generator_pb2
try:
    from proto import FreeFire_pb2
except ImportError:
    import FreeFire_pb2

warnings.simplefilter('ignore', InsecureRequestWarning)

app = Flask(__name__)
app.logger.setLevel(logging.CRITICAL)

# Fast JWT Constants
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASEVERSION = "OB52"

# Pad data function
def pad_data(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt_fast(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.encrypt(pad_data(plaintext))

async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = f"{account}&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
        resp = await client.post(url, data=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("access_token", "0"), data.get("open_id", "0")

async def create_jwt_fast(uid: str, password: str):
    try:
        account = f"uid={uid}&password={password}"
        token_val, open_id = await get_access_token(account)
        body = {
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": token_val,
            "orign_platform_type": "4"
        }
        login_req = FreeFire_pb2.LoginReq()
        ParseDict(body, login_req)
        proto_bytes = login_req.SerializeToString()

        payload = aes_cbc_encrypt_fast(MAIN_KEY, MAIN_IV, proto_bytes)  
        url = "https://loginbp.ggblueshark.com/MajorLogin"  
        headers = {  
            'User-Agent': USERAGENT,  
            'Connection': "Keep-Alive",  
            'Accept-Encoding': "gzip",  
            'Content-Type': "application/octet-stream",  
            'Expect': "100-continue",  
            'X-Unity-Version': "2022.3.47f1",  
            'X-GA': "v1 1",  
            'ReleaseVersion': RELEASEVERSION  
        }  
        async with httpx.AsyncClient(timeout=20.0, verify=False) as client:  
            resp = await client.post(url, data=payload, headers=headers)  
            resp.raise_for_status()  
            res_msg = FreeFire_pb2.LoginRes.FromString(resp.content)  
            return res_msg.token  
    except Exception as e:  
        app.logger.error(f"JWT Generation failed for {uid}: {e}")  
        return None

# Modified token loader with fallback tokens
def load_tokens(server_name):
    """
    Load tokens from region-specific account files or use fallback
    """
    try:
        # For Vercel deployment, use fallback tokens
        # You should replace these with your actual tokens
        fallback_tokens = [
            {"token": "YOUR_FALLBACK_TOKEN_1"},
            {"token": "YOUR_FALLBACK_TOKEN_2"}
        ]
        
        # Try to load from file (for local development)
        account_file = f"accounts_{server_name.lower()}.json"
        try:
            with open(account_file, "r") as f:
                accounts = json.load(f)

            async def batch_generate():  
                tasks = []  
                for acc in accounts:  
                    tasks.append(create_jwt_fast(str(acc['uid']), str(acc['password'])))  
                return await asyncio.gather(*tasks)  

            jwt_list = asyncio.run(batch_generate())  
            tokens = [{"token": tk} for tk in jwt_list if tk]  
            if tokens:
                return tokens
        except FileNotFoundError:
            app.logger.warning(f"Account file {account_file} not found, using fallback tokens")
        
        return fallback_tokens
    except Exception as e:  
        app.logger.error(f"Token load failed for {server_name}: {e}")   
        return None

def encrypt_message(plaintext):
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return binascii.hexlify(encrypted_message).decode('utf-8')
    except Exception as e:
        app.logger.error(f"Encryption failed. Error: {e}")
        return None

def create_protobuf_message(user_id, region):
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Protobuf creation (like) failed. Error: {e}")
        return None

async def send_request(encrypted_uid, token, url):
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB52"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers) as response:
                if response.status != 200:
                    return response.status
                return await response.text()
    except Exception as e:
        app.logger.error(f"Send request failed: {e}")
        return None

async def send_multiple_requests(uid, server_name, url):
    try:
        region = server_name
        protobuf_message = create_protobuf_message(uid, region)
        if protobuf_message is None: return None
        encrypted_uid = encrypt_message(protobuf_message)
        if encrypted_uid is None: return None
        
        tokens = load_tokens(server_name)
        if tokens is None or len(tokens) == 0: 
            return None
        
        tasks = []
        # Limit concurrent requests for Vercel
        max_requests = min(20, len(tokens))  # Reduced for serverless
        for i in range(max_requests):
            token = tokens[i % len(tokens)]["token"]
            tasks.append(send_request(encrypted_uid, token, url))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    except Exception as e:
        app.logger.error(f"Send multiple requests failed: {e}")
        return None

def create_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        return message.SerializeToString()
    except Exception as e:
        app.logger.error(f"Create protobuf failed: {e}")
        return None

def enc(uid):
    protobuf_data = create_protobuf(uid)
    if protobuf_data is None: return None
    return encrypt_message(protobuf_data)

def make_request(encrypt, server_name, token):
    try:
        if server_name == "IND":
            url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        else:
            url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
            
        edata = bytes.fromhex(encrypt)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB52"
        }
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=10) 
        hex_data = response.content.hex()
        binary = bytes.fromhex(hex_data)
        decode = decode_protobuf(binary)
        return decode
    except Exception as e:
        app.logger.error(f"Make request failed: {e}")
        return None

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except Exception as e:
        app.logger.error(f"Decode protobuf failed: {e}")
        return None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "FreeFire Like API",
        "endpoints": {
            "/like": "GET request with uid and server_name parameters"
        }
    })

@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400

    try:
        tokens = load_tokens(server_name)
        if tokens is None or len(tokens) == 0:
            return jsonify({"error": "Failed to load tokens."}), 500
        
        token = tokens[0]['token']
        encrypted_uid = enc(uid)
        if encrypted_uid is None:
            return jsonify({"error": "Encryption failed."}), 500

        before = make_request(encrypted_uid, server_name, token)
        if before is None:
            return jsonify({"error": "Failed initial info."}), 500
        
        data_before = json.loads(MessageToJson(before))
        before_like = int(data_before.get('AccountInfo', {}).get('Likes', 0))

        if server_name == "IND":
            url = "https://client.ind.freefiremobile.com/LikeProfile"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/LikeProfile"
        else:
            url = "https://clientbp.ggblueshark.com/LikeProfile"

        # Run async tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_multiple_requests(uid, server_name, url))
        loop.close()

        after = make_request(encrypted_uid, server_name, token)
        if after is None:
            return jsonify({"error": "Failed after info."}), 500
        
        data_after = json.loads(MessageToJson(after))
        after_like = int(data_after.get('AccountInfo', {}).get('Likes', 0))
        player_uid = int(data_after.get('AccountInfo', {}).get('UID', 0))
        player_name = str(data_after.get('AccountInfo', {}).get('PlayerNickname', ''))
        
        like_given = after_like - before_like
        result = {
            "LikesGivenByAPI": like_given,
            "LikesafterCommand": after_like,
            "LikesbeforeCommand": before_like,
            "PlayerNickname": player_name,
            "UID": player_uid,
            "status": 1 if like_given != 0 else 2
        }
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in handle_requests: {str(e)}")
        return jsonify({"error": str(e)}), 500

# For Vercel serverless
app.debug = False

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
