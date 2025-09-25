#!/usr/bin/env python3
"""
K-Beauty Remote MCP Server - HTTP/SSE Version
Korean Beauty and Skincare Assistant with AI-Powered Photo Analysis
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import original MCP tools
from server import server as mcp_server

app = FastAPI(title="K-Beauty Remote MCP Server", version="3.0.0")

# CORS 설정 (배포 시 필요한 도메인으로 제한)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 구체적인 도메인으로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Any
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Any
    result: Any = None
    error: Dict[str, Any] = None

# 세션 관리
sessions = {}

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "k-beauty-remote-mcp", "version": "3.0.0"}

@app.get("/mcp")
async def mcp_sse_endpoint(request: Request):
    """MCP Server-Sent Events (SSE) endpoint for initialization"""
    
    # 세션 생성
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created_at": datetime.utcnow(),
        "tools": None,
        "capabilities": None
    }
    
    async def event_generator():
        # 초기화 메시지
        init_message = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "logging": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "k-beauty-complete",
                    "version": "3.0.0"
                }
            }
        }
        
        # SSE 포맷으로 전송
        yield f"data: {json.dumps(init_message)}\n\n"
        
        # Keep connection alive
        while True:
            # 연결 유지를 위한 heartbeat
            heartbeat = {
                "jsonrpc": "2.0",
                "method": "notifications/heartbeat",
                "params": {"timestamp": datetime.utcnow().isoformat()}
            }
            yield f"data: {json.dumps(heartbeat)}\n\n"
            await asyncio.sleep(30)  # 30초마다 heartbeat
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Mcp-Session-Id": session_id
        }
    )

@app.post("/mcp")
async def mcp_streamable_http_endpoint(request: Request):
    """MCP Streamable HTTP endpoint (새로운 표준)"""
    
    try:
        # 요청 파싱
        body = await request.json()
        mcp_request = MCPRequest(**body)
        
        # 세션 ID 확인
        session_id = request.headers.get("Mcp-Session-Id")
        if not session_id:
            session_id = str(uuid.uuid4())
            sessions[session_id] = {"created_at": datetime.utcnow()}
        
        # 요청 처리
        result = await handle_mcp_request(mcp_request, session_id)
        
        response = MCPResponse(id=mcp_request.id, result=result)
        
        return JSONResponse(
            content=response.dict(exclude_none=True),
            headers={"Mcp-Session-Id": session_id}
        )
        
    except Exception as e:
        error_response = MCPResponse(
            id=getattr(mcp_request, 'id', None),
            error={
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        )
        return JSONResponse(
            content=error_response.dict(exclude_none=True),
            status_code=500
        )

@app.post("/messages")
async def mcp_messages_endpoint(request: Request):
    """MCP Messages endpoint (레거시 HTTP+SSE 지원)"""
    return await mcp_streamable_http_endpoint(request)

async def handle_mcp_request(request: MCPRequest, session_id: str) -> Any:
    """MCP 요청 처리"""
    
    if request.method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "logging": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": "k-beauty-complete", 
                "version": "3.0.0"
            }
        }
    
    elif request.method == "tools/list":
        # 원본 MCP 서버에서 도구 목록 가져오기
        tools = await get_tools_from_original_server()
        return {"tools": tools}
    
    elif request.method == "tools/call":
        # 도구 호출
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        # 원본 MCP 서버에서 도구 실행
        result = await call_tool_from_original_server(tool_name, arguments)
        return {"content": result}
    
    elif request.method == "ping":
        return {"status": "pong"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")

async def get_tools_from_original_server() -> List[Dict]:
    """원본 MCP 서버에서 도구 목록 가져오기"""
    
    # 원본 서버의 list_tools 함수 호출
    tools = await mcp_server.list_tools()
    
    # MCP 프로토콜 형식으로 변환
    mcp_tools = []
    for tool in tools:
        mcp_tool = {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        }
        mcp_tools.append(mcp_tool)
    
    return mcp_tools

async def call_tool_from_original_server(tool_name: str, arguments: Dict[str, Any]) -> List[Dict]:
    """원본 MCP 서버에서 도구 실행"""
    
    # 원본 서버의 call_tool 함수 호출
    result = await mcp_server.call_tool(tool_name, arguments)
    
    # TextContent를 딕셔너리로 변환
    content = []
    for item in result:
        content.append({
            "type": item.type,
            "text": item.text
        })
    
    return content

# OAuth 관련 엔드포인트 (선택사항)
@app.get("/.well-known/oauth-authorization-server")
async def oauth_discovery():
    """OAuth discovery endpoint"""
    return {
        "authorization_endpoint": f"{request.url_for('oauth_authorize')}",
        "token_endpoint": f"{request.url_for('oauth_token')}",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
