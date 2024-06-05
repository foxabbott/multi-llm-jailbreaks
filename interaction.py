
from math import ceil
from utils import get_players

class Interaction(object):
    def __init__(self, PlayerA, PlayerB, evaluators = None, max_turns = 2):

        self.PlayerA = PlayerA
        self.PlayerB = PlayerB
        self.turns = max_turns*2
        self.evaluators = evaluators
    
        self.turn = 1 

        self.message_log = []

    def reset(self):
        self.turn = 1 
        self.message_log = []

    def run(self):

        for i in range(1,self.turns+1):
            player = self.get_current_player()
            self.moderator_speak(f'This is turn {ceil(i/2)} for {player.name}')

            message_content = player.act(self.message_log)
            message = Message(agent_name = player.name, content = message_content)
            self.message_log.append(message)

            self.turn+=1

        if self.evaluators is not None:
            evaluator_messages = []
            for evaluator in self.evaluators:
                verdict = evaluator(self.message_log)
                message = Message(agent_name = 'evaluator', content = verdict)
                evaluator_messages.append(message)

            self.message_log.extend(evaluator_messages)
        
        output = []
        
        for msg in self.message_log:
            if msg.reason is not None:
                output.append((msg.agent_name, 'REASON: ' + msg.reason,'RESPONSE:', msg.content))
            else:
                output.append((msg.agent_name, msg.content))

        return output
        

    def get_current_player(self):
        return self.PlayerA if (self.turn -1) %2 == 0 else self.PlayerB
    

    def moderator_speak(self, content):
        message = Message('Moderator', content)
        self.message_log.append(message)



class Message(object):
    def __init__(self, agent_name, content):
        self.agent_name = agent_name
        self.reason = None

        if isinstance(content, tuple):
            self.reason, self.content = content
        else:
            self.content = content
    def __getitem__(self,idx):
        return (self.agent_name, self.content)[idx]
    