"""Home Assistant integration service."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
import httpx
import json

from bot.config import settings
from bot.services.n8n import n8n_service
from bot.utils.metrics import smart_home_commands


logger = logging.getLogger(__name__)


class HomeAssistantService:
    """Service for interacting with Home Assistant."""
    
    def __init__(self):
        self.base_url = settings.home_assistant_url
        self.token = settings.home_assistant_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self._entities_cache = {}
        self._cache_timestamp = 0
    
    async def check_connection(self) -> bool:
        """Check if Home Assistant is accessible."""
        if not self.base_url or not self.token:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def get_states(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get states of entities."""
        try:
            url = f"{self.base_url}/api/states"
            if entity_id:
                url += f"/{entity_id}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                if entity_id:
                    return [response.json()]
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting HA states: {e}")
            return []
    
    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: Optional[str] = None,
        service_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Call a Home Assistant service."""
        try:
            smart_home_commands.inc()
            
            url = f"{self.base_url}/api/services/{domain}/{service}"
            
            data = {}
            if entity_id:
                data["entity_id"] = entity_id
            if service_data:
                data.update(service_data)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=data
                )
                response.raise_for_status()
                
                # Also trigger n8n workflow for logging
                await n8n_service.process_smart_home_command(
                    f"{domain}.{service}",
                    entity_id or "all",
                    service_data
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Error calling HA service: {e}")
            return False
    
    async def get_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all entities for a specific domain."""
        try:
            states = await self.get_states()
            return [
                state for state in states
                if state.get("entity_id", "").startswith(f"{domain}.")
            ]
        except Exception as e:
            logger.error(f"Error getting entities for domain {domain}: {e}")
            return []
    
    async def toggle_entity(self, entity_id: str) -> bool:
        """Toggle an entity (light, switch, etc.)."""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "toggle", entity_id)
    
    async def turn_on_entity(self, entity_id: str, **kwargs) -> bool:
        """Turn on an entity with optional parameters."""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_on", entity_id, kwargs)
    
    async def turn_off_entity(self, entity_id: str) -> bool:
        """Turn off an entity."""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_off", entity_id)
    
    async def set_light_brightness(self, entity_id: str, brightness: int) -> bool:
        """Set light brightness (0-255)."""
        brightness = max(0, min(255, brightness))
        return await self.call_service(
            "light", "turn_on", entity_id, {"brightness": brightness}
        )
    
    async def set_light_color(self, entity_id: str, rgb_color: List[int]) -> bool:
        """Set light RGB color."""
        return await self.call_service(
            "light", "turn_on", entity_id, {"rgb_color": rgb_color}
        )
    
    async def activate_scene(self, scene_id: str) -> bool:
        """Activate a scene."""
        return await self.call_service("scene", "turn_on", scene_id)
    
    async def set_climate_temperature(self, entity_id: str, temperature: float) -> bool:
        """Set climate target temperature."""
        return await self.call_service(
            "climate", "set_temperature", entity_id, {"temperature": temperature}
        )
    
    async def get_sensor_value(self, entity_id: str) -> Optional[str]:
        """Get sensor value."""
        try:
            states = await self.get_states(entity_id)
            if states:
                return states[0].get("state")
            return None
        except Exception as e:
            logger.error(f"Error getting sensor value: {e}")
            return None
    
    async def find_entities(self, search_term: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find entities by name or friendly name."""
        try:
            states = await self.get_states()
            results = []
            
            search_lower = search_term.lower()
            
            for state in states:
                entity_id = state.get("entity_id", "")
                attributes = state.get("attributes", {})
                friendly_name = attributes.get("friendly_name", "").lower()
                
                # Filter by domain if specified
                if domain and not entity_id.startswith(f"{domain}."):
                    continue
                
                # Check if search term matches
                if (search_lower in entity_id.lower() or 
                    search_lower in friendly_name):
                    results.append({
                        "entity_id": entity_id,
                        "friendly_name": attributes.get("friendly_name", entity_id),
                        "state": state.get("state"),
                        "domain": entity_id.split(".")[0]
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding entities: {e}")
            return []
    
    async def get_areas(self) -> List[Dict[str, Any]]:
        """Get all areas/rooms."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/config/area_registry",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting areas: {e}")
            return []
    
    async def get_devices_in_area(self, area_id: str) -> List[Dict[str, Any]]:
        """Get devices in a specific area."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/config/device_registry",
                    headers=self.headers
                )
                response.raise_for_status()
                
                devices = response.json()
                return [
                    device for device in devices
                    if device.get("area_id") == area_id
                ]
        except Exception as e:
            logger.error(f"Error getting devices in area: {e}")
            return []
    
    async def create_automation(
        self,
        name: str,
        trigger: Dict[str, Any],
        action: Dict[str, Any],
        condition: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new automation."""
        try:
            automation_config = {
                "alias": name,
                "trigger": trigger,
                "action": action
            }
            
            if condition:
                automation_config["condition"] = condition
            
            return await self.call_service(
                "automation", "reload"
            )  # Simplified - would need to write to config
            
        except Exception as e:
            logger.error(f"Error creating automation: {e}")
            return False
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get Home Assistant system information."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/config",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}


# Global Home Assistant service instance
ha_service = HomeAssistantService()
