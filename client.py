import os
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv(".environment")  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.messages = []
        self.anthropic = Anthropic()

    def get_anthropic_response(self, messages, **kwargs):
        model = kwargs.get("model", "claude-3-7-sonnet-20250219")
        result = self.anthropic.messages.create(
            model=model, messages=messages, **kwargs
        )
        return result

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = ".env/bin/python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str, max_tool_calls: int = 5) -> str:
        """Process a query using Claude and available tools"""
        self.messages.append({"role": "user", "content": query})

        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]

        done = False
        tool_calls = 0
        while not done and tool_calls < max_tool_calls:
            # logger.debug(f"{self.messages=}")
            response = self.get_anthropic_response(
                self.messages,
                tools=available_tools,
                max_tokens=1000,
            )
            # logger.info(f"Response: {response}")
            # Process response and handle tool calls
            done = True
            for content in response.content:
                if content.type == "text":
                    print(content.text + "\n")
                    self.messages.append({"role": "assistant", "content": content.text})
                elif content.type == "tool_use":
                    done = False  # If there is tool use continue
                    tool_name = content.name
                    tool_args = content.input
                    tool_use_id = content.id
                    current_content = []
                    # Continue conversation with tool results
                    if hasattr(content, "text") and content.text:
                        print(content.text + "\n")
                        current_content.append({"type": "text", "text": content.text})
                    current_content.append(
                        {
                            "type": "tool_use",
                            "id": tool_use_id,
                            "name": tool_name,
                            "input": tool_args,
                        }
                    )
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": current_content,
                        }
                    )
                    print(f"[Calling tool {tool_name} with args {tool_args}]")
                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    result_content = " ".join(
                        [content.text for content in result.content]
                    )

                    tool_calls += 1
                    #
                    if result_content:
                        self.messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": result_content,
                                    }
                                ],
                            }
                        )
                    else:
                        self.messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": "No response from tool",
                                    }
                                ],
                            }
                        )
                        done = True

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery => ").strip()

                if query.lower() == "quit":
                    break

                await self.process_query(query)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
