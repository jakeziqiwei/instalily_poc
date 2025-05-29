import json
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.services.agent_runner import handle_tool_call
from src.services.llm import LLM
from src.agents.criticAgent import CriticAgent

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm = LLM()
critic = CriticAgent()


class ChatRequest(BaseModel):
    message: str
    user_id: str = "user123"
    conversation_history: list = []


class ChatResponse(BaseModel):
    response: str
    tools_used: list = []


@app.get("/")
def read_root():
    return {"status": "running"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Prepare conversation with recent context
        recent_history = request.conversation_history[-2:
                                                      ] if request.conversation_history else []
        conversation = recent_history + \
            [{"role": "user", "content": request.message}]

        # Get LLM response
        response = await llm.ask_llm(conversation)
        tools_used = []
        final_response = ""

        # Handle tool calls
        if response.choices and response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tools_used.append(tool_name)

            # Execute tool
            tool_result = await handle_tool_call(tool_name, tool_args)

            if tool_result and not tool_result.get('error'):
                # For structured responses (like troubleshooting), pass the message directly
                if isinstance(tool_result, dict) and "message" in tool_result:
                    final_response = await critic.run(tool_result["message"])
                else:
                    final_response = await critic.run(str(tool_result))
            else:
                final_response = tool_result.get(
                    'message', "No results found. Please try a different search.")
        else:
            final_response = response.choices[0].message.content if response.choices else "I couldn't understand your request."

        return ChatResponse(
            response=final_response or "Please try rephrasing your request.",
            tools_used=tools_used
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid tool arguments")
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(
            status_code=500, detail="Service temporarily unavailable")
