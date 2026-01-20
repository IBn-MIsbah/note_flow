from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    ALGORITHM: str = "HS256"
    ENVIRONMENT: str = "development"

    @property
    def COOKIE_SECURE(self) -> bool:  # type: ignore
        self.ENVIRONMENT == "production"  # type: ignore

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
