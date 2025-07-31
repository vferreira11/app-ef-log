"""
🤖 SISTEMA DE REGISTRO DE AGENTES
==================================

Este arquivo mantém o estado do sistema de agentes para GitHub Copilot.
Atualizado automaticamente conforme agentes são ativados/desativados.

IMPORTANTE: Este arquivo é apenas para tracking interno.
O sistema funciona nativamente através dos prompts do GitHub Copilot.
"""

import json
import datetime
from typing import Optional, Dict, Any

class RegistroAgentes:
    """Sistema de tracking de agentes ativos (apenas para logging)"""
    
    def __init__(self):
        self.agente_ativo: Optional[str] = None
        self.sessao_id: Optional[str] = None
        self.historico: list = []
        self.contexto_acumulado: Dict[str, Any] = {}
        
    def log_ativacao(self, agente: str, trigger: str, contexto: str = ""):
        """Registra ativação de agente"""
        timestamp = datetime.datetime.now().isoformat()
        
        registro = {
            "timestamp": timestamp,
            "acao": "ATIVACAO",
            "agente": agente,
            "trigger": trigger,
            "contexto": contexto,
            "agente_anterior": self.agente_ativo
        }
        
        self.agente_ativo = agente
        self.historico.append(registro)
        
        print(f"📝 [{timestamp}] {agente.upper()} ativado via '{trigger}'")
        
    def log_acao(self, acao: str, detalhes: Dict[str, Any]):
        """Registra ação do agente ativo"""
        if not self.agente_ativo:
            return
            
        timestamp = datetime.datetime.now().isoformat()
        
        registro = {
            "timestamp": timestamp,
            "agente": self.agente_ativo,
            "acao": acao,
            "detalhes": detalhes
        }
        
        self.historico.append(registro)
        
    def reset_contexto(self):
        """Reset do sistema"""
        timestamp = datetime.datetime.now().isoformat()
        
        if self.agente_ativo:
            print(f"🔄 [{timestamp}] Reset: {self.agente_ativo.upper()} desativado")
            
        self.agente_ativo = None
        self.sessao_id = None
        self.contexto_acumulado.clear()
        
    def status_atual(self) -> Dict[str, Any]:
        """Retorna status atual do sistema"""
        return {
            "agente_ativo": self.agente_ativo,
            "sessao_id": self.sessao_id,
            "total_acoes": len(self.historico),
            "ultima_atividade": self.historico[-1]["timestamp"] if self.historico else None
        }

# Instância global para tracking (não interfere no funcionamento)
_registro = RegistroAgentes()

def get_agente_ativo() -> Optional[str]:
    """Retorna agente atualmente ativo"""
    return _registro.agente_ativo

def get_status() -> Dict[str, Any]:
    """Retorna status completo do sistema"""
    return _registro.status_atual()

def log_trigger(agente: str, trigger: str, contexto: str = ""):
    """Log de ativação via trigger"""
    _registro.log_ativacao(agente, trigger, contexto)

def log_acao_agente(acao: str, **kwargs):
    """Log de ação do agente ativo"""
    _registro.log_acao(acao, kwargs)

def reset_sistema():
    """Reset completo do sistema"""
    _registro.reset_contexto()

# Exemplo de uso interno (não necessário para funcionamento)
if __name__ == "__main__":
    # Simulação de uso
    log_trigger("frontend_expert", "@frontend", "Otimização de landing page")
    log_acao_agente("analise_codigo", arquivos=["src/pages/landing.tsx"])
    log_acao_agente("criar_branch", nome="feature/frontend-landing-optimization")
    
    print(f"Status: {get_status()}")
