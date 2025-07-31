"""
Módulo de tratamento de erros centralizado.
Fornece classes e decoradores para gerenciamento de erros.
"""

import logging
import traceback
from functools import wraps
from typing import Optional, Any, Callable
import streamlit as st

# Configuração de logging
logger = logging.getLogger(__name__)

class AppError(Exception):
    """
    Exceção base para erros da aplicação.
    Permite categorização e formatação consistente.
    """
    def __init__(self, message: str, category: str = "error", details: Optional[str] = None):
        self.message = message
        self.category = category
        self.details = details
        super().__init__(message)

class ValidationError(AppError):
    """Erro de validação de dados."""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "validation", details)

class ProcessingError(AppError):
    """Erro durante processamento."""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "processing", details)

class VisualizationError(AppError):
    """Erro na visualização."""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "visualization", details)

def show_error(error: AppError):
    """
    Exibe erro na interface de forma apropriada.
    
    Args:
        error: Exceção a ser exibida
    """
    if error.category == "validation":
        st.warning(error.message)
    elif error.category == "error":
        st.error(error.message)
    else:
        st.error(f"Erro ({error.category}): {error.message}")
        
    if error.details and st.checkbox("Ver detalhes"):
        st.code(error.details)

def error_handler(show_traceback: bool = False) -> Callable:
    """
    Decorador para tratamento de erros.
    
    Args:
        show_traceback: Se deve mostrar stack trace
        
    Returns:
        Decorator configurado
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except AppError as e:
                show_error(e)
                if show_traceback:
                    logger.error(traceback.format_exc())
            except Exception as e:
                error = AppError(str(e), "unexpected", traceback.format_exc())
                show_error(error)
                logger.error(traceback.format_exc())
        return wrapper
    return decorator

def validate_input(condition: bool, message: str):
    """
    Valida uma condição, lançando erro se falsa.
    
    Args:
        condition: Condição a validar
        message: Mensagem de erro
    
    Raises:
        ValidationError: Se condição é falsa
    """
    if not condition:
        raise ValidationError(message)

def validate_processing(condition: bool, message: str):
    """
    Valida uma condição de processamento.
    
    Args:
        condition: Condição a validar
        message: Mensagem de erro
    
    Raises:
        ProcessingError: Se condição é falsa
    """
    if not condition:
        raise ProcessingError(message)

def validate_visualization(condition: bool, message: str):
    """
    Valida uma condição de visualização.
    
    Args:
        condition: Condição a validar
        message: Mensagem de erro
    
    Raises:
        VisualizationError: Se condição é falsa
    """
    if not condition:
        raise VisualizationError(message)