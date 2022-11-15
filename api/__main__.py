import uvicorn

import main as api
from app import app

app.init(seed=True)
api.init()

if __name__ == "__main__":
	uvicorn.run(api.api, host="0.0.0.0", port=8000)
