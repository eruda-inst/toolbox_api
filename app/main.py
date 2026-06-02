from .api.v1 import schemas
from pydantic import HttpUrl
from fastapi import FastAPI, Request

app = FastAPI(
    title="Toolbox API",
    description="API da plataforma de centralização de ferramentas utilizadas na Newnet",
    version="Mark I (0.1.1)",
)


@app.get(path="/", summary="Endpoint raíz da API")
def index(request: Request) -> schemas.IndexOut:
    """
    Retorna informações sobre a API, incluíndo URLs para documentações docs e redoc
    """
    titulo = app.title
    descricao = app.description
    base_url = str(request.base_url).rstrip("/")
    url_documentacao_docs = HttpUrl(base_url + str(app.docs_url))
    url_documentacao_redoc = HttpUrl(base_url + str(app.redoc_url))
    return schemas.IndexOut(
        titulo=titulo,
        descricao=descricao,
        url_documentacao_docs=url_documentacao_docs,
        url_documentacao_redoc=url_documentacao_redoc,
    )
