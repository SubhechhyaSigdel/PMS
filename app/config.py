from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname:str
    database_port:str
    database_name:str
    database_password:str
    database_username:str
    secret_key:str
    algorithm:str
    expiration_time:int

    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings=Settings()