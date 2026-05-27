"""DeepSeek-powered recommendation agent with function calling.

Handles DeepSeek's thinking mode (reasoning_content) properly.
"""

import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "searchProducts",
            "description": "Search for esports products by category, keyword, or price range",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoryId": {"type": "integer", "description": "Category ID (1=鼠标, 2=键盘, 3=耳机, 4=鼠标垫, 5=电竞椅)"},
                    "keyword": {"type": "string", "description": "Search keyword in product name"},
                    "minPrice": {"type": "number", "description": "Minimum price"},
                    "maxPrice": {"type": "number", "description": "Maximum price"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getUserBrowseHistory",
            "description": "Get the current user's recent browse history",
            "parameters": {
                "type": "object",
                "properties": {
                    "userId": {"type": "integer", "description": "User ID"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                },
                "required": ["userId"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getHotProducts",
            "description": "Get currently hot/trending products",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoryId": {"type": "integer", "description": "Optional category filter"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compareProducts",
            "description": "Compare two products side by side",
            "parameters": {
                "type": "object",
                "properties": {
                    "spuId1": {"type": "integer", "description": "First product SPU ID"},
                    "spuId2": {"type": "integer", "description": "Second product SPU ID"},
                },
                "required": ["spuId1", "spuId2"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are an esports equipment recommendation expert specializing in mice, keyboards, headsets, mousepads, and gaming chairs.
Rules:
- Understand user's game type (FPS/MOBA/MMO), hand size, budget, usage habits
- Call tools to search matching products
- Compare products highlighting key differences (sensor, switch, weight, connectivity)
- Answer concisely with specific reasons
- Do NOT recommend non-esports products
- Do NOT fabricate prices or specs
- Do NOT answer questions outside esports equipment expertise"""


async def _execute_tool_call(name: str, args: dict, user_id: int | None) -> str:
    """Execute a tool call and return the result as a string."""
    async with AsyncSessionLocal() as db:
        from app.services.agent_tools import (
            search_products_tool,
            get_user_browse_history_tool,
            get_hot_products_tool,
            compare_products_tool,
        )

        if name == "searchProducts":
            return await search_products_tool(
                db,
                category_id=args.get("categoryId"),
                keyword=args.get("keyword"),
                min_price=args.get("minPrice"),
                max_price=args.get("maxPrice"),
                limit=args.get("limit", 10),
            )
        elif name == "getUserBrowseHistory":
            return await get_user_browse_history_tool(
                db,
                user_id=args.get("userId", user_id),
                limit=args.get("limit", 10),
            )
        elif name == "getHotProducts":
            return await get_hot_products_tool(
                db,
                category_id=args.get("categoryId"),
                limit=args.get("limit", 10),
            )
        elif name == "compareProducts":
            return await compare_products_tool(
                db,
                spu_id_1=args["spuId1"],
                spu_id_2=args["spuId2"],
            )
    return f"Unknown tool: {name}"


async def chat_with_recommend_agent(
    message: str,
    user_id: int | None = None,
) -> str:
    """Send a message to the DeepSeek recommendation agent with function calling.

    Uses model_dump() for full message fidelity when handling tool calls,
    preserving DeepSeek-specific fields like reasoning_content.
    """
    try:
        client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        # Loop to handle multiple rounds of tool calling
        max_rounds = 8
        for _ in range(max_rounds):
            response = await client.chat.completions.create(
                model=settings.deepseek_model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2048,
            )

            choice = response.choices[0]
            reply_message = choice.message

            # No more tool calls — final answer
            if not reply_message.tool_calls:
                return reply_message.content or ""

            # Handle tool calls
            assistant_msg = reply_message.model_dump(exclude_none=True)
            assistant_msg.pop("refusal", None)
            messages.append(assistant_msg)

            for tc in reply_message.tool_calls:
                args = json.loads(tc.function.arguments)
                result = await _execute_tool_call(tc.function.name, args, user_id)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        return "I'm sorry, I couldn't complete the recommendation in the allotted steps."

    except Exception as e:
        logger.error(f"Recommend agent error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"
