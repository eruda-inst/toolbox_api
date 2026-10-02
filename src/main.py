from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl

from .api import api_v1_router
from .api.v1 import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's startup and shutdown lifecycle.

    This context manager runs when the FastAPI application starts and exits.
    It can be used to initialize and release shared resources, such as database
    connections, caches, or background task handlers.

    Args:
        app: The FastAPI application instance.
    """
    yield


app = FastAPI(
    title="Toolbox",
    description="Hub for centralizing tools used in Newnet.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_v1_router)


@app.get(path="/", summary="Get API metadata and documentation links.")
def root(request: Request) -> schemas.RootOutSchema:
    """
    Return basic API metadata and absolute documentation URLs.

    Builds the URLs for the interactive Swagger UI and ReDoc interfaces from the incoming request's base URL so they remain correct regardless of the host or reverse proxy used to access the API.
    """
    title = app.title
    description = app.description
    base_url = str(request.base_url).rstrip("/")
    docs_url = HttpUrl(base_url + str(app.docs_url))
    redoc_url = HttpUrl(base_url + str(app.redoc_url))
    return schemas.RootOutSchema(
        title=title, description=description, docs_url=docs_url, redoc_url=redoc_url
    )
