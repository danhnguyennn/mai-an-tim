from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer
import threading

print("Api Running ...")
app = Flask(__name__)
data_lock = threading.Lock()

@app.route('/api/data', methods=['GET'])
def lay_du_lieu():
    with data_lock:
        with open('data\\mail\\gmail.txt', 'r') as file:
            lines = file.readlines()
            data_storage = {i: line.strip() for i, line in enumerate(lines)}

        du_lieu = {}
        for key in list(data_storage.keys())[:1]:
            du_lieu['email'] = data_storage.pop(key)

        with open('data\\mail\\gmail.txt', 'w') as file:
            for key, value in data_storage.items():
                file.write(f'{value}\n')

    return jsonify(du_lieu)

@app.route('/api/data', methods=['POST'])
def them_du_lieu():
    with data_lock:
        content = request.get_json()
        if 'account' in content:
            with open('data\\mail\\gmail.txt', 'a') as file:
                file.write(f"{content['account']}\n")
                
            return jsonify({"message": "Account added successfully"}), 201
        else:
            return jsonify({"error": "Invalid requests"}), 400

@app.route('/api/getKeyWwproxy', methods=['GET'])
def get_api_key_proxy():
    with data_lock:
        with open('data\\proxy\\proxy_log.txt', 'r') as file:
            lines = file.readlines()
            data_key = {i: line.strip() for i, line in enumerate(lines)}

        du_lieu = {}
        for key in list(data_key.keys())[:1]:
            du_lieu['api_key'] = data_key.pop(key)

        with open('data\\proxy\\proxy_log.txt', 'w') as file:
            for key, value in data_key.items():
                file.write(f'{value}\n')

    return jsonify(du_lieu)

@app.route('/api/sendKeyWwproxy', methods=['POST'])
def them_api_key_proxy():
    with data_lock:
        content = request.get_json()
        if 'ApiKey' in content:
            with open('data\\proxy\\proxy_log.txt', 'a') as file:
                file.write(f"{content['ApiKey']}\n")
                
            return jsonify({"message": "ApiKey added successfully"}), 201
        else:
            return jsonify({"error": "Invalid requests"}), 400
        
if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
