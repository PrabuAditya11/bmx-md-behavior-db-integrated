from flask import Blueprint, request, jsonify, current_app
from services.map_processor import MapProcessor
import os

api_bp = Blueprint('api', __name__)
map_processor = MapProcessor()

@api_bp.route('/upload', methods=['POST'])
def upload_csv():
    try:
        # Debug logging
        print("Files in request:", request.files)
        print("Form data:", request.form)
        
        if 'csv_file' not in request.files:
            print("csv_file not found in request.files")
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['csv_file']
        print("Received file:", file.filename)
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'error': 'Please upload a CSV file'})
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file temporarily
        temp_path = os.path.join(upload_dir, file.filename)
        file.save(temp_path)
        print(f"File saved to: {temp_path}")
        
        # Process the saved file
        result = map_processor.process_file(temp_path)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not result.get('success'):
            print("Processing failed:", result.get('error'))
            return jsonify(result)
            
        return jsonify({'success': True, 'message': 'File processed successfully'})
        
    except Exception as e:
        print("Error processing upload:", str(e))
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/data', methods=['GET'])
def get_map_data():
    try:
        return jsonify(map_processor.get_processed_data())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/clear', methods=['POST'])
def clear_data():
    try:
        # Clear all data including clusters from the map processor
        map_processor.clear_data()
        
        # Clear any saved data files
        data_dir = os.path.join(current_app.root_path, 'static', 'data')
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                file_path = os.path.join(data_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': 'All data and clusters cleared'
        })
    except Exception as e:
        print("Error clearing data:", str(e))
        return jsonify({
            'success': False,
            'error': f'Failed to clear data: {str(e)}'
        })