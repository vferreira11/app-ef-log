"""
Módulo de formatação de dados.
Centraliza funções de formatação para consistência.
"""

from typing import Union, Tuple, Dict, Any
import locale

# Configura locale para formatação BR
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def format_br_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Formata números no padrão brasileiro.
    
    Args:
        value: Número a formatar
        decimals: Casas decimais
        
    Returns:
        String formatada
    """
    try:
        if decimals == 0:
            return f"{int(value):,}".replace(',', '.')
        else:
            formatted = f"{value:,.{decimals}f}"
            parts = formatted.split('.')
            if len(parts) > 1:
                decimal_part = parts[-1]
                integer_part = '.'.join(parts[:-1]).replace(',', '.')
                return f"{integer_part},{decimal_part}"
            return formatted.replace(',', '.')
    except Exception as e:
        return str(value)

def format_br_currency(value: float) -> str:
    """
    Formata valores monetários no padrão brasileiro.
    
    Args:
        value: Valor a formatar
        
    Returns:
        String formatada como moeda
    """
    try:
        return f"R$ {format_br_number(value, 2)}"
    except Exception as e:
        return f"R$ {value}"

def format_br_percentage(value: float) -> str:
    """
    Formata porcentagens no padrão brasileiro.
    
    Args:
        value: Valor da porcentagem
        
    Returns:
        String formatada
    """
    try:
        return f"{format_br_number(value, 1)}%"
    except Exception as e:
        return f"{value}%"

def format_dimensions(dimensions: Tuple[int, int, int]) -> str:
    """
    Formata dimensões 3D.
    
    Args:
        dimensions: Tupla (x, y, z)
        
    Returns:
        String formatada
    """
    try:
        return f"{dimensions[0]}×{dimensions[1]}×{dimensions[2]}"
    except Exception as e:
        return str(dimensions)

def format_placement(placement: Dict[str, Any]) -> str:
    """
    Formata dados de alocação.
    
    Args:
        placement: Dicionário com dados
        
    Returns:
        String formatada
    """
    try:
        x = placement.get('x', 0)
        y = placement.get('y', 0)
        z = placement.get('z', 0)
        return f"({x}, {y}, {z})"
    except Exception as e:
        return str(placement)

def format_volume(value: Union[int, float], unit: str = "cm³") -> str:
    """
    Formata volumes com unidade.
    
    Args:
        value: Valor do volume
        unit: Unidade de medida
        
    Returns:
        String formatada
    """
    try:
        return f"{format_br_number(value)} {unit}"
    except Exception as e:
        return f"{value} {unit}"

def format_weight(value: Union[int, float], unit: str = "kg") -> str:
    """
    Formata pesos com unidade.
    
    Args:
        value: Valor do peso
        unit: Unidade de medida
        
    Returns:
        String formatada
    """
    try:
        return f"{format_br_number(value, 3)} {unit}"
    except Exception as e:
        return f"{value} {unit}"