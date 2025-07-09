from fastapi import FastAPI

app = FastAPI(title="测试应用")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/status")
async def status():
    return {"status": "operational"} 