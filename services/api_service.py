import requests
from typing import Dict, Any, Optional
import config
import logging

logger = logging.getLogger(__name__)


class APIService:
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.timeout = config.API_TIMEOUT

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
                print(response)
                json_response = {"detail": response.text}
            logger.debug(f"Response status: {response.status_code}, JSON: {json_response}")
            if response.status_code in [200, 201]:
                return {'sucesso': True, 'dados': json_response}
            elif response.status_code == 404:
                return {'sucesso': False, 'mensagem': "Recurso não encontrado (404)", 'status_code': 404}
            else:
                mensagem_erro = (
                        json_response.get('message') or
                        json_response.get('detail') or
                        json_response.get('error') or
                        f"Erro do servidor (código {response.status_code})"
                )
                return {'sucesso': False, 'mensagem': mensagem_erro, 'status_code': response.status_code}
        except requests.exceptions.Timeout:
            return {'sucesso': False, 'mensagem': "⏱️ Tempo esgotado ao conectar com o servidor"}
        except requests.exceptions.ConnectionError:
            return {'sucesso': False, 'mensagem': "🔌 Não foi possível conectar ao servidor"}
        except Exception as e:
            return {'sucesso': False, 'mensagem': f"❌ Erro inesperado: {str(e)}"}

    def verificar_cadastro(self, filtro: str, pesquisa: str) -> Dict[str, Any]:
        return self._request("GET", f"/users?{filtro}={pesquisa}")

    def cadastrar_usuario(self, nome: str, email: str, telegram_id: str) -> Dict[str, Any]:
        dados = {
            "name": nome,
            "email": email,
            "telegram_id": telegram_id
        }
        return self._request("POST", "/users", dados)

    def criar_transacao(
            self,
            telegram_id: str,
            mensagem_original: str
    ) -> Dict[str, Any]:
        dados = {
            "telegram_id": telegram_id,
            "original_message": mensagem_original
        }

        resultado = self._request("POST", "/transactions", dados)
        print('----------------------------------------------')
        print(resultado)
        print('----------------------------------------------')

        if resultado['sucesso']:
            transacao = resultado['dados'].get('transaction', {})
            return {
                'sucesso': True,
                'transacao_id': transacao.get('id'),
                'tipo': transacao.get('type'),
                'categoria': transacao.get('category').get('title') or 'desconhecido',
                'valor': float(transacao.get('amount') or 0),
                'descricao': transacao.get('description')
            }
        else:
            return resultado