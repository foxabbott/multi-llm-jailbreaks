
from math import ceil
from utils import get_players

class Interaction(object):
    def __init__(self, PlayerA, PlayerB, evaluators = None, max_turns = 2):

        self.PlayerA = PlayerA
        self.PlayerB = PlayerB
        self.players = [PlayerA.name, PlayerB.name]
        self.CoT_players = [player.name for player in (PlayerA,PlayerB) if player.CoT]
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

            self.moderator_speak(f'This is turn {ceil(i/2)} for {player.name}', visibility = self.players)
            if player.name in self.CoT_players:
                self.moderator_speak(f'Remember to separate your response into REASONING: Followed by a paragraph explaining your chain of thought, and MESSAGE: Followed by your message to you opponent', visibility = self.CoT_players)

            visible_messages = [msg for msg in self.message_log if player.name in msg.visibility]
            message_content = player.act(visible_messages)
            message = Message(agent_name = player.name, content = message_content, visibility=self.players)
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
    

    def moderator_speak(self, content, visibility = None):
        message = Message('Moderator', content, visibility=visibility)
        self.message_log.append(message)



class Message(object):
    def __init__(self, agent_name, content, visibility = None):
        self.agent_name = agent_name
        self.reason = None
        self.visibility = visibility

        if isinstance(content, tuple):
            self.reason, self.content = content
        else:
            self.content = content
    def __getitem__(self,idx):
        return (self.agent_name, self.content)[idx]
    