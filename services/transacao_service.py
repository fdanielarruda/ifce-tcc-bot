from typing import Dict, Any
import re
from services.api_service import APIService


class TransacaoService:
    def __init__(self):
        self.api_service = APIService()

    async def verificar_cadastro(self, filtro: str, valor: str) -> bool:
        unico = self.api_service.verificar_cadastro(filtro, valor)
        return bool(unico['dados']['usuarios'])

    async def cadastrar_usuario(self, nome: str, email: str, telegram_id: str) -> Dict[str, Any]:
        return self.api_service.cadastrar_usuario(nome, email, telegram_id)

    def validar_email(self, email: str) -> bool:
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.match(regex, email, re.IGNORECASE) is not None

    async def processar_mensagem(self, texto: str, telegram_id: str) -> str:
        return await self._processar_transacao(texto, telegram_id)

    async def _processar_transacao(
            self,
            texto: str,
            telegram_id: str
    ) -> str:
        resultado = self.api_service.criar_transacao(
            telegram_id=telegram_id,
            mensagem_original=texto
        )

        if resultado['sucesso']:
            return self._formatar_mensagem_sucesso(resultado)

        return f"⚠️ {resultado['mensagem']}"

    def _formatar_mensagem_sucesso(self, resultado: Dict[str, Any]) -> str:
        emoji = "💸" if resultado['tipo'] == "debito" else "💰"
        tipo_texto = "Débito" if resultado['tipo'] == "debito" else "Crédito"

        mensagem = (
            f"✅ Transação registrada!\n\n"
            f"{emoji} {tipo_texto}: R$ {resultado['valor']:.2f}\n"
            f"📝 {resultado['descricao']}"
        )

        if resultado.get('transacao_id'):
            mensagem += f"\n🔖 ID: {resultado['transacao_id']}"

        return mensagem