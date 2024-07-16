from flask import Flask, request, send_file, render_template
import os
from PyPDF2 import PdfReader
from gtts import gTTS
import tempfile

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
        text = pdf_to_text(temp_pdf.name)
        text_to_audio(text, temp_audio.name)
        os.remove(temp_pdf.name)
        return send_file(temp_audio.name, as_attachment=True, download_name='output_audio.mp3')
    return "Invalid file type"

if __name__ == '__main__':
    app.run(debug=True)
