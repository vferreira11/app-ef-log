# 🔧 PERSONA: devops_engineer
"""
Exemplo de Integração dos Marcadores de Persona
Demonstra como usar o sistema em diferentes contextos
"""

from persona_markers import PersonaMarker
import json
import yaml

# ═══════════════════════════════════════════════════════════════
# 🔧 DEVOPS ENGINEER - Configuração de Deploy
# ═══════════════════════════════════════════════════════════════

@PersonaMarker.wrap_function_with_persona("devops_engineer", "Configuração de Deploy")
def setup_deployment():
    """Configura ambiente de deploy com marcadores de persona"""
    
    # Docker compose com marcador
    docker_compose = """
# 🔧 PERSONA: devops_engineer
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PERSONA_ACTIVE=devops_engineer
  
  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=app_db
      # 🔧 PERSONA: devops_engineer - Configuração segura
      - POSTGRES_PASSWORD=${DB_PASSWORD}
"""
    
    # Kubernetes deployment
    k8s_config = """
# 🔧 PERSONA: devops_engineer
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  labels:
    persona: devops_engineer
    managed-by: persona-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
        persona: devops_engineer
    spec:
      containers:
      - name: webapp
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: PERSONA_ACTIVE
          value: "devops_engineer"
"""
    
    print("📁 docker-compose.yml criado")
    print("📁 k8s-deployment.yaml criado")
    return "Deploy configurado"

# ═══════════════════════════════════════════════════════════════
# 🔒 SECURITY ANALYST - Análise de Segurança
# ═══════════════════════════════════════════════════════════════

@PersonaMarker.wrap_function_with_persona("security_analyst", "Auditoria de Segurança")
def security_audit():
    """Executa auditoria com marcadores de persona"""
    
    PersonaMarker.print_persona_output(
        "security_analyst",
        "🔍 Iniciando auditoria de segurança...\n" +
        "✅ Verificação de vulnerabilidades\n" +
        "✅ Análise de dependências\n" +
        "✅ Scan de código\n" +
        "⚠️  2 vulnerabilidades encontradas\n" +
        "📋 Relatório gerado",
        "Auditoria Completa"
    )
    
    # Script de segurança
    security_script = '''#!/bin/bash
# 🔒 PERSONA: security_analyst

echo "🔒 SECURITY ANALYST - Iniciando scan..."

# Verificar portas abertas
nmap -sT localhost

# Análise de dependências
safety check

# Scan de código
bandit -r .

echo "✅ Auditoria concluída"
'''
    
    return "Auditoria executada"

# ═══════════════════════════════════════════════════════════════
# 🤖 AI SPECIALIST - Análise de Machine Learning
# ═══════════════════════════════════════════════════════════════

@PersonaMarker.wrap_function_with_persona("ai_specialist", "Treinamento de Modelo")
def train_model():
    """Treina modelo ML com marcadores de persona"""
    
    # Código Python para ML
    ml_code = '''
# 🤖 PERSONA: ai_specialist
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def train_model():
    """
    🤖 PERSONA: ai_specialist
    Treina modelo de classificação com Random Forest
    """
    print("🤖 AI SPECIALIST - Carregando dados...")
    
    # Simular carregamento de dados
    data = pd.DataFrame({
        'feature1': np.random.randn(1000),
        'feature2': np.random.randn(1000),
        'target': np.random.randint(0, 2, 1000)
    })
    
    X = data[['feature1', 'feature2']]
    y = data['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 🤖 PERSONA: ai_specialist - Treinamento do modelo
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"✅ Modelo treinado com acurácia: {accuracy:.3f}")
    
    return model
'''
    
    PersonaMarker.print_persona_output(
        "ai_specialist",
        "🧠 Iniciando treinamento de modelo ML...\n" +
        "📊 Dados carregados: 1000 amostras\n" +
        "🔄 Treinando Random Forest...\n" +
        "📈 Acurácia obtida: 87.5%\n" +
        "💾 Modelo salvo",
        "Treinamento Concluído"
    )
    
    return "Modelo treinado"

# ═══════════════════════════════════════════════════════════════
# 🎨 FRONTEND DEV - Interface de Monitoramento
# ═══════════════════════════════════════════════════════════════

def create_monitoring_dashboard():
    """Cria dashboard com marcadores de persona"""
    
    # JavaScript para dashboard
    js_code = '''
// 🎨 PERSONA: frontend_dev
class PersonaDashboard {
    constructor() {
        this.activePersonas = [];
        this.init();
    }
    
    init() {
        console.log('🎨 FRONTEND DEV - Inicializando dashboard...');
        this.createPersonaIndicators();
        this.setupRealTimeUpdates();
    }
    
    // 🎨 PERSONA: frontend_dev - Indicadores visuais
    createPersonaIndicators() {
        const personas = [
            { name: 'frontend_dev', icon: '🎨', color: '#4ecdc4' },
            { name: 'backend_dev', icon: '⚙️', color: '#2ecc71' },
            { name: 'devops_engineer', icon: '🔧', color: '#f39c12' },
            { name: 'security_analyst', icon: '🔒', color: '#e74c3c' },
            { name: 'ai_specialist', icon: '🤖', color: '#9b59b6' }
        ];
        
        personas.forEach(persona => {
            this.createPersonaCard(persona);
        });
    }
    
    createPersonaCard(persona) {
        const card = document.createElement('div');
        card.className = 'persona-card';
        card.innerHTML = `
            <div class="persona-icon">${persona.icon}</div>
            <div class="persona-name">${persona.name}</div>
            <div class="persona-status" id="status-${persona.name}">Inactive</div>
        `;
        card.style.borderLeft = `4px solid ${persona.color}`;
        document.getElementById('persona-dashboard').appendChild(card);
    }
    
    // 🎨 PERSONA: frontend_dev - Atualizações em tempo real
    activatePersona(personaName) {
        const statusElement = document.getElementById(`status-${personaName}`);
        if (statusElement) {
            statusElement.textContent = 'ACTIVE';
            statusElement.className = 'persona-status active';
        }
        
        // Animação visual
        this.showPersonaNotification(personaName);
    }
    
    showPersonaNotification(personaName) {
        const notification = document.createElement('div');
        notification.className = 'persona-notification';
        notification.textContent = `${personaName} is now active`;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Inicializar dashboard
const dashboard = new PersonaDashboard();
'''

    PersonaMarker.print_persona_output(
        "frontend_dev",
        "🖥️ Dashboard de monitoramento criado\n" +
        "📊 Indicadores visuais implementados\n" +
        "🔄 Sistema de notificações ativo\n" +
        "🎨 Interface responsiva configurada",
        "Dashboard Operacional"
    )

# ═══════════════════════════════════════════════════════════════
# ORQUESTRAÇÃO - Exemplo de uso completo
# ═══════════════════════════════════════════════════════════════

def demonstrate_persona_system():
    """Demonstra o sistema completo de personas"""
    
    print("\n" + "="*80)
    print("🌟 DEMONSTRAÇÃO COMPLETA DO SISTEMA DE PERSONAS")
    print("="*80 + "\n")
    
    # 1. DevOps configura ambiente
    print(f"{PersonaMarker.create_inline_marker('devops_engineer')} Configurando ambiente...")
    setup_deployment()
    
    print("\n" + "-"*50 + "\n")
    
    # 2. Security faz auditoria
    print(f"{PersonaMarker.create_inline_marker('security_analyst')} Executando auditoria...")
    security_audit()
    
    print("\n" + "-"*50 + "\n")
    
    # 3. AI Specialist treina modelo
    print(f"{PersonaMarker.create_inline_marker('ai_specialist')} Treinando modelo...")
    train_model()
    
    print("\n" + "-"*50 + "\n")
    
    # 4. Frontend cria dashboard
    print(f"{PersonaMarker.create_inline_marker('frontend_dev')} Criando interface...")
    create_monitoring_dashboard()
    
    print("\n" + "-"*50 + "\n")
    
    # 5. Backend finaliza integração
    PersonaMarker.print_persona_output(
        "backend_dev",
        "🔗 Integrando todos os componentes...\n" +
        "✅ APIs configuradas\n" +
        "✅ Database sincronizada\n" +
        "✅ Serviços conectados\n" +
        "✅ Sistema operacional",
        "Integração Completa"
    )
    
    print("\n" + "="*80)
    print("🎉 SISTEMA DE PERSONAS TOTALMENTE OPERACIONAL!")
    print("="*80 + "\n")

if __name__ == "__main__":
    demonstrate_persona_system()
