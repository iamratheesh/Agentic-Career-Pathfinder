import json
import re
import asyncio
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class StrategyQuestionsAgent:
    def __init__(self, api_key: str, resume_file: str = "resume.txt"):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
        self.parser = JsonOutputParser()
        self.resume_data = self._load_resume(resume_file)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert career guidance AI. Your task is to generate assessment questions tailored to a candidate's resume and a specified domain. Use the provided resume data to create relevant, in-depth strategy questions that assess the candidate's expertise in the domain. Provide the output as a JSON array of objects, where each object has an 'id' (integer, starting from 1) and 'question' (string). Do NOT include markdown backticks or extra text."""),
            ("human", """Generate 10 strategy questions to assess a student's depth in {domain}.
Resume data: {resume_data}
Example:
[
    {{"id": 1, "question": "Question 1"}},
    {{"id": 2, "question": "Question 2"}}
]
Domain: {domain}
""")
        ])
        self.chain = self.prompt | self.llm

    def _load_resume(self, resume_file: str) -> str:
        try:
            with open(resume_file, 'r', encoding='utf-8') as file:
                resume_content = file.read()
            return resume_content
        except FileNotFoundError:
            print(f"Error: Resume file '{resume_file}' not found.")
            return "Resume data unavailable."
        except Exception as e:
            print(f"Error reading resume file: {e}")
            return "Resume data unavailable."

    def _extract_and_parse_json(self, text: str) -> Optional[List[Dict]]:
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str_match = re.search(r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]', text, re.DOTALL)
            if json_str_match:
                json_str = json_str_match.group(0)
            else:
                print(f"DEBUG: No JSON array found in text: {text[:500]}...")
                return None
        
        try:
            parsed_json = json.loads(json_str)
            if isinstance(parsed_json, list) and all(isinstance(q, dict) and 'id' in q and 'question' in q for q in parsed_json):
                return parsed_json
            else:
                print(f"DEBUG: JSON is list, but does not match Question structure: {json_str[:200]}...")
                return None
        except json.JSONDecodeError:
            print(f"DEBUG: Failed to parse extracted JSON string: {json_str[:200]}...")
            return None
        
        return None

    async def generate_questions(self, domain: str) -> List[Dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                raw_response = await self.chain.ainvoke({
                    "domain": domain,
                    "resume_data": self.resume_data
                })
                
                if hasattr(raw_response, 'content'):
                    response_content = raw_response.content
                else:
                    response_content = str(raw_response)

                response = self._extract_and_parse_json(response_content)

                if response is not None:
                    return response
                else:
                    print(f"Attempt {attempt + 1}: Agent returned malformed or unparseable JSON for questions. Retrying...")
                    await asyncio.sleep(2 * (attempt + 1))
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error generating strategy questions: {e}. Retrying...")
                await asyncio.sleep(2 * (attempt + 1))
        
        print(f"Failed to generate strategy questions after {max_retries} attempts.")
        return [{"id": i+1, "question": f"Error-fallback question {i+1} for {domain}"} for i in range(10)]