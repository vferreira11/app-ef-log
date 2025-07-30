"""
Interface de comunicação entre agentes do sistema.
Gerencia o fluxo de mensagens e validações.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import logging
from .validador_escopo import ValidadorEscopo, ResultadoValidacao, StatusValidacao

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoMensagem(Enum):
    """Tipos de mensagem suportados na comunicação entre agentes."""
    SOLICITACAO = "solicitacao"
    RESPOSTA = "resposta"
    VALIDACAO = "validacao"
    ERRO = "erro"

class AgenteComunicacao:
    """
    Gerencia comunicação entre agentes com suporte a validação assíncrona.
    """

    def __init__(self, nome_agente: str, validador: ValidadorEscopo):
        """
        Inicializa o gerenciador de comunicação.
        
        Args:
            nome_agente: Nome do agente para identificação
            validador: Instância do ValidadorEscopo para validações
        """
        self.nome = nome_agente
        self.validador = validador
        self.fila_mensagens = asyncio.Queue()
        self._callbacks: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        logger.info(f"Agente '{nome_agente}' inicializado")

    async def enviar_mensagem(
        self,
        destinatario: str,
        tipo: TipoMensagem,
        conteudo: Any,
        validacoes: List[Dict[str, Any]] = None
    ) -> ResultadoValidacao:
        """
        Envia mensagem para outro agente com validação opcional.
        
        Args:
            destinatario: Nome do agente destinatário
            tipo: Tipo da mensagem
            conteudo: Conteúdo da mensagem
            validacoes: Lista de validações a serem executadas
            
        Returns:
            Resultado das validações se houver
        """
        mensagem = {
            'origem': self.nome,
            'destino': destinatario,
            'tipo': tipo,
            'conteudo': conteudo
        }

        # Executa validações se especificadas
        if validacoes:
            resultado = await self.validador.validar_multiplos(validacoes)
            if any(r.status == StatusValidacao.ERRO for r in resultado.values()):
                logger.error(f"Erro nas validações da mensagem para {destinatario}")
                return ResultadoValidacao(
                    status=StatusValidacao.ERRO,
                    mensagem="Falha nas validações",
                    detalhes=resultado
                )
            mensagem['validacoes'] = resultado

        # Adiciona à fila de mensagens
        await self.fila_mensagens.put(mensagem)
        logger.info(f"Mensagem enviada para {destinatario}")

        return ResultadoValidacao(
            status=StatusValidacao.CONCLUIDO,
            mensagem="Mensagem enviada com sucesso",
            detalhes={'validacoes': validacoes} if validacoes else None
        )

    async def receber_mensagem(self) -> Dict[str, Any]:
        """
        Recebe próxima mensagem da fila de forma assíncrona.
        
        Returns:
            Dicionário com dados da mensagem
        """
        mensagem = await self.fila_mensagens.get()
        logger.info(f"Mensagem recebida de {mensagem['origem']}")
        return mensagem

    async def registrar_callback(
        self,
        tipo_mensagem: TipoMensagem,
        callback: callable
    ) -> None:
        """
        Registra callback para processar mensagens de um tipo específico.
        
        Args:
            tipo_mensagem: Tipo de mensagem para acionar o callback
            callback: Função a ser chamada
        """
        async with self._lock:
            self._callbacks[tipo_mensagem] = callback
            logger.info(f"Callback registrado para mensagens do tipo {tipo_mensagem}")

    async def processar_mensagens(self) -> None:
        """
        Processa mensagens da fila continuamente,
        executando callbacks registrados.
        """
        while True:
            try:
                mensagem = await self.receber_mensagem()
                tipo = mensagem['tipo']

                if tipo in self._callbacks:
                    callback = self._callbacks[tipo]
                    await callback(mensagem)
                else:
                    logger.warning(f"Nenhum callback registrado para mensagens do tipo {tipo}")

            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {str(e)}")
                continue

    async def validar_mensagem(
        self,
        mensagem: Dict[str, Any],
        validacoes: List[Dict[str, Any]]
    ) -> ResultadoValidacao:
        """
        Valida uma mensagem usando o ValidadorEscopo.
        
        Args:
            mensagem: Mensagem a ser validada
            validacoes: Lista de validações a executar
            
        Returns:
            Resultado das validações
        """
        return await self.validador.validar_multiplos(validacoes)

    def iniciar_processamento(self) -> None:
        """Inicia o processamento assíncrono de mensagens."""
        asyncio.create_task(self.processar_mensagens())
        logger.info(f"Processamento de mensagens iniciado para agente {self.nome}")

    async def parar_processamento(self) -> None:
        """
        Para o processamento de mensagens e limpa recursos.
        """
        # Limpa callbacks
        async with self._lock:
            self._callbacks.clear()

        # Limpa fila de mensagens
        while not self.fila_mensagens.empty():
            await self.fila_mensagens.get()

        logger.info(f"Processamento de mensagens interrompido para agente {self.nome}")