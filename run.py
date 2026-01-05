from app import create_app

# This MUST be named 'app' for the flask command to find it automatically
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)