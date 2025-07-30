"""
Testes para o ValidadorEscopo e sistema de comunicação entre agentes.
"""
import pytest
import asyncio
from datetime import datetime
from scripts.core.validador_escopo import ValidadorEscopo, Entrega, ResultadoValidacao
from scripts.core.agentes_comunicacao import AgenteComunicacao, Agente

class AgenteEngenheiro(Agente):
    async def processar_mensagem(self, entrega: Entrega):
        return {"codigo": "def test(): pass", "tipo": "python"}

class AgentePlanejador(Agente):
    async def processar_mensagem(self, entrega: Entrega):
        return {"plano": "Implementar feature X", "etapas": ["A", "B"]}

@pytest.mark.asyncio
async def test_validacao_escopo():
    validador = ValidadorEscopo()
    
    entrega = Entrega(
        agente_origem="engenheiro_de_software",
        agente_destino="planejador_head",
        conteudo={"codigo": "def test(): pass"},
        timestamp=datetime.now(),
        escopo_original={
            "campos_obrigatorios": ["codigo"],
            "tipos": {"codigo": str}
        }
    )
    
    resultado = await validador.validar_entrega(entrega)
    assert resultado.valido == True
    assert "timestamp_validacao" in resultado.detalhes

@pytest.mark.asyncio
async def test_validacao_escopo_invalido():
    validador = ValidadorEscopo()
    
    entrega = Entrega(
        agente_origem="engenheiro_de_software",
        agente_destino="planejador_head",
        conteudo={},  # Falta campo obrigatório
        timestamp=datetime.now(),
        escopo_original={
            "campos_obrigatorios": ["codigo"],
            "tipos": {"codigo": str}
        }
    )
    
    resultado = await validador.validar_entrega(entrega)
    assert resultado.valido == False
    assert "Campo obrigatório ausente" in resultado.mensagem

@pytest.mark.asyncio
async def test_comunicacao_entre_agentes():
    comunicador = AgenteComunicacao()
    
    engenheiro = AgenteEngenheiro("engenheiro_de_software", comunicador)
    planejador = AgentePlanejador("planejador_head", comunicador)
    
    resultado = await engenheiro.enviar_para(
        "planejador_head",
        {"codigo": "def test(): pass"},
        {
            "campos_obrigatorios": ["codigo"],
            "tipos": {"codigo": str}
        }
    )
    
    assert resultado.valido == True

@pytest.mark.asyncio
async def test_cache_validacao():
    validador = ValidadorEscopo()
    
    entrega = Entrega(
        agente_origem="engenheiro_de_software",
        agente_destino="planejador_head",
        conteudo={"codigo": "def test(): pass"},
        timestamp=datetime.now(),
        escopo_original={
            "campos_obrigatorios": ["codigo"],
            "tipos": {"codigo": str}
        }
    )
    
    # Primeira validação
    resultado1 = await validador.validar_entrega(entrega)
    assert resultado1.valido == True
    
    # Segunda validação (deve usar cache)
    resultado2 = await validador.validar_entrega(entrega)
    assert resultado2.valido == True
    assert resultado1.detalhes["timestamp_validacao"] == resultado2.detalhes["timestamp_validacao"]

@pytest.mark.asyncio
async def test_validacoes_em_paralelo():
    validador = ValidadorEscopo()
    
    entregas = [
        Entrega(
            agente_origem="engenheiro_de_software",
            agente_destino="planejador_head",
            conteudo={"codigo": f"def test{i}(): pass"},
            timestamp=datetime.now(),
            escopo_original={
                "campos_obrigatorios": ["codigo"],
                "tipos": {"codigo": str}
            }
        )
        for i in range(5)
    ]
    
    resultados = await asyncio.gather(
        *[validador.validar_entrega(e) for e in entregas]
    )
    
    assert all(r.valido for r in resultados)
    assert len(set(r.detalhes["timestamp_validacao"] for r in resultados)) == 5