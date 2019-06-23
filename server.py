from aiohttp import web
import socketio
import handlers

sio = socketio.AsyncServer(async_mode='aiohttp')

app = web.Application()

sio.attach(app)

sio.register_namespace(handlers.Game('/game'))

if __name__ == '__main__':
    web.run_app(app, port = 8000)