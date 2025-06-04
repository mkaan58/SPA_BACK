# spa/services/mcp_photo_client.py
import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from django.conf import settings
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class MCPPhotoServiceClient:
    """
    MCP Photo Service ile iletişim kuran client sınıfı
    Context-aware fotoğrafları Django backend'e entegre eder
    """
    
    def __init__(self):
        self.mcp_process = None
        self.mcp_stdin = None
        self.mcp_stdout = None
        self.request_id = 0
        self.is_connected = False
        self.max_connection_attempts = 3
        self.connection_timeout = 10
        
    async def connect(self):
        """MCP servisine bağlan - Geliştirilmiş hata yönetimi ile"""
        for attempt in range(self.max_connection_attempts):
            try:
                logger.info(f"🔌 MCP connection attempt {attempt + 1}/{self.max_connection_attempts}")
                
                # MCP service script path'ini bul
                mcp_script_path = self._find_mcp_script()
                if not mcp_script_path:
                    raise Exception("MCP service script not found")
                
                logger.info(f"📍 Found MCP script at: {mcp_script_path}")
                
                # MCP servisini subprocess olarak başlat
                self.mcp_process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        sys.executable, mcp_script_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=os.path.dirname(mcp_script_path)
                    ),
                    timeout=self.connection_timeout
                )
                
                self.mcp_stdin = self.mcp_process.stdin
                self.mcp_stdout = self.mcp_process.stdout
                
                # Initialize bağlantısı - timeout ile
                await asyncio.wait_for(
                    self._send_initialize(),
                    timeout=5.0
                )
                
                self.is_connected = True
                logger.info("✅ MCP Photo Service connected successfully")
                return True
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ MCP connection timeout on attempt {attempt + 1}")
                await self._cleanup_connection()
            except Exception as e:
                logger.warning(f"⚠️ MCP connection failed on attempt {attempt + 1}: {e}")
                await self._cleanup_connection()
                
                if attempt == self.max_connection_attempts - 1:
                    logger.error("❌ All MCP connection attempts failed")
                    raise Exception(f"MCP connection failed after {self.max_connection_attempts} attempts")
                    
                # Wait before retry
                await asyncio.sleep(1 * (attempt + 1))
        
        return False
    
    def _find_mcp_script(self) -> Optional[str]:
        """MCP service script'inin yerini bul"""
        
        # Olası lokasyonlar
        possible_paths = [
            # Django project içinde
            os.path.join(settings.BASE_DIR, 'spa', 'services', 'mcp_photo_service.py'),
            os.path.join(settings.BASE_DIR, 'mcp_photo_service.py'),
            os.path.join(settings.BASE_DIR, 'services', 'mcp_photo_service.py'),
            
            # Virtual environment içinde
            os.path.join(os.path.dirname(sys.executable), 'mcp_photo_service.py'),
            
            # Settings'ten custom path
            getattr(settings, 'MCP_SCRIPT_PATH', None),
        ]
        
        for path in possible_paths:
            if path and os.path.isfile(path):
                logger.info(f"📁 Found MCP script: {path}")
                return path
        
        logger.error("❌ MCP script not found in any expected location")
        logger.info(f"🔍 Searched locations: {[p for p in possible_paths if p]}")
        return None
    
    async def _cleanup_connection(self):
        """Bağlantı temizliği"""
        try:
            if self.mcp_process:
                self.mcp_process.terminate()
                try:
                    await asyncio.wait_for(self.mcp_process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    self.mcp_process.kill()
                    await self.mcp_process.wait()
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
        finally:
            self.mcp_process = None
            self.mcp_stdin = None
            self.mcp_stdout = None
            self.is_connected = False
    
    async def disconnect(self):
        """MCP servisinden bağlantıyı kes"""
        logger.info("🔌 Disconnecting from MCP service...")
        await self._cleanup_connection()
        logger.info("✅ MCP service disconnected")
    
    async def _send_initialize(self):
        """MCP initialize protokolü - Geliştirilmiş"""
        init_message = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "django-spa-app",
                    "version": "1.0.0"
                }
            }
        }
        
        await self._send_message(init_message)
        response = await self._read_response()
        
        if "error" in response:
            raise Exception(f"MCP initialize failed: {response['error']}")
            
        logger.info(f"🚀 MCP initialized successfully: {response.get('result', {}).get('protocolVersion', 'unknown')}")
    
    async def _send_message(self, message: Dict):
        """MCP'ye mesaj gönder - Geliştirilmiş hata yönetimi"""
        if not self.mcp_stdin:
            raise Exception("MCP not connected - stdin unavailable")
        
        try:
            message_json = json.dumps(message) + '\n'
            self.mcp_stdin.write(message_json.encode('utf-8'))
            await self.mcp_stdin.drain()
            logger.debug(f"📤 Sent MCP message: {message.get('method', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Failed to send MCP message: {e}")
            self.is_connected = False
            raise Exception(f"MCP message send failed: {e}")
    
    async def _read_response(self) -> Dict:
        """MCP'den yanıt oku - Geliştirilmiş hata yönetimi"""
        if not self.mcp_stdout:
            raise Exception("MCP not connected - stdout unavailable")
        
        try:
            # Timeout ile line okuma
            line_bytes = await asyncio.wait_for(
                self.mcp_stdout.readline(), 
                timeout=10.0
            )
            
            if not line_bytes:
                raise Exception("MCP process ended unexpectedly")
            
            line = line_bytes.decode('utf-8').strip()
            if not line:
                raise Exception("Empty response from MCP")
            
            response = json.loads(line)
            logger.debug(f"📥 Received MCP response: {response.get('id', 'unknown')}")
            return response
            
        except asyncio.TimeoutError:
            logger.error("⏰ MCP response timeout")
            self.is_connected = False
            raise Exception("MCP response timeout")
        except json.JSONDecodeError as e:
            logger.error(f"❌ MCP JSON decode error: {e}")
            raise Exception(f"Invalid JSON response from MCP: {e}")
        except Exception as e:
            logger.error(f"❌ MCP response read error: {e}")
            self.is_connected = False
            raise Exception(f"MCP response read failed: {e}")
    
    def _get_request_id(self) -> int:
        """Unique request ID üret"""
        self.request_id += 1
        return self.request_id
    
    async def get_context_aware_photos(
        self, 
        design_plan: str, 
        user_preferences: Dict, 
        section_requirements: List[Dict] = None
    ) -> Dict:
        """
        Ana fonksiyon: Context-aware fotoğrafları getir - Geliştirilmiş
        """
        logger.info("🖼️ Starting context-aware photo generation via MCP...")
        
        # Bağlantı kontrolü
        if not self.is_connected:
            logger.info("🔌 MCP not connected, attempting connection...")
            success = await self.connect()
            if not success:
                raise Exception("Failed to establish MCP connection")
        
        try:
            # Input validation
            if not design_plan or not isinstance(user_preferences, dict):
                raise ValueError("Invalid input parameters for MCP")
            
            # MCP tool call mesajı oluştur
            tool_call = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "tools/call",
                "params": {
                    "name": "get_design_photos",
                    "arguments": {
                        "design_plan": design_plan[:1000],  # Limit size
                        "user_preferences": user_preferences,
                        "section_requirements": section_requirements or []
                    }
                }
            }
            
            logger.info("📤 Sending photo generation request to MCP...")
            await self._send_message(tool_call)
            
            logger.info("⏳ Waiting for MCP response...")
            response = await asyncio.wait_for(
                self._read_response(),
                timeout=30.0  # Uzun timeout - image generation zaman alabilir
            )
            
            # Error kontrolü
            if "error" in response:
                error_msg = response["error"]
                logger.error(f"❌ MCP tool error: {error_msg}")
                raise Exception(f"MCP tool error: {error_msg}")
            
            # Yanıtı parse et
            result = response.get("result", {})
            if not result:
                raise Exception("Empty result from MCP")
                
            content = result.get("content", [])
            if not content:
                raise Exception("No content in MCP result")
            
            logger.info(f"✅ MCP returned {len(content)} content items")
            
            # JSON verisini çıkar
            photos_data = {}
            for item in content:
                text = item.get("text", "")
                if "JSON Data:" in text:
                    try:
                        json_text = text.split("JSON Data: ", 1)[1]
                        photos_data = json.loads(json_text)
                        logger.info(f"📊 Extracted photo data: {len(photos_data)} sections")
                        break
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ JSON parse error in MCP response: {e}")
                        continue
            
            if not photos_data:
                raise Exception("No valid photo data found in MCP response")
            
            # Process ve return
            processed_images = self._process_photo_response(photos_data)
            logger.info(f"🎉 Successfully processed {len(processed_images)} context-aware images")
            return processed_images
            
        except asyncio.TimeoutError:
            logger.error("⏰ MCP photo generation timeout")
            self.is_connected = False
            raise Exception("MCP photo generation timeout")
        except Exception as e:
            logger.error(f"❌ MCP photo generation failed: {e}")
            raise Exception(f"MCP context-aware photo generation failed: {e}")
    
    def _process_photo_response(self, photos_data: List[Dict]) -> Dict:
        """MCP yanıtını işle ve optimize et - Geliştirilmiş"""
        processed = {
            "hero_image": None,
            "about_image": None,
            "portfolio_1": None,
            "portfolio_2": None,
            "portfolio_3": None,
            "service_image": None,
            "all_photos": []
        }
        
        logger.info(f"🔄 Processing {len(photos_data)} photo sections...")
        
        # Bölümlere göre fotoğrafları kategorize et
        for section_data in photos_data:
            if not isinstance(section_data, dict):
                continue
                
            section_name = section_data.get("section", "").lower()
            photos = section_data.get("photos", [])
            
            if not photos:
                logger.warning(f"⚠️ No photos found for section: {section_name}")
                continue
            
            logger.info(f"📸 Processing {len(photos)} photos for section: {section_name}")
            
            # En iyi fotoğrafı seç (kalite skoruna göre)
            try:
                best_photo = max(photos, key=lambda p: p.get("quality_score", 0))
                processed["all_photos"].extend(photos)
                
                # Bölüm eşleştirmesi - Daha geniş matching
                if any(keyword in section_name for keyword in ["hero", "main", "banner", "header"]):
                    processed["hero_image"] = best_photo["url"]
                    logger.info(f"✅ Set hero image: {best_photo.get('url', 'N/A')[:50]}...")
                elif any(keyword in section_name for keyword in ["about", "profile", "bio", "team"]):
                    processed["about_image"] = best_photo["url"]
                    logger.info(f"✅ Set about image: {best_photo.get('url', 'N/A')[:50]}...")
                elif any(keyword in section_name for keyword in ["service", "offering", "feature"]):
                    processed["service_image"] = best_photo["url"]
                    logger.info(f"✅ Set service image: {best_photo.get('url', 'N/A')[:50]}...")
                elif any(keyword in section_name for keyword in ["portfolio", "work", "project", "gallery"]):
                    # Portfolio için 3 fotoğraf
                    portfolio_photos = sorted(photos, key=lambda p: p.get("quality_score", 0), reverse=True)[:3]
                    for i, photo in enumerate(portfolio_photos):
                        if i < 3:  # Max 3 portfolio item
                            processed[f"portfolio_{i+1}"] = photo["url"]
                            logger.info(f"✅ Set portfolio_{i+1}: {photo.get('url', 'N/A')[:50]}...")
            except Exception as e:
                logger.warning(f"⚠️ Error processing section {section_name}: {e}")
                continue
        
        # Eksik fotoğrafları doldur (fallback)
        missing_count = self._fill_missing_photos(processed)
        if missing_count > 0:
            logger.warning(f"⚠️ Filled {missing_count} missing photos with fallbacks")
        
        return processed
    
    def _fill_missing_photos(self, processed: Dict) -> int:
        """Eksik fotoğrafları yedek URL'lerle doldur"""
        fallback_urls = {
            "hero_image": "https://picsum.photos/1200/600?random=1",
            "about_image": "https://picsum.photos/400/400?random=2",
            "portfolio_1": "https://picsum.photos/600/400?random=3",
            "portfolio_2": "https://picsum.photos/600/400?random=4", 
            "portfolio_3": "https://picsum.photos/600/400?random=5",
            "service_image": "https://picsum.photos/800/500?random=6"
        }
        
        missing_count = 0
        for key, fallback_url in fallback_urls.items():
            if not processed.get(key):
                processed[key] = fallback_url
                missing_count += 1
                logger.warning(f"🔄 Using fallback URL for {key}")
        
        return missing_count

# Singleton instance
mcp_photo_client = MCPPhotoServiceClient()