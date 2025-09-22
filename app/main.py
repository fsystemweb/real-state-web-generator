from fastapi import FastAPI
from app.models import PropertyData
from app.chains import generate_and_evaluate

app = FastAPI()

@app.post("/generate-listing")
def generate_listing(property_data: PropertyData):
    return generate_and_evaluate(property_data)
