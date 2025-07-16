from flask import Flask, render_template
from routes.api import api_bp
import os
import shutil
import atexit

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 16MB max file size
    app.register_blueprint(api_bp, url_prefix='/api')
   
    CACHE_FOLDER = os.path.join(app.root_path, 'static', 'cache')

    # Cleanup function to delete cache folder
    def clear_cache_on_exit():
        if os.path.exists(CACHE_FOLDER):
            shutil.rmtree(CACHE_FOLDER)
            print(f"[Shutdown] Deleted cache folder: {CACHE_FOLDER}")

    # Register the function to run on server shutdown
    atexit.register(clear_cache_on_exit)
        
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    CACHE_FOLDER = os.path.join(app.root_path, 'static', 'cache')
    os.makedirs(CACHE_FOLDER, exist_ok=True) 

    app.run(host='0.0.0.0', port=5000, debug=True)