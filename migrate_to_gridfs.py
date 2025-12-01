from app import app, fs
import os

UPLOAD_FOLDER = 'static/uploads'

with app.app_context():
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                # Check if file exists in GridFS
                if not fs.exists(filename=filename):
                    print(f"Uploading {filename} to GridFS...")
                    with open(file_path, 'rb') as f:
                        fs.put(f, filename=filename, content_type='image/png') # Assuming png for simplicity
                    print(f"Uploaded {filename}.")
                else:
                    print(f"{filename} already exists in GridFS.")
    else:
        print(f"Directory {UPLOAD_FOLDER} not found.")
