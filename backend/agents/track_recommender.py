
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from typing import List, Dict, Optional
import json
import re
import asyncio

class CareerTrackRecommenderAgent:
    def __init__(self, api_key: str, tavily_api_key: str):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

        self.tavily_tool = TavilySearchResults(api_key=tavily_api_key, max_results=5)
        self.tools = [self.tavily_tool]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert career guidance AI. Your goal is to suggest 2-3 career roles based on the user's domain and skill level, enriching them with salary, skills, tools, and growth prospects using web search tools if necessary. Your final answer MUST be a JSON array of objects as per the example provided, without any extra text, preamble, or markdown backticks."),
            ("human", """{input}
            
            For each role, provide:
            - title: The job title.
            - avgSalary: Average salary range (e.g., "8-12 LPA"). Use web search tool if needed to find current and relevant salary data.
            - skills: Key skills required. Use web search tool if needed to find comprehensive skill sets.
            - tools: Essential tools used in this role. Use web search tool if needed to identify common tools.
            - growth: Potential career growth path. Use web search tool if needed to understand career progression.
            
            Provide the output as a JSON array of objects.
            Example:
            [
                {{
                    "title": "React Developer",
                    "avgSalary": "8-12 LPA",
                    "skills": ["React", "Redux"],
                    "tools": ["Vite", "Next.js"],
                    "growth": "Can become Frontend Architect"
                }},
                {{
                    "title": "Angular Developer",
                    "avgSalary": "7-11 LPA",
                    "skills": ["Angular", "TypeScript"],
                    "tools": ["Angular CLI", "RxJS"],
                    "growth": "Can become Full-stack Lead"
                }}
            ]
            """),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent_chain = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        self.executor = AgentExecutor(agent=self.agent_chain, tools=self.tools, verbose=True)

    def _extract_and_parse_json(self, text: str) -> Optional[List[Dict]]:
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str_match = re.search(r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]', text, re.DOTALL)
            if json_str_match:
                json_str = json_str_match.group(0)
            else:
                print(f"DEBUG: No valid JSON array found in text: {text[:500]}...")
                return None
        
        try:
            parsed_json = json.loads(json_str)
            if isinstance(parsed_json, list) and all(isinstance(t, dict) and 'title' in t for t in parsed_json):
                return parsed_json
            else:
                print(f"DEBUG: JSON is list, but does not match CareerTrack structure: {json_str[:200]}...")
                return None
        except json.JSONDecodeError:
            print(f"DEBUG: Failed to parse extracted JSON string: {json_str[:200]}...")
            return None
        
        return None

    async def recommend_tracks(self, domain: str, level: str) -> List[Dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                agent_query_input = (
                    f"Suggest 2-3 career roles in the '{domain}' domain for a '{level}' learner."
                    " Provide detailed information for each role, including average salary, key skills required,"
                    " essential tools used, and potential career growth paths."
                    " Utilize web search tools to gather accurate and up-to-date information."
                    " Ensure the output is STRICTLY a JSON array as per the example provided, with no extra text or formatting."
                )
                
                response = await self.executor.ainvoke({"input": agent_query_input})

                if "output" in response:
                    tracks = self._extract_and_parse_json(response["output"])
                    
                    if tracks is not None:
                        return tracks
                    else:
                        print(f"Attempt {attempt + 1}: Agent returned malformed or unparseable JSON output. Retrying...")
                        await asyncio.sleep(2 * (attempt + 1))
                else:
                    print(f"Attempt {attempt + 1}: Agent response missing 'output' key. Retrying...")
                    await asyncio.sleep(2 * (attempt + 1))

            except Exception as e:
                print(f"Attempt {attempt + 1}: Error during agent execution: {e}. Retrying...")
                await asyncio.sleep(2 * (attempt + 1))
        
        print(f"Failed to recommend career tracks after {max_retries} attempts.")
        return []