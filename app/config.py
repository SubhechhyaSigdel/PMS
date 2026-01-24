from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #database configuration

    database_hostname:str
    database_port:str
    database_name:str
    database_password:str
    database_username:str

    #jwt/auth configuration
    secret_key:str
    algorithm:str
    expiration_time:int

    class Config:
        env_file = ".env"

settings=Settings()