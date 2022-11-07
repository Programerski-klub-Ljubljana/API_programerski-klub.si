import logging

import uvicorn
from fastapi import FastAPI
from fastapi_utils.timing import add_timing_middleware, record_timing

from src import env, api
from src.db import seed


print(env.load_dotenv())
seed.init()




if __name__ == "__main__":
	uvicorn.run(api.app, host="0.0.0.0", port=8000)
