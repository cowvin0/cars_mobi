import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from dash_app import app as car_dash

app = FastAPI()

app.mount('/car_dash', WSGIMiddleware(car_dash.server))

@app.get('/')
def index():
    return 'Hello'


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.0')