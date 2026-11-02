from fastapi import FastAPI

app = FastAPI(title="BizPartnerCheck API")


@app.get("/health")
def health_check():
    return {"status": "ok"}