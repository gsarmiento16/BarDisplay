from pydantic import BaseModel, ConfigDict, Field


class TelegramUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str | None = None


class TelegramChat(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    type: str | None = None


class TelegramPhotoSize(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    file_id: str
    file_unique_id: str | None = None
    width: int | None = None
    height: int | None = None
    file_size: int | None = None


class TelegramMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message_id: int
    date: int | None = None
    chat: TelegramChat
    text: str | None = None
    photo: list[TelegramPhotoSize] | None = None
    caption: str | None = None
    from_: TelegramUser | None = Field(default=None, alias="from")


class TelegramUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    update_id: int
    message: TelegramMessage | None = None
    edited_message: TelegramMessage | None = None
