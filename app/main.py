from pydantic import HttpUrl
from fastapi.logger import logger
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from .api.v1 import schemas, api_v1_router, db as db_package, services


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler(timezone="America/Bahia")

    async def job_wrapper():
        try:
            async with db_package.SessionLocal() as db:
                await services.CleanupService.del_expired_blacklist_tokens(db)
        except Exception as e:
            logger.error(f"Erro na limpeza da blacklist: {e}")

    scheduler.add_job(  # type: ignore
        func=job_wrapper,
        trigger=IntervalTrigger(hours=24),
        id="cleanup_blacklist",
        replace_existing=True,
    )
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Toolbox API",
    description="API da plataforma de centralização de ferramentas utilizadas na Newnet",
    version="0.29.2",
    routes=api_v1_router.routes,
    lifespan=lifespan,
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
