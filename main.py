from fastapi import FastAPI
from pydantic import BaseModel
import kociemba

app = FastAPI()

class CubeState(BaseModel):
  state: str

@app.post("/solve")
def solve(data: CubeState):
  try:
    solution = kociemba.solve(data.state)
    return {"solution": solution}
  except Exception as e:
    return {"error": str(e)}