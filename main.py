from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Calculator Server")


# Tool 1: Addition
@mcp.tool()
def add(a: float, b: float) -> float:
    """Return sum of two numbers"""
    return a + b


# Tool 2: Subtraction
@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Return subtraction of two numbers"""
    return a - b


# Tool 3: Multiplication
@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Return multiplication of two numbers"""
    return a * b


# Tool 4: Division
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Return division of two numbers"""
    if b == 0:
        return "Error: Division by zero"
    return a / b


if __name__ == "__main__":
    mcp.run()