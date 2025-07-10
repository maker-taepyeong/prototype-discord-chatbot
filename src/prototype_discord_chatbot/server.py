from fastmcp import FastMCP

# AI 서버 만들기
# Note: sessionId 오류 우회하기 위해 플래그 추가
mcp = FastMCP("안녕 MCP!!", stateless_http=True)

@mcp.tool()
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다"""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")