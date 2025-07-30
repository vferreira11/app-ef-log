"""
Validador de escopo para entregas intermediárias entre agentes.
Garante consistência e qualidade das entregas em cada etapa do fluxo.
"""
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging

@dataclass
class Entrega:
    agente_origem: str
    agente_destino: str
    conteudo: dict
    timestamp: datetime
    escopo_original: dict
    
@dataclass
class ResultadoValidacao:
    valido: bool
    mensagem: str
    detalhes: Optional[Dict] = None

class ValidadorEscopo:
    def __init__(self):
        self._cache: Dict[str, ResultadoValidacao] = {}
        self._validacoes_em_andamento: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)
        
    async def validar_entrega(self, entrega: Entrega, timeout: float = 30.0) -> ResultadoValidacao:
        """Valida uma entrega de forma assíncrona com timeout."""
        entrega_hash = self._gerar_hash_entrega(entrega)
        
        # Verifica cache
        if resultado_cache := self._cache.get(entrega_hash):
            self.logger.debug(f"Resultado encontrado em cache para {entrega_hash}")
            return resultado_cache
            
        # Verifica se já existe validação em andamento
        if task := self._validacoes_em_andamento.get(entrega_hash):
            self.logger.debug(f"Aguardando validação em andamento para {entrega_hash}")
            try:
                return await asyncio.wait_for(task, timeout=timeout)
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout aguardando validação para {entrega_hash}")
                return ResultadoValidacao(
                    valido=False,
                    mensagem="Timeout na validação da entrega",
                    detalhes={"timeout": timeout}
                )
            
        # Inicia nova validação
        task = asyncio.create_task(self._executar_validacao(entrega))
        self._validacoes_em_andamento[entrega_hash] = task
        
        try:
            resultado = await asyncio.wait_for(task, timeout=timeout)
            self._cache[entrega_hash] = resultado
            return resultado
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout na validação para {entrega_hash}")
            return ResultadoValidacao(
                valido=False,
                mensagem="Timeout na validação da entrega",
                detalhes={"timeout": timeout}
            )
        finally:
            del self._validacoes_em_andamento[entrega_hash]
            
    async def _executar_validacao(self, entrega: Entrega) -> ResultadoValidacao:
        """Executa a validação real da entrega."""
        try:
            # Valida escopo
            if not self._validar_escopo(entrega):
                return ResultadoValidacao(
                    valido=False,
                    mensagem="Campo obrigatório ausente",
                    detalhes={"escopo_original": entrega.escopo_original}
                )
                
            # Valida conteúdo específico por tipo de agente
            if not await self._validar_conteudo_especifico(entrega):
                return ResultadoValidacao(
                    valido=False,
                    mensagem="Conteúdo específico inválido",
                    detalhes={"agente": entrega.agente_origem}
                )
                
            # Valida integridade
            if not self._validar_integridade(entrega):
                return ResultadoValidacao(
                    valido=False,
                    mensagem="Falha na integridade dos dados",
                    detalhes={"timestamp": entrega.timestamp}
                )
                
            return ResultadoValidacao(
                valido=True,
                mensagem="Entrega válida",
                detalhes={"timestamp_validacao": datetime.now()}
            )
            
        except Exception as e:
            self.logger.error(f"Erro na validação: {str(e)}")
            return ResultadoValidacao(
                valido=False,
                mensagem=f"Erro na validação: {str(e)}"
            )
            
    def _validar_escopo(self, entrega: Entrega) -> bool:
        """Valida se a entrega atende ao escopo original."""
        escopo_original = entrega.escopo_original
        conteudo = entrega.conteudo
        
        # Valida campos obrigatórios
        for campo in escopo_original.get("campos_obrigatorios", []):
            if campo not in conteudo:
                self.logger.warning(f"Campo obrigatório ausente: {campo}")
                return False
                
        # Valida tipos de dados
        for campo, tipo in escopo_original.get("tipos", {}).items():
            if campo in conteudo and not isinstance(conteudo[campo], tipo):
                self.logger.warning(f"Tipo inválido para {campo}")
                return False
                
        # Valida restrições específicas
        for restricao in escopo_original.get("restricoes", []):
            if not self._validar_restricao(restricao, conteudo):
                self.logger.warning(f"Restrição não atendida: {restricao}")
                return False
                
        return True
        
    async def _validar_conteudo_especifico(self, entrega: Entrega) -> bool:
        """Valida o conteúdo específico baseado no tipo de agente."""
        validacoes = {
            "engenheiro_de_software": self._validar_codigo,
            "front_end_dev": self._validar_interface,
            "matematico": self._validar_calculos,
            "escritor_head": self._validar_documentacao
        }
        
        if validador := validacoes.get(entrega.agente_origem):
            return await validador(entrega.conteudo)
            
        return True  # Agentes sem validação específica
        
    async def _validar_codigo(self, conteudo: dict) -> bool:
        """Valida entregas de código."""
        if "acao" not in conteudo:
            return False
            
        # Ações permitidas específicas por agente
        acoes_permitidas = {
            "revisar": ["status"],
            "implementar": ["codigo"],
            "planejar": ["tarefa"],
            "inicio": []
        }
        
        acao = conteudo["acao"]
        if acao not in acoes_permitidas:
            return False
            
        # Valida campos obrigatórios para a ação
        campos_obrigatorios = acoes_permitidas[acao]
        for campo in campos_obrigatorios:
            if campo not in conteudo:
                return False
                
        return True
        
    async def _validar_interface(self, conteudo: dict) -> bool:
        """Valida entregas de interface."""
        return "componentes" in conteudo and "estilos" in conteudo
        
    async def _validar_calculos(self, conteudo: dict) -> bool:
        """Valida entregas matemáticas."""
        return "resultados" in conteudo and "metodologia" in conteudo
        
    async def _validar_documentacao(self, conteudo: dict) -> bool:
        """Valida entregas de documentação."""
        return "conteudo" in conteudo and "formato" in conteudo
        
    def _validar_integridade(self, entrega: Entrega) -> bool:
        """Valida a integridade geral da entrega."""
        # Valida timestamp
        if entrega.timestamp > datetime.now():
            return False
            
        # Valida consistência entre origem e destino
        if entrega.agente_origem == entrega.agente_destino and entrega.agente_destino != "distribuidor":
            return False
            
        return True
        
    async def _validar_sintaxe(self, codigo: str) -> bool:
        """Valida a sintaxe do código."""
        # Implementação específica de validação de sintaxe
        return True
        
    async def _validar_estilo(self, codigo: str) -> bool:
        """Valida o estilo do código."""
        # Implementação específica de validação de estilo
        return True
        
    async def _validar_seguranca(self, codigo: str) -> bool:
        """Valida aspectos de segurança do código."""
        # Implementação específica de validação de segurança
        return True
        
    def _validar_restricao(self, restricao: dict, conteudo: dict) -> bool:
        """Valida uma restrição específica no conteúdo."""
        tipo = restricao.get("tipo")
        valor = restricao.get("valor")
        campo = restricao.get("campo")
        
        if not all([tipo, valor, campo]):
            return False
            
        if campo not in conteudo:
            return False
            
        validacoes = {
            "min": lambda x: x >= valor,
            "max": lambda x: x <= valor,
            "igual": lambda x: x == valor,
            "diferente": lambda x: x != valor,
            "contem": lambda x: valor in x,
            "tamanho": lambda x: len(x) == valor
        }
        
        if validador := validacoes.get(tipo):
            return validador(conteudo[campo])
            
        return False
        
    def _gerar_hash_entrega(self, entrega: Entrega) -> str:
        """Gera um hash único para a entrega."""
        return f"{entrega.agente_origem}_{entrega.agente_destino}_{entrega.timestamp.isoformat()}"
        
    def limpar_cache(self):
        """Limpa o cache de validações."""
        self._cache.clear()
        self.logger.info("Cache de validações limpo")