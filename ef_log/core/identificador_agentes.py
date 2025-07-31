# -*- coding: utf-8 -*-
"""
Sistema de Identificação Automática de Agentes
=============================================

Este módulo identifica automaticamente todos os agentes disponíveis no sistema,
suas capacidades, status de conexão e hierarquia de comunicação.

Uso:
    from scripts.core.identificador_agentes import IdentificadorAgentes
    
    identificador = IdentificadorAgentes()
    agentes = identificador.identificar_todos()
    print(identificador.gerar_relatorio_visual())
"""

import os
import sys
import ast
import json
import importlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
import inspect

@dataclass
class InfoAgente:
    """Informações completas de um agente."""
    nome: str
    tipo: str
    status: str
    capacidades: List[str]
    cor_codigo: str
    arquivo_origem: str
    linha_definicao: int
    descricao: str
    comandos_suportados: List[str]
    dependencias: List[str]
    prioridade: int
    ativo: bool
    tempo_resposta_medio: float
    ultima_atividade: Optional[datetime] = None

@dataclass
class HierarquiaAgentes:
    """Estrutura hierárquica do sistema de agentes."""
    coordenadores: List[str]
    especialistas: List[str]
    executores: List[str]
    validadores: List[str]
    fluxo_comunicacao: Dict[str, List[str]]

class IdentificadorAgentes:
    """
    Identificador automático de agentes no sistema.
    
    Escaneia o projeto inteiro e identifica:
    - Agentes definidos em classes
    - Agentes em documentação
    - Agentes em configurações
    - Status e capacidades de cada um
    """
    
    def __init__(self, diretorio_projeto: str = None):
        """
        Inicializa o identificador.
        
        Args:
            diretorio_projeto: Diretório raiz do projeto (auto-detecta se None)
        """
        self.logger = logging.getLogger(__name__)
        self.diretorio_projeto = diretorio_projeto or self._detectar_diretorio_projeto()
        self.agentes_encontrados: Dict[str, InfoAgente] = {}
        self.hierarquia: Optional[HierarquiaAgentes] = None
        
        # Cores padrão para diferentes tipos de agentes
        self.cores_tipo = {
            "coordenador": "#FF6B35",    # Laranja vibrante
            "especialista": "#9900FF",   # Roxo IA
            "executor": "#00D4AA",       # Verde tecnológico
            "validador": "#FF0000",      # Vermelho segurança
            "comunicador": "#0077B5",    # Azul LinkedIn
            "distribuidor": "#FFD700",   # Dourado
            "revisor": "#8A2BE2",        # Azul violeta
            "planejador": "#32CD32",     # Verde lima
            "engenheiro": "#1E90FF",     # Azul dodger
            "front_end": "#FF69B4",      # Rosa hot pink
            "matematico": "#4169E1",     # Azul royal
            "escritor": "#FF4500",       # Laranja red
            "default": "#666666"         # Cinza padrão
        }
        
    def _detectar_diretorio_projeto(self) -> str:
        """Detecta automaticamente o diretório raiz do projeto."""
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        
        # Sobe até encontrar arquivos característicos do projeto
        while diretorio_atual != "/":
            if any(os.path.exists(os.path.join(diretorio_atual, arquivo)) 
                   for arquivo in ["app_gpu_fixed.py", "requirements.txt", ".git"]):
                return diretorio_atual
            diretorio_atual = os.path.dirname(diretorio_atual)
            
        return os.getcwd()
    
    def identificar_todos(self) -> Dict[str, InfoAgente]:
        """
        Identifica todos os agentes no sistema.
        
        Returns:
            Dicionário com informações completas de todos os agentes
        """
        self.logger.info("🔍 Iniciando identificação automática de agentes...")
        
        # Limpa resultados anteriores
        self.agentes_encontrados.clear()
        
        # Múltiplas estratégias de identificação
        self._escanear_classes_agente()
        self._escanear_arquivos_teste()
        self._escanear_documentacao()
        self._escanear_configuracoes()
        self._detectar_hierarquia()
        self._verificar_status_agentes()
        
        self.logger.info(f"✅ Identificação concluída! {len(self.agentes_encontrados)} agentes encontrados.")
        
        return self.agentes_encontrados
    
    def _escanear_classes_agente(self):
        """Escaneia classes que herdam de Agente."""
        scripts_dir = os.path.join(self.diretorio_projeto, "scripts")
        tests_dir = os.path.join(self.diretorio_projeto, "tests")
        
        for diretorio in [scripts_dir, tests_dir]:
            if not os.path.exists(diretorio):
                continue
                
            for root, dirs, files in os.walk(diretorio):
                for arquivo in files:
                    if arquivo.endswith(".py"):
                        caminho_arquivo = os.path.join(root, arquivo)
                        self._analisar_arquivo_python(caminho_arquivo)
    
    def _analisar_arquivo_python(self, caminho_arquivo: str):
        """Analisa um arquivo Python procurando definições de agentes."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            tree = ast.parse(conteudo)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._processar_classe(node, caminho_arquivo, conteudo)
                    
        except Exception as e:
            self.logger.warning(f"Erro ao analisar {caminho_arquivo}: {e}")
    
    def _processar_classe(self, node: ast.ClassDef, arquivo: str, conteudo: str):
        """Processa uma classe para determinar se é um agente."""
        nome_classe = node.name
        
        # Verifica se herda de Agente ou contém "Agente" no nome
        eh_agente = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Agente":
                eh_agente = True
                break
        
        if not eh_agente and "agente" not in nome_classe.lower():
            return
        
        # Extrai informações da classe
        docstring = ast.get_docstring(node) or ""
        capacidades = self._extrair_capacidades(node, conteudo)
        comandos = self._extrair_comandos(node, conteudo)
        tipo_agente = self._determinar_tipo_agente(nome_classe, docstring)
        
        info_agente = InfoAgente(
            nome=self._normalizar_nome_agente(nome_classe),
            tipo=tipo_agente,
            status="detectado",
            capacidades=capacidades,
            cor_codigo=self.cores_tipo.get(tipo_agente, self.cores_tipo["default"]),
            arquivo_origem=arquivo,
            linha_definicao=node.lineno,
            descricao=docstring,
            comandos_suportados=comandos,
            dependencias=[],
            prioridade=self._calcular_prioridade(tipo_agente),
            ativo=True,
            tempo_resposta_medio=0.0
        )
        
        self.agentes_encontrados[info_agente.nome] = info_agente
    
    def _extrair_capacidades(self, node: ast.ClassDef, conteudo: str) -> List[str]:
        """Extrai capacidades do agente analisando métodos e docstrings."""
        capacidades = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                nome_metodo = item.name
                if nome_metodo.startswith("processar"):
                    capacidades.append("processamento_mensagens")
                elif nome_metodo.startswith("validar"):
                    capacidades.append("validacao")
                elif nome_metodo.startswith("analisar"):
                    capacidades.append("analise")
                elif nome_metodo.startswith("implementar"):
                    capacidades.append("implementacao")
                elif nome_metodo.startswith("revisar"):
                    capacidades.append("revisao")
                elif nome_metodo.startswith("planejar"):
                    capacidades.append("planejamento")
                elif nome_metodo.startswith("recomendar"):
                    capacidades.append("recomendacao")
        
        return list(set(capacidades))
    
    def _extrair_comandos(self, node: ast.ClassDef, conteudo: str) -> List[str]:
        """Extrai comandos suportados pelo agente."""
        comandos = []
        
        # Procura por padrões de ação em strings
        linhas = conteudo.split('\n')
        for linha in linhas:
            if '"acao"' in linha and '"' in linha:
                # Extrai ações como "implementar", "revisar", etc.
                import re
                acoes = re.findall(r'"acao"[^"]*"([^"]+)"', linha)
                comandos.extend(acoes)
        
        return list(set(comandos))
    
    def _determinar_tipo_agente(self, nome_classe: str, docstring: str) -> str:
        """Determina o tipo do agente baseado no nome e descrição."""
        nome_lower = nome_classe.lower()
        doc_lower = docstring.lower()
        
        # Mapeamento de palavras-chave para tipos
        tipos_keywords = {
            "coordenador": ["coordenador", "orquestrador", "distribuidor"],
            "especialista": ["specialist", "expert", "ia_", "matematico"],
            "executor": ["engenheiro", "executor", "implementador"],
            "validador": ["validador", "revisor", "verificador"],
            "comunicador": ["comunicacao", "mensagem", "notificador"],
            "planejador": ["planejador", "planner", "estrategista"],
            "front_end": ["front", "ui", "interface"],
            "escritor": ["escritor", "documentacao", "redator"]
        }
        
        for tipo, keywords in tipos_keywords.items():
            if any(keyword in nome_lower or keyword in doc_lower for keyword in keywords):
                return tipo
        
        return "executor"  # Tipo padrão
    
    def _normalizar_nome_agente(self, nome_classe: str) -> str:
        """Normaliza o nome do agente para formato padrão."""
        # Remove sufixos comuns
        nome = nome_classe
        if nome.endswith("Agente"):
            nome = nome[:-6]
        elif nome.endswith("Agent"):
            nome = nome[:-5]
        
        # Converte CamelCase para snake_case
        import re
        nome = re.sub('([a-z0-9])([A-Z])', r'\1_\2', nome).lower()
        
        return nome
    
    def _calcular_prioridade(self, tipo_agente: str) -> int:
        """Calcula prioridade baseada no tipo do agente."""
        prioridades = {
            "coordenador": 10,
            "distribuidor": 9,
            "planejador": 8,
            "especialista": 7,
            "executor": 6,
            "validador": 5,
            "comunicador": 4,
            "front_end": 3,
            "escritor": 2
        }
        return prioridades.get(tipo_agente, 1)
    
    def _escanear_arquivos_teste(self):
        """Escaneia arquivos de teste para identificar agentes de exemplo."""
        tests_dir = os.path.join(self.diretorio_projeto, "tests")
        if not os.path.exists(tests_dir):
            return
            
        for arquivo in os.listdir(tests_dir):
            if arquivo.startswith("test_") and arquivo.endswith(".py"):
                caminho = os.path.join(tests_dir, arquivo)
                self._extrair_agentes_de_teste(caminho)
    
    def _extrair_agentes_de_teste(self, caminho_arquivo: str):
        """Extrai informações de agentes de arquivos de teste."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Procura por nomes de agentes em strings
            import re
            agentes_teste = re.findall(r'"([a-z_]+(?:_specialist|_head|_dev|_expert))"', conteudo)
            
            for nome_agente in set(agentes_teste):
                if nome_agente not in self.agentes_encontrados:
                    tipo = self._determinar_tipo_agente(nome_agente, "")
                    
                    info_agente = InfoAgente(
                        nome=nome_agente,
                        tipo=tipo,
                        status="teste",
                        capacidades=["teste"],
                        cor_codigo=self.cores_tipo.get(tipo, self.cores_tipo["default"]),
                        arquivo_origem=caminho_arquivo,
                        linha_definicao=0,
                        descricao=f"Agente identificado em testes: {nome_agente}",
                        comandos_suportados=[],
                        dependencias=[],
                        prioridade=self._calcular_prioridade(tipo),
                        ativo=False,
                        tempo_resposta_medio=0.0
                    )
                    
                    self.agentes_encontrados[nome_agente] = info_agente
                    
        except Exception as e:
            self.logger.warning(f"Erro ao escanear arquivo de teste {caminho_arquivo}: {e}")
    
    def _escanear_documentacao(self):
        """Escaneia arquivos de documentação em busca de definições de agentes."""
        docs_patterns = ["**/*.md", "**/*.rst", "**/*.txt"]
        
        for root, dirs, files in os.walk(self.diretorio_projeto):
            for arquivo in files:
                if arquivo.endswith(('.md', '.rst', '.txt')):
                    caminho = os.path.join(root, arquivo)
                    self._extrair_agentes_de_doc(caminho)
    
    def _extrair_agentes_de_doc(self, caminho_arquivo: str):
        """Extrai definições de agentes de arquivos de documentação."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            import re
            
            # Procura por definições de agentes em markdown
            padroes = [
                r'name:\s*([a-z_]+)',  # name: agente_nome
                r'###\s*([A-Za-z\s]+Agent)',  # ### Nome Agent
                r'##\s*([A-Za-z\s]+Specialist)',  # ## Nome Specialist
            ]
            
            for padrao in padroes:
                matches = re.findall(padrao, conteudo, re.IGNORECASE)
                for match in matches:
                    nome_agente = self._normalizar_nome_agente(match.strip())
                    
                    if nome_agente and nome_agente not in self.agentes_encontrados:
                        tipo = self._determinar_tipo_agente(nome_agente, "")
                        
                        info_agente = InfoAgente(
                            nome=nome_agente,
                            tipo=tipo,
                            status="documentado",
                            capacidades=["documentado"],
                            cor_codigo=self.cores_tipo.get(tipo, self.cores_tipo["default"]),
                            arquivo_origem=caminho_arquivo,
                            linha_definicao=0,
                            descricao=f"Agente documentado em {os.path.basename(caminho_arquivo)}",
                            comandos_suportados=[],
                            dependencias=[],
                            prioridade=self._calcular_prioridade(tipo),
                            ativo=False,
                            tempo_resposta_medio=0.0
                        )
                        
                        self.agentes_encontrados[nome_agente] = info_agente
                        
        except Exception as e:
            self.logger.warning(f"Erro ao escanear documentação {caminho_arquivo}: {e}")
    
    def _escanear_configuracoes(self):
        """Escaneia arquivos de configuração em busca de agentes."""
        config_files = ["settings.json", "config.json", ".claude/settings.json"]
        
        for config_file in config_files:
            caminho = os.path.join(self.diretorio_projeto, config_file)
            if os.path.exists(caminho):
                self._extrair_agentes_de_config(caminho)
    
    def _extrair_agentes_de_config(self, caminho_arquivo: str):
        """Extrai configurações de agentes de arquivos JSON."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Procura por seções de agentes
            if "agents" in config:
                for nome, info in config["agents"].items():
                    if nome not in self.agentes_encontrados:
                        tipo = info.get("type", "executor")
                        
                        info_agente = InfoAgente(
                            nome=nome,
                            tipo=tipo,
                            status="configurado",
                            capacidades=info.get("capabilities", []),
                            cor_codigo=info.get("color", self.cores_tipo.get(tipo, self.cores_tipo["default"])),
                            arquivo_origem=caminho_arquivo,
                            linha_definicao=0,
                            descricao=info.get("description", ""),
                            comandos_suportados=info.get("commands", []),
                            dependencias=info.get("dependencies", []),
                            prioridade=info.get("priority", self._calcular_prioridade(tipo)),
                            ativo=info.get("active", True),
                            tempo_resposta_medio=info.get("avg_response_time", 0.0)
                        )
                        
                        self.agentes_encontrados[nome] = info_agente
                        
        except Exception as e:
            self.logger.warning(f"Erro ao escanear configuração {caminho_arquivo}: {e}")
    
    def _detectar_hierarquia(self):
        """Detecta a hierarquia e fluxo de comunicação entre agentes."""
        coordenadores = []
        especialistas = []
        executores = []
        validadores = []
        fluxo = {}
        
        for nome, agente in self.agentes_encontrados.items():
            if agente.tipo == "coordenador" or agente.tipo == "distribuidor":
                coordenadores.append(nome)
            elif agente.tipo == "especialista":
                especialistas.append(nome)
            elif agente.tipo == "validador" or agente.tipo == "revisor":
                validadores.append(nome)
            else:
                executores.append(nome)
        
        # Detecta fluxo baseado nos testes e código
        fluxo = self._analisar_fluxo_comunicacao()
        
        self.hierarquia = HierarquiaAgentes(
            coordenadores=coordenadores,
            especialistas=especialistas,
            executores=executores,
            validadores=validadores,
            fluxo_comunicacao=fluxo
        )
    
    def _analisar_fluxo_comunicacao(self) -> Dict[str, List[str]]:
        """Analisa o fluxo de comunicação entre agentes."""
        fluxo = {}
        
        # Analisa arquivos de teste para entender o fluxo
        tests_dir = os.path.join(self.diretorio_projeto, "tests")
        if os.path.exists(tests_dir):
            for arquivo in os.listdir(tests_dir):
                if arquivo.endswith(".py"):
                    caminho = os.path.join(tests_dir, arquivo)
                    try:
                        with open(caminho, 'r', encoding='utf-8') as f:
                            conteudo = f.read()
                        
                        # Procura por padrões de comunicação
                        import re
                        padroes_envio = re.findall(r'enviar_para\("([^"]+)"', conteudo)
                        
                        for i, destino in enumerate(padroes_envio):
                            if i > 0:
                                origem = padroes_envio[i-1]
                                if origem not in fluxo:
                                    fluxo[origem] = []
                                if destino not in fluxo[origem]:
                                    fluxo[origem].append(destino)
                                    
                    except Exception:
                        continue
        
        return fluxo
    
    def _verificar_status_agentes(self):
        """Verifica o status de conexão dos agentes."""
        for nome, agente in self.agentes_encontrados.items():
            try:
                # Tenta importar a classe do agente se disponível
                if agente.status == "detectado":
                    agente.status = "ativo"
                    agente.ativo = True
                elif agente.status == "teste":
                    agente.status = "teste_disponivel"
                    agente.ativo = False
                elif agente.status == "documentado":
                    agente.status = "planejado"
                    agente.ativo = False
                    
            except Exception:
                agente.status = "inativo"
                agente.ativo = False
    
    def gerar_relatorio_visual(self) -> str:
        """
        Gera um relatório visual colorido dos agentes identificados.
        
        Returns:
            String com relatório formatado com cores e ícones
        """
        if not self.agentes_encontrados:
            return "❌ Nenhum agente identificado!"
        
        relatorio = []
        relatorio.append("🤖 SISTEMA DE AGENTES IDENTIFICADOS")
        relatorio.append("=" * 50)
        relatorio.append(f"📊 Total de agentes: {len(self.agentes_encontrados)}")
        relatorio.append("")
        
        # Agrupa por tipo
        por_tipo = {}
        for agente in self.agentes_encontrados.values():
            if agente.tipo not in por_tipo:
                por_tipo[agente.tipo] = []
            por_tipo[agente.tipo].append(agente)
        
        # Icons por tipo
        icons_tipo = {
            "coordenador": "👑",
            "especialista": "🧠",
            "executor": "⚙️",
            "validador": "🔍",
            "comunicador": "📡",
            "distribuidor": "🎯",
            "revisor": "📋",
            "planejador": "📝",
            "engenheiro": "🔧",
            "front_end": "🎨",
            "matematico": "📐",
            "escritor": "✍️"
        }
        
        # Status icons
        status_icons = {
            "ativo": "🟢",
            "detectado": "🟡",
            "teste": "🔵",
            "teste_disponivel": "🔵",
            "documentado": "📄",
            "planejado": "⚪",
            "configurado": "⚙️",
            "inativo": "🔴"
        }
        
        for tipo, agentes in sorted(por_tipo.items()):
            relatorio.append(f"{icons_tipo.get(tipo, '🤖')} {tipo.upper()}")
            relatorio.append("-" * 30)
            
            for agente in sorted(agentes, key=lambda x: x.prioridade, reverse=True):
                status_icon = status_icons.get(agente.status, "❓")
                capacidades_str = ", ".join(agente.capacidades[:3])
                if len(agente.capacidades) > 3:
                    capacidades_str += "..."
                
                relatorio.append(f"  {status_icon} {agente.nome}")
                relatorio.append(f"    📍 Status: {agente.status}")
                relatorio.append(f"    🎯 Capacidades: {capacidades_str}")
                if agente.comandos_suportados:
                    comandos_str = ", ".join(agente.comandos_suportados[:2])
                    relatorio.append(f"    💬 Comandos: {comandos_str}")
                relatorio.append(f"    📂 Arquivo: {os.path.basename(agente.arquivo_origem)}")
                relatorio.append("")
        
        # Hierarquia
        if self.hierarquia:
            relatorio.append("🏗️ HIERARQUIA DO SISTEMA")
            relatorio.append("-" * 30)
            relatorio.append(f"👑 Coordenadores: {', '.join(self.hierarquia.coordenadores)}")
            relatorio.append(f"🧠 Especialistas: {', '.join(self.hierarquia.especialistas)}")
            relatorio.append(f"⚙️ Executores: {', '.join(self.hierarquia.executores)}")
            relatorio.append(f"🔍 Validadores: {', '.join(self.hierarquia.validadores)}")
            relatorio.append("")
        
        # Estatísticas
        ativos = sum(1 for a in self.agentes_encontrados.values() if a.ativo)
        relatorio.append("📈 ESTATÍSTICAS")
        relatorio.append("-" * 20)
        relatorio.append(f"🟢 Agentes ativos: {ativos}")
        relatorio.append(f"🔴 Agentes inativos: {len(self.agentes_encontrados) - ativos}")
        relatorio.append(f"🎯 Tipos únicos: {len(por_tipo)}")
        
        return "\n".join(relatorio)
    
    def exportar_json(self, caminho_arquivo: str = None) -> str:
        """
        Exporta informações dos agentes para JSON.
        
        Args:
            caminho_arquivo: Caminho para salvar (auto-gera se None)
            
        Returns:
            Caminho do arquivo gerado
        """
        if not caminho_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_arquivo = os.path.join(
                self.diretorio_projeto, 
                f"agentes_identificados_{timestamp}.json"
            )
        
        dados_export = {
            "timestamp": datetime.now().isoformat(),
            "total_agentes": len(self.agentes_encontrados),
            "diretorio_projeto": self.diretorio_projeto,
            "agentes": {nome: asdict(agente) for nome, agente in self.agentes_encontrados.items()},
            "hierarquia": asdict(self.hierarquia) if self.hierarquia else None
        }
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_export, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"📄 Dados exportados para: {caminho_arquivo}")
        return caminho_arquivo
    
    def obter_agente_por_nome(self, nome: str) -> Optional[InfoAgente]:
        """
        Obtém informações de um agente específico.
        
        Args:
            nome: Nome do agente
            
        Returns:
            Informações do agente ou None se não encontrado
        """
        return self.agentes_encontrados.get(nome)
    
    def listar_agentes_ativos(self) -> List[InfoAgente]:
        """
        Lista apenas os agentes ativos.
        
        Returns:
            Lista de agentes ativos ordenada por prioridade
        """
        agentes_ativos = [a for a in self.agentes_encontrados.values() if a.ativo]
        return sorted(agentes_ativos, key=lambda x: x.prioridade, reverse=True)
    
    def obter_agentes_por_tipo(self, tipo: str) -> List[InfoAgente]:
        """
        Obtém agentes de um tipo específico.
        
        Args:
            tipo: Tipo do agente (coordenador, especialista, etc.)
            
        Returns:
            Lista de agentes do tipo especificado
        """
        return [a for a in self.agentes_encontrados.values() if a.tipo == tipo]
    
    def verificar_dependencias(self) -> Dict[str, List[str]]:
        """
        Verifica dependências entre agentes.
        
        Returns:
            Dicionário com dependências não satisfeitas
        """
        dependencias_nao_satisfeitas = {}
        
        for nome, agente in self.agentes_encontrados.items():
            nao_satisfeitas = []
            for dep in agente.dependencias:
                if dep not in self.agentes_encontrados:
                    nao_satisfeitas.append(dep)
            
            if nao_satisfeitas:
                dependencias_nao_satisfeitas[nome] = nao_satisfeitas
        
        return dependencias_nao_satisfeitas


def main():
    """Função principal para execução direta do script."""
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Cria identificador e executa
    identificador = IdentificadorAgentes()
    agentes = identificador.identificar_todos()
    
    # Exibe relatório
    print(identificador.gerar_relatorio_visual())
    
    # Exporta dados
    arquivo_json = identificador.exportar_json()
    print(f"\n📄 Dados completos salvos em: {arquivo_json}")
    
    # Verificações adicionais
    dependencias = identificador.verificar_dependencias()
    if dependencias:
        print("\n⚠️  DEPENDÊNCIAS NÃO SATISFEITAS:")
        for agente, deps in dependencias.items():
            print(f"  {agente}: {', '.join(deps)}")


if __name__ == "__main__":
    main()
