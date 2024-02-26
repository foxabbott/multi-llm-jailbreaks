import replicate
from chatarena.backends import IntelligenceBackend
from chatarena.message import SYSTEM_NAME as SYSTEM, Message
from typing import List, Union
import re


DEFAULT_MAX_TOKENS = 4096


def is_replicate_available():

    #Check if replicate is set up
    try:
        import replicate
    except ImportError:
        available = False
    else:
        if 'REPLICATE_API_TOKEN' in os.environ:
            available = True
        else:
            available = False

    return available


class ReplicateBackend(IntelligenceBackend):

    stateful=False
    type_name="replicate"

    def __init__(self, model, max_tokens = DEFAULT_MAX_TOKENS, **kwargs):
        
        assert (is_replicate_available), 'replicate not installed or API key not set'

        self.max_tokens = max_tokens  
        self.model = model

        super().__init__(**kwargs)

    
    def _get_response(self, all_messages, *args, **kwargs):
        output = replicate.run(
            self.model,
            input={
                "prompt": all_messages,
                "max_new_tokens": self.max_tokens
            }
        )

        return ''.join(list(output))



    def query(
        self,
        agent_name: str,
        role_desc: str,
        history_messages: List[Message],
        global_prompt: str = None,
        request_msg: Message = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Format the input and call ReplicateAPI.

        args:
            agent_name: the name of the agent
            role_desc: the description of the role of the agent
            env_desc: the description of the environment
            history_messages: the history of the conversation, or the observation for the agent
            request_msg: the request from the system to guide the agent's next response
        """

        all_messages = (
            [(SYSTEM, global_prompt), (SYSTEM, role_desc)]
            if global_prompt
            else [(SYSTEM, role_desc)]
        )


        for message in history_messages:
            all_messages.append((message.agent_name, message.content))
        if request_msg:
            all_messages.append((SYSTEM, request_msg.content))


        response = self._get_response(str(all_messages), *args, **kwargs)

        # Remove the agent name if the response starts with it
        # Remove the agent name if the response starts with it
        response = re.sub(rf"^\s*\[.*]:", "", response).strip()  # noqa: F541
        response = re.sub(
            rf"^\s*{re.escape(agent_name)}\s*:", "", response
        ).strip()  # noqa: F451


        return response