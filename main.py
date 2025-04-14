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
  state: str = ""
  moves: str = ""

def generate_valid_state(scr: str = "", fcs: dict[str, str] = {}) -> str:
  scramble = scr or generate_valid_scramble()
  faces = fcs or data["solved_faces"]

  for mv in scramble.strip().split():
    m = mv[0]
    s = mv[1:]

    faces = move(m, s, faces)

  return to_state(faces)

def rotate_face(face: str) -> str:
  
  return "".join([
    "".join([face[6], face[3], face[0]]),
    "".join([face[7], face[4], face[1]]),
    "".join([face[8], face[5], face[2]]),
  ])

def move(mv: str, s: str, state: dict[str, str]) -> dict[str, str]:
  new_state = state
  turns = 1 if s == "" else 2 if s == "2" else 3

  ignore = data["opposite"][mv]

  for _ in range(turns):
    temp = {}

    for face in data["ref"]:
      if face == mv:
        temp[face] = rotate_face(new_state[face])
      elif face != ignore:
        target = data["map"][mv][face]["target"]
        from_i = data["map"][mv][face]["from_i"]
        to_i = data["map"][mv][face]["to_i"]

        new_face = new_state[face]
        for i in range(3):
          sticker_b4 = new_state[target][from_i[i]]
          new_face = new_face[:to_i[i]]+sticker_b4+new_face[to_i[i]+1:]
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

def to_state(faces: dict[str, str]) -> str:
  return "".join(faces.values())

def to_faces(state: str) -> dict[str, str]:
  return {
    "U": state[0:9],
    "R": state[9:18],
    "F": state[18:27],
    "D": state[27:36],
    "L": state[36:45],
    "B": state[45:54]
  }

@app.get("/start")
def start(x_api_key: str = Header(None)) -> dict[str, str]:
  if x_api_key != API_KEY:
    raise HTTPException(status_code=403, detail="Unauthorized")
  
  try:
    while True:
      state = generate_valid_state()
      moves = kociemba.solve(state)
      moves_inverted = invert_scramble(moves)
      if len(moves.strip().split()) == 20:
        return {
          "state": generate_valid_state(moves_inverted),
          "scramble": moves_inverted
        }
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

@app.post("/move")
def unique_move(data: CubeState, x_api_key: str = Header(None)) -> dict[str, str]:
  if x_api_key != API_KEY:
    raise HTTPException(status_code=403, detail="Unauthorized")
  
  try:
    faces = to_faces(data.state)
    state = generate_valid_state(data.moves, faces)
    return {"state": state}
  except Exception as e:
    return {"error": str(e)}