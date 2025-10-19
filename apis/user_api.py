from typing import Dict, Any
from apis.base_api import BaseAPI
import logging

logger = logging.getLogger(__name__)


class UserAPI(BaseAPI):
    async def check_user(self, filter_by: str, value: str) -> Dict[str, Any]:
        endpoint = f"/users?{filter_by}={value}"
        return await self._request("GET", endpoint)

    async def create_user(
            self,
            name: str,
            email: str,
            telegram_id: str
    ) -> Dict[str, Any]:
        data = {
            "name": name,
            "email": email,
            "telegram_id": telegram_id
        }

        return await self._request("POST", "/users", data)

    async def delete_user(
            self,
            telegram_id: str,
            email: str
    ) -> Dict[str, Any]:
        endpoint = f"/users?telegram_id={telegram_id}&email={email}"
        return await self._request("DELETE", endpoint)