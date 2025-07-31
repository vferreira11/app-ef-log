"""
Sistema de comunicação entre agentes com validação de escopo.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Callable
from .validador_escopo import ValidadorEscopo, Entrega, ResultadoValidacao
from .interceptador import InterceptadorAgentes

class AgenteComunicacao:
    def __init__(self):
        self.validador = ValidadorEscopo()
        self.interceptador = InterceptadorAgentes()
        self._callbacks: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self._fila_mensagens: asyncio.Queue = asyncio.Queue()
        self._processando = False
        asyncio.create_task(self._processar_fila())
        
    async def enviar_mensagem(
        self,
        agente_origem: str,
        agente_destino: str,
        conteudo: dict,
        escopo: dict,
        timeout: float = 30.0,
        profundidade: int = 0
    ) -> ResultadoValidacao:
        """Envia mensagem entre agentes com validação e interceptação."""
        
        # Intercepta operação
        if not await self.interceptador.interceptar(
            agente_origem,
            agente_destino,
            "envio_mensagem",
            conteudo,
            profundidade
        ):
            return ResultadoValidacao(
                valido=False,
                mensagem="Operação bloqueada pelo interceptador",
                detalhes={"origem": agente_origem, "destino": agente_destino}
            )
            
        entrega = Entrega(
            agente_origem=agente_origem,
            agente_destino=agente_destino,
            conteudo=conteudo,
            timestamp=datetime.now(),
            escopo_original=escopo
        )
        
        try:
            # Valida entrega com timeout
            resultado = await asyncio.wait_for(
                self.validador.validar_entrega(entrega),
                timeout=timeout/2  # Divide timeout entre validação e notificação
            )
            
            if resultado.valido:
                try:
                    # Notifica agente destino com timeout
                    await asyncio.wait_for(
                        self._notificar_agente(agente_destino, entrega),
                        timeout=timeout/2
                    )
                except asyncio.TimeoutError:
                    self.logger.error(
                        f"Timeout na notificação: {agente_origem} -> {agente_destino}"
                    )
                    return ResultadoValidacao(
                        valido=False,
                        mensagem="Timeout na notificação do agente",
                        detalhes={
                            "origem": agente_origem,
                            "destino": agente_destino,
                            "timeout": timeout/2
                        }
                    )
                
            return resultado
        except asyncio.TimeoutError:
            self.logger.error(
                f"Timeout na comunicação: {agente_origem} -> {agente_destino}"
            )
            return ResultadoValidacao(
                valido=False,
                mensagem="Timeout na comunicação entre agentes",
                detalhes={
                    "origem": agente_origem,
                    "destino": agente_destino,
                    "timeout": timeout
                }
            )
        
    def registrar_callback(
        self,
        agente: str,
        callback: Callable[[Entrega], None]
    ) -> None:
        """Registra callback para recebimento de mensagens."""
        self._callbacks[agente] = callback
        
    async def _notificar_agente(self, agente: str, entrega: Entrega) -> None:
        """Notifica um agente sobre nova mensagem."""
        await self._fila_mensagens.put((agente, entrega))

    async def _processar_fila(self):
        """Processa mensagens da fila de forma assíncrona."""
        while True:
            agente, entrega = await self._fila_mensagens.get()
            if callback := self._callbacks.get(agente):
                try:
                    await callback(entrega)
                except Exception as e:
                    self.logger.error(f"Erro ao notificar agente {agente}: {str(e)}")
            self._fila_mensagens.task_done()
                
class Agente:
    """Classe base para agentes do sistema."""
    
    def __init__(self, nome: str, comunicador: AgenteComunicacao):
        self.nome = nome
        self.comunicador = comunicador
        self.logger = logging.getLogger(__name__)
        
        # Registra callback para receber mensagens
        comunicador.registrar_callback(nome, self._receber_mensagem)
        
    async def enviar_para(
        self,
        agente_destino: str,
        conteudo: dict,
        escopo: dict,
        timeout: float = 30.0
    ) -> ResultadoValidacao:
        """Envia mensagem para outro agente."""
        return await self.comunicador.enviar_mensagem(
            self.nome,
            agente_destino,
            conteudo,
            escopo
        )
        
    async def _receber_mensagem(self, entrega: Entrega) -> None:
        """Processa mensagem recebida."""
        try:
            await self.processar_mensagem(entrega)
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {str(e)}")
            
    async def processar_mensagem(self, entrega: Entrega) -> None:
        """
        Processa mensagem recebida.
        Deve ser implementado pelos agentes específicos.
        """
        raise NotImplementedError