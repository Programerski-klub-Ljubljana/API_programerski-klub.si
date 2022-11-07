import logging

import uvicorn
from fastapi import FastAPI
from fastapi_utils.timing import add_timing_middleware, record_timing

from src import env, api
from src.db import seed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(env.load_dotenv())
seed.init()


app = FastAPI()
add_timing_middleware(app, record=logger.info, prefix="app", exclude="untimed")
app.include_router(api.router)

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
