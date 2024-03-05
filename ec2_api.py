# ec2_api.py

from flask import Flask, request, jsonify
from test import test
import util
import cv2
import numpy as np
import io

app = Flask(__name__)

# Mock database
user_db = set()

@app.route('/face_recognition', methods=['POST'])
def face_recognition():
    image = request.files['image'].read()
    image_array = np.frombuffer(image, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    label = test(frame, model_dir='./resources/anti_spoof_models', device_id=0)

    if label == 1:
        name = util.recognize(frame, 'path_to_db_dir')
        return jsonify({'status': 'success', 'message': f'Welcome back, {name}!', 'name': name})
    else:
        return jsonify({'status': 'error', 'message': 'Authentication failed!'})

@app.route('/logout', methods=['POST'])
def logout():
    image = request.files['image'].read()
    image_array = np.frombuffer(image, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    label = test(frame, model_dir='./resources/anti_spoof_models', device_id=0)

    if label == 1:
        name = util.recognize(frame, 'path_to_db_dir')
        if name not in ['unknown_person', 'no_persons_found']:
            user_db.remove(name)  # Simulate removing user from active session
            return jsonify({'status': 'success', 'message': f'Goodbye, {name}!'})
        else:
            return jsonify({'status': 'error', 'message': 'Unknown user!'})
    else:
        return jsonify({'status': 'error', 'message': 'Authentication failed!'})

@app.route('/register', methods=['POST'])
def register():
    image = request.files['image'].read()
    image_array = np.frombuffer(image, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Mock user registration logic
    name = util.recognize(frame, './db')
    if name not in ['unknown_person', 'no_persons_found']:
        user_db.add(name)  # Simulate adding user to the active session
        return jsonify({'status': 'success', 'message': f'User {name} registered successfully!'})
    else:
        return jsonify({'status': 'error', 'message': 'Registration failed!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
