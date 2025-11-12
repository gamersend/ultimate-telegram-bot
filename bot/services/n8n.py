"""n8n workflow automation integration."""

import logging
import httpx
from typing import Dict, Any, Optional, List

from bot.config import settings


logger = logging.getLogger(__name__)


class N8nService:
    """Service for interacting with n8n workflow automation."""

    def __init__(self):
        self.base_url = settings.n8n_url.rstrip('/') if settings.n8n_url else None
        self.token = settings.n8n_token
        self.enabled = self.base_url is not None and self.token is not None
        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Content-Type": "application/json"
        }
    
    async def trigger_webhook(self, webhook_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Trigger an n8n webhook."""
        if not self.enabled:
            logger.warning("n8n service is not configured, skipping webhook trigger")
            return None

        try:
            url = f"{self.base_url}/webhook/{webhook_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=self.headers)
                response.raise_for_status()
                
                if response.content:
                    return response.json()
                return {"status": "success"}
                
        except Exception as e:
            logger.error(f"Error triggering n8n webhook {webhook_id}: {e}")
            return None
    
    async def execute_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an n8n workflow."""
        if not self.enabled:
            logger.warning("n8n service is not configured, skipping workflow execution")
            return None

        try:
            url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=self.headers)
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error executing n8n workflow {workflow_id}: {e}")
            return None
    
    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflows."""
        if not self.enabled:
            logger.warning("n8n service is not configured")
            return []

        try:
            url = f"{self.base_url}/api/v1/workflows"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                return response.json().get("data", [])
                
        except Exception as e:
            logger.error(f"Error getting n8n workflows: {e}")
            return []
    
    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get workflow executions."""
        if not self.enabled:
            logger.warning("n8n service is not configured")
            return []

        try:
            url = f"{self.base_url}/api/v1/executions"
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                
                return response.json().get("data", [])
                
        except Exception as e:
            logger.error(f"Error getting n8n executions: {e}")
            return []
    
    async def send_telegram_message(self, user_id: int, message: str, workflow_id: str = "telegram_sender") -> bool:
        """Send a message via n8n Telegram workflow."""
        try:
            data = {
                "user_id": user_id,
                "message": message,
                "timestamp": "now"
            }
            
            result = await self.execute_workflow(workflow_id, data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error sending Telegram message via n8n: {e}")
            return False
    
    async def process_smart_home_command(self, command: str, entity: str, value: Any = None) -> Optional[Dict[str, Any]]:
        """Process smart home commands via n8n."""
        try:
            data = {
                "command": command,
                "entity": entity,
                "value": value,
                "source": "telegram_bot"
            }
            
            return await self.trigger_webhook("smart_home", data)
            
        except Exception as e:
            logger.error(f"Error processing smart home command via n8n: {e}")
            return None
    
    async def log_user_activity(self, user_id: int, activity: str, metadata: Dict[str, Any] = None) -> bool:
        """Log user activity via n8n."""
        try:
            data = {
                "user_id": user_id,
                "activity": activity,
                "metadata": metadata or {},
                "timestamp": "now"
            }
            
            result = await self.trigger_webhook("user_activity", data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error logging user activity via n8n: {e}")
            return False
    
    async def create_automation(self, trigger: str, action: str, conditions: Dict[str, Any] = None) -> Optional[str]:
        """Create a new automation workflow."""
        if not self.enabled:
            logger.warning("n8n service is not configured")
            return None

        try:
            workflow_data = {
                "name": f"Telegram Bot Automation - {trigger}",
                "nodes": [
                    {
                        "name": "Trigger",
                        "type": "n8n-nodes-base.webhook",
                        "parameters": {
                            "path": f"automation_{trigger.lower().replace(' ', '_')}"
                        }
                    },
                    {
                        "name": "Action",
                        "type": "n8n-nodes-base.function",
                        "parameters": {
                            "functionCode": f"// Automation: {action}\nreturn items;"
                        }
                    }
                ],
                "connections": {
                    "Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Action",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                }
            }
            
            url = f"{self.base_url}/api/v1/workflows"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=workflow_data, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                return result.get("data", {}).get("id")
                
        except Exception as e:
            logger.error(f"Error creating automation workflow: {e}")
            return None


# Global n8n service instance
n8n_service = N8nService()


async def trigger_n8n_workflow(workflow_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convenience function to trigger n8n workflows."""
    return await n8n_service.trigger_webhook(workflow_name, data)


async def log_bot_activity(user_id: int, command: str, success: bool, metadata: Dict[str, Any] = None) -> None:
    """Log bot activity to n8n for analytics."""
    activity_data = {
        "user_id": user_id,
        "command": command,
        "success": success,
        "metadata": metadata or {}
    }
    
    await n8n_service.log_user_activity(user_id, "bot_command", activity_data)
