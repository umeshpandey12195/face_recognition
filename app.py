from flask import Flask, jsonify, request
from main import App, test

app_instance = App()

app = Flask(__name__)

# Add API endpoint for face recognition
@app.route('/recognize', methods=['POST'])
def api_recognize():
    # Get the image data from the request
    image_data = request.get_data()

    # Perform face recognition using the test function from main.py
    label = test(image_data, model_dir='/path/on/ec2/resources/anti_spoof_models', device_id=0)

    # Return the result as JSON
    return jsonify({'label': label})

if __name__ == '__main__':
    app_instance.start()
    app.run(host='0.0.0.0', port=80)