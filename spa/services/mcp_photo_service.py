#!/usr/bin/env python3
# spa/services/mcp_photo_service.py - Test implementation

import sys
import json
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - MCP - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockMCPPhotoService:
    """Test MCP Photo Service - returns mock data"""
    
    def __init__(self):
        self.request_id = 0
        
    async def handle_initialize(self, params):
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": [
                    {
                        "name": "get_design_photos",
                        "description": "Generate context-aware photos for website designs"
                    }
                ]
            },
            "serverInfo": {
                "name": "mock-mcp-photo-service",
                "version": "1.0.0"
            }
        }
    
    async def handle_tool_call(self, params):
        """Handle tool call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "get_design_photos":
            return await self.generate_mock_photos(arguments)
        else:
            raise Exception(f"Unknown tool: {tool_name}")
    
    async def generate_mock_photos(self, arguments):
        """Generate mock photo data"""
        design_plan = arguments.get("design_plan", "")
        user_preferences = arguments.get("user_preferences", {})
        
        logger.info(f"Generating mock photos for plan length: {len(design_plan)}")
        logger.info(f"User preferences: {user_preferences}")
        
        # Mock photo data
        mock_photos = [
            {
                "section": "hero",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=600&fit=crop",
                        "quality_score": 0.9,
                        "context_match": 0.8,
                        "description": "Modern office workspace"
                    }
                ]
            },
            {
                "section": "about", 
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
                        "quality_score": 0.85,
                        "context_match": 0.9,
                        "description": "Professional portrait"
                    }
                ]
            },
            {
                "section": "portfolio",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&h=400&fit=crop",
                        "quality_score": 0.88,
                        "context_match": 0.85,
                        "description": "Creative project showcase"
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop",
                        "quality_score": 0.87,
                        "context_match": 0.82,
                        "description": "Development work"
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop",
                        "quality_score": 0.86,
                        "context_match": 0.80,
                        "description": "Business solution"
                    }
                ]
            },
            {
                "section": "services",
                "photos": [
                    {
                        "url": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=500&fit=crop",
                        "quality_score": 0.84,
                        "context_match": 0.78,
                        "description": "Technology services"
                    }
                ]
            }
        ]
        
        # Return in MCP format
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Generated {len(mock_photos)} photo sections for your design.\nJSON Data: {json.dumps(mock_photos)}"
                }
            ]
        }
    
    async def run(self):
        """Main MCP service loop"""
        logger.info("🚀 Mock MCP Photo Service starting...")
        
        try:
            while True:
                # Read JSON-RPC message from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    message = json.loads(line.strip())
                    logger.info(f"📥 Received: {message.get('method', 'unknown')}")
                    
                    # Handle different message types
                    method = message.get("method")
                    params = message.get("params", {})
                    request_id = message.get("id")
                    
                    if method == "initialize":
                        result = await self.handle_initialize(params)
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": result
                        }
                    elif method == "tools/call":
                        result = await self.handle_tool_call(params)
                        response = {
                            "jsonrpc": "2.0", 
                            "id": request_id,
                            "result": result
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                    
                    # Send response
                    response_json = json.dumps(response) + '\n'
                    sys.stdout.write(response_json)
                    sys.stdout.flush()
                    logger.info(f"📤 Sent response for: {method}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                except Exception as e:
                    logger.error(f"❌ Request handling error: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id") if 'message' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("🛑 Service interrupted")
        except Exception as e:
            logger.error(f"❌ Service error: {e}")
        finally:
            logger.info("🔚 Mock MCP Photo Service stopped")

if __name__ == "__main__":
    service = MockMCPPhotoService()
    asyncio.run(service.run())