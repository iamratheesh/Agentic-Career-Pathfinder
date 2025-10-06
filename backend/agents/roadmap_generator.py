from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from typing import List, Dict, Optional
import json
import re
import asyncio
import traceback

class RoadmapGeneratorAgent:
    def __init__(self, api_key: str, tavily_api_key: str):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0.5, max_tokens=4096) 

        self.tavily_tool = TavilySearchResults(api_key=tavily_api_key, max_results=3)
        self.tools = [self.tavily_tool]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI specialized in creating structured learning roadmaps. For each task, you MUST try to find a relevant, high-quality online resource link. Prioritize finding **YouTube video tutorials or playlists** for each task. Use the provided search tool to find these resources.
            Your final answer MUST be a complete and perfectly valid JSON array of objects, where each object has a 'week' (integer) and 'tasks' (array of task objects). Each task object MUST have 'task' (string) and 'resourceLink' (string, or null if no relevant YouTube link is found after searching).
            IMPORTANT: Do NOT include ANY extra text, preamble, postamble, or markdown backticks around the JSON. The JSON should be the ABSOLUTE ONLY content in your final answer. Ensure all commas and brackets are correctly placed and the array is fully closed.
            Example:
            [
                {{
                    "week": 1,
                    "tasks": [
                        {{"task": "Learn HTML/CSS basics", "resourceLink": "https://www.youtube.com/watch?v=k_lG5k36fB4"}},
                        {{"task": "Understand CSS Flexbox", "resourceLink": "https://www.youtube.com/watch?v=33Qh3z12o-1"}}
                    ]
                }},
                {{
                    "week": 2,
                    "tasks": [
                        {{"task": "Master JavaScript ES6+", "resourceLink": "https://www.youtube.com/playlist?list=PL_XQdYtU1d3_E5L6yU3wU8y0a0e_2x2x2"}},
                        {{"task": "Build DOM projects", "resourceLink": null}}
                    ]
                }}
            ]
            """),
            ("human", """Generate a 12-week learning roadmap for job readiness in 3 months based on the following: {input}. For each task, search for and provide one highly relevant **YouTube tutorial or playlist link** as a resource."""),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent_chain = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        self.executor = AgentExecutor(agent=self.agent_chain, tools=self.tools, verbose=True)

    def _extract_and_parse_json(self, text: str) -> Optional[List[Dict]]:
        """
        Attempts to extract and parse a JSON array from a given string.
        Handles cases where LLM might include markdown or extra text.
        Prioritizes markdown code blocks, then tries raw JSON array.
        """
        json_str = None
        
        json_match_md = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match_md:
            json_str = json_match_md.group(1)
            print(f"DEBUG: Found JSON in markdown block. Trying to parse: {json_str[:200]}...")
        
        if json_str is None:
            json_str_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_str_match:
                json_str = json_str_match.group(0)
                print(f"DEBUG: Found raw JSON array. Trying to parse: {json_str[:200]}...")
        
        if json_str:
            try:
                parsed_json = json.loads(json_str)
                if isinstance(parsed_json, list):
                    if all(isinstance(week, dict) and 'week' in week and 'tasks' in week and isinstance(week['tasks'], list) for week in parsed_json):
                        print("DEBUG: JSON parsed and validated successfully.")
                        return parsed_json
                    else:
                        print(f"DEBUG: JSON list found, but does not match expected RoadmapWeek structure criteria. Raw: {json_str[:500]}...")
                        return None
            except json.JSONDecodeError as e:
                print(f"DEBUG: Failed to parse extracted JSON string. Error: {e}. String (full): {json_str} \n--- Raw Text from LLM was: {text[:2000]}...")
                return None
        
        print(f"DEBUG: No valid JSON array found in text after all attempts. Raw text (full): {text[:2000]}...")
        return None

    async def generate_roadmap(self, domain: str, level: str) -> List[Dict]:
        """Generates a weekly learning roadmap with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1} to generate roadmap for {domain} ({level})...")
            try:
                agent_query_input = f"Domain: {domain}, Level: {level} learner. Generate a detailed roadmap."
                
                response = await self.executor.ainvoke({"input": agent_query_input})
                
                raw_agent_output = response.get("output")

                if raw_agent_output:
                    generated_weeks_data = self._extract_and_parse_json(raw_agent_output)
                    
                    if generated_weeks_data is not None:
                        print(f"Roadmap generated successfully on attempt {attempt + 1}.")
                        return generated_weeks_data
                    else:
                        print(f"Attempt {attempt + 1}: Agent returned malformed or unparseable JSON output for roadmap. Retrying...")
                        await asyncio.sleep(2 * (attempt + 1))
                else:
                    print(f"Attempt {attempt + 1}: Agent response missing 'output' key. Raw response: {response}. Retrying...")
                    await asyncio.sleep(2 * (attempt + 1))

            except Exception as e:
                print(f"Attempt {attempt + 1}: Error during agent execution: {e}. Retrying...")
                traceback.print_exc()
                await asyncio.sleep(2 * (attempt + 1))
        
        print(f"Failed to generate roadmap after {max_retries} attempts.")
        return []