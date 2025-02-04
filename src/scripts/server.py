from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define request body model
class CalculationRequest(BaseModel):
    number1: float
    number2: float

# Define API endpoint
@app.post("/calculate")
async def calculate(data: CalculationRequest):
    result = data.number1 + data.number2  # Example calculation
    return {"result": result}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)