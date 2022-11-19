import uvicorn

from api import API

if __name__ == "__main__":
	API.init(timing=True)
	uvicorn.run(API.fapi, host="0.0.0.0", port=8000)
