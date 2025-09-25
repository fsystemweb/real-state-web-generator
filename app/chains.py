import logging
from dotenv import load_dotenv
import os
load_dotenv()
import re
import json

from pathlib import Path
from fastapi import HTTPException
from app.models import PropertyData
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Ensure your OpenAI API key is set
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError("OPENAI_API_KEY not found in environment")

# Load prompt templates from files
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
generator_template = (PROMPT_DIR / "generator_prompt_gpt-4o-mini.txt").read_text()
evaluator_template = (PROMPT_DIR / "evaluator_prompt_gpt-4-turbo.txt").read_text()

generator_prompt = PromptTemplate(
    input_variables=["property_json", "language_name", "language_code"],
    template=generator_template
)
evaluator_prompt = PromptTemplate(input_variables=["html_output"], template=evaluator_template)

# Initialize ChatOpenAI with API key
generator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=openai_api_key)
evaluator_llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=openai_api_key)

# Setup chains using LCEL (LangChain Expression Language)
output_parser = StrOutputParser()
generator_chain = generator_prompt | generator_llm | output_parser
evaluator_chain = evaluator_prompt | evaluator_llm | output_parser

MAX_RETRIES = 3
MIN_SCORE = 3

def generate_and_evaluate(property_data: PropertyData):
    logger.info("Request: %s", property_data)
    retries = 0
    failed_criteria_log = []

    while retries < MAX_RETRIES:
        property_dict = property_data.model_dump()
        language_code = property_dict.get("language", "en")
        
        if language_code not in ["en", "pt", "es"]:
            language_code = "en"
        
        logger.info("Language Code: %s", language_code)

        language_names = {"en": "English", "pt": "Portuguese", "es": "Spanish"}
        language_name = language_names[language_code]

        html_output = generator_chain.invoke({
            "property_json": property_data.model_dump_json(),
            "language_name": language_name,
            "language_code": language_code
        })
        logger.info("HTML Output: %s", html_output)
        
        evaluation_str = evaluator_chain.invoke({"html_output": html_output})
        evaluation_str = re.sub(r"^```.*\n|```$", "", evaluation_str.strip(), flags=re.MULTILINE)
        
        try:
            evaluation_json = json.loads(evaluation_str)
        except json.JSONDecodeError:
            logger.error("Invalid evaluator JSON: %s", evaluation_str)
            raise HTTPException(status_code=500, detail="Evaluator returned invalid JSON")
        
        logger.info("Evaluation JSON: %s", evaluation_json)

        total_score = evaluation_json.get("total_score", 0)

        if total_score >= MIN_SCORE:
            return {
                "html": html_output,
                "evaluation": evaluation_json,
                "retries": retries,
                "failed_criteria_log": failed_criteria_log
            }

        failing_criteria = {
            k: int(v) for k, v in evaluation_json.items()
            if k != "total_score" and int(v) < MIN_SCORE
        }
        failed_criteria_log.append({"retry": retries + 1, "failing_criteria": failing_criteria})
        retries += 1

    raise HTTPException(
        status_code=422,
        detail={
            "message": f"Generated content did not reach minimum score {MIN_SCORE} after {MAX_RETRIES} attempts",
            "failed_criteria_log": failed_criteria_log
        },
    )