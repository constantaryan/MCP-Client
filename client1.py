import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.messages import ToolMessage

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
}

async def main():
    client = MultiServerMCPClient(SERVERS) # hamesa client hi suru krta h server 
    tools = await client.get_tools() # isse humko saare tools mil jayenge

    named_tools = {}
    for tool in tools:
        named_tools[tool.name] = tool

    # print(named_tools) # we are just testing ki hamare tools kon konse h, simply tools ke naam ko dict m key bana diya h so that we
    # can easily access the tool names.

    llm = ChatMistralAI()
    llm_with_tools = llm.bind_tools(tools) # now our LLM is connected to tools so abb wo tools ko access krr skta h 

    prompt = "what is the Sum of 69 and 69?"
    response =await llm_with_tools.ainvoke(prompt) # we are only able to connect to the tools and tool ko apna input mil gya h but
    # tool se output generate nhi krwaya h abhi tkk

    # Handling if we have a llm call jisme tool use nhi hua h 
    # we are simply checking that if there is no attribute 'tool_calls' in response then not se True ho jaeyga then if condition m
    # enter krr jayenge
    if not getattr(response, "tool_calls",None):
        print(response.content)
        return
    
    selected_tool = response.tool_calls[0]["name"]
    selected_tools_args = response.tool_calls[0]["args"]
    selected_tool_id = response.tool_calls[0]["id"]
    # print(selected_tool)
    # print(selected_tools_args)
    tool_result = await named_tools[selected_tool].ainvoke(selected_tools_args)

    # print(tool_result)

    tool_message = ToolMessage(content=str(tool_result), tool_call_id = selected_tool_id)

    # prompt = it is still the same
    # response = ye initial response h jisme llm n pahchaan liya ki usko tool use krna h 
    # tool_message = tool n kya result diya usko tool_message m wrap krke bej rhe 

    final_response = await llm_with_tools.ainvoke([prompt, response, tool_message])
    print("LLM reply: ",final_response.content)

if __name__ == '__main__':
    asyncio.run(main())
