# Python Maps App

## Overview
The Python Maps App is a web application that allows users to visualize geographical data on a map. It processes CSV files containing coordinates and displays them on an interactive map using Flask for the backend and Leaflet for the frontend.

## Project Structure
```
python-maps-app
├── src
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── map.js
│   ├── templates
│   │   └── index.html
│   ├── services
│   │   ├── map_processor.py
│   │   └── data_processor.py
│   ├── models
│   │   └── coordinate.py
│   ├── routes
│   │   └── api.py
│   └── app.py
├── tests
│   └── test_map_processor.py
├── requirements.txt
└── README.md
```

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd python-maps-app
   ```

2. **Install dependencies:**
   Make sure you have Python 3.x installed. Then, create a virtual environment and install the required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run the application:**
   Start the Flask server:
   ```bash
   python src/app.py
   ```

4. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000` to view the application.

## Usage
- Upload a CSV file containing coordinates to visualize them on the map.
- Use the clear data button to remove all displayed data from the map.

## Testing
To run the tests for the map processing logic, execute:
```bash
pytest tests/test_map_processor.py
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.