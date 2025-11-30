import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'banana_nano_secret_key'

# Configuration for Vercel (Read-only file system handling)
if os.environ.get('VERCEL'):
    app.instance_path = '/tmp'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/banana_prompts.db'
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banana_prompts.db'
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Model
class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Admin Credentials
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin@1998"

@app.route('/')
def home():
    prompts = Prompt.query.all()
    return render_template('index.html', prompts=prompts)

@app.route('/login', methods=['GET', 'POST'])
def login():
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
        return redirect(url_for('login'))
    
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_prompt = Prompt(image_filename=filename, prompt_text=prompt_text)
            db.session.add(new_prompt)
            db.session.commit()
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
