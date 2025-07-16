import pandas as pd
import os
import orjson  # install with: pip install orjson

class MapProcessor:
    def __init__(self):
        self.data_file = 'static/data/processed_data.json'
        self.processed_data = None
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']

    def process_file(self, file):
        try:
            # Load only needed columns
            usecols = ['longitude', 'latitude', 'store_name', 'store_id',
                       'full_name', 'tanggal', 'area_name', 'area_id']
            df = pd.read_csv(file, usecols=usecols)

            # Coordinate cleanup
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df.dropna(subset=['longitude', 'latitude'], inplace=True)

            # Efficient types
            df['store_id'] = df['store_id'].astype('category')
            df['area_id'] = df['area_id'].astype('category')
            df['tanggal'] = pd.to_datetime(df['tanggal'])

            # Date range
            start_date = df['tanggal'].min().strftime('%Y-%m-%d')
            end_date = df['tanggal'].max().strftime('%Y-%m-%d')

            # Areas (keep both id & name)
            if 'area_name' not in df.columns:
                df['area_name'] = 'Unknown'
            else:
                df['area_name'] = df['area_name'].fillna('Unknown')

            # Remove duplicates and cast to string for safety
            df['area_id'] = df['area_id'].astype(str)
            df['area_name'] = df['area_name'].astype(str)

            areas = df[['area_id', 'area_name']].drop_duplicates().to_dict('records')

            # Top 5 store info
            top_5_counts = df['store_id'].value_counts().head(5)
            top_5_ids = top_5_counts.index.tolist()

            top_5_map = {}
            for i, store_id in enumerate(top_5_ids):
                store_data = df[df['store_id'] == store_id].iloc[0]
                top_5_map[store_id] = {
                    'store_id': str(store_id),
                    'store_name': str(store_data['store_name']),
                    'visit_count': int(top_5_counts[store_id]),
                    'color': self.colors[i],
                    'latitude': float(store_data['latitude']),
                    'longitude': float(store_data['longitude']),
                    'area_name': str(store_data['area_name']),
                    'area_id': str(store_data['area_id'])
                }

            # is_top_5 as a column
            df['is_top_5'] = df['store_id'].isin(top_5_ids)

            # Format tanggal as string
            df['tanggal'] = df['tanggal'].dt.strftime('%Y-%m-%d')

            # Make sure all values are strings for JSON compatibility
            df['store_id'] = df['store_id'].astype(str)
            df['area_id'] = df['area_id'].astype(str)

            coordinates = df.to_dict('records')

            self.processed_data = {
                'success': True,
                'coordinates': coordinates,
                'top_5_stores': list(top_5_map.values()),
                'areas': areas,
                'stats': {
                    'total_points': len(df),
                    'total_stores': df['store_id'].nunique(),
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
                with open(self.data_file, 'rb') as f:
                    self.processed_data = orjson.loads(f.read())
            else:
                return {'success': False, 'error': 'data nya belum ada'}
        return self.processed_data

    def clear_data(self):
        self.processed_data = None
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def _save_to_file(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'wb') as f:
            f.write(orjson.dumps(self.processed_data))
