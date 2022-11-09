import uvicorn

from src import env, api
from src.db import seed

env
seed.init()

if __name__ == "__main__":
	uvicorn.run(api.app, host="0.0.0.0", port=8000)
