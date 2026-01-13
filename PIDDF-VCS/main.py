import os
from api import app, settings
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_APP_HOST'),
        port=int(os.getenv('FLASK_APP_PORT')),
        debug=os.getenv('FLASK_APP_DEBUG'),
        threaded=True
    )

    with app.app_context():
        print("App context is created")
        # read all constants from settings
        for key, value in settings.__dict__.items():
            print(f'{key}: {value}')
            if key.isupper():
                app.config[key] = value

    print("App is running")