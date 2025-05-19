import os
from datetime import datetime

def get_file_metadata(file_path):
	"""Get metadata for a specific file."""
	try:
		file_size = os.path.getsize(file_path)
		file_type = os.path.splitext(file_path)[1].lower()
		modified_time = os.path.getmtime(file_path)
		upload_date = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')	
		return {
			"size": file_size,
			"type": file_type,
			"modified": upload_date
		}
	except FileNotFoundError:
		return None

def get_all_files_with_metadata(upload_folder):
	"""Get metadata for all files in the uploads directory."""
	files = os.listdir(upload_folder)
	file_data = []

	for file_name in files:
		file_path=os.path.join(upload_folder, file_name)
		metadata=get_file_metadata(file_path=file_path)
		if metadata:
			file_data.append({"name": file_name, **metadata})		
	return file_data