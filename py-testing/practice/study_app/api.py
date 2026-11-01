from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from study_app.calculator import divide


class Division(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    a: float
    b: float


def create_app():
    app = FastAPI(title="Testing study API")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.post("/divide")
    def divide_numbers(body: Division):
        try:
            return {"result": divide(body.a, body.b)}
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return app


app = create_app()
