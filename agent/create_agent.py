"""
Create a Foundry Agent with MCP Tool for Football Statistics.

This script:
  1. Connects to the Microsoft Foundry project
  2. Registers the remote MCP server (Azure Functions) as a tool
  3. Creates an agent that can query football player stats
  4. Runs a test conversation
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
)

# ─── Configuration ──────────────────────────────────────────────────────────
FOUNDRY_ENDPOINT = os.environ.get(
    "FOUNDRY_ENDPOINT",
    "https://<your-foundry-resource>.services.ai.azure.com/api/projects/<your-project>",
)
MCP_SERVER_URL = os.environ.get(
    "MCP_SERVER_URL",
    "https://<your-function-app>.azurewebsites.net/runtime/webhooks/mcp",
)
MCP_SERVER_KEY = os.environ.get("MCP_SERVER_KEY")  # Required: mcp_extension system key
MODEL = "gpt-4.1-mini"


def main():
    # Authenticate
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=credential,
    )

    print("✅ Connected to Foundry project")

    # Define MCP tool pointing to the Azure Functions MCP server
    mcp_tool = MCPTool(
        server_label="football-stats",
        server_url=MCP_SERVER_URL,
        headers={"x-functions-key": MCP_SERVER_KEY},
        require_approval="never",
    )

    # Create the agent
    agent = project_client.agents.create_version(
        agent_name="football-scout-agent",
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions=(
                "You are a football (soccer) statistics expert. "
                "Use the MCP tools to search for players, get their stats, "
                "and compare players when asked. Always present data in a "
                "clear, readable format. When comparing players, highlight "
                "key differences and provide your analysis."
            ),
            tools=[mcp_tool],
        ),
    )

    print(f"✅ Agent created: {agent.id}")
    print(f"   Name: {agent.name}")
    print(f"   Version: {agent.version}")

    # Get OpenAI client for conversations
    openai_client = project_client.get_openai_client()

    # ─── Test conversation ──────────────────────────────────────────────
    test_messages = [
        "Who are the Polish players in your database?",
        "Get me detailed stats for Haaland",
        "Compare Lewandowski and Mbappé — who's having a better season?",
    ]

    conversation = None

    for user_msg in test_messages:
        print(f"\n{'='*60}")
        print(f"👤 User: {user_msg}")
        print(f"{'='*60}")

        if conversation is None:
            # Create a new conversation with the first message
            conversation = openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": user_msg}],
            )
        else:
            # Add follow-up messages
            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[{"type": "message", "role": "user", "content": user_msg}],
            )

        # Get response from agent
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "name": agent.name,
                    "type": "agent_reference",
                }
            },
        )

        print(f"🤖 Agent: {response.output_text}")

    # ─── Cleanup ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("🧹 Cleaning up...")
    openai_client.conversations.delete(conversation_id=conversation.id)
    project_client.agents.delete_version(
        agent_name=agent.name, agent_version=agent.version
    )
    print("✅ Agent and conversation deleted. Done!")


if __name__ == "__main__":
    main()
