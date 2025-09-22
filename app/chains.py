from pathlib import Path
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from app.models import PropertyData
from fastapi import HTTPException

# Load prompt templates from files
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
generator_template = (PROMPT_DIR / "generator_prompt.txt").read_text()
evaluator_template = (PROMPT_DIR / "evaluator_prompt.txt").read_text()

generator_prompt = PromptTemplate(input_variables=["property_json"], template=generator_template)
evaluator_prompt = PromptTemplate(input_variables=["html_output"], template=evaluator_template)

generator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

generator_chain = LLMChain(llm=generator_llm, prompt=generator_prompt)
evaluator_chain = LLMChain(llm=evaluator_llm, prompt=evaluator_prompt)

MAX_RETRIES = 3
MIN_SCORE = 8

def generate_and_evaluate(property_data: PropertyData):
    retries = 0
    failed_criteria_log = []

    while retries < MAX_RETRIES:
        html_output = generator_chain.run(property_json=property_data.model_dump_json())
        evaluation_json = evaluator_chain.run(html_output=html_output)

        try:
            evaluation = eval(evaluation_json)  # Convert JSON string to dict
        except Exception:
            raise HTTPException(status_code=500, detail="Evaluator returned invalid JSON")

        total_score = evaluation.get("total_score", 0)

        if total_score >= MIN_SCORE:
            return {
                "html": html_output,
                "evaluation": evaluation,
                "retries": retries,
                "failed_criteria_log": failed_criteria_log
            }

        failing_criteria = {
            k: v for k, v in evaluation.items() if k != "total_score" and v < 8
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
