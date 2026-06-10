from pydantic import HttpUrl
from fastapi import FastAPI, Request
from .api.v1 import schemas, api_v1_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Toolbox API",
    description="API da plataforma de centralização de ferramentas utilizadas na Newnet",
    version="Mark I (0.27.1)",
    routes=api_v1_router.routes,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
