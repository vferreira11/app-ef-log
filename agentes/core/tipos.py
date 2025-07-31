"""
Tipos e estruturas base para o sistema de agentes com personas.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class TipoAgente(Enum):
    """Tipos de agentes disponíveis no sistema."""
    FRONT_END = "front_end"
    BACK_END = "back_end"
    FULLSTACK = "fullstack"
    DEVOPS = "devops"
    IA_SPECIALIST = "ia_specialist"
    SECURITY = "security"
    DESIGNER = "designer"
    PROJECT_MANAGER = "project_manager"
    CONSULTOR = "consultor"

@dataclass
class PersonaAgente:
    """Define a persona de um agente especializado."""
    nome: str
    tipo: TipoAgente
    emoji: str
    cor_codigo: str
    especialidades: List[str]
    linguagens: List[str]
    frameworks: List[str]
    ferramentas: List[str]
    estilo_comunicacao: str
    comandos_especiais: List[str]
    prompt_sistema: str
    
    def __post_init__(self):
        """Inicialização pós-criação da persona."""
        self.ativo = False
        self.contexto_atual = {}

@dataclass
class ContextoTrabalho:
    """Contexto atual de trabalho do agente."""
    projeto_atual: Optional[str] = None
    tecnologias_stack: List[str] = None
    fase_projeto: str = "planejamento"
    objetivos: List[str] = None
    restricoes: List[str] = None
    preferencias_usuario: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tecnologias_stack is None:
            self.tecnologias_stack = []
        if self.objetivos is None:
            self.objetivos = []
        if self.restricoes is None:
            self.restricoes = []
        if self.preferencias_usuario is None:
            self.preferencias_usuario = {}

@dataclass
class ResultadoOperacao:
    """Resultado de uma operação do agente."""
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    sugestoes: List[str] = None
    proximos_passos: List[str] = None
    
    def __post_init__(self):
        if self.sugestoes is None:
            self.sugestoes = []
        if self.proximos_passos is None:
            self.proximos_passos = []
