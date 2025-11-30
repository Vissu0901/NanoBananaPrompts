import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import gridfs
import certifi

app = Flask(__name__)
app.secret_key = 'banana_nano_secret_key'

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://viswanathvarikutivissu_db_user:OcPz6nWdSuA3LZVl@cluster0.r651jwd.mongodb.net/banana_prompts?appName=Cluster0"
mongo = PyMongo(app, tlsCAFile=certifi.where())
fs = gridfs.GridFS(mongo.db)

# Admin Credentials
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin@1998"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    grid_out = fs.find_one({'filename': filename})
    if grid_out:
        return send_file(grid_out, mimetype=grid_out.content_type or 'image/png', download_name=filename)
    return "Image not found", 404

@app.route('/')
def home():
    prompts = mongo.db.prompts.find()
    return render_template('index.html', prompts=prompts)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['image']
        prompt_text = request.form['prompt_text']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            print(f"DEBUG: Processing upload for {filename}")
            
            # Check if file already exists in GridFS to avoid duplicates or handle overwrites
            if fs.exists(filename=filename):
                 print(f"DEBUG: File {filename} exists, deleting old version")
                 old_file = fs.find_one({'filename': filename})
                 if old_file:
                     fs.delete(old_file._id)

            file_id = fs.put(file, filename=filename, content_type=file.content_type)
            print(f"DEBUG: File saved to GridFS with ID: {file_id}")
            
            mongo.db.prompts.insert_one({
                'image_filename': filename,
                'prompt_text': prompt_text
            })
            flash('Prompt uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
            
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
