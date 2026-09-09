from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuracoes da aplicacao, carregadas de variaveis de ambiente (.env).
    Usar pydantic-settings garante validacao de tipos e falha rapida
    caso uma variavel obrigatoria esteja ausente.
    """

    app_name: str = "NEXUS - Intelligent Process & Risk Platform"
    environment: str = "development"

    # Banco de dados: SQLite agora, PostgreSQL no futuro,
    # trocando apenas esta string de conexao.
    database_url: str = "sqlite:///./nexus.db"

    # Autenticacao JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
