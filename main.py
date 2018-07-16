import json
import base64
import os
from cryptography import fernet
from collections import defaultdict
from aiohttp import web, WSMsgType
from util import log, redirect, login_required
from aiohttp_session import session_middleware, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from db import User


async def request_user_middleware(app, handler):
    async def middleware(request):
        request.session = await get_session(request)
        request.user = None
        user_id = request.session.get('user')
        if user_id is not None:
            request.user = await request.app.objects.get(User, id=user_id)
        return await handler(request)
    return middleware


@login_required
async def index(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.FileResponse('./index.html')


async def login(request):
    return web.FileResponse('./login.html')


async def login_api(request):
    data = await request.post()
    username = data.get("username")
    password = data.get("password")
    log(username, password)
    result = {
        "status": "success"
    }
    return web.json_response(result)


class chatroom(web.View):
    """
    chat room web socket
    """
    async def get(self):
        self.room = self.request.match_info['room'].lower()
        # self.room = await get_object_or_404(self.request, Room, name=self.request.match_info['room'].lower())
        user = self.request.user
        if not user:
            return web.Response(status=400, content_type='application/json')

        app = self.request.app

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        app.connections[self.room].add(ws)
        log(app.connections)
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    app.connections[self.room].remove(ws)
                    await ws.close()
                else:
                    message = json.loads(msg.data).get("message", "")
                    await self.brocast(message, self.room)

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

    async def brocast(self, message: str, room: str)->None:
        for ws in self.request.app.connections[room]:
            await ws.send_json({"message": message})


async def create_app():
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    # use encrypt cookies as session
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    middlewares = [session_middleware(
        EncryptedCookieStorage(secret_key)), request_user_middleware]
    app = web.Application(middlewares=middlewares)

    # add router
    app.add_routes([web.get('/', index)])
    app.add_routes([web.get('/login/', login)])

    app.router.add_route('GET', '/', index, name='index')
    app.router.add_route('GET', '/login', login, name='login')
    app.router.add_route('POST', '/login_api', login_api, name='login_api')
    app.router.add_route('GET', '/ws/chat/{room}/', chatroom, name='chatroom')
    app.router.add_static('/static/',
                          path=PROJECT_ROOT + '/static',
                          name='static')

    # init connections store
    app.connections = defaultdict(set)

    return app


def main():
    app = create_app()
    # app = web.Application()
    web.run_app(app, port=8000)


if __name__ == '__main__':
    main()
