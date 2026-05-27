from app import create_app
from app.routes.auth_routes import AuthRoutes

app = create_app()

auth_route = AuthRoutes()
app.register_blueprint(auth_route.register())

if __name__ == "__main__":
    app.run(debug=True)