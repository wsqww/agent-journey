"""CLI 聊天机器人入口。

启动方式：
    cd phase-1/chatbot
    cp .env.example .env  # 填入 API Key
    uv sync
    uv run python -m chatbot
"""
import sys
from rich.console import Console
from chatbot.config import Config
from chatbot.session import ChatSession

console = Console()


def main():
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
            session.switch_model(model)
            console.print(f"[dim]已切换到模型: {model}[/]")
            continue

        try:
            console.print("[bold green]AI>[/] ", end="")
            for chunk in session.stream_chat(user_input):
                console.print(chunk, end="")
            console.print()
        except Exception as e:
            console.print(f"[red]错误: {e}[/]")

    console.print("\n[dim]再见！[/]")


if __name__ == "__main__":
    main()
