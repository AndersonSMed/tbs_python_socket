import socketio
import asyncio
import json
from random import randint

class Game(socketio.AsyncNamespace):
    
    _players = list()
    _max_players = 2
    _dead_players = 0
    _player_turn = None
    _stamina_increase_by_pass = 20
    _actions_list = [
        {
            'id': 1,
            'name': 'Empurrão',
            'cost': 20,
            'damage': 10
        },
        {
            'id': 2,
            'name': 'Soco',
            'cost': 30,
            'damage': 15
        },
        {
            'id': 3,
            'name': 'Chute',
            'cost': 40,
            'damage': 20
        },
        {
            'id': 4,
            'name': 'Cabeçada',
            'cost': 60,
            'damage': 30
        }
    ]

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
                'alive': True
            })

        new_message = {
            'player': 'Servidor',
            'message': 'Um novo companheiro se junta ao lobby, deem boas vindas ao ' + str(nickname)
        }
        
        await self.emit('new_message', data = json.dumps(new_message))

        await self.emit('info', data = 'Seja bem vindo, ' + str(nickname) + ', esperamos que você se divirta.', room = sid)

        await self.emit('players', data = str(len(self._players)) + '/' + str(self._max_players))

        await self.emit('send_info', json.dumps(self._players))

        if len(self._players) == self._max_players:

            await self.emit('start_game', data = '')

            self._player_turn = randint(0, len(self._players) - 1)

            player = self._players[self._player_turn]

            await self.emit('info', data = 'É a sua vez de jogar, ' + player['nickname'] + '.', room = player['sid'])

            await self.emit('set_turn', data = True, room = player['sid'])

            await self.emit('set_turn', data = False, skip_sid = player['sid'])

            await self.emit('set_actions', data = json.dumps(self._actions_list))

            await self.emit('log', data = 'Quem joga nessa rodada é ' + player['nickname'] + '.')

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

        await self.emit('players', data = str(len(self._players)) + '/' + str(self._max_players))

        await self.emit('send_info', json.dumps(self._players))
    
    async def on_passar_vez(self, sid):

        for player in self._players:

            if str(sid) == player['sid']:

                await self.emit('log', data = player['nickname'] + ' passou a vez. +' + str(self._stamina_increase_by_pass) + ' pts de stamina')

                player['stamina'] += self._stamina_increase_by_pass

                if player['stamina'] > 100:

                    player['stamina'] = 100

                self._player_turn = (self._player_turn + 1) % len(self._players)

                while not self._players[self._player_turn]['alive']:

                    self._player_turn = (self._player_turn + 1) % len(self._players)

                break
        
        player = self._players[self._player_turn]

        player['stamina'] += self._stamina_increase_by_pass

        if player['stamina'] > 100:

            player['stamina'] = 100

        await self.emit('send_info', json.dumps(self._players))

        await self.emit('info', data = 'É a sua vez de jogar, ' + player['nickname'] + '.', room = player['sid'])

        await self.emit('set_turn', data = True, room = player['sid'])

        await self.emit('set_turn', data = False, skip_sid = player['sid'])

        await self.emit('log', data = 'Quem joga nessa rodada é ' + player['nickname'] + '.')

    async def on_attack(self, sid, sid_target, id):
        
        player = None
        target_player = None
        action = None

        for pl in self._players:

            if str(sid) == pl['sid']:

                player = pl
            
            elif str(sid_target) == pl['sid']:

                target_player = pl

        for act in self._actions_list:

            if str(act['id']) == str(id):

                action = act

        player['stamina'] -= action['cost']

        target_player['vida'] -= action['damage']
        
        if target_player['vida'] <= 0:

            target_player['vida'] = 0

            target_player['alive'] = False

        self._player_turn = (self._player_turn + 1) % len(self._players)

        while not self._players[self._player_turn]['alive']:

            self._player_turn = (self._player_turn + 1) % len(self._players)
        
        await self.emit('log', data = player['nickname'] + ' atacou ' + target_player['nickname'] + ' com um(a) ' + action['name'])

        if not target_player['alive']:

            await self.emit('info', data = 'Você morreu, ' + target_player['nickname'] + '.', room = target_player['sid'])

            await self.emit('log', data = target_player['nickname'] + ' morreu.')

            self._dead_players += 1

        if self._dead_players == len(self._players) - 1:

            await self.emit('log', data = player['nickname'] + ' ganhou a partida.')
        
            await self.emit('info', data = 'Parabéns, ' + player['nickname'] + ' você ganhou a partida.', room = player['sid'])

            await self.emit('send_info', json.dumps(self._players))

            return

        player = self._players[self._player_turn]

        await self.emit('log', data = 'Quem joga nessa rodada é ' + player['nickname'] + '.')
        
        await self.emit('info', data = 'É a sua vez de jogar, ' + player['nickname'] + '.', room = player['sid'])

        await self.emit('set_turn', data = True, room = player['sid'])

        await self.emit('set_turn', data = False, skip_sid = player['sid'])

        await self.emit('send_info', json.dumps(self._players))

