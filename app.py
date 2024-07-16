from flask import Flask, request, send_file, render_template, redirect, url_for
import os
from PyPDF2 import PdfReader
from gtts import gTTS
import tempfile
import threading

app = Flask(__name__)

def pdf_to_text(pdf_file):
    text = ""
    with open(pdf_file, 'rb') as f:
        reader = PdfReader(f)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def text_to_audio(text, output_file):
    tts = gTTS(text)
    tts.save(output_file)

def process_file(file_path, audio_path):
    text = pdf_to_text(file_path)
    text_to_audio(text, audio_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and file.filename.endswith('.pdf'):
        temp_pdf = tempfile.NamedTemporaryFile(delete=False)
        temp_pdf.write(file.read())
        temp_pdf.close()

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        threading.Thread(target=process_file, args=(temp_pdf.name, temp_audio.name)).start()

        return redirect(url_for('download_file', path=temp_audio.name))

    return "Invalid file type"

@app.route('/download/<path:path>', methods=['GET'])
def download_file(path):
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name='output_audio.mp3')
    else:
        return "File processing, please wait and try again later."

if __name__ == '__main__':
    app.run(debug=True)
