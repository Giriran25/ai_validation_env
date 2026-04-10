from fastapi import FastAPI
from env.environment import AIValidationEnv

app = FastAPI()

env = AIValidationEnv()


@app.post("/reset")
def reset():
    return env.reset()


@app.post("/step")
def step(action: dict):
    return env.step(action)


@app.get("/state")
def state():
    return env.state()