import config

class BotMessages:
    @staticmethod
    def get_welcome_back_message(name: str) -> str:
        return (
            f"👋 Olá novamente, {name}!\n\n"
            f"Envie suas transações e eu vou processá-las para você!\n\n"
            f"💡 Dicas:\n"
            f"• Envie uma mensagem de texto com a transação\n"
            f"• Envie uma foto do comprovante\n"
            f"• Envie um PDF com a nota fiscal\n\n"
            f"Use /ajuda para ver todos os comandos disponíveis."
        )

    @staticmethod
    def get_registration_message(name: str) -> str:
        return (
            f"👋 Olá, {name}! Bem-vindo ao Bot de Finanças!\n\n"
            f"Para começar, preciso fazer seu cadastro.\n\n"
            f"Por favor, me informe seu nome completo:"
        )

    @staticmethod
    def get_ask_email_message() -> str:
        return "📧 Ótimo! Agora me informe seu email:"

    @staticmethod
    def get_invalid_email_message() -> str:
        return (
            "❌ Email inválido. Por favor, informe um email válido.\n\n"
            "Exemplo: seu.nome@exemplo.com"
        )

    @staticmethod
    def get_email_already_registered_message() -> str:
        return (
            "⚠️ Este email já está cadastrado no sistema.\n\n"
            "Por favor, informe outro email ou entre em contato com o suporte."
        )

    @staticmethod
    def get_registration_success_message(name: str) -> str:
        return (
            f"✅ Cadastro realizado com sucesso, {name}!\n\n"
            f"Agora você pode:\n"
            f"• Enviar mensagens de texto com suas transações\n"
            f"• Enviar fotos de comprovantes\n"
            f"• Enviar PDFs de notas fiscais\n\n"
            f"Exemplo de mensagem:\n"
            f"• Comprei um café por R$ 8,50 na padaria\n\n"
            f"🌐 Para gerenciar transações e ter acesso a relatórios, acesse:\n"
            f"{config.APP_BASE_URL}\n\n"
            f"Digite /ajuda para ver mais informações."
        )

    @staticmethod
    def get_registration_error_message(error: str) -> str:
        return (
            f"❌ Erro ao realizar o cadastro.\n\n"
            f"Detalhes: {error}\n\n"
            f"Por favor, tente novamente mais tarde ou use /start para recomeçar."
        )

    @staticmethod
    def get_not_registered_message() -> str:
        return (
            "⚠️ Você ainda não está cadastrado.\n\n"
            "Use o comando /start para fazer seu cadastro e começar a usar o bot."
        )

    @staticmethod
    def get_help_message() -> str:
        return (
            "📚 Ajuda - Bot de Finanças\n\n"
            "Comandos disponíveis:\n"
            "/start - Inicia o bot e faz cadastro\n"
            "/ajuda - Mostra esta mensagem de ajuda\n"
            "/link - Para acessar nossa página web\n"
            "/resumo - Mostra resumo de gastos\n"
            "/exclusao - Exclui sua conta permanentemente\n\n"
            "❓Como registrar transações:\n\n"
            "1️⃣ Mensagem de texto\n"
            "Envie uma descrição da sua transação:\n"
            "• Almoço no restaurante por R$ 45\n"
            "• Recebi R$ 1000 de salário\n"
            "• Comprei sapato por R$ 150\n\n"
            "2️⃣ Foto de comprovante\n"
            "Tire uma foto clara do comprovante e envie. O bot vai extrair as informações automaticamente.\n\n"
            "3️⃣ PDF de nota fiscal\n"
            "Envie o arquivo PDF e o bot processará as informações.\n\n"
            "💡 Dicas:\n"
            "• Seja claro nas descrições\n"
            "• Fotos com boa iluminação funcionam melhor\n"
            "• O bot identifica automaticamente se é receita ou despesa"
        )

    @staticmethod
    def get_link_message() -> str:
        return (
            f"🌐 Para gerenciar transações e ter acesso a relatórios, acesse:\n"
            f"{config.APP_BASE_URL}\n\n"
        )

    @staticmethod
    def get_processing_message() -> str:
        return "⏳ Processando... Por favor, aguarde."

    @staticmethod
    def get_error_message(action: str) -> str:
        return (
            f"❌ Ocorreu um erro ao {action}.\n\n"
            f"Por favor, tente novamente mais tarde."
        )

    @staticmethod
    def get_unsupported_file_message() -> str:
        return (
            "⚠️ Tipo de arquivo não suportado.\n\n"
            "Envie apenas:\n"
            "• Imagens (JPG, PNG)\n"
            "• Documentos PDF"
        )

    @staticmethod
    def get_delete_account_confirmation() -> str:
        return (
            "⚠️ EXCLUSÃO DE CONTA\n\n"
            "Você está prestes a excluir sua conta permanentemente.\n\n"
            "⚠️ Esta ação NÃO pode ser desfeita!\n"
            "⚠️ Todas as suas transações serão perdidas!\n\n"
            "Para confirmar, digite seu email cadastrado:"
        )

    @staticmethod
    def get_delete_account_cancelled() -> str:
        return (
            "✅ Exclusão cancelada.\n\n"
            "Sua conta permanece ativa."
        )

    @staticmethod
    def get_delete_account_success() -> str:
        return (
            "✅ Conta excluída com sucesso!\n\n"
            "Todos os seus dados foram removidos.\n\n"
            "Foi um prazer ter você conosco. "
            "Se quiser voltar, use /start para criar uma nova conta."
        )

    @staticmethod
    def get_delete_account_error(message: str) -> str:
        return (
            f"❌ Erro ao excluir conta.\n\n"
            f"Detalhes: {message}\n\n"
            f"Tente novamente ou entre em contato com o suporte."
        )

    @staticmethod
    def get_delete_account_email_mismatch() -> str:
        return (
            "❌ Email incorreto!\n\n"
            "O email informado não corresponde ao cadastrado.\n\n"
            "Digite /exclusao novamente para tentar outra vez ou "
            "envie qualquer mensagem para cancelar."
        )
        
    @staticmethod
    def get_summary_choice_message() -> str:
        return (
            "📊 RESUMO DE TRANSAÇÕES\n\n"
            "Escolha o tipo de resumo:\n\n"
            "1️⃣ Por mês\n"
            "2️⃣ Por categoria\n\n"
            "Digite 1 ou 2:"
        )
        
