from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import SecretStr


class DBSettings(BaseSettings):
    DB_URL: SecretStr
    
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

db_settings = DBSettings()

