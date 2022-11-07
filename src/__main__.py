import uvicorn
from fastapi import FastAPI
from src import env, api
from src.db import seed

print(env.load_dotenv())
seed.init()

app = FastAPI()
app.include_router(api.router)

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
