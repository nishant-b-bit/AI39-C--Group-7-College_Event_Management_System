from app import create_app
from app.models import create_tables
from app.routes import create_auth_blueprint

app = create_app()
create_tables()

app.register_blueprint(create_auth_blueprint())

if __name__ == "__main__":
    app.run(debug=True)
