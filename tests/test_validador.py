"""
Testes unitários e de integração para o ValidadorEscopo.
"""

import pytest
import asyncio
from typing import Dict, Any
from scripts.core.validador_escopo import (
    ValidadorEscopo,
    StatusValidacao,
    ResultadoValidacao
)
from scripts.core.validacoes import (
    validar_dimensoes_container,
    validar_produtos,
    validar_alocacao,
    validar_restricoes_ergonomicas
)
from scripts.core.models import ContainerConfig
from scripts.core.agentes_comunicacao import AgenteComunicacao, TipoMensagem

# Fixtures
@pytest.fixture
def validador():
    """Fixture que fornece uma instância do ValidadorEscopo."""
    return ValidadorEscopo(max_workers=2)

@pytest.fixture
def container_valido():
    """Fixture que fornece um container válido."""
    return ContainerConfig(dx=100, dy=100, dz=100, quantidade=1)

@pytest.fixture
def produtos_validos():
    """Fixture que fornece uma lista de produtos válidos."""
    return [
        {
            'dims': (10, 10, 10),
            'peso': 2.5,
            'categoria': 'Utilidades',
            'demanda': 10
        },
        {
            'dims': (20, 20, 20),
            'peso': 5.0,
            'categoria': 'Brinquedos',
            'demanda': 5
        }
    ]

@pytest.fixture
def alocacoes_validas():
    """Fixture que fornece alocações válidas."""
    return [
        (0, 0, 0, 0),      # Produto 0 na origem
        (20, 0, 0, 1)      # Produto 1 ao lado
    ]

# Testes Unitários
@pytest.mark.asyncio
async def test_registrar_validacao(validador):
    """Testa registro de nova validação."""
    async def func_teste(dados: Dict[str, Any]) -> Dict[str, Any]:
        return {'valido': True}

    await validador.registrar_validacao('teste', func_teste)
    assert 'teste' in validador.validacoes_registradas

@pytest.mark.asyncio
async def test_validar_entrega_inexistente(validador):
    """Testa validação de entrega não registrada."""
    resultado = await validador.validar_entrega('nao_existe', {})
    assert resultado.status == StatusValidacao.ERRO
    assert "não encontrada" in resultado.mensagem

@pytest.mark.asyncio
async def test_validar_container(validador, container_valido):
    """Testa validação de container."""
    await validador.registrar_validacao(
        'container',
        validar_dimensoes_container
    )
    
    resultado = await validador.validar_entrega(
        'container',
        {'container': container_valido}
    )
    
    assert resultado.status == StatusValidacao.CONCLUIDO
    assert resultado.detalhes['valido'] is True

@pytest.mark.asyncio
async def test_validar_produtos(validador, container_valido, produtos_validos):
    """Testa validação de produtos."""
    await validador.registrar_validacao(
        'produtos',
        validar_produtos
    )
    
    dados = {
        'container': container_valido,
        'produtos': produtos_validos
    }
    
    resultado = await validador.validar_entrega('produtos', dados)
    assert resultado.status == StatusValidacao.CONCLUIDO
    assert resultado.detalhes['valido'] is True

@pytest.mark.asyncio
async def test_validar_alocacao(validador, container_valido, produtos_validos, alocacoes_validas):
    """Testa validação de alocação."""
    await validador.registrar_validacao(
        'alocacao',
        validar_alocacao
    )
    
    dados = {
        'container': container_valido,
        'produtos': produtos_validos,
        'alocacoes': alocacoes_validas
    }
    
    resultado = await validador.validar_entrega('alocacao', dados)
    assert resultado.status == StatusValidacao.CONCLUIDO
    assert resultado.detalhes['valido'] is True

@pytest.mark.asyncio
async def test_validar_restricoes_ergonomicas(validador, produtos_validos, alocacoes_validas):
    """Testa validação de restrições ergonômicas."""
    await validador.registrar_validacao(
        'ergonomia',
        validar_restricoes_ergonomicas
    )
    
    dados = {
        'produtos': produtos_validos,
        'alocacoes': alocacoes_validas
    }
    
    resultado = await validador.validar_entrega('ergonomia', dados)
    assert resultado.status == StatusValidacao.CONCLUIDO
    assert resultado.detalhes['valido'] is True

@pytest.mark.asyncio
async def test_validar_multiplos(validador, container_valido, produtos_validos):
    """Testa validação múltipla em paralelo."""
    # Registra validações
    await validador.registrar_validacao('container', validar_dimensoes_container)
    await validador.registrar_validacao('produtos', validar_produtos)
    
    # Prepara dados
    validacoes = [
        {
            'nome': 'container',
            'dados': {'container': container_valido}
        },
        {
            'nome': 'produtos',
            'dados': {
                'container': container_valido,
                'produtos': produtos_validos
            }
        }
    ]
    
    resultados = await validador.validar_multiplos(validacoes)
    assert len(resultados) == 2
    assert all(r.status == StatusValidacao.CONCLUIDO for r in resultados.values())

# Testes de Integração
@pytest.mark.asyncio
async def test_integracao_validador_agente(validador, container_valido, produtos_validos):
    """Testa integração entre ValidadorEscopo e AgenteComunicacao."""
    # Cria agentes
    agente1 = AgenteComunicacao("agente1", validador)
    agente2 = AgenteComunicacao("agente2", validador)
    
    # Registra validações
    await validador.registrar_validacao('container', validar_dimensoes_container)
    await validador.registrar_validacao('produtos', validar_produtos)
    
    # Prepara mensagem com validações
    validacoes = [
        {
            'nome': 'container',
            'dados': {'container': container_valido}
        },
        {
            'nome': 'produtos',
            'dados': {
                'container': container_valido,
                'produtos': produtos_validos
            }
        }
    ]
    
    # Registra callback para processar resposta
    resultado_callback = None
    async def callback_teste(mensagem):
        nonlocal resultado_callback
        resultado_callback = mensagem
    
    await agente2.registrar_callback(TipoMensagem.SOLICITACAO, callback_teste)
    
    # Inicia processamento
    agente2.iniciar_processamento()
    
    # Envia mensagem com validações
    resultado = await agente1.enviar_mensagem(
        "agente2",
        TipoMensagem.SOLICITACAO,
        {"acao": "processar_produtos"},
        validacoes
    )
    
    # Aguarda processamento
    await asyncio.sleep(0.1)
    
    # Verifica resultados
    assert resultado.status == StatusValidacao.CONCLUIDO
    assert resultado_callback is not None
    assert resultado_callback['tipo'] == TipoMensagem.SOLICITACAO
    
    # Limpa
    await agente2.parar_processamento()

@pytest.mark.asyncio
async def test_fluxo_completo_validacao(validador, container_valido, produtos_validos, alocacoes_validas):
    """Testa fluxo completo de validação com múltiplos agentes."""
    # Cria agentes
    distribuidor = AgenteComunicacao("distribuidor", validador)
    planejador = AgenteComunicacao("planejador", validador)
    executor = AgenteComunicacao("executor", validador)
    
    # Registra todas as validações
    await validador.registrar_validacao('container', validar_dimensoes_container)
    await validador.registrar_validacao('produtos', validar_produtos)
    await validador.registrar_validacao('alocacao', validar_alocacao)
    await validador.registrar_validacao('ergonomia', validar_restricoes_ergonomicas)
    
    # Registra callbacks
    resultados = []
    async def callback_generico(mensagem):
        resultados.append(mensagem)
    
    await planejador.registrar_callback(TipoMensagem.SOLICITACAO, callback_generico)
    await executor.registrar_callback(TipoMensagem.SOLICITACAO, callback_generico)
    
    # Inicia processamento
    planejador.iniciar_processamento()
    executor.iniciar_processamento()
    
    # Simula fluxo completo
    # 1. Distribuidor → Planejador: Validação inicial
    await distribuidor.enviar_mensagem(
        "planejador",
        TipoMensagem.SOLICITACAO,
        {
            "acao": "planejar",
            "container": container_valido,
            "produtos": produtos_validos
        },
        [
            {
                'nome': 'container',
                'dados': {'container': container_valido}
            },
            {
                'nome': 'produtos',
                'dados': {
                    'container': container_valido,
                    'produtos': produtos_validos
                }
            }
        ]
    )
    
    # 2. Planejador → Executor: Execução com validação
    await planejador.enviar_mensagem(
        "executor",
        TipoMensagem.SOLICITACAO,
        {
            "acao": "executar",
            "container": container_valido,
            "produtos": produtos_validos,
            "alocacoes": alocacoes_validas
        },
        [
            {
                'nome': 'alocacao',
                'dados': {
                    'container': container_valido,
                    'produtos': produtos_validos,
                    'alocacoes': alocacoes_validas
                }
            },
            {
                'nome': 'ergonomia',
                'dados': {
                    'produtos': produtos_validos,
                    'alocacoes': alocacoes_validas
                }
            }
        ]
    )
    
    # Aguarda processamento
    await asyncio.sleep(0.1)
    
    # Verifica resultados
    assert len(resultados) == 2  # Uma mensagem para cada agente
    assert all(r['tipo'] == TipoMensagem.SOLICITACAO for r in resultados)
    
    # Limpa
    await planejador.parar_processamento()
    await executor.parar_processamento()

# Testes de Erro
@pytest.mark.asyncio
async def test_validacao_com_erro(validador):
    """Testa tratamento de erro na validação."""
    async def validacao_com_erro(dados):
        raise ValueError("Erro simulado")
    
    await validador.registrar_validacao('erro', validacao_com_erro)
    resultado = await validador.validar_entrega('erro', {})
    
    assert resultado.status == StatusValidacao.ERRO
    assert "Erro simulado" in resultado.mensagem

@pytest.mark.asyncio
async def test_container_invalido(validador):
    """Testa validação com container inválido."""
    container_invalido = ContainerConfig(dx=-1, dy=100, dz=100, quantidade=1)
    
    await validador.registrar_validacao('container', validar_dimensoes_container)
    resultado = await validador.validar_entrega(
        'container',
        {'container': container_invalido}
    )
    
    assert resultado.status == StatusValidacao.CONCLUIDO
    assert resultado.detalhes['valido'] is False