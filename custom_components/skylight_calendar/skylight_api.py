"""Skylight API client."""
import base64
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SkylightAPI:
    """Client for Skylight API."""
    
    def __init__(self):
        self.base_url = "https://app.ourskylight.com"
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.frame_id = None
        self.email = None
        self.password = None
    
    async def authenticate(self, email: str, password: str) -> Dict:
        """Authenticate with Skylight API."""
        self.email = email
        self.password = password
        
        async with aiohttp.ClientSession() as session:
            data = {"email": email, "password": password}
            async with session.post(f"{self.base_url}/api/sessions", json=data) as resp:
                if resp.status != 200:
                    raise Exception("Authentication failed")
                
                result = await resp.json()
                user_data = result["data"]
                
                self.user_id = user_data["id"]
                token = user_data["attributes"]["token"]
                
                # Create Basic auth token as per API spec
                auth_string = f"{self.user_id}:{token}"
                self.auth_token = base64.b64encode(auth_string.encode()).decode()
                
                return result
    
    async def _make_request(self, method: str, url: str, **kwargs):
        """Make authenticated request with auto-retry on auth failure."""
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Basic {self.auth_token}"
        kwargs["headers"] = headers
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as resp:
                if resp.status == 401:  # Token expired, re-authenticate
                    await self.authenticate(self.email, self.password)
                    headers["Authorization"] = f"Basic {self.auth_token}"
                    async with session.request(method, url, **kwargs) as retry_resp:
                        return retry_resp
                return resp
    
    async def get_frames(self) -> List[Dict]:
        """Get user's frames."""
        async with await self._make_request("GET", f"{self.base_url}/api/frames/calendar") as resp:
            if resp.status == 200:
                result = await resp.json()
                frames = result.get("data", [])
                if frames:
                    self.frame_id = frames[0]["id"]  # Use first frame
                return frames
            return []
    
    async def get_categories(self) -> List[Dict]:
        """Get categories (people) for the frame."""
        if not self.frame_id:
            await self.get_frames()
        
        url = f"{self.base_url}/api/frames/{self.frame_id}/categories"
        async with await self._make_request("GET", url) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("data", [])
            return []
    
    async def get_chores_for_today(self) -> List[Dict]:
        """Get today's chores."""
        if not self.frame_id:
            await self.get_frames()
        
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"{self.base_url}/api/frames/{self.frame_id}/chores"
        params = {"after": today, "before": today}
        
        async with await self._make_request("GET", url, params=params) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get("data", [])
            return []
    
    async def check_category_completion(self, category_id: str) -> bool:
        """Check if all tasks for a category are completed today."""
        chores = await self.get_chores_for_today()
        
        category_chores = [
            chore for chore in chores 
            if chore.get("relationships", {}).get("category", {}).get("data", {}).get("id") == category_id
        ]
        
        if not category_chores:
            return True  # No tasks = completed
        
        return all(
            chore.get("attributes", {}).get("status") == "completed" 
            for chore in category_chores
        )
