"""
Testes para o interceptador de agentes.
"""
import pytest
from datetime import datetime
from scripts.core.interceptador import InterceptadorAgentes

@pytest.fixture
def interceptador():
    return InterceptadorAgentes()

@pytest.mark.asyncio
async def test_primeira_operacao_distribuidor(interceptador):
    """Testa se primeira operação deve ser para o distribuidor."""
    
    # Tenta enviar para outro agente primeiro
    resultado = await interceptador.interceptar(
        "usuario",
        "planejador_head",
        "inicio",
        {}
    )
    assert resultado == False
    
    # Envia para distribuidor
    resultado = await interceptador.interceptar(
        "usuario",
        "distribuidor",
        "inicio",
        {}
    )
    assert resultado == True
    
    # Verifica sequência
    assert interceptador.obter_sequencia_atual() == ["distribuidor"]

@pytest.mark.asyncio
async def test_sequencia_valida(interceptador):
    """Testa sequência válida de operações."""
    
    # Fluxo correto: usuario -> distribuidor -> planejador -> agente
    assert await interceptador.interceptar("usuario", "distribuidor", "inicio", {})
    assert await interceptador.interceptar("distribuidor", "planejador_head", "planejar", {})
    assert await interceptador.interceptar("planejador_head", "engenheiro_de_software", "executar", {})
    
    sequencia = interceptador.obter_sequencia_atual()
    assert sequencia == ["distribuidor", "planejador_head", "engenheiro_de_software"]

@pytest.mark.asyncio
async def test_sequencia_invalida(interceptador):
    """Testa sequências inválidas de operações."""
    
    # Configura sequência inicial válida
    await interceptador.interceptar("usuario", "distribuidor", "inicio", {})
    await interceptador.interceptar("distribuidor", "planejador_head", "planejar", {})
    
    # Tenta chamar distribuidor novamente (deve falhar)
    resultado = await interceptador.interceptar(
        "usuario",
        "distribuidor",
        "inicio",
        {}
    )
    assert resultado == False
    
    # Tenta pular para revisor_final sem terminar (deve falhar)
    resultado = await interceptador.interceptar(
        "planejador_head",
        "revisor_final",
        "revisar",
        {}
    )
    assert resultado == False

@pytest.mark.asyncio
async def test_historico_operacoes(interceptador):
    """Testa registro de histórico de operações."""
    
    # Executa algumas operações
    await interceptador.interceptar("usuario", "distribuidor", "inicio", {"dado": 1})
    await interceptador.interceptar("distribuidor", "planejador_head", "planejar", {"dado": 2})
    
    # Verifica histórico
    historico = interceptador.obter_historico()
    assert len(historico) == 2
    
    # Verifica conteúdo do histórico
    ultima_operacao = list(historico.values())[-1]
    assert ultima_operacao.origem == "distribuidor"
    assert ultima_operacao.destino == "planejador_head"
    assert ultima_operacao.tipo_operacao == "planejar"
    assert ultima_operacao.conteudo == {"dado": 2}

@pytest.mark.asyncio
async def test_limpar_sequencia(interceptador):
    """Testa limpeza da sequência de operações."""
    
    # Configura algumas operações
    await interceptador.interceptar("usuario", "distribuidor", "inicio", {})
    await interceptador.interceptar("distribuidor", "planejador_head", "planejar", {})
    
    # Verifica sequência
    assert len(interceptador.obter_sequencia_atual()) == 2
    
    # Limpa sequência
    interceptador.limpar_sequencia()
    
    # Verifica se foi limpa
    assert len(interceptador.obter_sequencia_atual()) == 0
    
    # Verifica se pode iniciar nova sequência
    assert await interceptador.interceptar("usuario", "distribuidor", "inicio", {})