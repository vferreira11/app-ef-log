"""
Classe base para agentes especializados com personas.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from .tipos import PersonaAgente, ContextoTrabalho, ResultadoOperacao, TipoAgente
from .comunicacao import AgenteComunicacao

class BaseAgente(ABC):
    """Classe base para todos os agentes com personas."""
    
    def __init__(self, persona: PersonaAgente, comunicador: AgenteComunicacao):
        self.persona = persona
        self.comunicador = comunicador
        self.contexto = ContextoTrabalho()
        self.historico_operacoes = []
        self.estado_atual = "inativo"
        
    def ativar_persona(self, contexto_inicial: Optional[Dict[str, Any]] = None) -> ResultadoOperacao:
        """Ativa a persona do agente com contexto específico."""
        self.estado_atual = "ativo"
        self.persona.ativo = True
        
        if contexto_inicial:
            self._atualizar_contexto(contexto_inicial)
            
        mensagem = f"{self.persona.emoji} **{self.persona.nome}** ativado!\n"
        mensagem += f"🎯 Especialidades: {', '.join(self.persona.especialidades)}\n"
        mensagem += f"💻 Stack: {', '.join(self.persona.linguagens)}\n"
        mensagem += f"🔧 Ferramentas: {', '.join(self.persona.ferramentas)}\n"
        mensagem += f"📋 Comandos disponíveis: {', '.join(self.persona.comandos_especiais)}"
        
        return ResultadoOperacao(
            sucesso=True,
            mensagem=mensagem,
            dados={"persona_ativa": self.persona.nome, "contexto": self.contexto.__dict__}
        )
    
    def desativar_persona(self) -> ResultadoOperacao:
        """Desativa a persona do agente."""
        self.estado_atual = "inativo"
        self.persona.ativo = False
        
        return ResultadoOperacao(
            sucesso=True,
            mensagem=f"{self.persona.emoji} **{self.persona.nome}** desativado."
        )
    
    def _atualizar_contexto(self, novo_contexto: Dict[str, Any]):
        """Atualiza o contexto de trabalho do agente."""
        for key, value in novo_contexto.items():
            if hasattr(self.contexto, key):
                setattr(self.contexto, key, value)
    
    @abstractmethod
    async def processar_comando(self, comando: str, parametros: Dict[str, Any]) -> ResultadoOperacao:
        """Processa um comando específico da persona."""
        pass
    
    @abstractmethod
    def obter_sugestoes_contextuais(self) -> List[str]:
        """Retorna sugestões baseadas no contexto atual."""
        pass
    
    def _formatar_resposta_persona(self, conteudo: str) -> str:
        """Formata a resposta seguindo o estilo da persona."""
        header = f"{self.persona.emoji} **{self.persona.nome}**"
        
        if self.persona.estilo_comunicacao == "tecnico":
            return f"{header}\n\n🔧 **ANÁLISE TÉCNICA:**\n{conteudo}"
        elif self.persona.estilo_comunicacao == "criativo":
            return f"{header}\n\n🎨 **PROPOSTA CRIATIVA:**\n{conteudo}"
        elif self.persona.estilo_comunicacao == "direto":
            return f"{header}\n\n⚡ **AÇÃO DIRETA:**\n{conteudo}"
        else:
            return f"{header}\n\n{conteudo}"
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna o status atual do agente."""
        return {
            "nome": self.persona.nome,
            "tipo": self.persona.tipo.value,
            "ativo": self.persona.ativo,
            "estado": self.estado_atual,
            "contexto": self.contexto.__dict__,
            "ultima_atividade": datetime.now().isoformat()
        }
