from app import create_app

app = create_app()

if __name__ == '__main__':
    # Pokreće aplikaciju u režimu za debagovanje
    app.run(debug=True)
