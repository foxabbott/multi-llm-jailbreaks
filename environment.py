import random
from typing import List,Union
from chatarena.environments.base import TimeStep, Environment
from chatarena.message import Message, MessagePool
from chatarena.utils import extract_jsons
from chatarena.agent import Player
from prompts import get_prompts


class Game(Environment):

    def __init__(self, debate_topic: str, max_turn:int):
        super().__init__(player_names=["LLM-A", "LLM-B"])
        self.debate_topic = debate_topic
        self.max_turn = max_turn
        self.turn = 0
        self.message_pool = MessagePool()
        self._terminal = False
        self.reset()

    def _moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"):
        """
        Function for the moderator to speak to the players.
        """
        message = Message(agent_name="Moderator", content=text, turn=self.turn, visible_to=visible_to)
        self.message_pool.append_message(message)

    def reset(self):
        """
        Reset the game.
        """
        self.turn = 0
        self.message_pool.reset()
        self._terminal = False

        # Moderator
        self._moderator_speak(f"Welcome to the debate on {self.debate_topic}.")
        observation = self.get_observation(self.get_next_player())
        return TimeStep(observation=observation, reward=self._get_zero_rewards(), terminal=False)

    def get_observation(self, player_name=None) -> List[Message]:
        """
        Get the observation of the player.
        """
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(player_name, turn=self.turn)

    def get_next_player(self) -> str:
        """
        Get the name of the next player.
        """
        return "LLM-A" if self.turn % 2 == 0 else "LLM-B"

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        Step function for the game.
        """

        #Check correct player taking turn
        assert player_name == self.get_next_player(), f"Wrong player! It is {self.get_next_player()}'s turn."

        #Add Message to Pool
        arguments = action
        message = Message(agent_name=player_name, content=arguments, turn=self.turn, visible_to="all")
        self.message_pool.append_message(message)

        # Update turn
        self.turn += 1

        self._moderator_speak(f"This is Turn {self.turn}.")

        # Check for termination

        if self.turn >= self.max_turn:
            self._terminal = True
            self._moderator_speak("The conversation is over.")

        observation = self.get_observation(self.get_next_player())
        reward = self._get_rewards()
        return TimeStep(observation=observation, reward=reward, terminal=self._terminal)

    def _get_rewards(self):
        """
        Get the reward of the current state.
        """
        return {self.player_names[0]: 0, self.player_names[1]: 0}

    def _get_zero_rewards(self):
        return {self.player_names[0]: 0, self.player_names[1]: 0}
    


def get_players(setting, debate_topic, max_turns, backend_A, backend_B):

    prompts = get_prompts(setting, debate_topic, max_turns)

    LLM_A = Player(
        name = 'LLM-A',
        role_desc = prompts['LLM-A'] + prompts['format_spec'],
        backend = backend_A
    )

    LLM_B = Player(
        name = 'LLM-B',
        role_desc = prompts['LLM-B'] + prompts['format_spec'],
        backend = backend_B
    )

    return [LLM_A, LLM_B]

