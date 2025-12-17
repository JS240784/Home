from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 업로드 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '파일을 선택해주세요'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '허용되지 않는 파일 형식입니다'}), 400
    
    filename = secure_filename(file.filename)
    # 같은 이름의 파일 방지
    import uuid
    filename = str(uuid.uuid4())[:8] + '_' + filename
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/uploads/{filename}'
    })

@app.route('/api/photos', methods=['GET'])
def get_photos():
    photos = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                photos.append({
                    'filename': filename,
                    'url': f'/uploads/{filename}'
                })
    return jsonify({'photos': photos})

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath) and allowed_file(filename):
        os.remove(filepath)
        return jsonify({'success': True})
    return jsonify({'error': '파일을 찾을 수 없습니다'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
