import socketio
import asyncio
import json

class Game(socketio.AsyncNamespace):
    
    _players = list()

    async def on_enter(self, sid, nickname):
        playerFound = False
        for index in range(0, len(self._players)):
            
            if str(sid) == self._players[index]['sid']:
                self._players[index]['nickname'] = str(nickname)
                playerFound = True
                break

        if not playerFound:
            
            self._players.append({
                'nickname': str(nickname),
                'sid': str(sid),
                'vida': 100,
                'stamina': 100,
                'pronto': False
            })

        new_message = {
            'player': 'Servidor',
            'message': 'Um novo companheiro se junta ao lobby, deem boas vindas ao ' + str(nickname)
        }
        
        await self.emit('new_message', data = json.dumps(new_message))

        await self.emit('info', data = 'Seja bem vindo, ' + str(nickname) + ', esperamos que você se divirta.', room = sid)

        await self.emit('players', data = str(len(self._players)) + '/4')

        if len(self._players) == 1:

            await self.emit('send_info', json.dumps(self._players))

            await self.emit('start_game', data = '')

    async def on_send_message(self, sid, message):
        for player in self._players:
            if str(sid) == player['sid']:
                new_message = {
                    'player': player['nickname'],
                    'message': str(message)
                }
                await self.emit('new_message', json.dumps(new_message))
                break

    async def on_disconnect(self, sid):
        
        for index in range(0, len(self._players)):
            
            if str(sid) == self._players[index]['sid']:

                new_message = {
                    'player': 'Servidor',
                    'message': self._players[index]['nickname'] + ' saiu do jogo.'
                }

                await self.emit('new_message', data = json.dumps(new_message))

                self._players.pop(index)
                break

        await self.emit('players', data = str(len(self._players)) + '/4')
    