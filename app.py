import binascii
import requests
from flask import Flask, jsonify, request
import threading
import time
import re
from datetime import datetime

app = Flask(__name__)
jwt_token = None
jwt_lock = threading.Lock()
cache = {}
cache_lock = threading.Lock()

def convert_timestamp(release_time):
    return datetime.utcfromtimestamp(release_time).strftime('%Y-%m-%d %H:%M:%S')

def extract_token_from_response(data, region):
    if region == "IND":
        if data.get('status') in ['success', 'live']:
            return data.get('token')
    elif region in ["BR", "US", "SAC", "NA"]:
        if isinstance(data, dict) and 'token' in data:
            return data['token']
    else: 
        if data.get('status') == 'success':
            return data.get('token')
    return None

def get_jwt_token_sync(region):
    global jwt_token
    endpoints = {
        "IND": "https://jwtgenerater.vercel.app/token?uid=3828066210&password=C41B0098956AE7B79F752FCA873C747060C71D3C17FBE4794F5EB9BD71D4DA95",
        "BR": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "US": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=&password=",
        "SAC": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=&password=",
        "NA": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "ME": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3763606630&password=7FF33285F290DDB97D9A31010DCAA10C2021A03F27C4188A2F6ABA418426527C",
        "SG": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3829602603&password=601849AE2D73FC68E34E84240DF09B814C270876365CEFBA454861A6B264199B",
        "CIS": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3804678376&password=CC026379A10A6ABAEEE7C48C6E0AEA3A5361603C9481165AD06E6E4689912596",
        "BD": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3533430236&password=A284E7DD367F808EB079EAF4DDE85AB4F977A249E510A3A168298FE44011BB93"
    }
    url = endpoints.get(region, endpoints["IND"])
    with jwt_lock:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = extract_token_from_response(data, region)
                if token:
                    jwt_token = token
                    print(f"JWT Token for {region} updated successfully: {token[:50]}...")
                    return jwt_token
                else:
                    print(f"Failed to extract token from response for {region}")
            else:
                print(f"Failed to get JWT token for {region}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request error for {region}: {e}")   
    return None

def ensure_jwt_token_sync(region):
    global jwt_token
    if not jwt_token:
        print(f"JWT token for {region} is missing. Attempting to fetch a new one...")
        return get_jwt_token_sync(region)
    return jwt_token

def jwt_token_updater(region):
    while True:
        get_jwt_token_sync(region)
        time.sleep(300)

def get_api_endpoint(region):
    endpoints = {
        "IND": "https://client.ind.freefiremobile.com/LoginGetSplash",
        "BR": "https://client.us.freefiremobile.com/LoginGetSplash",
        "US": "https://client.us.freefiremobile.com/LoginGetSplash",
        "SAC": "https://client.us.freefiremobile.com/LoginGetSplash",
        "NA": "https://client.us.freefiremobile.com/LoginGetSplash",
        "ME": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "CIS": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "SG": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "BD": "https://clientbp.ggblueshark.com/LoginGetSplash"
    }
    return endpoints.get(region, endpoints["IND"])

def apis(idd, region):
    global jwt_token    
    token = ensure_jwt_token_sync(region)
    if not token:
        raise Exception(f"Failed to get JWT token for region {region}")    
    endpoint = get_api_endpoint(region)    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB48',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    region_data = {
        "IND": "03f7f38095daae1bf887928b4f2c0eb4",
        "BR": "",
        "US": "",
        "SAC": "",
        "NA": "9223af2eab91b7a150d528f657731074",
        "BD": "9223af2eab91b7a150d528f657731074",
        "ME": "9223af2eab91b7a150d528f657731074",
        "CIS": "5b 27 f0 86 9e 37 f9 2b 6f 84 c3 a7 39 34 7d b1",
        "SG": "9223af2eab91b7a150d528f657731074"
    }
    
    data_hex = region_data.get(region, "")
    if not data_hex:
        raise Exception("Invalid region or missing data")
    
    try:
        data = bytes.fromhex(data_hex)
        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        return response.content.hex()
    except requests.exceptions.RequestException as e:
        print(f"API request to {endpoint} failed: {e}")
        raise

@app.route('/eventes', methods=['GET'])
def get_player_info():
    try:
        region = request.args.get('region', 'IND').upper()
        key = request.args.get('key')
        
        if not key:
            return jsonify({"error": "Missing key"}), 400
        
        cache_key = f"{region}_{key}"
        with cache_lock:
            cached = cache.get(cache_key)
            if cached and (datetime.now() - cached['timestamp']).seconds < 300:
                return jsonify(cached['data'])
        
        response_hex = apis(key, region)
        if not response_hex:
            return jsonify({"error": "Failed to get response from API"}), 500
            
        response_text = binascii.unhexlify(response_hex).decode('utf-8', errors='ignore')
        urls = re.findall(r'https?://[^\s]+\.png', response_text)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        results = []
        for url in urls:
            clean_url = url.strip()
            event_name = clean_url.split('/')[-1].replace('_880x520_BR_pt.png', '').replace('_', ' ')
            results.append({
                "title": event_name,
                "image_url": clean_url
            })
        
        response_data = {
            "status": "success",
            "events": results,
            "count": len(results),
            "date": current_date,
            "time": current_time
        }
        
        with cache_lock:
            cache[cache_key] = {
                'data': response_data,
                'timestamp': datetime.now()
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == "__main__":
    ensure_jwt_token_sync("IND")
    app.run(host="0.0.0.0", port=5552)