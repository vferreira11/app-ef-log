"""
Implementa validações intermediárias para o fluxo de agentes.
"""

from typing import Dict, Any, List, Tuple
import logging
from .models import ContainerConfig, BlockType, Placement

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validar_dimensoes_container(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida dimensões e capacidade do container.
    
    Args:
        dados: Dicionário com configuração do container
        
    Returns:
        Resultado da validação com status e detalhes
    """
    try:
        container = dados.get('container')
        if not isinstance(container, ContainerConfig):
            return {
                'valido': False,
                'mensagem': 'Dados de container inválidos'
            }

        # Valida dimensões mínimas
        if (container.dx <= 0 or container.dy <= 0 or container.dz <= 0):
            return {
                'valido': False,
                'mensagem': 'Dimensões do container devem ser positivas'
            }

        # Valida quantidade
        if container.quantidade <= 0:
            return {
                'valido': False,
                'mensagem': 'Quantidade de containers deve ser positiva'
            }

        return {
            'valido': True,
            'mensagem': 'Container válido',
            'detalhes': {
                'volume_total': container.volume_total,
                'dimensoes': container.dimensions()
            }
        }

    except Exception as e:
        logger.error(f"Erro ao validar container: {str(e)}")
        return {
            'valido': False,
            'mensagem': f'Erro na validação: {str(e)}'
        }

def validar_produtos(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida dados dos produtos a serem empacotados.
    
    Args:
        dados: Dicionário com lista de produtos e suas propriedades
        
    Returns:
        Resultado da validação
    """
    try:
        produtos = dados.get('produtos', [])
        if not produtos:
            return {
                'valido': False,
                'mensagem': 'Lista de produtos vazia'
            }

        container = dados.get('container')
        if not container:
            return {
                'valido': False,
                'mensagem': 'Container não especificado'
            }

        erros = []
        for i, produto in enumerate(produtos):
            # Valida dimensões
            dims = produto.get('dims')
            if not dims or len(dims) != 3:
                erros.append(f'Produto {i}: dimensões inválidas')
                continue

            # Valida se cabe no container
            if (dims[0] > container.dx or 
                dims[1] > container.dy or 
                dims[2] > container.dz):
                erros.append(f'Produto {i}: maior que o container')

            # Valida peso
            peso = produto.get('peso', 0)
            if peso <= 0:
                erros.append(f'Produto {i}: peso inválido')

            # Valida categoria
            categoria = produto.get('categoria', '')
            if not categoria:
                erros.append(f'Produto {i}: categoria não especificada')

        if erros:
            return {
                'valido': False,
                'mensagem': 'Produtos com erros',
                'detalhes': {'erros': erros}
            }

        return {
            'valido': True,
            'mensagem': 'Produtos válidos',
            'detalhes': {
                'total_produtos': len(produtos)
            }
        }

    except Exception as e:
        logger.error(f"Erro ao validar produtos: {str(e)}")
        return {
            'valido': False,
            'mensagem': f'Erro na validação: {str(e)}'
        }

def validar_alocacao(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida resultado de alocação de produtos no container.
    
    Args:
        dados: Dicionário com alocações e configurações
        
    Returns:
        Resultado da validação
    """
    try:
        container = dados.get('container')
        alocacoes = dados.get('alocacoes', [])
        produtos = dados.get('produtos', [])

        if not container or not alocacoes or not produtos:
            return {
                'valido': False,
                'mensagem': 'Dados incompletos'
            }

        # Verifica colisões
        ocupado = set()
        erros = []
        for i, alocacao in enumerate(alocacoes):
            if len(alocacao) < 4:
                erros.append(f'Alocação {i}: formato inválido')
                continue

            x, y, z, idx = alocacao[:4]
            if idx >= len(produtos):
                erros.append(f'Alocação {i}: índice de produto inválido')
                continue

            # Obtém dimensões do produto
            dims = produtos[idx].get('dims')
            if not dims:
                erros.append(f'Alocação {i}: produto sem dimensões')
                continue

            # Verifica limites do container
            if (x + dims[0] > container.dx or 
                y + dims[1] > container.dy or 
                z + dims[2] > container.dz):
                erros.append(f'Alocação {i}: fora do container')
                continue

            # Verifica colisões
            for dx in range(dims[0]):
                for dy in range(dims[1]):
                    for dz in range(dims[2]):
                        pos = (x + dx, y + dy, z + dz)
                        if pos in ocupado:
                            erros.append(f'Alocação {i}: colisão na posição {pos}')
                        ocupado.add(pos)

        if erros:
            return {
                'valido': False,
                'mensagem': 'Alocação com erros',
                'detalhes': {'erros': erros}
            }

        # Calcula estatísticas
        volume_ocupado = sum(p['dims'][0] * p['dims'][1] * p['dims'][2] 
                           for p in produtos)
        eficiencia = (volume_ocupado / container.volume_total) * 100

        return {
            'valido': True,
            'mensagem': 'Alocação válida',
            'detalhes': {
                'total_alocacoes': len(alocacoes),
                'volume_ocupado': volume_ocupado,
                'eficiencia': f'{eficiencia:.2f}%'
            }
        }

    except Exception as e:
        logger.error(f"Erro ao validar alocação: {str(e)}")
        return {
            'valido': False,
            'mensagem': f'Erro na validação: {str(e)}'
        }

def validar_restricoes_ergonomicas(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida restrições ergonômicas das alocações.
    
    Args:
        dados: Dicionário com alocações e dados dos produtos
        
    Returns:
        Resultado da validação
    """
    try:
        alocacoes = dados.get('alocacoes', [])
        produtos = dados.get('produtos', [])

        if not alocacoes or not produtos:
            return {
                'valido': False,
                'mensagem': 'Dados incompletos'
            }

        erros = []
        alertas = []

        for i, alocacao in enumerate(alocacoes):
            if len(alocacao) < 4:
                continue

            x, y, z, idx = alocacao[:4]
            produto = produtos[idx]
            peso = produto.get('peso', 0)
            categoria = produto.get('categoria', '')

            # Valida altura para produtos pesados
            if peso > 5 and z > 120:  # Acima de 120cm
                erros.append(
                    f'Alocação {i}: produto pesado ({peso}kg) muito alto (z={z}cm)'
                )

            # Valida produtos frágeis
            if categoria == 'Frágil' and z < 30:  # Abaixo de 30cm
                alertas.append(
                    f'Alocação {i}: produto frágil próximo ao chão (z={z}cm)'
                )

            # Valida altura máxima por peso
            altura_maxima = {
                (0, 2): 180,    # Até 2kg: 180cm
                (2, 5): 150,    # 2-5kg: 150cm
                (5, 10): 120,   # 5-10kg: 120cm
                (10, float('inf')): 60  # >10kg: 60cm
            }

            for faixa, max_altura in altura_maxima.items():
                if faixa[0] < peso <= faixa[1] and z > max_altura:
                    erros.append(
                        f'Alocação {i}: produto de {peso}kg acima da altura máxima '
                        f'recomendada ({max_altura}cm)'
                    )

        if erros:
            return {
                'valido': False,
                'mensagem': 'Violações ergonômicas encontradas',
                'detalhes': {
                    'erros': erros,
                    'alertas': alertas
                }
            }

        return {
            'valido': True,
            'mensagem': 'Restrições ergonômicas respeitadas',
            'detalhes': {
                'alertas': alertas
            } if alertas else None
        }

    except Exception as e:
        logger.error(f"Erro ao validar restrições ergonômicas: {str(e)}")
        return {
            'valido': False,
            'mensagem': f'Erro na validação: {str(e)}'
        }