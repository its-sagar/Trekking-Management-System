"""Flask development server entry point."""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print('\n[API] TMA Backend running on http://localhost:5000\n')
    app.run(debug=True, port=5000, host='0.0.0.0')