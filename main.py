from fastapi import FastAPI
import uvicorn

from api.couriers import couriers_api


app = FastAPI()
app.include_router(couriers_api)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)