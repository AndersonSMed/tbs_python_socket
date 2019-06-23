from aiohttp import web
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')

app = web.Application()

sio.attach(app)

if __name__ == '__main__':
    web.run_app(app, port = 8000)