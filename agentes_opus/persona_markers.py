"""
Sistema de Marcadores de Persona
Cria marcas visuais que sinalizam quando uma persona está envolvida no output
"""

import sys
from typing import Dict, Optional
from enum import Enum

class PersonaStyle(Enum):
    """Estilos visuais para diferentes tipos de persona"""
    FRONTEND = {"icon": "🎨", "color": "\033[94m", "border": "═"}  # Azul
    BACKEND = {"icon": "⚙️", "color": "\033[92m", "border": "━"}   # Verde
    DEVOPS = {"icon": "🔧", "color": "\033[93m", "border": "─"}    # Amarelo
    SECURITY = {"icon": "🔒", "color": "\033[91m", "border": "▬"}  # Vermelho
    AI_SPECIALIST = {"icon": "🤖", "color": "\033[95m", "border": "┅"} # Magenta
    FULLSTACK = {"icon": "🌟", "color": "\033[96m", "border": "┈"}  # Ciano
    DEFAULT = {"icon": "👤", "color": "\033[97m", "border": "─"}   # Branco

class PersonaMarker:
    """Classe principal para gerenciar marcadores de persona"""
    
    RESET_COLOR = "\033[0m"
    
    PERSONAS = {
        "frontend_dev": PersonaStyle.FRONTEND,
        "backend_dev": PersonaStyle.BACKEND,
        "devops_engineer": PersonaStyle.DEVOPS,
        "security_analyst": PersonaStyle.SECURITY,
        "ai_specialist": PersonaStyle.AI_SPECIALIST,
        "fullstack_dev": PersonaStyle.FULLSTACK,
    }
    
    @classmethod
    def create_marker_banner(cls, persona_name: str, action: str = "") -> str:
        """Cria um banner visual para marcar a persona ativa"""
        style = cls.PERSONAS.get(persona_name, PersonaStyle.DEFAULT).value
        
        # Texto principal
        persona_display = persona_name.replace("_", " ").title()
        action_text = f" • {action}" if action else ""
        main_text = f"{style['icon']} {persona_display}{action_text}"
        
        # Cálculo do tamanho
        text_length = len(main_text) - len(style['icon']) + 2  # Ajuste para emoji
        border_length = max(50, text_length + 6)
        
        # Construção do banner
        top_border = style['border'] * border_length
        bottom_border = style['border'] * border_length
        side_border = style['border']
        
        banner = f"""
{style['color']}{top_border}
{side_border} {main_text:<{border_length-4}} {side_border}
{bottom_border}{cls.RESET_COLOR}"""
        
        return banner
    
    @classmethod
    def create_inline_marker(cls, persona_name: str) -> str:
        """Cria uma marca inline mais discreta"""
        style = cls.PERSONAS.get(persona_name, PersonaStyle.DEFAULT).value
        return f"{style['color']}[{style['icon']} {persona_name}]{cls.RESET_COLOR}"
    
    @classmethod
    def create_comment_marker(cls, persona_name: str, language: str = "python") -> str:
        """Cria marcador para comentários em código"""
        style = cls.PERSONAS.get(persona_name, PersonaStyle.DEFAULT).value
        
        comment_chars = {
            "python": "# ",
            "javascript": "// ",
            "typescript": "// ",
            "java": "// ",
            "html": "<!-- ",
            "css": "/* ",
            "sql": "-- ",
            "bash": "# ",
            "yaml": "# ",
            "json": "",  # JSON não tem comentários
        }
        
        comment_end = {
            "html": " -->",
            "css": " */",
        }
        
        comment_start = comment_chars.get(language, "# ")
        comment_close = comment_end.get(language, "")
        
        if language == "json":
            return f'"_persona": "{style["icon"]} {persona_name}"'
        
        return f'{comment_start}{style["icon"]} PERSONA: {persona_name}{comment_close}'
    
    @classmethod
    def print_persona_output(cls, persona_name: str, message: str, action: str = ""):
        """Imprime uma mensagem com marcador de persona"""
        banner = cls.create_marker_banner(persona_name, action)
        print(banner)
        print(f"\n{message}\n")
    
    @classmethod
    def wrap_function_with_persona(cls, persona_name: str, action: str = ""):
        """Decorator para marcar funções com persona específica"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                banner = cls.create_marker_banner(persona_name, action or func.__name__)
                print(banner)
                result = func(*args, **kwargs)
                print(f"{cls.RESET_COLOR}")
                return result
            return wrapper
        return decorator

# Funções de conveniência para uso rápido
def mark_frontend(action: str = ""):
    """Marca rápida para frontend"""
    return PersonaMarker.create_marker_banner("frontend_dev", action)

def mark_backend(action: str = ""):
    """Marca rápida para backend"""
    return PersonaMarker.create_marker_banner("backend_dev", action)

def mark_devops(action: str = ""):
    """Marca rápida para DevOps"""
    return PersonaMarker.create_marker_banner("devops_engineer", action)

def mark_security(action: str = ""):
    """Marca rápida para Security"""
    return PersonaMarker.create_marker_banner("security_analyst", action)

def mark_ai(action: str = ""):
    """Marca rápida para AI Specialist"""
    return PersonaMarker.create_marker_banner("ai_specialist", action)

# Exemplos de uso
if __name__ == "__main__":
    # Demonstração dos marcadores
    print("\n=== DEMONSTRAÇÃO DO SISTEMA DE MARCADORES DE PERSONA ===\n")
    
    # Banner completo
    PersonaMarker.print_persona_output(
        "frontend_dev", 
        "Criando componente React responsivo com TypeScript",
        "Desenvolvimento de Interface"
    )
    
    # Marcador inline
    print(f"Processando... {PersonaMarker.create_inline_marker('backend_dev')}")
    
    # Comentários para diferentes linguagens
    print("\n--- Marcadores para Comentários ---")
    print(PersonaMarker.create_comment_marker("frontend_dev", "javascript"))
    print(PersonaMarker.create_comment_marker("backend_dev", "python"))
    print(PersonaMarker.create_comment_marker("devops_engineer", "yaml"))
    print(PersonaMarker.create_comment_marker("security_analyst", "html"))
    
    # Decorador
    @PersonaMarker.wrap_function_with_persona("ai_specialist", "Análise de Dados")
    def analyze_data():
        print("Executando análise complexa de machine learning...")
        return "Análise concluída"
    
    result = analyze_data()
