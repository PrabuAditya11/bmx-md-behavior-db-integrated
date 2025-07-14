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
            
            # Ensure numeric types for coordinates
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            
            # Remove rows with invalid coordinates
            df = df.dropna(subset=['longitude', 'latitude'])
            
            # Convert tanggal to datetime and get date range
            df['tanggal'] = pd.to_datetime(df['tanggal'])
            start_date = df['tanggal'].min().strftime('%Y-%m-%d')
            end_date = df['tanggal'].max().strftime('%Y-%m-%d')
            
            # Process areas - ensure area_id is string for consistency
            df['area_id'] = df['area_id'].astype(str)
            areas = df[['area_id', 'area_name']].drop_duplicates().to_dict('records')
            
            # Process top 5 stores
            top_5_stores = df['store_id'].value_counts().head(5)
            top_5_info = []
            
            for i, (store_id, visit_count) in enumerate(top_5_stores.items()):
                store_data = df[df['store_id'] == store_id].iloc[0]
                top_5_info.append({
                    'store_id': str(store_id),
                    'store_name': str(store_data['store_name']),
                    'visit_count': int(visit_count),
                    'color': self.colors[i],
                    'latitude': float(store_data['latitude']),
                    'longitude': float(store_data['longitude']),
                    'area_name': str(store_data['area_name']),
                    'area_id': str(store_data['area_id'])
                })
            
            # Convert to list of dictionaries with explicit type conversion
            coordinates = []
            for _, row in df.iterrows():
                coordinates.append({
                    'longitude': float(row['longitude']),
                    'latitude': float(row['latitude']),
                    'store_name': str(row['store_name']),
                    'store_id': str(row['store_id']),
                    'full_name': str(row['full_name']),
                    'tanggal': row['tanggal'].strftime('%Y-%m-%d'),
                    'area_name': str(row['area_name']),
                    'area_id': str(row['area_id']),
                    'is_top_5': row['store_id'] in top_5_stores.index
                })
            
            # Save processed data
            self.processed_data = {
                'success': True,
                'coordinates': coordinates,
                'top_5_stores': top_5_info,
                'areas': areas,
                'stats': {
                    'total_points': len(coordinates),
                    'total_stores': len(set(c['store_id'] for c in coordinates)),
                    'total_areas': len(areas),
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