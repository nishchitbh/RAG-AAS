from agent.models import model
from agent.prompt import chat_history_summarizer_prompt
from agent.agents.prompt_reporter import PromptReporter
from agent.agents.main_agent import MainAgent
from api.end_users.infrastructure.end_user_repo import (
    EndUserRepo,
    LatestChat,
    EndUserUpdate,
)
from langchain_core.output_parsers import StrOutputParser

from api.chat.domain.services import ChatServices


class ChatUseCases:
    def __init__(self, chat_services: ChatServices):
        self.chat_services = chat_services

    def verify(self, company: str, user: str):
        self.chat_services.verify_company(company)
        self.chat_services.verify_user(user)

    def summarize_history(self, current_history: dict, previous_summary=None):
        prompt = f"{chat_history_summarizer_prompt}\nPrevious Chat History Summary: {previous_summary if previous_summary!="" else "Beginning of the conversation."}\nConversation: {current_history if current_history!=[] else "Beginning of the conversation."}"
        chain = model | StrOutputParser()
        summarized_history = chain.invoke(prompt)
        return summarized_history

    def chat_pipeline(self, company_id, user_id, prompt: str):
        end_user_repo = EndUserRepo()
        prompt_reporter = PromptReporter(user_id, company_id)
        sanitized = prompt_reporter.agent_executor.invoke({"input": prompt})["output"]
        user = end_user_repo.get_user_by_id(user_id)
        user_chat_history_summary = user.chat_summary
        last_convo = user.chat_history[-1] if not user.chat_history == [] else None
        final_agent = MainAgent(user_id=user_id, company_id=company_id)
        reply = final_agent.agent_executor.invoke(
            {
                "chat_history": user_chat_history_summary,
                "input": sanitized,
                "last_conversation": last_convo,
            }
        )["output"]
        current_history = {"user": prompt, "bot": reply}
        summary = self.summarize_history(
            current_history=current_history, previous_summary=user_chat_history_summary
        )
        end_user_repo.update_user(
            generated_id=user_id, user_update=EndUserUpdate(chat_summary=summary)
        )
        end_user_repo.push_to_history(
            generated_id=user_id, user_update=LatestChat(**current_history)
        )
        return reply
