from .api.v1 import schemas
from pydantic import HttpUrl
from fastapi import FastAPI, Request

app = FastAPI(
    title="Toolbox API",
    description="API da plataforma de centralização de ferramentas utilizadas na Newnet",
    version="Mark I (0.7.3)",
)


@app.get(path="/", summary="Endpoint raíz da API")
def index(request: Request) -> schemas.IndexOut:
    """
    Retorna informações sobre a API, incluíndo URLs para documentações docs e redoc
    """
    title = app.title
    description = app.description
    base_url = str(request.base_url).rstrip("/")
    docs_url = HttpUrl(base_url + str(app.docs_url))
    redoc_url = HttpUrl(base_url + str(app.redoc_url))
    return schemas.IndexOut(
        titulo=title,
        descricao=description,
        url_documentacao_docs=docs_url,
        url_documentacao_redoc=redoc_url,
    )
