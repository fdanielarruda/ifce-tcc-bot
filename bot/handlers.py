from telegram import Update
from telegram.ext import ContextTypes
from services.transacao_service import TransacaoService
import logging

logger = logging.getLogger(__name__)

AGUARDANDO_NOME = 1
AGUARDANDO_EMAIL = 2
CADASTRADO = 3


class BotHandlers:
    def __init__(self):
        self.transacao_service = TransacaoService()

    def _get_user_state(self, context: ContextTypes.DEFAULT_TYPE) -> int:
        return context.user_data.get('state', 0)

    def _set_user_state(self, context: ContextTypes.DEFAULT_TYPE, state: int):
        context.user_data['state'] = state

    async def _checar_cadastro_e_iniciar_fluxo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = str(update.effective_user.id)

        if self._get_user_state(context) == CADASTRADO:
            return True

        is_registered = await self.transacao_service.verificar_cadastro('telegram_id', telegram_id)

        if is_registered:
            self._set_user_state(context, CADASTRADO)
            return True
        else:
            self._set_user_state(context, AGUARDANDO_NOME)
            mensagem = (
                "🛑 **Primeiro, precisamos do seu cadastro!**\n\n"
                "Para começar a gerenciar suas finanças, por favor, me diga **seu nome completo**."
            )
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mensagem_boas_vindas = (
            "👋 Olá! Bem-vindo ao Gerenciador de Finanças!\n\n"
            "Registre suas transações de forma simples:\n"
            "• Envie mensagem: `gastei 20 com hamburger`\n"
            "• Ou envie foto/PDF do comprovante 📸\n\n"
        )
        await update.message.reply_text(mensagem_boas_vindas, parse_mode='Markdown')
        await self._checar_cadastro_e_iniciar_fluxo(update, context)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        mensagem_ajuda = (
            "ℹ️ **Como usar o bot**\n\n"
            "**Opção 1 - Texto:**\n"
            "• gastei 20 com hamburger\n"
            "• recebi 2000 de salário\n\n"
            "**Opção 2 - Comprovante:**\n"
            "• Envie foto do comprovante 📸\n"
            "• Ou envie PDF do comprovante 📄\n\n"
            "**Lembre-se:** Você precisa estar cadastrado. "
            "Digite `/start` para verificar seu status."
        )
        await update.message.reply_text(mensagem_ajuda, parse_mode='Markdown')

    async def processar_mensagem(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        texto = update.message.text
        telegram_id = str(update.effective_user.id)
        current_state = self._get_user_state(context)

        await update.message.chat.send_action(action="typing")

        if current_state == 0:
            await self._checar_cadastro_e_iniciar_fluxo(update, context)
            return

        elif current_state == AGUARDANDO_NOME:
            context.user_data['nome_candidato'] = texto
            self._set_user_state(context, AGUARDANDO_EMAIL)
            mensagem = (
                f"Que ótimo, **{texto}**! Agora, por favor, me informe **seu melhor email** "
                "para associarmos à sua conta de finanças. (Ex: `seuemail@exemplo.com`)"
            )
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            return

        elif current_state == AGUARDANDO_EMAIL:
            email = texto
            nome = context.user_data.get('nome_candidato')

            if not self.transacao_service.validar_email(email):
                await update.message.reply_text(
                    "🚫 Email inválido. Por favor, digite um formato de email válido. (Ex: `seunome@email.com`)",
                    parse_mode='Markdown'
                )
                return

            is_registered = await self.transacao_service.verificar_cadastro('email', email)

            if is_registered:
                await update.message.reply_text(
                    "❌ Email já está sendo utilizado por outro usuário do telegram"
                )
                return

            resultado = await self.transacao_service.cadastrar_usuario(nome, email, telegram_id)

            if resultado['sucesso']:
                self._set_user_state(context, CADASTRADO)
                context.user_data.pop('nome_candidato', None)
                mensagem_sucesso = (
                    f"🎉 Cadastro concluído, **{nome}**!\n\n"
                    "Agora você pode registrar suas transações:\n"
                    "• Enviando mensagens de texto\n"
                    "• Ou enviando comprovantes (foto/PDF) 📸\n\n"
                    f"Seu email de acesso: `{email}`"
                )
                await update.message.reply_text(mensagem_sucesso, parse_mode='Markdown')
            else:
                self._set_user_state(context, 0)
                mensagem_erro = (
                    f"❌ Erro ao finalizar o cadastro. Por favor, tente novamente com `/start`.\n"
                    f"Detalhes: {resultado['mensagem']}"
                )
                await update.message.reply_text(mensagem_erro)
            return

        elif current_state == CADASTRADO:
            resposta = await self.transacao_service.processar_mensagem(texto, telegram_id)
            await update.message.reply_text(resposta, parse_mode='Markdown')
            return

        else:
            await update.message.reply_text(
                "🤔 Estado do bot inesperado. Digite `/start` para recomeçar."
            )
            self._set_user_state(context, 0)

    async def processar_foto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = str(update.effective_user.id)
        current_state = self._get_user_state(context)

        if current_state != CADASTRADO:
            await update.message.reply_text(
                "🛑 Você precisa estar cadastrado para enviar comprovantes.\n"
                "Digite `/start` para se cadastrar."
            )
            return

        await update.message.chat.send_action(action="typing")
        await update.message.reply_text("📸 Processando comprovante, aguarde...")

        try:
            foto = update.message.photo[-1]
            arquivo = await context.bot.get_file(foto.file_id)

            arquivo_bytes = await arquivo.download_as_bytearray()

            resposta = await self.transacao_service.processar_comprovante(
                arquivo_bytes=bytes(arquivo_bytes),
                tipo_mime='image/jpeg',
                telegram_id=telegram_id
            )

            await update.message.reply_text(resposta, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"❌ Erro ao processar foto: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Erro ao processar o comprovante. Tente novamente ou digite a transação manualmente."
            )

    async def processar_documento(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = str(update.effective_user.id)
        current_state = self._get_user_state(context)

        if current_state != CADASTRADO:
            await update.message.reply_text(
                "🛑 Você precisa estar cadastrado para enviar comprovantes.\n"
                "Digite `/start` para se cadastrar."
            )
            return

        documento = update.message.document
        tipo_mime = documento.mime_type

        tipos_suportados = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
        if tipo_mime not in tipos_suportados:
            await update.message.reply_text(
                "⚠️ Tipo de arquivo não suportado.\n"
                "Envie: PDF, JPG ou PNG"
            )
            return

        if documento.file_size > 20 * 1024 * 1024:
            await update.message.reply_text(
                "⚠️ Arquivo muito grande. Tamanho máximo: 20MB"
            )
            return

        await update.message.chat.send_action(action="upload_document")
        await update.message.reply_text("📄 Processando documento, aguarde...")

        try:
            arquivo = await context.bot.get_file(documento.file_id)
            arquivo_bytes = await arquivo.download_as_bytearray()

            resposta = await self.transacao_service.processar_comprovante(
                arquivo_bytes=bytes(arquivo_bytes),
                tipo_mime=tipo_mime,
                telegram_id=telegram_id
            )

            await update.message.reply_text(resposta, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"❌ Erro ao processar documento: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Erro ao processar o documento. Tente novamente ou digite a transação manualmente."
            )