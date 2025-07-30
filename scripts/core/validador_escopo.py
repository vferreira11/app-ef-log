"""
Validador de escopo para o fluxo de agentes.
Verifica e valida entregas intermediárias de forma assíncrona.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatusValidacao(Enum):
    """Status possíveis de uma validação."""
    PENDENTE = "pendente"
    EM_PROGRESSO = "em_progresso"
    CONCLUIDO = "concluido"
    ERRO = "erro"

@dataclass
class ResultadoValidacao:
    """Resultado de uma validação específica."""
    status: StatusValidacao
    mensagem: str
    detalhes: Dict[str, Any] = None

class ValidadorEscopo:
    """
    Validador assíncrono de escopo para o fluxo de agentes.
    Permite validação de entregas intermediárias sem criar gargalos.
    """

    def __init__(self, max_workers: int = 4):
        """
        Inicializa o validador.
        
        Args:
            max_workers: Número máximo de workers para validações paralelas
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.validacoes_registradas: Dict[str, Callable] = {}
        self.resultados: Dict[str, ResultadoValidacao] = {}
        self._lock = asyncio.Lock()

    async def registrar_validacao(self, nome: str, func_validacao: Callable) -> None:
        """
        Registra uma nova função de validação.
        
        Args:
            nome: Identificador único da validação
            func_validacao: Função que implementa a validação
        """
        async with self._lock:
            if nome in self.validacoes_registradas:
                logger.warning(f"Validação '{nome}' já registrada. Substituindo...")
            self.validacoes_registradas[nome] = func_validacao
            logger.info(f"Validação '{nome}' registrada com sucesso")

    async def validar_entrega(self, nome: str, dados: Any) -> ResultadoValidacao:
        """
        Executa uma validação específica de forma assíncrona.
        
        Args:
            nome: Nome da validação a ser executada
            dados: Dados a serem validados
            
        Returns:
            ResultadoValidacao com o status e detalhes
        """
        if nome not in self.validacoes_registradas:
            return ResultadoValidacao(
                status=StatusValidacao.ERRO,
                mensagem=f"Validação '{nome}' não encontrada"
            )

        try:
            # Marca como em progresso
            async with self._lock:
                self.resultados[nome] = ResultadoValidacao(
                    status=StatusValidacao.EM_PROGRESSO,
                    mensagem="Validação em andamento"
                )

            # Executa validação em thread separada
            func_validacao = self.validacoes_registradas[nome]
            loop = asyncio.get_event_loop()
            resultado = await loop.run_in_executor(
                self.executor,
                func_validacao,
                dados
            )

            # Atualiza resultado
            async with self._lock:
                self.resultados[nome] = ResultadoValidacao(
                    status=StatusValidacao.CONCLUIDO,
                    mensagem="Validação concluída com sucesso",
                    detalhes=resultado
                )
                return self.resultados[nome]

        except Exception as e:
            logger.error(f"Erro na validação '{nome}': {str(e)}")
            resultado = ResultadoValidacao(
                status=StatusValidacao.ERRO,
                mensagem=f"Erro na validação: {str(e)}"
            )
            async with self._lock:
                self.resultados[nome] = resultado
            return resultado

    async def validar_multiplos(self, validacoes: List[Dict[str, Any]]) -> Dict[str, ResultadoValidacao]:
        """
        Executa múltiplas validações em paralelo.
        
        Args:
            validacoes: Lista de dicionários com nome e dados para validação
            
        Returns:
            Dicionário com resultados de cada validação
        """
        tarefas = []
        for val in validacoes:
            nome = val.get('nome')
            dados = val.get('dados')
            if nome and dados:
                tarefa = asyncio.create_task(
                    self.validar_entrega(nome, dados)
                )
                tarefas.append((nome, tarefa))

        resultados = {}
        for nome, tarefa in tarefas:
            try:
                resultados[nome] = await tarefa
            except Exception as e:
                logger.error(f"Erro ao aguardar validação '{nome}': {str(e)}")
                resultados[nome] = ResultadoValidacao(
                    status=StatusValidacao.ERRO,
                    mensagem=f"Erro ao aguardar validação: {str(e)}"
                )

        return resultados

    def obter_status(self, nome: str) -> Optional[ResultadoValidacao]:
        """
        Retorna o status atual de uma validação.
        
        Args:
            nome: Nome da validação
            
        Returns:
            ResultadoValidacao ou None se não encontrada
        """
        return self.resultados.get(nome)

    async def limpar_resultados(self) -> None:
        """Limpa o histórico de resultados de validação."""
        async with self._lock:
            self.resultados.clear()
            logger.info("Histórico de validações limpo")

    def __del__(self):
        """Cleanup ao destruir o objeto."""
        self.executor.shutdown(wait=True)