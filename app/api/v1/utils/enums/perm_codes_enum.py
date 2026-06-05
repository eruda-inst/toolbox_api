from enum import StrEnum


class PermCodes(StrEnum):
    CREATE_USERS = "criar:usuarios"
    READ_USERS = "ver:usuarios"
    UPDATE_USERS = "alterar:usuarios"
    DEL_USERS = "remover:usuarios"
