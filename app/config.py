from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/shop_agent?charset=utf8mb4"

    # JWT
    jwt_secret: str = "change-me-to-a-random-secret"
    jwt_expiry_hours: int = 24

    # DeepSeek
    deepseek_api_key: str = "sk-your-deepseek-api-key"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # SMTP
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 587
    smtp_username: str = "your-email@qq.com"
    smtp_password: str = "your-smtp-authorization-code"

    # CORS
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
