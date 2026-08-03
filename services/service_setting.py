from pydantic_settings import SettingsConfigDict, BaseSettings

class ServiceSetting(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    RESEND_API_KEY: str

service_setting = ServiceSetting()