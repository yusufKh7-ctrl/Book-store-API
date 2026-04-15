from fastapi import FastAPI

app = FastAPI(title="Book-store")

@app.get("/")
async def home():
    return {"msg": "Welcome Home"}