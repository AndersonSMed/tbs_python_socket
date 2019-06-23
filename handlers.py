import socketio
import json

class Game(socketio.AsyncNamespace):
    
    _players = list()

    def on_enter(self, sid, nickname):
        self._players.append({
            'nickname': str(nickname),
            'sid': str(sid)
        })
        new_message = {
            'player': 'Servidor',
            'message': 'Um novo companheiro se junta ao lobby, deem boas vindas ao ' + str(nickname)
        }
        self.emit('new_message', data = json.dumps(new_message))

    def on_send_message(self, sid, message):
        for player in self._players:
            if str(sid) == player.sid:
                new_message = {
                    'player': player['nickname'],
                    'message': str(message)
                }
                self.emit('new_message', json.dumps(new_message))
                break