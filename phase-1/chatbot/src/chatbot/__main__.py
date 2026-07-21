"""CLI 聊天机器人入口。

启动方式：
    cd phase-1/chatbot
    cp .env.example .env  # 填入 API Key
    uv sync
    uv run python -m chatbot
"""

from __future__ import annotations

from rich.console import Console

from chatbot.config import Config
from chatbot.session import ChatSession

console = Console()


def main() -> None:
    """CLI 主循环：读输入 → 分发命令 → 流式输出。

    命令列表：/quit /clear /model <name>
    其他输入视为对话，走 stream_chat 流式输出。
    """
    config = Config()
    session = ChatSession(config)

    console.print("[bold green]CLI 聊天机器人[/]")
    console.print("命令：/quit 退出 | /clear 清空 | /model <name> 切换模型\n")

    while True:
        try:
            user_input = console.input("[bold blue]你>[/] ")
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input.strip():
            continue
        if user_input == "/quit":
            break
        if user_input == "/clear":
            session.clear()
            console.print("[dim]对话已清空[/]")
            continue
        if user_input.startswith("/model "):
            model = user_input[7:].strip()
            if not model:
                console.print("[red]用法：/model <name>，如 /model claude-sonnet-4-5-latest[/]")
                continue
            session.switch_model(model)
            console.print(f"[dim]已切换到模型: {model}[/]")
            continue

        try:
            console.print("[bold green]AI>[/] ", end="")
            # 流式打字机效果：逐 chunk 打印（纯文本）。
            # 不在流式过程中做 Markdown 渲染——跨 chunk 的不完整 Markdown 会渲染失败。
            # 想要"流式 + Markdown 渲染"需要用 rich.live.Live 实时刷新，留给 Week 5 升级。
            for chunk in session.stream_chat(user_input):
                console.print(chunk, end="")
            console.print()  # 换行
        except Exception as e:  # noqa: BLE001 —— CLI 顶层兜底，避免崩溃
            console.print(f"\n[red]错误: {e}[/]")

    console.print("\n[dim]再见！[/]")


if __name__ == "__main__":
    main()
