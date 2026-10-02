from pydantic import BaseModel, Field, HttpUrl


class RootOutSchema(BaseModel):
    title: str = Field(description="Title of the API.", examples=["Title of the API."])
    description: str = Field(
        description="Description of the API.", examples=["Description of the API."]
    )
    docs_url: HttpUrl = Field(
        description="URL to access docs documentation.",
        examples=["http://localhost:8000/docs"],
    )
    redoc_url: HttpUrl = Field(
        description="URL to access redoc documentation.",
        examples=["http://localhost:8000/redoc"],
    )
