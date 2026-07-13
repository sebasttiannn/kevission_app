from app import create_app

app = create_app()

if __name__ == '__main__':
    # El host='0.0.0.0' permite que otros dispositivos en tu red (como tu celular) se conecten
    app.run(debug=True, host='0.0.0.0')