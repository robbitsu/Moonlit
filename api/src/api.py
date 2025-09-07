from fastapi import FastAPI
import uvicorn
from database import SessionLocal, engine, Base
import time

app = FastAPI(title="Moonlit API", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "time": time.time()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8123)