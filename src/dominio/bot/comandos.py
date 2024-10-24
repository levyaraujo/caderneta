from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
import inspect


@dataclass
class Comando:
    name: str
    handler: Callable
    description: str
    aliases: List[str] = None

    def __post_init__(self):
        self.aliases = self.aliases or []


class GerenciadorComandos:
    def __init__(self):
        self.commands: Dict[str, Comando] = {}
        self.prefix = "!"

    def command(self, name: str, description: str, aliases: List[str] = None):
        """Decorator to register commands"""

        def decorator(func: Callable):
            cmd = Comando(name, func, description, aliases)
            self.register_command(cmd)
            return func

        return decorator

    def register_command(self, command: Comando):
        """Register a command and its aliases"""
        self.commands[command.name] = command
        for alias in command.aliases or []:
            self.commands[alias] = command

    async def handle_message(self, message: str) -> Optional[str]:
        """Handle incoming messages and execute commands"""
        if not message.startswith(self.prefix):
            return None

        parts = message[len(self.prefix) :].strip().split()
        if not parts:
            return None

        command_name = parts[0].lower()
        args = parts[1:]

        command = self.commands.get(command_name)
        if not command:
            return f"Unknown command: {command_name}"

        try:
            if inspect.iscoroutinefunction(command.handler):
                return await command.handler(*args)
            return command.handler(*args)
        except Exception as e:
            return f"Error executing command {command_name}: {str(e)}"

    def get_help(self) -> str:
        """Generate help text listing all commands"""
        help_text = "Available commands:\n"
        unique_commands = {cmd.name: cmd for cmd in self.commands.values()}
        for cmd in unique_commands.values():
            aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_text += f"{self.prefix}{cmd.name}: {cmd.description}{aliases}\n"
        return help_text
