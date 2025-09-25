#!/usr/bin/env python3
"""
K-Beauty Remote MCP Server - Simplified HTTP Version
Korean Beauty and Skincare Assistant with AI-Powered Analysis
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="K-Beauty Remote MCP Server", version="3.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# K-Beauty 도구 정의
KBEAUTY_TOOLS = [
    {
        "name": "analyze_skin_from_photo",
        "description": "Comprehensive AI-powered skin analysis from photo using Claude's vision capabilities. Analyzes skin tone, pigmentation, acne, blackheads, pores, texture, and provides personalized K-Beauty solutions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_description": {
                    "type": "string",
                    "description": "User should upload an image and Claude will analyze it. This field is for any additional context about the photo (lighting conditions, skin concerns to focus on, etc.)"
                },
                "skin_type_self_assessment": {
                    "type": "string",
                    "enum": ["oily", "dry", "combination", "sensitive", "normal", "unknown"],
                    "description": "User's own assessment of their skin type"
                },
                "user_age": {
                    "type": "number",
                    "description": "User's age for age-appropriate recommendations"
                },
                "analysis_focus": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["skin_tone", "pigmentation", "acne", "blackheads", "pores", "texture", "wrinkles", "dark_circles", "overall_condition"]
                    },
                    "description": "Specific aspects to focus on during analysis"
                }
            },
            "required": ["image_description"]
        }
    },
    {
        "name": "search_kbeauty_brands",
        "description": "Search for K-Beauty brands and get comprehensive brand information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "description": "The K-Beauty brand name to search for"
                }
            },
            "required": ["brand_name"]
        }
    },
    {
        "name": "recommend_routine",
        "description": "Get personalized K-Beauty skincare routine recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skin_type": {
                    "type": "string",
                    "enum": ["oily", "dry", "combination", "sensitive", "normal"],
                    "description": "Primary skin type"
                },
                "skin_concerns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of skin concerns"
                },
                "budget": {
                    "type": "string",
                    "enum": ["budget", "mid-range", "luxury", "mixed"],
                    "description": "Budget preference"
                }
            },
            "required": ["skin_type"]
        }
    },
    {
        "name": "analyze_ingredients",
        "description": "Analyze skincare ingredients and their benefits",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ingredients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ingredients to analyze"
                },
                "skin_type": {
                    "type": "string",
                    "enum": ["oily", "dry", "combination", "sensitive", "normal"],
                    "description": "Skin type for compatibility assessment"
                }
            },
            "required": ["ingredients"]
        }
    },
    {
        "name": "product_comparison",
        "description": "Compare K-Beauty products",
        "inputSchema": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of products to compare"
                },
                "comparison_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Criteria for comparison (price, ingredients, effectiveness, etc.)"
                }
            },
            "required": ["products"]
        }
    },
    {
        "name": "kbeauty_trends",
        "description": "Analyze current K-Beauty trends",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trend_type": {
                    "type": "string",
                    "enum": ["ingredients", "brands", "products", "techniques"],
                    "description": "Type of trend analysis"
                },
                "time_period": {
                    "type": "string",
                    "enum": ["current", "2024", "2025", "emerging"],
                    "description": "Time period for trend analysis"
                }
            },
            "required": ["trend_type"]
        }
    },
    {
        "name": "seasonal_skincare_guide",
        "description": "Get season-specific K-Beauty recommendations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "enum": ["spring", "summer", "fall", "winter"],
                    "description": "Current season"
                },
                "skin_type": {
                    "type": "string",
                    "enum": ["oily", "dry", "combination", "sensitive", "normal"],
                    "description": "Skin type"
                },
                "climate": {
                    "type": "string",
                    "enum": ["humid", "dry", "temperate", "tropical"],
                    "description": "Local climate type"
                }
            },
            "required": ["season", "skin_type"]
        }
    },
    {
        "name": "dupes_finder",
        "description": "Find affordable alternatives for expensive K-Beauty products",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_product": {
                    "type": "string",
                    "description": "Expensive product to find dupes for"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price for dupe products"
                }
            },
            "required": ["target_product"]
        }
    },
    {
        "name": "skin_concern_matcher",
        "description": "Match specific skin concerns with effective K-Beauty ingredients and products",
        "inputSchema": {
            "type": "object",
            "properties": {
                "concerns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific skin concerns"
                },
                "severity": {
                    "type": "string",
                    "enum": ["mild", "moderate", "severe"],
                    "description": "Severity level of concerns"
                }
            },
            "required": ["concerns"]
        }
    }
]

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "k-beauty-remote-mcp", "version": "3.0.0"}

async def handle_mcp_request(request: MCPRequest) -> MCPResponse:
    """Handle MCP requests"""
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "k-beauty-complete",
                        "version": "3.0.0"
                    }
                }
            )
        
        elif request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={"tools": KBEAUTY_TOOLS}
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            # K-Beauty 도구 실행 시뮬레이션
            result = await execute_kbeauty_tool(tool_name, arguments)
            
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            )
        
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
            )
            
    except Exception as e:
        return MCPResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )

async def execute_kbeauty_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute K-Beauty tools with mock responses"""
    
    if tool_name == "analyze_skin_from_photo":
        return """🧴 AI 피부 분석 결과

📸 이미지 분석:
• 피부톤: 밝은 웜톤 (Warm Light)
• 피부타입: 복합성 피부 (T존 지성, 볼 건성)
• 주요 고민: 모공, 약간의 색소침착

🎯 K-Beauty 추천:
• 클렌징: 이니스프리 그린티 클렌징폼
• 토너: 원더미라클 패치토너
• 세럼: 더오디너리 니아신아마이드 10%
• 보습: 라로슈포제 에파클라 듀오

✨ 추천 루틴:
아침: 순한 클렌징 → 토너 → 비타민C 세럼 → 선크림
저녁: 더블 클렌징 → 토너 → 니아신아마이드 → 보습크림"""

    elif tool_name == "search_kbeauty_brands":
        brand = arguments.get("brand_name", "Unknown")
        return f"""🏷️ {brand} 브랜드 정보

📋 브랜드 개요:
• 설립연도: 2013년
• 본사: 영국 (K-Beauty 영향받은 글로벌 브랜드)
• 특징: 합리적 가격의 효과적인 성분 중심

🧪 주력 제품:
• 니아신아마이드 10% + 징크 1%
• 하이알루로닉애씨드 2% + B5
• AHA 30% + BHA 2% 필링솔루션
• 레티노이드 제품군

💰 가격대: 1만-3만원 (매우 합리적)
🌟 평점: 4.3/5.0 (글로벌 뷰티 커뮤니티)"""

    elif tool_name == "recommend_routine":
        skin_type = arguments.get("skin_type", "normal")
        return f"""🌟 {skin_type} 피부 맞춤 K-Beauty 루틴

🌅 모닝 루틴:
1. 클렌징: 코스알엑스 굿모닝 젤클렌저
2. 토너: 토르든 히알루로닉애씨드 토너
3. 세럼: 미샤 비타C 플러스 스팟 코렉팅&페이딩 세럼
4. 보습: 토르든 세라마이드 크림
5. 선크림: 뷰티오브조선 선크림

🌙 이브닝 루틴:
1. 클렌징오일: DHC 딥클렌징오일
2. 폼클렌징: 세타필 젠틀 폼클렌저
3. 토너: 토르든 히알루로닉애씨드 토너
4. 세럼: 더오디너리 니아신아마이드 (주 3회)
5. 보습: 일리윤 세라마이드 아토 로션

💡 주간 스페셜 케어:
• 화: BHA 각질케어 (토르든 살리실릭애씨드)
• 금: 마스크팩 (메디힐 N.M.F 아쿠아링)"""

    elif tool_name == "analyze_ingredients":
        ingredients = arguments.get("ingredients", [])
        return f"""🧪 성분 분석 결과

📊 분석된 성분: {', '.join(ingredients[:5])}

🔬 주요 성분 효능:
• 니아신아마이드: 모공 축소, 유수분 밸런스, 브라이트닝
• 하이알루로닉애씨드: 강력한 보습, 수분 보유력 향상
• 세라마이드: 피부장벽 강화, 수분 손실 방지

⚠️ 주의사항:
• 레티놀 + AHA/BHA 동시 사용 주의
• 비타민C + 니아신아마이드 농도 확인 필요
• 새로운 성분은 패치 테스트 권장

💡 추천 조합:
아침: 항산화제 (비타민C) + 선크림
저녁: 각질케어 (AHA/BHA) or 레티놀 (번갈아 사용)"""

    elif tool_name == "kbeauty_trends":
        return """📈 2024-2025 K-Beauty 트렌드

🔥 인기 성분:
• 센텔라 아시아티카 (진정, 항염)
• 스네일 세크리션 (재생, 보습)
• 프로폴리스 (항균, 진정)
• 글루타티온 (브라이트닝)

🌟 트렌드 제품:
• 글래스 스킨 베이스 메이크업
• 멀티 레이어링 보습 시스템
• 개인 맞춤형 스킨케어
• 친환경 패키징

💫 새로운 브랜드들:
• 토르든 (Torriden)
• 라운드랩 (Round Lab)
• 미녹시딜 (Minoxidil) - 헤어케어
• 퍼미들 (Purmild)

🎯 2025 전망:
AI 기반 피부 분석, 개인 맞춤형 제품이 대세가 될 전망"""

    else:
        return f"K-Beauty 도구 '{tool_name}' 실행 완료! 자세한 분석을 위해 Claude에게 문의하세요."

@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Main MCP endpoint for HTTP requests"""
    response = await handle_mcp_request(request)
    return response.dict()

@app.get("/mcp")
async def mcp_sse_endpoint(request: Request):
    """MCP endpoint for Server-Sent Events"""
    async def event_stream():
        session_id = str(uuid.uuid4())
        
        # 초기화 메시지
        init_data = {
            "jsonrpc": "2.0",
            "id": "init",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "k-beauty-complete", "version": "3.0.0"}
            }
        }
        
        yield f"data: {json.dumps(init_data)}\n\n"
        
        # Keep connection alive
        while True:
            yield f"data: {json.dumps({'ping': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(30)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
