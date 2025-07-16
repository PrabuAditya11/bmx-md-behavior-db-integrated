import pandas as pd
import os
from utils.db import get_db_connection
import hashlib
import orjson

class MapProcessor:
    def __init__(self):
        self.data_file = 'static/data/processed_data.json'
        self.processed_data = None
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']

    def clear_data(self):
        self.processed_data = None
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def load_from_database(self, start_date, end_date, area_id=None, account_id=None):
        try:
            key_string = f"{start_date}-{end_date}-{area_id}-{account_id}"
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            cache_file = os.path.join('static', 'cache', f"{key_hash}.json")

            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    self.processed_data = orjson.loads(f.read())
                    return self.processed_data
                
            conn = get_db_connection()

            sql = """
            SELECT 
                a.longitude,
                a.latitude,
                c.store_name,
                e.account_name,
                c.store_id,
                b.full_name, 
                a.tanggal,
                d.area_name,
                d.area_id
            FROM 
                visit a 
            JOIN 
                surveyor b ON a.surveyor_id = b.surveyor_id 
            JOIN
                store c ON a.store_id = c.store_id
            JOIN
                store_area d ON c.area_id = d.area_id
            JOIN 
                store_account e ON c.account_id = e.account_id
            WHERE 
                c.is_dummy != 1
                AND a.longitude IS NOT NULL
                AND a.tanggal BETWEEN %s AND %s
                AND d.area_id != 1
                AND e.account_id != 1
                AND e.is_active = 1
            """

            params = [start_date, end_date]

            if area_id not in [None, '', 'null']:
                sql += " AND d.area_id = %s"
                params.append(area_id)
            if account_id not in [None, '', 'null']:
                sql += " AND e.account_id = %s"
                params.append(account_id)

            df = pd.read_sql(sql, conn, params=params)
            conn.close()

            # Reuse your processing logic from `process_file`
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df.dropna(subset=['longitude', 'latitude'], inplace=True)
            df['tanggal'] = pd.to_datetime(df['tanggal'])
            df['tanggal_str'] = df['tanggal'].dt.strftime('%Y-%m-%d')
            df['area_id'] = df['area_id'].astype(str)
            df['store_id'] = df['store_id'].astype(str)

            areas = df[['area_id', 'area_name']].drop_duplicates().to_dict('records')

            top_5 = df['store_id'].value_counts().head(5)
            top_5_map = []
            grouped = df.groupby('store_id').first()
            for i, (store_id, count) in enumerate(top_5.items()):
                row = grouped.loc[store_id]
                top_5_map.append({
                    'store_id': str(store_id),
                    'store_name': str(row['store_name']),
                    'visit_count': int(count),
                    'color': self.colors[i],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'area_name': str(row['area_name']),
                    'area_id': str(row['area_id']),
                })

            df['is_top_5'] = df['store_id'].isin(top_5.index)

            self.processed_data = {
                'success': True,
                'coordinates': df.drop(columns=['tanggal']).rename(columns={'tanggal_str': 'tanggal'}).to_dict('records'),
                'top_5_stores': top_5_map,
                'areas': areas,
                'stats': {
                    'total_points': len(df),
                    'total_stores': df['store_id'].nunique(),
                    'total_areas': len(areas),
                    'date_range': {
                        'start': df['tanggal_str'].min() if not df.empty else "N/A",
                        'end': df['tanggal_str'].max() if not df.empty else "N/A"
                    }
                }
            }

            with open(cache_file, 'wb') as f:
                f.write(orjson.dumps(self.processed_data))

            return self.processed_data

        except Exception as e:
            return {'success': False, 'error': str(e)}

    