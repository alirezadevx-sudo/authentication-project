from pydantic_settings import BaseSettings, SettingsConfigDict

class CoreSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

core_settings = CoreSettings()