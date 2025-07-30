# 📝 Templates para Criação de Agentes
### Modelos prontos para acelerar o desenvolvimento

---

## 🎯 **TEMPLATE: ARQUIVO DE PERSONA**

```markdown
# [EMOJI] [Nome do Agente] - Persona de Agente

## Identidade
- **Nome**: [Nome Completo do Agente]
- **Emoji**: [emoji único]
- **Cor**: [#HEXCOLOR]
- **Ativação**: "@[trigger]" ou "[comando de ativação]"

## Personalidade & Estilo
[Descreva a personalidade única do agente. Como ele fala? Qual o tom? Formal ou informal? 
Técnico ou didático? Use 2-3 frases que capturem a essência.]

Exemplo:
> Sou um especialista [área] que adora [característica]. Falo de forma **[estilo]** e sempre 
> foco em [objetivo principal]. [Frase característica ou filosofia].

## Especialidades
- **[Área Principal 1]**: [Descrição específica do que domina]
- **[Área Principal 2]**: [Descrição específica do que domina]
- **[Área Principal 3]**: [Descrição específica do que domina]
- **[Área Principal 4]**: [Descrição específica do que domina]

## Stack Preferido
```
[Categoria 1]: [Tecnologia 1], [Tecnologia 2], [Tecnologia 3]
[Categoria 2]: [Tecnologia 1], [Tecnologia 2], [Tecnologia 3]
[Categoria 3]: [Tecnologia 1], [Tecnologia 2], [Tecnologia 3]
[Categoria 4]: [Tecnologia 1], [Tecnologia 2], [Tecnologia 3]
[Categoria 5]: [Tecnologia 1], [Tecnologia 2], [Tecnologia 3]
```

## Como Opero
Quando ativado, eu:

1. **[Primeira Ação]**: [Descrição detalhada do que faz primeiro]
2. **[Segunda Ação]**: [Descrição detalhada da segunda etapa]
3. **[Terceira Ação]**: [Descrição detalhada da terceira etapa]
4. **[Quarta Ação]**: [Descrição detalhada da quarta etapa]
5. **[Quinta Ação]**: [Descrição detalhada da finalização]

## Exemplos de Ativação
### Trigger Principal
- "@[trigger] [exemplo de comando]"
- "@[trigger] [outro exemplo]"

### Triggers Alternativos
- "[alias 1] [comando]"
- "[alias 2] [comando]"
- "[palavra-chave específica da área]"

## Workflows Especializados

### [Nome do Workflow 1]
```
📋 Input → 🔍 Análise → 🎯 Planejamento → 🔧 Implementação → ✅ Validação
```

**Detalhamento:**
1. **Input**: [O que recebe como entrada]
2. **Análise**: [Como analisa o problema]
3. **Planejamento**: [Como cria o plano de ação]
4. **Implementação**: [Como executa as soluções]
5. **Validação**: [Como valida os resultados]

### [Nome do Workflow 2]
```
🎯 Objetivo → 📊 Diagnóstico → 🚀 Otimização → 📈 Monitoramento
```

**Detalhamento:**
1. **Objetivo**: [Define metas claras]
2. **Diagnóstico**: [Identifica problemas/oportunidades]
3. **Otimização**: [Implementa melhorias]
4. **Monitoramento**: [Acompanha resultados]

## Frases Características
- "[Frase típica que o agente usaria]"
- "[Expressão característica da área]"
- "[Motto ou filosofia do agente]"
- "[Forma típica de cumprimentar]"
- "[Forma típica de finalizar]"

## Comandos Especiais
- **Reset**: "reset [nome do agente]" ou "limpar contexto [área]"
- **Status**: "status [nome do agente]" ou "como está [área]?"
- **Help**: "ajuda [nome do agente]" ou "comandos [área]"

## Métricas de Sucesso
- 📊 **[Métrica 1]**: [Como medir sucesso nesta área]
- 📈 **[Métrica 2]**: [Indicador de performance]
- ✅ **[Métrica 3]**: [Critério de qualidade]
- 🎯 **[Métrica 4]**: [Meta de eficiência]

## Casos de Uso Típicos
1. **[Cenário 1]**: [Descrição do problema] → [Como o agente resolve]
2. **[Cenário 2]**: [Descrição do problema] → [Como o agente resolve]
3. **[Cenário 3]**: [Descrição do problema] → [Como o agente resolve]

## Integrações MCP Preferenciais
- **[Função MCP 1]**: [Quando e como usa]
- **[Função MCP 2]**: [Quando e como usa]
- **[Função MCP 3]**: [Quando e como usa]

---
*Template criado em: [DATA]*
*Para uso no Sistema de Agentes v1.0.0*
```

---

## ⚙️ **TEMPLATE: CONFIGURAÇÃO JSON**

```json
{
  "@[trigger]": {
    "agente": "[nome_agente]",
    "emoji": "[emoji]",
    "cor": "[#HEXCOLOR]",
    "persona_file": "agentes/personas/[nome_agente].md",
    "aliases": [
      "ative [nome] expert",
      "[area] specialist", 
      "[palavra-chave-1]",
      "[palavra-chave-2]",
      "[palavra-chave-3]"
    ],
    "mcp_functions": [
      "[categoria_mcp_1]",
      "[categoria_mcp_2]"
    ],
    "workflows": [
      "[workflow_principal]",
      "[workflow_especializado]"
    ],
    "metadata": {
      "versao": "1.0.0",
      "criado_em": "[YYYY-MM-DD]",
      "autor": "[seu_nome]",
      "descricao": "[Breve descrição do agente]",
      "tags": ["[tag1]", "[tag2]", "[tag3]"]
    }
  }
}
```

---

## 🐍 **TEMPLATE: CLASSE PYTHON (OPCIONAL)**

```python
"""
[EMOJI] [Nome do Agente] - Especialista em [Área]

Este módulo implementa a lógica específica para o agente [nome],
focado em [área de especialização] e integrado ao Sistema de Agentes.

Autor: [Seu Nome]
Data: [Data de Criação]
Versão: 1.0.0
"""

from typing import Dict, List, Optional, Any
from agentes.core.base_agente import BaseAgente
from agentes.core.tipos import TipoAgente, StatusExecucao
from agentes.core.comunicacao import ComunicacaoMCP
import logging

logger = logging.getLogger(__name__)

class [NomeAgente](BaseAgente):
    """
    Agente especializado em [área de atuação]
    
    Características:
    - [Característica 1]
    - [Característica 2] 
    - [Característica 3]
    
    Triggers:
    - @[trigger] (principal)
    - [alias1], [alias2] (alternativos)
    """
    
    def __init__(self):
        """Inicializa o agente [nome] com configurações específicas"""
        super().__init__(
            nome="[nome_agente]",
            tipo=TipoAgente.ESPECIALISTA,
            especialidades=[
                "[especialidade1]",
                "[especialidade2]", 
                "[especialidade3]",
                "[especialidade4]"
            ],
            persona_file="agentes/personas/[nome_agente].md",
            emoji="[emoji]",
            cor="[#HEXCOLOR]"
        )
        
        # Configurações específicas do agente
        self.stack_preferido = {
            "[categoria1]": ["[tech1]", "[tech2]", "[tech3]"],
            "[categoria2]": ["[tech1]", "[tech2]", "[tech3]"],
            "[categoria3]": ["[tech1]", "[tech2]", "[tech3]"]
        }
        
        # Workflows específicos
        self.workflows = {
            "[workflow1]": [
                "📋 [Etapa 1]",
                "🔍 [Etapa 2]", 
                "🎯 [Etapa 3]",
                "🔧 [Etapa 4]",
                "✅ [Etapa 5]"
            ],
            "[workflow2]": [
                "🎯 [Etapa 1]",
                "📊 [Etapa 2]",
                "🚀 [Etapa 3]", 
                "📈 [Etapa 4]"
            ]
        }
        
        logger.info(f"{self.emoji} {self.nome} inicializado com sucesso")
    
    async def processar_requisicao(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa requisições específicas do agente [nome]
        
        Args:
            mensagem: Mensagem do usuário
            contexto: Contexto da sessão atual
            
        Returns:
            Dict contendo:
            - status: StatusExecucao
            - resposta: Resposta formatada
            - acoes_realizadas: Lista de ações executadas
            - proximos_passos: Sugestões para continuidade
            - metricas: Métricas de performance
        """
        try:
            logger.info(f"{self.emoji} Processando requisição: {mensagem[:50]}...")
            
            # 1. Análise inicial da requisição
            analise = await self._analisar_requisicao_especializada(mensagem, contexto)
            
            # 2. Determinar workflow apropriado
            workflow = self._determinar_workflow(analise)
            
            # 3. Executar workflow específico
            resultado = await self._executar_workflow(workflow, analise, contexto)
            
            # 4. Gerar resposta na persona
            resposta = self._gerar_resposta_personalizada(resultado, analise)
            
            # 5. Registrar métricas
            metricas = self._calcular_metricas(resultado)
            
            return {
                "status": StatusExecucao.SUCESSO,
                "resposta": resposta,
                "acoes_realizadas": resultado.get("acoes", []),
                "proximos_passos": resultado.get("proximos_passos", []),
                "metricas": metricas,
                "workflow_usado": workflow
            }
            
        except Exception as e:
            logger.error(f"{self.emoji} Erro ao processar requisição: {str(e)}")
            return {
                "status": StatusExecucao.ERRO,
                "resposta": f"{self.emoji} ❌ Ops! Encontrei um problema: {str(e)}",
                "erro": str(e)
            }
    
    async def _analisar_requisicao_especializada(self, mensagem: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise específica da área de expertise
        
        Returns:
            Dict com análise detalhada:
            - tipo_requisicao: Classificação da solicitação
            - complexidade: Nível de complexidade (baixa/média/alta)
            - areas_envolvidas: Áreas técnicas relevantes
            - contexto_necessario: Informações adicionais necessárias
            - estimativa_tempo: Tempo estimado para execução
        """
        # Implementar lógica específica de análise
        # Exemplo de estrutura:
        
        analise = {
            "tipo_requisicao": self._classificar_tipo_requisicao(mensagem),
            "complexidade": self._avaliar_complexidade(mensagem),
            "areas_envolvidas": self._identificar_areas(mensagem),
            "contexto_necessario": self._identificar_contexto_necessario(mensagem, contexto),
            "estimativa_tempo": self._estimar_tempo_execucao(mensagem),
            "palavras_chave": self._extrair_palavras_chave(mensagem),
            "urgencia": self._avaliar_urgencia(mensagem)
        }
        
        logger.debug(f"{self.emoji} Análise concluída: {analise}")
        return analise
    
    def _determinar_workflow(self, analise: Dict[str, Any]) -> str:
        """Determina qual workflow usar baseado na análise"""
        tipo_req = analise.get("tipo_requisicao", "")
        complexidade = analise.get("complexidade", "")
        
        # Lógica para escolher workflow
        if "[condição_workflow1]" in tipo_req:
            return "[workflow1]"
        elif "[condição_workflow2]" in tipo_req:
            return "[workflow2]"
        else:
            return "padrao"
    
    async def _executar_workflow(self, workflow: str, analise: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o workflow específico escolhido"""
        
        resultado = {
            "acoes": [],
            "arquivos_criados": [],
            "prs_criados": [],
            "proximos_passos": [],
            "metricas_preliminares": {}
        }
        
        if workflow == "[workflow1]":
            resultado = await self._executar_workflow1(analise, contexto)
        elif workflow == "[workflow2]":
            resultado = await self._executar_workflow2(analise, contexto)
        else:
            resultado = await self._executar_workflow_padrao(analise, contexto)
        
        return resultado
    
    async def _executar_workflow1(self, analise: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o workflow especializado 1
        
        Etapas:
        1. [Etapa 1]
        2. [Etapa 2]
        3. [Etapa 3]
        4. [Etapa 4]
        5. [Etapa 5]
        """
        resultado = {"acoes": [], "arquivos_criados": [], "proximos_passos": []}
        
        # Implementar cada etapa do workflow
        # Etapa 1: [Descrição]
        logger.info(f"{self.emoji} 📋 Executando [Etapa 1]...")
        # [código específico]
        resultado["acoes"].append("📋 [Etapa 1] concluída")
        
        # Etapa 2: [Descrição]
        logger.info(f"{self.emoji} 🔍 Executando [Etapa 2]...")
        # [código específico]
        resultado["acoes"].append("🔍 [Etapa 2] concluída")
        
        # Continue para todas as etapas...
        
        return resultado
    
    def _gerar_resposta_personalizada(self, resultado: Dict[str, Any], analise: Dict[str, Any]) -> str:
        """Gera resposta na voz característica do agente"""
        
        resposta = f"""
{self.emoji} **[Nome do Agente] Ativado!**

🔍 **Análise**: {self._resumir_analise(analise)}

📋 **Plano de Ação**:
{self._formatar_plano_acao(resultado.get("acoes", []))}

🚀 **Executando...**
{self._formatar_acoes_realizadas(resultado.get("acoes", []))}

✅ **Resultado**: {self._resumir_resultado(resultado)}

💡 **Próximos Passos**: 
{self._formatar_proximos_passos(resultado.get("proximos_passos", []))}

📊 **Métricas**:
{self._formatar_metricas(resultado.get("metricas_preliminares", {}))}
"""
        
        return resposta.strip()
    
    def _calcular_metricas(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas específicas do agente"""
        return {
            "[metrica1]": "[valor]",
            "[metrica2]": "[valor]",
            "[metrica3]": "[valor]",
            "tempo_execucao": "[tempo]",
            "arquivos_modificados": len(resultado.get("arquivos_criados", [])),
            "acoes_executadas": len(resultado.get("acoes", []))
        }
    
    # Métodos auxiliares específicos da área
    def _classificar_tipo_requisicao(self, mensagem: str) -> str:
        """Classifica o tipo de requisição específica da área"""
        # Implementar lógica específica
        pass
    
    def _avaliar_complexidade(self, mensagem: str) -> str:
        """Avalia complexidade específica da área"""
        # Implementar lógica específica
        pass
    
    def _identificar_areas(self, mensagem: str) -> List[str]:
        """Identifica áreas técnicas envolvidas"""
        # Implementar lógica específica
        pass
    
    # Continue implementando outros métodos auxiliares...


# Exemplo de uso
if __name__ == "__main__":
    agente = [NomeAgente]()
    print(f"{agente.emoji} Agente {agente.nome} carregado com sucesso!")
```

---

## 🧪 **TEMPLATE: TESTES**

```python
"""
Testes para o agente [Nome do Agente]

Este módulo contém testes abrangentes para validar o funcionamento
do agente [nome] em diversos cenários.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from agentes.especialistas.[nome_agente] import [NomeAgente]
from agentes.core.tipos import StatusExecucao

class Test[NomeAgente]:
    """Suite de testes para [Nome do Agente]"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.agente = [NomeAgente]()
        self.contexto_mock = {
            "sessao_id": "test_123",
            "usuario": "test_user",
            "projeto": "test_project",
            "historico": []
        }
    
    def test_inicializacao_agente(self):
        """Testa inicialização correta do agente"""
        assert self.agente.nome == "[nome_agente]"
        assert self.agente.emoji == "[emoji]"
        assert self.agente.cor == "[#HEXCOLOR]"
        assert "[especialidade1]" in self.agente.especialidades
    
    @pytest.mark.asyncio
    async def test_ativacao_por_trigger_principal(self):
        """Testa ativação via trigger principal"""
        mensagem = "@[trigger] [comando de teste]"
        resultado = await self.agente.processar_requisicao(mensagem, self.contexto_mock)
        
        assert resultado["status"] == StatusExecucao.SUCESSO
        assert "[emoji]" in resultado["resposta"]
        assert "Ativado" in resultado["resposta"]
    
    @pytest.mark.asyncio
    async def test_workflow_principal(self):
        """Testa execução do workflow principal"""
        mensagem = "@[trigger] execute [acao_principal]"
        resultado = await self.agente.processar_requisicao(mensagem, self.contexto_mock)
        
        assert resultado["status"] == StatusExecucao.SUCESSO
        assert len(resultado["acoes_realizadas"]) > 0
        assert len(resultado["proximos_passos"]) > 0
    
    @pytest.mark.asyncio
    async def test_analise_requisicao_complexa(self):
        """Testa análise de requisição complexa"""
        mensagem = "@[trigger] [requisicao_complexa_da_area]"
        resultado = await self.agente.processar_requisicao(mensagem, self.contexto_mock)
        
        assert resultado["status"] == StatusExecucao.SUCESSO
        assert "complexidade" in str(resultado["resposta"]).lower()
    
    @pytest.mark.asyncio
    async def test_integracao_mcp(self):
        """Testa integração com funções MCP"""
        with patch('agentes.core.comunicacao.ComunicacaoMCP') as mock_mcp:
            mock_mcp.return_value.criar_branch.return_value = {"status": "sucesso"}
            
            mensagem = "@[trigger] crie um branch para [feature]"
            resultado = await self.agente.processar_requisicao(mensagem, self.contexto_mock)
            
            assert resultado["status"] == StatusExecucao.SUCESSO
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Testa tratamento de erros"""
        with patch.object(self.agente, '_analisar_requisicao_especializada', side_effect=Exception("Erro simulado")):
            mensagem = "@[trigger] comando que gera erro"
            resultado = await self.agente.processar_requisicao(mensagem, self.contexto_mock)
            
            assert resultado["status"] == StatusExecucao.ERRO
            assert "❌" in resultado["resposta"]
    
    def test_classificacao_tipos_requisicao(self):
        """Testa classificação de diferentes tipos de requisição"""
        casos_teste = [
            ("[requisicao_tipo1]", "[tipo_esperado1]"),
            ("[requisicao_tipo2]", "[tipo_esperado2]"),
            ("[requisicao_tipo3]", "[tipo_esperado3]")
        ]
        
        for requisicao, tipo_esperado in casos_teste:
            tipo = self.agente._classificar_tipo_requisicao(requisicao)
            assert tipo == tipo_esperado
    
    def test_metricas_calculadas(self):
        """Testa cálculo de métricas"""
        resultado_mock = {
            "acoes": ["acao1", "acao2", "acao3"],
            "arquivos_criados": ["arquivo1.py", "arquivo2.md"]
        }
        
        metricas = self.agente._calcular_metricas(resultado_mock)
        
        assert "acoes_executadas" in metricas
        assert metricas["acoes_executadas"] == 3
        assert metricas["arquivos_modificados"] == 2
    
    @pytest.mark.parametrize("mensagem,complexidade_esperada", [
        ("[mensagem_simples]", "baixa"),
        ("[mensagem_media]", "média"),
        ("[mensagem_complexa]", "alta")
    ])
    def test_avaliacao_complexidade(self, mensagem, complexidade_esperada):
        """Testa avaliação de complexidade para diferentes mensagens"""
        complexidade = self.agente._avaliar_complexidade(mensagem)
        assert complexidade == complexidade_esperada

# Testes de integração
class TestIntegracao[NomeAgente]:
    """Testes de integração do agente com o sistema"""
    
    def setup_method(self):
        self.agente = [NomeAgente]()
    
    @pytest.mark.asyncio
    async def test_fluxo_completo_criacao_pr(self):
        """Testa fluxo completo de criação de PR"""
        # Implementar teste de integração completo
        pass
    
    @pytest.mark.asyncio 
    async def test_persistencia_contexto(self):
        """Testa persistência de contexto entre requisições"""
        # Implementar teste de contexto
        pass
```

---

## 📊 **TEMPLATE: MÉTRICAS E MONITORAMENTO**

```python
"""
Sistema de métricas para agente [Nome do Agente]
"""

from dataclasses import dataclass
from typing import Dict, List
import time
import json

@dataclass
class MetricasAgente:
    """Estrutura para métricas do agente"""
    agente_nome: str
    ativacoes_total: int = 0
    ativacoes_por_trigger: Dict[str, int] = None
    tempo_medio_resposta: float = 0.0
    taxa_sucesso: float = 0.0
    prs_criados: int = 0
    funcoes_mcp_utilizadas: Dict[str, int] = None
    workflows_executados: Dict[str, int] = None
    
    def __post_init__(self):
        if self.ativacoes_por_trigger is None:
            self.ativacoes_por_trigger = {}
        if self.funcoes_mcp_utilizadas is None:
            self.funcoes_mcp_utilizadas = {}
        if self.workflows_executados is None:
            self.workflows_executados = {}

class MonitorAgente:
    """Monitor de performance e métricas do agente"""
    
    def __init__(self, agente_nome: str):
        self.agente_nome = agente_nome
        self.metricas = MetricasAgente(agente_nome)
        self.historico_execucoes = []
    
    def registrar_ativacao(self, trigger: str, tempo_execucao: float, sucesso: bool):
        """Registra uma ativação do agente"""
        self.metricas.ativacoes_total += 1
        
        if trigger not in self.metricas.ativacoes_por_trigger:
            self.metricas.ativacoes_por_trigger[trigger] = 0
        self.metricas.ativacoes_por_trigger[trigger] += 1
        
        # Atualizar tempo médio
        total_tempo = self.metricas.tempo_medio_resposta * (self.metricas.ativacoes_total - 1)
        self.metricas.tempo_medio_resposta = (total_tempo + tempo_execucao) / self.metricas.ativacoes_total
        
        # Atualizar taxa de sucesso
        sucessos = sum(1 for exec in self.historico_execucoes if exec.get("sucesso", False))
        if sucesso:
            sucessos += 1
        self.metricas.taxa_sucesso = sucessos / self.metricas.ativacoes_total
        
        # Registrar no histórico
        self.historico_execucoes.append({
            "timestamp": time.time(),
            "trigger": trigger,
            "tempo_execucao": tempo_execucao,
            "sucesso": sucesso
        })
    
    def gerar_relatorio(self) -> Dict:
        """Gera relatório completo de métricas"""
        return {
            "agente": self.agente_nome,
            "metricas_gerais": {
                "ativacoes_total": self.metricas.ativacoes_total,
                "tempo_medio_resposta": f"{self.metricas.tempo_medio_resposta:.2f}s",
                "taxa_sucesso": f"{self.metricas.taxa_sucesso:.1%}",
                "prs_criados": self.metricas.prs_criados
            },
            "distribuicao_triggers": self.metricas.ativacoes_por_trigger,
            "funcoes_mcp_mais_usadas": dict(sorted(
                self.metricas.funcoes_mcp_utilizadas.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]),
            "workflows_populares": dict(sorted(
                self.metricas.workflows_executados.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3])
        }
```

---

## 🔧 **SCRIPT DE CRIAÇÃO AUTOMATIZADA**

```bash
#!/bin/bash
# create_agent.sh - Script para criar novo agente automaticamente

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Criador Automático de Agentes${NC}"
echo -e "${BLUE}===================================${NC}"

# Coletar informações
read -p "Nome do agente (ex: mobile_expert): " AGENT_NAME
read -p "Trigger principal (ex: @mobile): " TRIGGER
read -p "Emoji do agente (ex: 📱): " EMOJI
read -p "Cor hex (ex: #00C853): " COLOR
read -p "Área de especialização (ex: Desenvolvimento Mobile): " AREA
read -p "Seu nome (autor): " AUTHOR

# Validações básicas
if [[ ! "$TRIGGER" =~ ^@[a-z]+$ ]]; then
    echo -e "${RED}❌ Trigger deve começar com @ e conter apenas letras minúsculas${NC}"
    exit 1
fi

if [[ ! "$COLOR" =~ ^#[0-9A-Fa-f]{6}$ ]]; then
    echo -e "${RED}❌ Cor deve estar no formato #RRGGBB${NC}"
    exit 1
fi

# Criar diretórios se necessário
mkdir -p agentes/personas
mkdir -p agentes/especialistas
mkdir -p tests

# Criar arquivo de persona
PERSONA_FILE="agentes/personas/${AGENT_NAME}.md"
echo -e "${YELLOW}📝 Criando persona: ${PERSONA_FILE}${NC}"

cat > "$PERSONA_FILE" << EOL
# ${EMOJI} ${AREA} Expert - Persona de Agente

## Identidade
- **Nome**: ${AREA} Expert
- **Emoji**: ${EMOJI}
- **Cor**: ${COLOR}
- **Ativação**: "${TRIGGER}" ou "ative ${AREA,,} expert"

## Personalidade & Estilo
Sou um especialista em ${AREA,,} apaixonado por criar soluções inovadoras. Falo de forma **prática e direta**, sempre focando em resultados de qualidade. Adoro compartilhar conhecimento e ajudar a resolver desafios complexos.

## Especialidades
- **[Área 1]**: [Descrição específica]
- **[Área 2]**: [Descrição específica]
- **[Área 3]**: [Descrição específica]
- **[Área 4]**: [Descrição específica]

## Stack Preferido
\`\`\`
[Categoria 1]: [Tech 1], [Tech 2], [Tech 3]
[Categoria 2]: [Tech 1], [Tech 2], [Tech 3]
[Categoria 3]: [Tech 1], [Tech 2], [Tech 3]
\`\`\`

## Como Opero
Quando ativado, eu:

1. **Analiso o contexto** do seu projeto
2. **Identifico oportunidades** de melhoria
3. **Sugiro implementações** modernas e eficientes
4. **Crio soluções** práticas e testadas
5. **Documento** todo o processo

## Workflows Especializados
### Análise e Otimização
\`\`\`
📋 Análise → 🔍 Diagnóstico → 🎯 Planejamento → 🔧 Implementação → ✅ Validação
\`\`\`

### Desenvolvimento Rápido
\`\`\`
🎯 Objetivo → 🚀 Prototipação → 🧪 Testes → 📦 Deploy
\`\`\`

## Frases Características
- "Vamos fazer isso funcionar de forma elegante!"
- "A qualidade está nos detalhes."
- "Sempre há uma forma mais eficiente."

## Métricas de Sucesso
- 📊 **Performance**: Melhorias mensuráveis
- 📈 **Qualidade**: Código limpo e testado
- ✅ **Entrega**: Soluções funcionais
- 🎯 **Eficiência**: Processos otimizados

---
*Criado em: $(date +%Y-%m-%d) por ${AUTHOR}*
*Sistema de Agentes v1.0.0*
EOL

# Atualizar sistema_agentes.json
echo -e "${YELLOW}⚙️ Atualizando configuração do sistema...${NC}"

# Backup do arquivo atual
cp agentes/config/sistema_agentes.json agentes/config/sistema_agentes.json.bak

# Adicionar nova configuração (simplificado - em produção seria via Python)
cat > temp_config.json << EOL
{
  "${TRIGGER}": {
    "agente": "${AGENT_NAME}",
    "emoji": "${EMOJI}",
    "cor": "${COLOR}",
    "persona_file": "agentes/personas/${AGENT_NAME}.md",
    "aliases": [
      "ative ${AREA,,} expert",
      "${AREA,,} specialist",
      "${AREA,,}"
    ]
  }
}
EOL

echo -e "${YELLOW}📄 Criando arquivo de teste...${NC}"

# Criar arquivo de teste básico
TEST_FILE="tests/test_${AGENT_NAME}.py"
cat > "$TEST_FILE" << EOL
"""
Testes para ${AREA} Expert
"""

import pytest
from agentes.core.sistema import SistemaAgentes

class Test${AGENT_NAME^}:
    
    def setup_method(self):
        self.sistema = SistemaAgentes()
    
    def test_ativacao_por_trigger(self):
        """Testa ativação por trigger principal"""
        resposta = self.sistema.processar_mensagem("${TRIGGER} teste")
        assert "${EMOJI}" in resposta
        assert "Expert Ativado" in resposta
    
    def test_resposta_na_persona(self):
        """Testa resposta na persona específica"""
        resposta = self.sistema.processar_mensagem("${TRIGGER} me ajude")
        assert "especialista" in resposta.lower()
        assert "${AREA,,}" in resposta.lower()

# Executar com: pytest ${TEST_FILE} -v
EOL

echo -e "${GREEN}✅ Agente ${AGENT_NAME} criado com sucesso!${NC}"
echo ""
echo -e "${BLUE}📁 Arquivos criados:${NC}"
echo -e "   📝 ${PERSONA_FILE}"
echo -e "   🧪 ${TEST_FILE}"
echo ""
echo -e "${BLUE}📋 Próximos passos:${NC}"
echo -e "   1. Edite a persona em ${PERSONA_FILE}"
echo -e "   2. Adicione a configuração em sistema_agentes.json:"
echo -e "      ${YELLOW}$(cat temp_config.json)${NC}"
echo -e "   3. Execute os testes: ${YELLOW}pytest ${TEST_FILE} -v${NC}"
echo -e "   4. Teste o agente: ${YELLOW}${TRIGGER} olá${NC}"

# Limpar arquivo temporário
rm temp_config.json

echo ""
echo -e "${GREEN}🎉 Agente pronto para uso!${NC}"
```

---

## 📚 **RECURSOS ADICIONAIS**

### **Validador de Configuração**
```python
# validate_agent.py
def validar_agente_completo(agent_name: str) -> bool:
    """Valida se agente foi criado corretamente"""
    checks = {
        "Persona criada": os.path.exists(f"agentes/personas/{agent_name}.md"),
        "Config atualizada": check_config_updated(agent_name),
        "Testes criados": os.path.exists(f"tests/test_{agent_name}.py"),
        "Trigger único": check_unique_trigger(agent_name),
        "Emoji único": check_unique_emoji(agent_name)
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    return all(checks.values())
```

### **Generator de Documentação**
```python
# generate_docs.py
def gerar_documentacao_agente(agent_name: str):
    """Gera documentação automática do agente"""
    # Implementar geração automática baseada nos templates
    pass
```

---

**🎯 Templates Prontos para Acelerar o Desenvolvimento de Agentes!**

*Templates atualizados em: 30 de Julho de 2025*
*Compatível com Sistema de Agentes v1.0.0*
