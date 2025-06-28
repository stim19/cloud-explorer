import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from utils.file_utils import get_all_files_with_metadata
from utils.auth import User
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from extensions import db
from flask import abort

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdb.db'
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['MAX_CONTENT_LENGTH']=16*1024*1024 #16MB max file size
app.secret_key = 'supersecretkey'
db.init_app(app)
migrate=Migrate(app, db)


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@app.route('/dashboard')
@login_required
def dashboard():
	return f"Welcome, {current_user.username}!"

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username=request.form.get('username')
		password=request.form.get('password')
		user=User.query.filter_by(username=username).first()
		if user and user.check_password(password):
			login_user(user)
			return redirect(url_for('index'))
		flash('Invalid creds, try again.')
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username=request.form.get('username')
		password=request.form.get('password')
		user=User(username=username, role='user')
		user.password=password

def admin_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if current_user.role !='admin':
			flash('Admins only')
			return redirect(url_for('dashboard.html'))
		return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
	if current_user.role !='admin':
		abort(403)
	return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))
#Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

#Allowed file extensions
ALLOWED_EXTENSIONS =  {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf', 'docx'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
	if request.method == 'POST':
		file=request.files.get('file')
		if file and allowed_file(file.filename):
			filename= file.filename
			file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(file_path)
			flash('File uploaded successfully!', 'success')
			return redirect(url_for('index'))
		else:
			flash('Invalid file or no file selected.', 'error')
	files=get_all_files_with_metadata(upload_folder=app.config['UPLOAD_FOLDER'])
	return render_template('index.html', files=files, user=current_user)
	

@app.route('/uploads/<filename>')
def download_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
	file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
	if(os.path.exists(file_path)):
		os.remove(file_path)
		flash('File deleted successfully!', 'success')
	else:
		flash('File not found.', 'error')
	return redirect(url_for('index'))

@app.route('/search')
@login_required
def search():
	query = request.args.get('query', '').lower()
	files=get_all_files_with_metadata(app.config['UPLOAD_FOLDER'])
	#Filter files based on query 
	if query:
		filtered_files = [file for file in files if query in file['name'].lower()]
	else:
		filtered_files=[]
	return render_template('index.html', files=files, filtered_files=filtered_files, user=current_user)
	
if __name__ == '__main__':
	app.run(debug=True)