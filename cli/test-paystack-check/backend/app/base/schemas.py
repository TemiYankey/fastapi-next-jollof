from pydantic import BaseModel, ConfigDict


def to_camel_case(string: str) -> str:
    """Convert snake_case to camelCase."""
    acronyms = {"uuid", "api", "ip", "html", "css", "ai"}
    components = string.split("_")
    return components[0] + "".join(
        x.upper() if x in acronyms else x.capitalize() for x in components[1:]
    )


class BaseAppSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
        from_attributes=True,
    )
