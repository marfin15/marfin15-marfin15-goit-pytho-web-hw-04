from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import threading
import socket
import json
from datetime import datetime

app = Flask(__name__, template_folder='.', static_folder='.')

# Ensure data.json file exists
if not os.path.exists('data.json'):
    with open('data.json', 'w') as f:
        json.dump({}, f)

# Routes for HTML pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message.html')
def message():
    return render_template('message.html')

# Route for static files
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# Route to handle form submission
@app.route('/message', methods=['POST'])
def handle_message():
    username = request.form['username']
    message = request.form['message']
    timestamp = datetime.now().isoformat()
    data = {
        timestamp: {
            "username": username,
            "message": message
        }
    }

    # Send data to Socket server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(json.dumps(data).encode(), ('localhost', 5000))

    return jsonify({"status": "Message sent"}), 200

# Error handling for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Socket server function
def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind(('localhost', 5000))
        while True:
            data, addr = server_sock.recvfrom(1024)
            data = json.loads(data.decode())
            with open('data.json', 'r+') as f:
                file_data = json.load(f)
                file_data.update(data)
                f.seek(0)
                json.dump(file_data, f, indent=4)

# Run HTTP and Socket servers in separate threads
if __name__ == "__main__":
    threading.Thread(target=socket_server, daemon=True).start()
    app.run(port=3000, debug=True)