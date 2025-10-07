from langchain import hub
from agent.prompt import agent_prompt

react_docstore_prompt = hub.pull("hwchase17/react-chat")
react_docstore_prompt.template = agent_prompt
