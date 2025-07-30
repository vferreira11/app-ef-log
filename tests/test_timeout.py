"""
Testes para timeout na comunicação entre agentes.
"""
import pytest
import asyncio
from datetime import datetime
from scripts.core.validador_escopo import ValidadorEscopo, Entrega, ResultadoValidacao
from scripts.core.agentes_comunicacao import AgenteComunicacao, Agente

class AgenteComDelayFixo(Agente):
    def __init__(self, nome: str, comunicador: AgenteComunicacao, delay: float):
        super().__init__(nome, comunicador)
        self.delay = delay
        
    async def processar_mensagem(self, entrega: Entrega):
        await asyncio.sleep(self.delay)
        # Simula processamento lento para forçar timeout
        await asyncio.sleep(2.0)
        return {"status": "ok"}

@pytest.mark.asyncio
async def test_timeout_comunicacao():
    comunicador = AgenteComunicacao()
    agente_lento = AgenteComDelayFixo("agente_lento", comunicador, delay=2.0)
    distribuidor = AgenteComDelayFixo("distribuidor", comunicador, delay=0.1)
    
    resultado = await comunicador.enviar_mensagem(
        "test",
        "distribuidor",
        {"teste": "timeout"},
        {"campos_obrigatorios": ["teste"]},
        timeout=1.0
    )
    
    assert resultado.valido == False
    assert "Timeout" in resultado.mensagem
    assert resultado.detalhes["timeout"] == 0.5  # Timeout é dividido entre validação e notificação

@pytest.mark.asyncio
async def test_timeout_validacao():
    validador = ValidadorEscopo()
    
    entrega = Entrega(
        agente_origem="test",
        agente_destino="distribuidor",
        conteudo={"teste": "timeout"},
        timestamp=datetime.now(),
        escopo_original={"campos_obrigatorios": ["teste"]}
    )
    
    # Simula validação lenta
    async def validacao_lenta(entrega):
        await asyncio.sleep(2.0)
        return ResultadoValidacao(valido=True, mensagem="Ok")
    
    validador._executar_validacao = validacao_lenta
    
    resultado = await validador.validar_entrega(entrega, timeout=1.0)
    
    assert resultado.valido == False
    assert "Timeout" in resultado.mensagem
    assert resultado.detalhes["timeout"] == 1.0

@pytest.mark.asyncio
async def test_timeout_em_cascata():
    comunicador = AgenteComunicacao()
    distribuidor = AgenteComDelayFixo("distribuidor", comunicador, delay=0.5)
    agente1 = AgenteComDelayFixo("agente1", comunicador, delay=0.5)
    agente2 = AgenteComDelayFixo("agente2", comunicador, delay=0.5)
    
    # Total delay seria 1.0s, mas timeout é 0.8s
    resultado = await comunicador.enviar_mensagem(
        "test",
        "distribuidor",
        {"teste": "cascata"},
        {"campos_obrigatorios": ["teste"]},
        timeout=0.8
    )
    
    assert resultado.valido == False
    assert "Timeout" in resultado.mensagem