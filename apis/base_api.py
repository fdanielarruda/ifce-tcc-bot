import requests
from typing import Dict, Any, Optional
import config
import logging

logger = logging.getLogger(__name__)

class BaseAPI:
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.timeout = config.API_TIMEOUT

    async def _request(
            self,
            method: str,
            endpoint: str,
            data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "ngrok-skip-browser-warning": "true",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            logger.debug(f"Request {method} to {url} with data: {data}")

            response = requests.request(
                method,
                url,
                json=data,
                timeout=self.timeout,
                headers=headers
            )

            try:
                json_response = response.json()
            except requests.exceptions.JSONDecodeError:
                logger.warning(f"Resposta não é JSON válido: {response.text}")
                json_response = {"detail": response.text}

            logger.debug(
                f"Response status: {response.status_code}, JSON: {json_response}"
            )

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'data': json_response
                }

            elif response.status_code == 404:
                return {
                    'success': False,
                    'message': "Recurso não encontrado (404)",
                    'status_code': 404
                }

            else:
                error_message = (
                    json_response.get('message') or
                    json_response.get('detail') or
                    json_response.get('error') or
                    f"Erro do servidor (código {response.status_code})"
                )
                return {
                    'success': False,
                    'message': error_message,
                    'status_code': response.status_code
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': "Tempo esgotado ao conectar com o servidor"
            }

        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': "Não foi possível conectar ao servidor"
            }

        except Exception as e:
            logger.error(f"Erro inesperado na requisição: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Erro inesperado: {str(e)}"
            }