"""
Teste de fluxo completo do sistema multiagente.
"""
import pytest
import asyncio
from datetime import datetime
from scripts.core.agentes_comunicacao import AgenteComunicacao, Agente
from scripts.core.validador_escopo import Entrega

class TestAgente(Agente):
    def __init__(self, nome: str, comunicador: AgenteComunicacao):
        super().__init__(nome, comunicador)
        self.mensagens_recebidas = []
        
    async def processar_mensagem(self, entrega: Entrega):
        self.mensagens_recebidas.append(entrega)
        return True

@pytest.mark.asyncio
async def test_fluxo_completo():
    """Testa fluxo completo passando por todos os agentes."""
    
    comunicador = AgenteComunicacao()
    
    # Cria instâncias dos agentes
    distribuidor = TestAgente("distribuidor", comunicador)
    planejador = TestAgente("planejador_head", comunicador)
    engenheiro = TestAgente("engenheiro_de_software", comunicador)
    revisor = TestAgente("revisor_final", comunicador)
    
    # Tenta começar pelo planejador (deve falhar)
    resultado = await distribuidor.enviar_para(
        "planejador_head",
        {"acao": "inicio"},
        {"campos_obrigatorios": ["acao"]}
    )
    assert resultado.valido == False
    assert "Operação bloqueada pelo interceptador" in resultado.mensagem
    
    # Fluxo correto: distribuidor -> planejador -> engenheiro -> revisor
    
    # 1. Início pelo distribuidor
    resultado = await distribuidor.enviar_para(
        "distribuidor",
        {"acao": "inicio"},
        {"campos_obrigatorios": ["acao"]}
    )
    assert resultado.valido == True
    
    # 2. Distribuidor -> Planejador
    resultado = await distribuidor.enviar_para(
        "planejador_head",
        {"acao": "planejar", "tarefa": "implementar feature"},
        {"campos_obrigatorios": ["acao", "tarefa"]}
    )
    assert resultado.valido == True
    
    # 3. Planejador -> Engenheiro
    resultado = await planejador.enviar_para(
        "engenheiro_de_software",
        {"acao": "implementar", "codigo": "def test(): pass"},
        {"campos_obrigatorios": ["acao", "codigo"]}
    )
    assert resultado.valido == True
    
    # 4. Engenheiro -> Revisor Final
    resultado = await engenheiro.enviar_para(
        "revisor_final",
        {"acao": "revisar", "status": "completo"},
        {"campos_obrigatorios": ["acao", "status"]}
    )
    assert resultado.valido == True
    
    # Verifica histórico de mensagens
    historico = comunicador.interceptador.obter_historico()
    sequencia = comunicador.interceptador.obter_sequencia_atual()
    
    # Valida sequência final
    assert sequencia == [
        "distribuidor",
        "planejador_head",
        "engenheiro_de_software",
        "revisor_final"
    ]
    
    # Valida que cada agente recebeu suas mensagens
    assert len(distribuidor.mensagens_recebidas) == 1
    assert len(planejador.mensagens_recebidas) == 1
    assert len(engenheiro.mensagens_recebidas) == 1
    assert len(revisor.mensagens_recebidas) == 1
    
    # Tenta enviar para distribuidor novamente (deve falhar)
    resultado = await revisor.enviar_para(
        "distribuidor",
        {"acao": "novo_ciclo"},
        {"campos_obrigatorios": ["acao"]}
    )
    assert resultado.valido == False
    assert "Operação bloqueada pelo interceptador" in resultado.mensagem