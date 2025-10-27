from flask import Flask, request, jsonify, send_file
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from datetime import datetime

app = Flask(__name__, static_folder='../public', static_url_path='')

# Temp folder in root directory
TEMP_DIR = os.path.join(os.path.dirname(__file__), '../temp')
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.json
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Empty text input'}), 400

    # Unique filename: output_YYYYMMDD_HHMMSS.mp4
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"output_{timestamp}.mp4"
    video_path = os.path.join(TEMP_DIR, video_filename)

    # Video properties
    width, height = 1080, 1920
    duration = 18
    bg_color = (30, 30, 30)  # dark grey
    text_color = (255, 255, 255)

    # Create image
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Font setup
    try:
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Poppins-Regular.ttf')
        font_size = 70
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Function for wrapping text using textbbox (modern Pillow)
    def wrap_text(text, font, max_width):
        words = text.split()
        lines, current = [], ""

        for word in words:
            test_line = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current = test_line
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return "\n".join(lines)

    # Dynamically adjust font size for long text
    wrapped_text = wrap_text(text, font, width * 0.9)
    while True:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center', spacing=10)
        text_height = bbox[3] - bbox[1]
        text_width = bbox[2] - bbox[0]

        if (text_height < height * 0.8) and (text_width < width * 0.9):
            break

        font_size -= 3
        if font_size < 20:
            break

        font = ImageFont.truetype(font_path, font_size)
        wrapped_text = wrap_text(text, font, width * 0.9)

    # Center the text
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center', spacing=10)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = (height - (bbox[3] - bbox[1])) // 2

    draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=text_color, align='center', spacing=10)

    # Convert to video (no audio)
    clip = ImageClip(np.array(img)).set_duration(duration)
    clip.write_videofile(video_path, fps=30, codec='libx264', audio=False, preset='medium')

    return jsonify({'videoUrl': '/download/' + video_filename})

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
