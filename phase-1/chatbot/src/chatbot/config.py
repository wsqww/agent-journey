"""配置管理——从环境变量 / .env 文件加载。

任务：完善 Config 类，支持 OpenAI 和 Anthropic 的切换。
"""
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """应用配置，自动从环境变量 / .env 文件加载。

    使用方式：
        config = Config()
        print(config.openai_api_key)
    """
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_model: str = "gpt-5-latest"
    max_tokens: int = 1000
    temperature: float = 0.7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
