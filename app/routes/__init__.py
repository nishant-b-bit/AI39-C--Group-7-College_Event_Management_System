from app.routes.auth_routes import AuthRoutes


def create_auth_blueprint():
    return AuthRoutes().register()
