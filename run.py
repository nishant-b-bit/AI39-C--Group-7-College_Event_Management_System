from app import create_app

from app.routes.auth import home_bp

app=create_app()

app.register_blueprint(home_bp)

if __name__=="__main__":

    app.run(debug=True)
