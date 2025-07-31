"""
Middleware de interceptação para garantir fluxo correto entre agentes.
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class Interceptacao:
    timestamp: datetime
    origem: str
    destino: str
    tipo_operacao: str
    conteudo: dict
    sequencia_atual: list

class InterceptadorAgentes:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._historico: Dict[str, Interceptacao] = {}
        self._sequencia_atual: list = []
        self._ciclos_ativos: Dict[str, set] = {}
        self._max_profundidade = 5
        
    async def interceptar(
        self,
        origem: str,
        destino: str,
        operacao: str,
        conteudo: dict,
        profundidade: int = 0
    ) -> bool:
        if profundidade >= self._max_profundidade:
            self.logger.error(f"Profundidade máxima excedida: {profundidade}")
            return False
            
        # Detecta ciclos
        if origem not in self._ciclos_ativos:
            self._ciclos_ativos[origem] = set()
            
        if destino in self._ciclos_ativos[origem]:
            self.logger.error(f"Ciclo detectado: {origem} -> {destino}")
            return False
            
        self._ciclos_ativos[origem].add(destino)
        """Intercepta e valida uma operação entre agentes."""
        
        interceptacao = Interceptacao(
            timestamp=datetime.now(),
            origem=origem,
            destino=destino,
            tipo_operacao=operacao,
            conteudo=conteudo,
            sequencia_atual=self._sequencia_atual.copy()
        )
        
        # Valida se é primeira operação
        if not self._sequencia_atual:
            if destino != "distribuidor":
                self.logger.error(f"Primeira operação deve ser para o distribuidor, não {destino}")
                return False
                
        # Valida sequência de agentes
        if not self._validar_sequencia(origem, destino):
            self.logger.error(f"Sequência inválida: {origem} -> {destino}")
            return False
            
        # Registra operação
        self._registrar_operacao(interceptacao)
        
        # Atualiza sequência
        self._sequencia_atual.append(destino)
        
        return True
        
    def _validar_sequencia(self, origem: str, destino: str) -> bool:
        """Valida se a sequência de agentes está correta."""
        
        # Primeira operação deve ser para o distribuidor
        if not self._sequencia_atual and destino != "distribuidor":
            return False
            
        # Distribuidor só pode ser chamado no início
        if destino == "distribuidor" and self._sequencia_atual:
            return False
            
        # Planejador deve ser chamado após distribuidor
        if destino == "planejador_head" and (not self._sequencia_atual or self._sequencia_atual[-1] != "distribuidor"):
            return False
            
        # Revisor final deve ser o último e só pode ser chamado após execução completa
        if destino == "revisor_final":
            if not self._sequencia_atual or "engenheiro_de_software" not in self._sequencia_atual:
                return False
            
        return True
        
    def _registrar_operacao(self, interceptacao: Interceptacao) -> None:
        """Registra uma operação no histórico."""
        operacao_id = f"{interceptacao.timestamp.isoformat()}_{interceptacao.origem}_{interceptacao.destino}"
        self._historico[operacao_id] = interceptacao
        
        self.logger.info(
            f"Operação registrada: {interceptacao.origem} -> {interceptacao.destino} "
            f"({interceptacao.tipo_operacao})"
        )
        
    def obter_historico(self) -> Dict[str, Interceptacao]:
        """Retorna o histórico de operações."""
        return self._historico.copy()
        
    def obter_sequencia_atual(self) -> list:
        """Retorna a sequência atual de agentes."""
        return self._sequencia_atual.copy()
        
    def limpar_sequencia(self) -> None:
        """Limpa a sequência atual de agentes."""
        self._sequencia_atual.clear()
        self.logger.info("Sequência de agentes limpa")