from flask import Flask, request, jsonify, Response
import tempfile
import subprocess
import json
import os

app = Flask(__name__)
rhubarb_executable = "rhubarb"

@app.route('/process-voice', methods=['POST'])
def process_voice():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    input_bytes = file.read()

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio.write(input_bytes)
        temp_audio_path = temp_audio.name

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_json:
        temp_json_path = temp_json.name

    try:
        subprocess.run([
            rhubarb_executable,
            "-f", "json",
            "-o", temp_json_path,
            temp_audio_path,
            "-r", "phonetic"
        ], check=True)

        with open(temp_json_path, 'r', encoding='utf-8') as f:
            data = f.read()

        return Response(data, mimetype='application/json')

    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to process audio with Rhubarb', 'details': str(e)}), 500

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(temp_json_path):
            os.remove(temp_json_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
