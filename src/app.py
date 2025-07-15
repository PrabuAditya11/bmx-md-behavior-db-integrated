from flask import Flask, render_template
from routes.api import api_bp
import os

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 16MB max file size
    app.register_blueprint(api_bp, url_prefix='/api')

    data_file_path = os.path.join(app.root_path, 'static', 'data', 'processed_data.json')
    if os.path.exists(data_file_path):
        os.remove(data_file_path)
        print("✅ Deleted processed_data.json on startup")
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)