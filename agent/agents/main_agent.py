import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

from vector_store.vector_infra import VectorStoreService
from agent.prompt import react_docstore_prompt, agent_prompt

from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent

from agent.models import model
from copy import deepcopy

from api.tickets.infrastructure.ticket_repo import TicketRepo, Ticket


prompt = deepcopy(react_docstore_prompt)
prompt.template = agent_prompt


class MainAgent:
    def __init__(self, user_id, company_id):
        self.user_id = user_id
        self.company_id = company_id
        self.tools = [
            Tool.from_function(
                name="Retrieve context from VectorDB",
                func=self.create_context_retriever(self.company_id),
                description="Useful for retrieving context about a company from VectorDB. Args: prompt: str (A hypothetical paragraph which is similar to the answer to the user's question.)",
            ),
            Tool.from_function(
                name="Create Ticket",
                func=self.create_ticket(self.company_id, self.user_id),
                description="Useful for creating a ticket for Customer Support department admins to see. Args: issue: str (The issue faced by user to be reported to the admin.). Say the ticket id to the user after creating the ticket.",
            ),
            Tool.from_function(
                name="Search Internet",
                func=self.search,
                description="Useful for searching for websites in internet if the context retriever tool fails to provide much information. Arg: query: str. Use this format for searching in internet: X in finance. (where X is query). After using this tool, make sure put a note 'Note: Some of the contents in this response were retrieved from the internet.' in the response.",
            ),
        ]
        self.agent = create_react_agent(llm=model, tools=self.tools, prompt=prompt)
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            handle_parsing_errors=True,
            verbose=True,
        )

    def create_context_retriever(self, company_id):
        def context_retriever(prompt):
            try:
                vector_store = VectorStoreService()
                docs = vector_store.get_vectorstore_for_customer(
                    company_id
                ).similarity_search(query=prompt, k=5)
                return docs
            except Exception as e:
                return f"Failed to report prompt: {str(e)}"

        return context_retriever

    def create_ticket(self, company_id, user_id):
        def ticket_creator(issue):
            ticket_repo = TicketRepo()
            ticket = Ticket(
                company_id=company_id,
                user_id=user_id,
                issue=issue,
            )
            data = ticket_repo.create_ticket(ticket)
            return f"Ticket has been created with ID: {data.id}"

        return ticket_creator

    def search(self, query):

        print(f"Searching on internet: {query}")
        search_url = "https://duckduckgo.com/html/"
        params = {"q": query}

        response = requests.get(search_url, params=params)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("div", class_="result")

            try:
                result_list = []
                for result in results:
                    title_tag = result.find("a", class_="result__a")
                    if title_tag:
                        title = title_tag.get_text()
                        raw_link = title_tag.get("href")
                        parsed_url = urlparse(raw_link)
                        query_params = parse_qs(parsed_url.query)
                        actual_link = unquote(query_params.get("uddg", [""])[0])
                    else:
                        title, actual_link = "No title", "No link"

                    # Snippet
                    snippet_tag = result.find("a", class_="result__snippet")
                    snippet = (
                        snippet_tag.get_text().strip()
                        if snippet_tag
                        else "No description available"
                    )

                    # Combine result
                    result_item = {
                        "Title": title,
                        "Link": actual_link,
                        "Description": snippet,
                    }
                    result_list.append(result_item)

                return result_list
            except Exception as e:
                return f"Error: {e}"
        else:
            return "Error occurred while searching."
