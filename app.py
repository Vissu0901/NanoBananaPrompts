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
mongo = PyMongo(app)
fs = gridfs.GridFS(mongo.db)

# Admin Credentials
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin@1998"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        grid_out = fs.find_one({'filename': filename})
        if grid_out:
            return send_file(grid_out, mimetype=grid_out.content_type or 'image/png', download_name=filename)
        return "Image not found", 404
    except Exception as e:
        return f"Error retrieving image: {str(e)}", 500

@app.route('/')
def home():
    try:
        # Test connection with a quick command
        # mongo.db.command('ping')
        prompts = mongo.db.prompts.find()
        return render_template('index.html', prompts=prompts)
    except Exception as e:
        return f"""
        <h1>Database Connection Error</h1>
        <p>Could not connect to MongoDB. Please ensure you have whitelisted the IP address in MongoDB Atlas.</p>
        <p><strong>Error Details:</strong> {str(e)}</p>
        <p><em>Go to MongoDB Atlas -> Network Access -> Add IP Address -> Allow Access from Anywhere (0.0.0.0/0)</em></p>
        """, 500

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
            
    prompts = list(mongo.db.prompts.find())
    return render_template('dashboard.html', prompts=prompts)

@app.route('/delete/<prompt_id>')
def delete_prompt(prompt_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    from bson.objectid import ObjectId
    prompt = mongo.db.prompts.find_one({'_id': ObjectId(prompt_id)})
    
    if prompt:
        # Delete image from GridFS
        grid_out = fs.find_one({'filename': prompt['image_filename']})
        if grid_out:
            fs.delete(grid_out._id)
            
        # Delete prompt from DB
        mongo.db.prompts.delete_one({'_id': ObjectId(prompt_id)})
        flash('Prompt deleted successfully!', 'success')
    else:
        flash('Prompt not found.', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/edit/<prompt_id>', methods=['GET', 'POST'])
def edit_prompt(prompt_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
        
    from bson.objectid import ObjectId
    prompt = mongo.db.prompts.find_one({'_id': ObjectId(prompt_id)})
    
    if not prompt:
        flash('Prompt not found.', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        prompt_text = request.form['prompt_text']
        
        update_data = {'prompt_text': prompt_text}
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                
                # Delete old image
                grid_out = fs.find_one({'filename': prompt['image_filename']})
                if grid_out:
                    fs.delete(grid_out._id)
                
                # Save new image
                # Check if file already exists in GridFS
                if fs.exists(filename=filename):
                     old_file = fs.find_one({'filename': filename})
                     if old_file:
                         fs.delete(old_file._id)

                fs.put(file, filename=filename, content_type=file.content_type)
                update_data['image_filename'] = filename
        
        mongo.db.prompts.update_one({'_id': ObjectId(prompt_id)}, {'$set': update_data})
        flash('Prompt updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_prompt.html', prompt=prompt)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/sitemap.xml')
def sitemap():
    return send_file('static/sitemap.xml', mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True)
