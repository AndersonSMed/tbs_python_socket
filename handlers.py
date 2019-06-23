import socketio
import asyncio

class Game(socketio.AsyncNamespace):
    
    _players = list()

    async def on_enter(self, sid, nickname):
        playerFound = False
        for index in range(0, len(self._players)):
            
            if str(sid) == self._players[index]['sid']:
                self._players[index] = {
                    'nickname': str(nickname),
                    'sid': str(sid)
                }
                playerFound = True
                break

        if not playerFound:
            
            self._players.append({
                'nickname': str(nickname),
                'sid': str(sid)
            })

        new_message = {
            'player': 'Servidor',
            'message': 'Um novo companheiro se junta ao lobby, deem boas vindas ao ' + str(nickname)
        }
        
        await self.emit('new_message', data = new_message)

        await self.emit('info', data = 'Seja bem vindo, ' + str(nickname) + ', esperamos que você se divirta', room = sid)

    async def on_send_message(self, sid, message):
        for player in self._players:
            if str(sid) == player['sid']:
                new_message = {
                    'player': player['nickname'],
                    'message': str(message)
                }
                await self.emit('new_message', new_message)
                break