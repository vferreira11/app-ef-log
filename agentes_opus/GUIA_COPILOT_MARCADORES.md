# 🎯 Guia Prático: Usando Marcadores com GitHub Copilot

## Como Ativar Personas com Marcadores Visuais

### 1. Prompt Inicial com Persona
```
@persona: frontend_dev
🎨 Preciso criar um componente de menu responsivo em React com TypeScript
```

### 2. Resposta do Copilot com Marcador
```typescript
// 🎨 PERSONA: frontend_dev
import React, { useState } from 'react';
import './Menu.css';

interface MenuProps {
  items: MenuItem[];
  onItemClick: (item: MenuItem) => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  href?: string;
}

const ResponsiveMenu: React.FC<MenuProps> = ({ items, onItemClick }) => {
  const [isOpen, setIsOpen] = useState(false);

  // 🎨 PERSONA: frontend_dev - Toggle mobile menu
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="responsive-menu">
      {/* 🎨 PERSONA: frontend_dev - Mobile hamburger button */}
      <button 
        className="menu-toggle"
        onClick={toggleMenu}
        aria-label="Toggle menu"
      >
        <span className={`hamburger ${isOpen ? 'open' : ''}`}></span>
      </button>

      {/* 🎨 PERSONA: frontend_dev - Menu items */}
      <ul className={`menu-items ${isOpen ? 'open' : ''}`}>
        {items.map((item) => (
          <li key={item.id} className="menu-item">
            <a 
              href={item.href}
              onClick={() => onItemClick(item)}
              className="menu-link"
            >
              {item.icon && <span className="menu-icon">{item.icon}</span>}
              {item.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default ResponsiveMenu;
```

### 3. CSS com Marcadores
```css
/* 🎨 PERSONA: frontend_dev */
.responsive-menu {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* 🎨 PERSONA: frontend_dev - Mobile toggle button */
.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }
  
  /* 🎨 PERSONA: frontend_dev - Mobile menu styles */
  .menu-items {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    flex-direction: column;
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
  }
  
  .menu-items.open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }
}
```

## Workflow com Múltiplas Personas

### Cenário: Sistema de E-commerce

#### 1. Frontend Developer
```
@persona: frontend_dev
🎨 Criar página de produto com galeria de imagens e carrinho
```

#### 2. Backend Developer
```
@persona: backend_dev
⚙️ Implementar API para gerenciar produtos e carrinho de compras
```

#### 3. DevOps Engineer
```
@persona: devops_engineer
🔧 Configurar pipeline CI/CD e deploy automatizado
```

#### 4. Security Analyst
```
@persona: security_analyst
🔒 Implementar autenticação JWT e validação de dados
```

## Exemplos de Commits com Marcadores

```bash
# Frontend
git commit -m "frontend_dev: feat: 🎨 Adiciona componente de galeria responsiva"

# Backend  
git commit -m "backend_dev: feat: ⚙️ Implementa API de produtos com paginação"

# DevOps
git commit -m "devops_engineer: chore: 🔧 Configura Docker multi-stage build"

# Security
git commit -m "security_analyst: fix: 🔒 Corrige vulnerabilidade XSS no formulário"

# AI/ML
git commit -m "ai_specialist: feat: 🤖 Implementa sistema de recomendações"
```

## Pull Request Template com Personas

```markdown
## 📋 Revisão por Persona

### 🎨 Frontend Review (frontend_dev)
- [ ] Componentes responsivos
- [ ] Acessibilidade (WCAG)
- [ ] Performance otimizada
- [ ] Design system seguido
- [ ] Testes de interface

### ⚙️ Backend Review (backend_dev)
- [ ] APIs documentadas
- [ ] Validação de dados
- [ ] Tratamento de erros
- [ ] Testes unitários
- [ ] Performance de queries

### 🔧 DevOps Review (devops_engineer)
- [ ] Build funcionando
- [ ] Deploy configurado
- [ ] Monitoramento ativo
- [ ] Logs estruturados
- [ ] Rollback possível

### 🔒 Security Review (security_analyst)
- [ ] Vulnerabilidades verificadas
- [ ] Autenticação validada
- [ ] Autorização correta
- [ ] Dados sanitizados
- [ ] HTTPS configurado

### 🤖 AI/ML Review (ai_specialist)
- [ ] Modelos validados
- [ ] Dados limpos
- [ ] Performance avaliada
- [ ] Métricas coletadas
- [ ] Bias verificado

## 🎯 Persona Responsável
- **Persona Principal**: `frontend_dev`
- **Personas Colaboradoras**: `backend_dev`, `devops_engineer`
```

## Integração com VS Code

### 1. Snippets para Marcadores

```json
{
  "Frontend Persona Marker": {
    "prefix": "persona-fe",
    "body": [
      "// 🎨 PERSONA: frontend_dev",
      "$0"
    ],
    "description": "Adiciona marcador de persona frontend"
  },
  
  "Backend Persona Marker": {
    "prefix": "persona-be", 
    "body": [
      "# ⚙️ PERSONA: backend_dev",
      "$0"
    ],
    "description": "Adiciona marcador de persona backend"
  },
  
  "DevOps Persona Marker": {
    "prefix": "persona-ops",
    "body": [
      "# 🔧 PERSONA: devops_engineer", 
      "$0"
    ],
    "description": "Adiciona marcador de persona DevOps"
  }
}
```

### 2. Configuração de Cores
```json
{
  "editor.tokenColorCustomizations": {
    "textMateRules": [
      {
        "scope": "comment.line.personas.frontend",
        "settings": {
          "foreground": "#4ecdc4",
          "fontStyle": "bold"
        }
      },
      {
        "scope": "comment.line.personas.backend", 
        "settings": {
          "foreground": "#2ecc71",
          "fontStyle": "bold"
        }
      }
    ]
  }
}
```

## Scripts de Automação

### 1. Auto-adicionar Marcadores
```python
#!/usr/bin/env python3
# 🤖 PERSONA: ai_specialist

import os
import re

def auto_mark_files():
    """Adiciona marcadores automaticamente baseado no tipo de arquivo"""
    
    file_persona_map = {
        r'\.tsx?$': 'frontend_dev',
        r'\.jsx?$': 'frontend_dev', 
        r'\.css$': 'frontend_dev',
        r'\.scss$': 'frontend_dev',
        r'\.py$': 'backend_dev',
        r'\.java$': 'backend_dev',
        r'Dockerfile$': 'devops_engineer',
        r'\.ya?ml$': 'devops_engineer',
        r'security.*\.py$': 'security_analyst',
        r'model.*\.py$': 'ai_specialist'
    }
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            
            for pattern, persona in file_persona_map.items():
                if re.search(pattern, file):
                    add_persona_marker(file_path, persona)
                    break

def add_persona_marker(file_path, persona):
    """Adiciona marcador de persona no início do arquivo"""
    persona_icons = {
        'frontend_dev': '🎨',
        'backend_dev': '⚙️', 
        'devops_engineer': '🔧',
        'security_analyst': '🔒',
        'ai_specialist': '🤖'
    }
    
    icon = persona_icons.get(persona, '👤')
    marker = f"# {icon} PERSONA: {persona}\n"
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if f"PERSONA: {persona}" not in content:
            with open(file_path, 'w') as f:
                f.write(marker + content)
            print(f"✅ Marcador adicionado em {file_path}")
                
    except Exception as e:
        print(f"❌ Erro em {file_path}: {e}")

if __name__ == "__main__":
    auto_mark_files()
```

### 2. Relatório de Personas
```python
#!/usr/bin/env python3
# 📊 Script para gerar relatório de uso de personas

import os
import re
from collections import defaultdict

def generate_persona_report():
    """Gera relatório de uso de personas no projeto"""
    
    persona_files = defaultdict(list)
    persona_count = defaultdict(int)
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Buscar marcadores de persona
                matches = re.findall(r'PERSONA:\s*(\w+)', content)
                
                for persona in matches:
                    persona_files[persona].append(file_path)
                    persona_count[persona] += content.count(f"PERSONA: {persona}")
                    
            except Exception:
                continue
    
    # Gerar relatório
    print("📊 RELATÓRIO DE PERSONAS\n")
    print("="*50)
    
    for persona, files in persona_files.items():
        icon = {
            'frontend_dev': '🎨',
            'backend_dev': '⚙️',
            'devops_engineer': '🔧', 
            'security_analyst': '🔒',
            'ai_specialist': '🤖'
        }.get(persona, '👤')
        
        print(f"\n{icon} {persona.upper()}")
        print(f"   Arquivos: {len(files)}")
        print(f"   Marcadores: {persona_count[persona]}")
        print("   Arquivos:")
        
        for file_path in files[:5]:  # Mostrar até 5 arquivos
            print(f"     - {file_path}")
        
        if len(files) > 5:
            print(f"     ... e mais {len(files) - 5} arquivos")

if __name__ == "__main__":
    generate_persona_report()
```

## 🎉 Resultado Final

Com este sistema implementado, você terá:

✅ **Rastreabilidade Total**: Cada linha de código sabe sua origem  
✅ **Responsabilidade Clara**: Especialistas identificados instantaneamente  
✅ **Manutenção Facilitada**: Encontre rapidamente quem pode ajudar  
✅ **Code Review Eficiente**: Revisão focada por especialidade  
✅ **Onboarding Acelerado**: Novos desenvolvedores entendem a estrutura  
✅ **Qualidade Consistente**: Cada persona mantém seus padrões  

**O sistema de marcadores transforma seu código em uma narrativa clara de quem fez o quê, quando e por quê!** 🚀
