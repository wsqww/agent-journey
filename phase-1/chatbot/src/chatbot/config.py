"""配置管理——从环境变量 / .env 文件加载。

任务：完善 Config 类，支持 OpenAI 和 Anthropic 的切换。

参考实现说明：
    本文件提供一份可运行的参考实现，确保 ChatSession 能拿到合法的 API Key。
    若 Key 缺失，会在这里就抛出明确错误，而不是等 LLM 调用失败再返回模糊错误。
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """应用配置，自动从环境变量 / .env 文件加载。

    使用方式：
        config = Config()
        print(config.default_model)

    字段映射（环境变量名大小写不敏感）：
        - OPENAI_API_KEY    -> openai_api_key
        - ANTHROPIC_API_KEY -> anthropic_api_key
        - DEFAULT_MODEL     -> default_model
        - MAX_TOKENS        -> max_tokens
        - TEMPERATURE       -> temperature
    """

    # 允许空字符串占位（.env.example 用了占位符），但运行时会被校验
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_model: str = "gpt-5-latest"
    max_tokens: int = 1000
    temperature: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("openai_api_key", "anthropic_api_key")
    @classmethod
    def _strip_whitespace(cls, v: str) -> str:
        """去掉复制粘贴时常见的首尾空白，避免 'sk-xxx ' 这类难排查的报错。"""
        return v.strip()

    @field_validator("temperature")
    @classmethod
    def _check_temperature(cls, v: float) -> float:
        """temperature 合法范围是 [0.0, 2.0]，越界 SDK 会报错，这里提前拦截。"""
        if not 0.0 <= v <= 2.0:
            raise ValueError(f"temperature 必须在 [0.0, 2.0] 之间，当前值: {v}")
        return v

    def require_openai(self) -> str:
        """返回 OpenAI API Key；若缺失则抛错。

        前端类比：类似组件渲染前断言 props 必填——尽早失败、错误信息清晰。
        """
        if not self.openai_api_key or self.openai_api_key.startswith("sk-your"):
            raise ValueError(
                "未配置 OPENAI_API_KEY。请在 .env 中填入真实 Key（参考 .env.example）。"
            )
        return self.openai_api_key

    def require_anthropic(self) -> str:
        """返回 Anthropic API Key；若缺失则抛错。"""
        if not self.anthropic_api_key or self.anthropic_api_key.startswith("sk-ant-your"):
            raise ValueError(
                "未配置 ANTHROPIC_API_KEY。请在 .env 中填入真实 Key（参考 .env.example）。"
            )
        return self.anthropic_api_key
