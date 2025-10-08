"""Tesla integration service."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
import json

from bot.config import settings
from bot.services.n8n import n8n_service
from bot.utils.metrics import tesla_commands


logger = logging.getLogger(__name__)


class TeslaService:
    """Service for interacting with Tesla API."""
    
    def __init__(self):
        self.email = settings.tesla_email
        self.refresh_token = settings.tesla_refresh_token
        self.tesla = None
        self._vehicles_cache = {}
        self._cache_timestamp = 0
    
    async def initialize(self) -> bool:
        """Initialize Tesla API connection."""
        if not self.email or not self.refresh_token:
            logger.warning("Tesla credentials not configured")
            return False
        
        try:
            # Import teslapy here to avoid import errors if not installed
            import teslapy
            
            self.tesla = teslapy.Tesla(self.email)
            
            # Use refresh token if available
            if self.refresh_token:
                self.tesla.refresh_token = self.refresh_token
            
            # Test connection
            vehicles = await self.get_vehicles()
            logger.info(f"Tesla API initialized with {len(vehicles)} vehicles")
            return True
            
        except ImportError:
            logger.error("teslapy not installed. Install with: pip install teslapy")
            return False
        except Exception as e:
            logger.error(f"Error initializing Tesla API: {e}")
            return False
    
    async def get_vehicles(self) -> List[Dict[str, Any]]:
        """Get list of vehicles."""
        if not self.tesla:
            if not await self.initialize():
                return []
        
        try:
            tesla_commands.inc()
            
            # Run in thread pool since teslapy is synchronous
            loop = asyncio.get_event_loop()
            vehicles = await loop.run_in_executor(None, self.tesla.vehicle_list)
            
            # Convert to dict format
            vehicle_data = []
            for vehicle in vehicles:
                vehicle_data.append({
                    "id": vehicle.id,
                    "vehicle_id": vehicle.vehicle_id,
                    "vin": vehicle.vin,
                    "display_name": vehicle.display_name,
                    "state": vehicle.state,
                    "option_codes": vehicle.option_codes,
                    "color": vehicle.color,
                    "tokens": vehicle.tokens,
                    "id_s": vehicle.id_s,
                    "in_service": vehicle.in_service,
                    "calendar_enabled": vehicle.calendar_enabled
                })
            
            self._vehicles_cache = {v["id"]: v for v in vehicle_data}
            return vehicle_data
            
        except Exception as e:
            logger.error(f"Error getting Tesla vehicles: {e}")
            return []
    
    async def get_vehicle_data(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed vehicle data."""
        if not self.tesla:
            if not await self.initialize():
                return None
        
        try:
            vehicles = await self.get_vehicles()
            vehicle_obj = None
            
            for v in self.tesla.vehicle_list():
                if v.id == vehicle_id:
                    vehicle_obj = v
                    break
            
            if not vehicle_obj:
                return None
            
            # Get vehicle data
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, vehicle_obj.get_vehicle_data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting vehicle data: {e}")
            return None
    
    async def wake_up_vehicle(self, vehicle_id: int) -> bool:
        """Wake up a vehicle."""
        if not self.tesla:
            if not await self.initialize():
                return False
        
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.wake_up)
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error waking up vehicle: {e}")
            return False
    
    async def start_climate(self, vehicle_id: int) -> bool:
        """Start climate control."""
        try:
            tesla_commands.inc()
            
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "CLIMATE_ON")
            
            # Log to n8n
            await n8n_service.trigger_n8n_workflow("tesla_command", {
                "vehicle_id": vehicle_id,
                "command": "climate_on",
                "result": result
            })
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error starting climate: {e}")
            return False
    
    async def stop_climate(self, vehicle_id: int) -> bool:
        """Stop climate control."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "CLIMATE_OFF")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error stopping climate: {e}")
            return False
    
    async def set_temperature(self, vehicle_id: int, temp_celsius: float) -> bool:
        """Set climate temperature."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                vehicle.command, 
                "CHANGE_CLIMATE_TEMPERATURE_SETTING",
                driver_temp=temp_celsius,
                passenger_temp=temp_celsius
            )
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error setting temperature: {e}")
            return False
    
    async def start_charging(self, vehicle_id: int) -> bool:
        """Start charging."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "START_CHARGE")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error starting charge: {e}")
            return False
    
    async def stop_charging(self, vehicle_id: int) -> bool:
        """Stop charging."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "STOP_CHARGE")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error stopping charge: {e}")
            return False
    
    async def set_charge_limit(self, vehicle_id: int, limit_percent: int) -> bool:
        """Set charge limit percentage."""
        try:
            limit_percent = max(50, min(100, limit_percent))  # Tesla limits
            
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                vehicle.command, 
                "CHANGE_CHARGE_LIMIT",
                percent=limit_percent
            )
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error setting charge limit: {e}")
            return False
    
    async def lock_vehicle(self, vehicle_id: int) -> bool:
        """Lock vehicle."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "DOOR_LOCK")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error locking vehicle: {e}")
            return False
    
    async def unlock_vehicle(self, vehicle_id: int) -> bool:
        """Unlock vehicle."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "DOOR_UNLOCK")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error unlocking vehicle: {e}")
            return False
    
    async def honk_horn(self, vehicle_id: int) -> bool:
        """Honk horn."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "HONK_HORN")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error honking horn: {e}")
            return False
    
    async def flash_lights(self, vehicle_id: int) -> bool:
        """Flash lights."""
        try:
            vehicles = self.tesla.vehicle_list()
            vehicle = next((v for v in vehicles if v.id == vehicle_id), None)
            
            if not vehicle:
                return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, vehicle.command, "FLASH_LIGHTS")
            
            return result.get("response", {}).get("result", False)
            
        except Exception as e:
            logger.error(f"Error flashing lights: {e}")
            return False


# Global Tesla service instance
tesla_service = TeslaService()
