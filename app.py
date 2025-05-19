import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from utils.file_utils import get_all_files_with_metadata
from utils.auth import User
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['MAX_CONTENT_LENGTH']=16*1024*1024 #16MB max file size
app.secret_key = 'supersecretkey'


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username=request.form.get('username')
		password=request.form.get('password')
		user=User.validate(username=username,password=password)
		if user:
			login_user(user)
			return redirect(url_for('index'))
		flash('Invalid creds, try again.')
	return render_template('login.html')

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
	print(files)
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


if __name__ == '__main__':
	app.run(debug=True)