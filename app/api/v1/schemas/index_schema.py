from pydantic import BaseModel, HttpUrl, Field


class IndexOut(BaseModel):
    titulo: str = Field(
        description="Título da API exibido nas documentações docs e redoc",
        examples=["Lorem Ipsum"],
    )
    descricao: str = Field(
        description="Descrição da API exibida nas documentações docs e redoc",
        examples=["Lorem ipsum dolor sit amet"],
    )
    url_documentacao_docs: HttpUrl = Field(
        description="URL para acesso à documentação docs",
        examples=["http://localhost:8000/docs"],
    )
    url_documentacao_redoc: HttpUrl = Field(
        description="URL para acesso à documentação redoc",
        examples=["http://localhost:8000/redoc"],
    )
