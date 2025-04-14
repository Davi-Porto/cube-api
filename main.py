from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import kociemba
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

class CubeState(BaseModel):
  state: str

@app.post("/solve")
def solve(data: CubeState, x_api_key: str = Header(None)):
  if x_api_key != API_KEY:
    raise HTTPException(status_code=403, detail="Unauthorized")
  
  try:
    solution = kociemba.solve(data.state)
    return {"solution": solution}
  except Exception as e:
    return {"error": str(e)}