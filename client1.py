import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.messages import ToolMessage
import json

load_dotenv()

SERVERS = { 
    "math": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "C:/Users/aryan/OneDrive/Desktop/mcp-client/main.py"
       ]
    }
    ,
    "expense": {
        "transport": "streamable_http",  # if this fails, try "sse"
        "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
    },
    "manim-server": {
        "transport": "stdio",
        "command": "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
        "args": [
        "/Users/nitish/desktop/manim-mcp-server/src/manim_server.py"
      ],
        "env": {
        "MANIM_EXECUTABLE": "/Library/Frameworks/Python.framework/Versions/3.11/bin/manim"
      }
    }
}

async def main():
    client = MultiServerMCPClient(SERVERS) # hamesa client hi suru krta h server 
    tools = await client.get_tools() # isse humko saare tools mil jayenge

    named_tools = {}
    for tool in tools:
        named_tools[tool.name] = tool

    # print(named_tools) # we are just testing ki hamare tools kon konse h, simply tools ke naam ko dict m key bana diya h so that we
    # can easily access the tool names.
    print('available tools:', named_tools.keys())
    
    llm = ChatMistralAI()
    llm_with_tools = llm.bind_tools(tools) # now our LLM is connected to tools so abb wo tools ko access krr skta h 

    prompt = "What is the capital of srilanka?"
    response =await llm_with_tools.ainvoke(prompt) # we are only able to connect to the tools and tool ko apna input mil gya h but
    # tool se output generate nhi krwaya h abhi tkk

    # Handling if we have a llm call jisme tool use nhi hua h 
    # we are simply checking that if there is no attribute 'tool_calls' in response then not se True ho jaeyga then if condition m
    # enter krr jayenge
    if not getattr(response, "tool_calls",None):
        print(response.content)
        return
    
    # Handling Multiple Tool Calls
    # Simply each tool ko call krke ek list m store krr rhe h 
    tool_messages = []
    for tc in response.tool_calls:
        selected_tool = tc['name']
        selected_tool_args = tc.get('args') or {}
        selected_tool_id = tc['id']

        result = await named_tools[selected_tool].ainvoke(selected_tool_args)
        tool_messages.append(ToolMessage(tool_call_id = selected_tool_id, content=json.dumps(result)))
    
    # selected_tool = response.tool_calls[0]["name"]
    # selected_tools_args = response.tool_calls[0]["args"]
    # selected_tool_id = response.tool_calls[0]["id"]
    # print(selected_tool)
    # print(selected_tools_args)
    # tool_result = await named_tools[selected_tool].ainvoke(selected_tools_args)

    # print(tool_result)

    # tool_message = ToolMessage(content=str(tool_result), tool_call_id = selected_tool_id)

    # prompt = it is still the same
    # response = ye initial response h jisme llm n pahchaan liya ki usko tool use krna h 
    # tool_message = tool n kya result diya usko tool_message m wrap krke bej rhe 

    final_response = await llm_with_tools.ainvoke([prompt, response, *tool_messages])
    print("LLM reply: ",{final_response.content})



if __name__ == '__main__':
    asyncio.run(main())
