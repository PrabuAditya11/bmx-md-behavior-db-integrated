import pandas as pd
import json
import os

class MapProcessor:
    def __init__(self):
        self.data_file = 'static/data/processed_data.json'
        self.processed_data = None
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']

    def process_file(self, file):
        try:
            # Read CSV with pandas
            df = pd.read_csv(file)
            required_columns = ['longitude', 'latitude', 'store_name', 'store_id', 'full_name', 'tanggal']
            
            # Validate columns
            if not all(col in df.columns for col in required_columns):
                return {'success': False, 'error': 'Missing required columns'}
            
            # Convert tanggal to datetime and get date range
            df['tanggal'] = pd.to_datetime(df['tanggal'])
            start_date = df['tanggal'].min().strftime('%Y-%m-%d')
            end_date = df['tanggal'].max().strftime('%Y-%m-%d')
            
            # Process top 5 stores
            top_5_stores = df['store_id'].value_counts().head(5)
            top_5_info = []
            
            for i, (store_id, visit_count) in enumerate(top_5_stores.items()):
                store_data = df[df['store_id'] == store_id].iloc[0]
                top_5_info.append({
                    'store_id': store_id,
                    'store_name': store_data['store_name'],
                    'visit_count': int(visit_count),
                    'color': self.colors[i]
                })
            
            # Convert to list of dictionaries with formatted dates
            coordinates = df.assign(
                tanggal=df['tanggal'].dt.strftime('%Y-%m-%d'),
                is_top_5=df['store_id'].isin(top_5_stores.index)
            ).to_dict('records')
            
            # Save processed data
            self.processed_data = {
                'success': True,
                'coordinates': coordinates,
                'top_5_stores': top_5_info,
                'stats': {
                    'total_points': len(coordinates),
                    'total_stores': len(set(c['store_id'] for c in coordinates)),
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
            }
            
            self._save_to_file()
            return {'success': True}
            
        except Exception as e:
            print("Error processing file:", str(e))
            return {'success': False, 'error': str(e)}

    def get_processed_data(self):
        if not self.processed_data:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.processed_data = json.load(f)
            else:
                return {'success': False, 'error': 'No data available'}
        return self.processed_data

    def clear_data(self):
        self.processed_data = None
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def _save_to_file(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.processed_data, f)