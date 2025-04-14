from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import kociemba
import os
import random
import json

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

class CubeState(BaseModel):
  state: str

def generate_valid_state() -> str:
  scramble = generate_valid_scramble().strip().split()
  faces = data["solved_faces"]

  for move in scramble:
    mv = move[0]
    suffix = move[1] or ""

    faces = move(mv, suffix, faces)
  
  return "".join(faces.values())

def rotate_face(face: str) -> str:
  
  return "".join([
    "".join([face[6], face[3], face[0]]),
    "".join([face[7], face[4], face[1]]),
    "".join([face[8], face[5], face[2]]),
  ])

def move(mv: str, s: str, state: dict[str, str]) -> dict[str, str]:
  new_state = state
  turns = 1 if s == "" else 2 if s == "2" else 3
  
  ignore = data["beside"][mv]["o"]

  for _ in range(turns):
    temp = {}

    for face in data["ref"]:
      if face == mv:
        temp[face] = rotate_face(new_state[face])
      elif face != ignore:
        target, before, after = data["map"][mv][face]
        new_face = new_state[face]
        for i in range(3):
          sticker_b4 = new_state[target][before[i]]
          new_face = new_face[:after[i]]+sticker_b4+new_face[after[i]+1:]
        temp[face] = new_face
      else:
        temp[face] = new_state[face]
    
    new_state = temp

  return new_state

def generate_valid_scramble() -> str:
  moves = ["R", "L", "U", "D", "F", "B"]
  suffixes = ["'", "2", ""]
  scramble = []

  last_move = ""
  for _ in range(20):
    while True:
      move = random.choice(moves)
      if move != last_move:
        break
    last_move = move
    move += random.choice(suffixes)
    scramble.append(move)

  return " ".join(scramble)

def invert_scramble(scramble: str) -> str:
  moves = scramble.strip().split()
  inverted_moves = []

  for move in moves:
    if move.endswith("'"):
      inverted_moves.append(move[0])
    elif move.endswith("2"):
      inverted_moves.append(move)
    else:
      inverted_moves.append(move[0] + "'")
  
  return " ".join(inverted_moves)

@app.get("/start")
def start(x_api_key: str = Header(None)) -> dict[str, str]:
  if x_api_key != API_KEY:
    raise HTTPException(status_code=403, detail="Unauthorized")
  
  try:
    state = generate_valid_state()
    print(state, "State")
    scramble = invert_scramble(kociemba.solve(state))
    print(scramble, "Scramble")
    return {"state": state, "scramble": scramble}
  except Exception as e:
    return {"error": str(e)}

@app.post("/solve")
def solve(data: CubeState, x_api_key: str = Header(None)) -> dict[str, str]:
  if x_api_key != API_KEY:
    raise HTTPException(status_code=403, detail="Unauthorized")
  
  try:
    solution = kociemba.solve(data.state)
    return {"solution": solution}
  except Exception as e:
    return {"error": str(e)}