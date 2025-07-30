# career_pathfinder/agents/level_detector.py

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict

class LevelDetectorAgent:
    def __init__(self, api_key: str):
        # MODIFIED: Use an actively supported Groq model
        # 'llama3-8b-8192' is a good, fast choice.
        self.llm = ChatGroq(model="llama3-8b-8192", api_key=api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI that classifies a student's skill level based on their quiz answers."),
            ("human", """Based on these 10 QA pairs, classify the user as Beginner / Intermediate / Advanced.
            Your response should be only one word: 'Beginner', 'Intermediate', or 'Advanced'.
            QA Pairs:
            {qa_pairs}
            """)
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def detect_level(self, qa_pairs: List[Dict]) -> str:
        qa_text = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in qa_pairs])
        try:
            level = await self.chain.ainvoke({"qa_pairs": qa_text})
            valid_levels = ["Beginner", "Intermediate", "Advanced"]
            level = level.strip()
            if level in valid_levels:
                return level
            else:
                print(f"Agent returned unexpected level: '{level}'. Defaulting to 'Beginner'.")
                return "Beginner"
        except Exception as e:
            print(f"Error detecting skill level: {e}")
            return "Beginner"