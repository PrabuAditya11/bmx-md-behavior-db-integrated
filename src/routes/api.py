from flask import Blueprint, request, jsonify, current_app
from services.map_processor import MapProcessor
from utils.db import get_db_connection
import os

api_bp = Blueprint('api', __name__)
map_processor = MapProcessor()

@api_bp.route('/data', methods=['GET'])
def get_filtered_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    area_id = request.args.get('area_id') or None
    account_id = request.args.get('account_id') or None

    result = map_processor.load_from_database(start_date, end_date, area_id, account_id)
    return jsonify(result)

@api_bp.route('/clear', methods=['POST'])
def clear_data():
    try:
        cache_dir = os.path.join(current_app.root_path, 'static', 'cache')
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

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

@api_bp.route('/filters', methods=['GET'])
def get_filters():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT area_id, area_name FROM store_area WHERE area_id != 1")
        areas = cursor.fetchall()

        cursor.execute("SELECT account_id, account_name FROM store_account WHERE account_id != 1 AND is_active = 1")
        accounts = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'areas': areas, 'accounts': accounts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})