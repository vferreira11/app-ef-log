"""
Algoritmos de empacotamento 3D otimizados com lógica biomecânica.
"""

import numpy as np
import itertools
from typing import List, Tuple, Dict
from .models import ContainerConfig


# Zonas ergonômicas baseadas em operador de 170cm
ZONA_PREMIUM = (10, 16)      # 100-160cm: Cintura → Olhos (zona ótima)
ZONA_BOA = (16, 18)          # 160-180cm: Olhos → Alcance (esforço mínimo)  
ZONA_ACEITAVEL = (7, 10)     # 70-100cm: Flexão leve → Cintura (esforço baixo)
ZONA_RUIM = (3, 7)           # 30-70cm: Flexão moderada → Joelhos (esforço alto)
ZONA_CRITICA = (0, 3)        # 0-30cm: Chão → Flexão severa (evitar se possível)

def hybrid_intelligent_packing(container: ContainerConfig, block_dims: List[Tuple[int, int, int]], produtos_df) -> List[tuple]:
    """
    🎯 ALGORITMO HÍBRIDO INTELIGENTE - FUSÃO ABC + BIOMECÂNICO + GREEDY
    =====================================================================
    FLUXO OTIMIZADO DE 4 INTELIGÊNCIAS:
    1. 📊 ABC: Classificação por demanda/giro (prioridade operacional)
    2. 🧬 BIOMECÂNICO: Zoneamento ergonômico inteligente (ABC + peso + categoria)
    3. 🏭 CHÃO DO GALPÃO: Empilhamento estável + validação física
    4. 🚀 GREEDY OTIMIZADO: Ajuste fino + preenchimento de lacunas
    
    SEQUÊNCIA OTIMIZADA:
    ABC → Biomecânica → Física → Greedy → Compactação Final
    """
    print("[DEBUG] === 🎯 ALGORITMO HÍBRIDO INTELIGENTE (4 INTELIGÊNCIAS) ===")
    print(f"[DEBUG] Container: {container.dx}x{container.dy}x{container.dz}")
    print(f"[DEBUG] Blocos a processar: {len(block_dims)}")
    
    # 📊 ETAPA 1: ANÁLISE ABC + BIOMECÂNICA INTELIGENTE
    produtos_com_abc = []
    for i, dims in enumerate(block_dims):
        if i < len(produtos_df):
            peso = produtos_df.iloc[i].get('peso', produtos_df.iloc[i].get('peso_kg', 2.0))
            categoria = produtos_df.iloc[i].get('Categoria', produtos_df.iloc[i].get('categoria', 'Utilidades'))
            demanda = produtos_df.iloc[i].get('Previsão Próx. Mês', produtos_df.iloc[i].get('demanda', 10))
        else:
            peso = 2.0
            categoria = 'Utilidades'
            demanda = 10
        
        # Calcula inteligência ABC + Biomecânica
        classe_abc = classificar_abc_por_giro(demanda)
        zona_ergonomica = determinar_zona_biomecanica(demanda, peso, categoria)
        
        produtos_com_abc.append((i, dims, peso, categoria, classe_abc, zona_ergonomica, demanda))
    
    # 📊 ORDENAÇÃO INTELIGENTE: ABC → Demanda → Zona → Peso
    produtos_com_abc.sort(key=lambda x: (
        0 if x[4] == 'A' else 1 if x[4] == 'B' else 2,  # ABC primeiro
        -x[6],  # Demanda decrescente dentro da classe
        0 if x[5] == ZONA_PREMIUM else 1,  # Zona premium preferencial
        -x[2] if x[4] in ['A', 'B'] else x[2]  # Peso: pesados primeiro para A/B, leves primeiro para C
    ))
    
    print(f"[DEBUG] 📊 Ordenação ABC inteligente - Primeiros 5: {[(p[0], f'{p[2]:.1f}kg', p[4], f'{p[6]}dem', p[3]) for p in produtos_com_abc[:5]]}")
    
    alocacoes = []
    produtos_nao_alocados = []  # 🤖 LISTA PARA GREEDY
    posicoes_ocupadas = set()
    
    # 🏭 CHÃO DO GALPÃO: Define zonas ABC + biomecânicas baseadas na altura
    def get_zona_abc_biomecanica(z, peso, classe_abc, zona_ergonomica):
        """Determina adequação ABC + biomecânica por altura, peso e demanda"""
        z_min, z_max = zona_ergonomica
        
        # 📊 PRIORIDADE ABC: Classe A deve estar na zona correta
        if classe_abc == 'A':
            if not (z_min <= z <= z_max):
                return False  # Classe A DEVE estar na zona ABC correta
        elif classe_abc == 'B':
            if not (z_min <= z <= z_max + 3):  # Tolerância +3cm para classe B
                return False
        # Classe C pode ir em qualquer lugar (mais flexível)
        
        # 🧬 VERIFICAÇÃO BIOMECÂNICA: Backup de segurança por peso
        if z <= 5:  # 0-5cm: Zona do chão
            return peso >= 0.8  # Produtos médios/pesados no chão
        elif z <= 30:  # 5-30cm: Zona baixa
            return peso >= 0.3  # Produtos leves+ na zona baixa
        elif z <= 120:  # 30-120cm: Zona ergonômica ideal
            return True  # Qualquer peso - zona principal
        elif z <= 180:  # 120-180cm: Zona alta
            return peso <= 6.0  # Produtos até 6kg na zona alta
        else:  # >180cm: Zona crítica
            return peso <= 4.0  # Produtos até 4kg na zona crítica
    
    # 🚀 FUNÇÃO DE SCORE ABC + COMPACTAÇÃO
    def calcular_score_abc_inteligente(x, y, z, w, d, h, peso, categoria, classe_abc, zona_ergonomica):
        """Score que considera ABC + proximidade + adjacência"""
        # Base: proximidade ao canto (0,0,0)
        score = x + y + z * 0.1
        
        # 📊 BONUS/PENALIZAÇÃO ABC MASSIVA
        z_min, z_max = zona_ergonomica
        if classe_abc == 'A':
            if z_min <= z <= z_max:
                score -= 100.0  # BONUS ENORME para A na zona correta
            else:
                score += 50.0   # PENALIZAÇÃO SEVERA para A fora da zona
        elif classe_abc == 'B':
            if z_min <= z <= z_max + 3:  # Tolerância para B
                score -= 20.0   # Bonus moderado
            else:
                score += 10.0   # Penalização leve
        # Classe C não tem bonus/penalização (flexível)
        
        # Bonus por adjacência (blocos vizinhos)
        bonus_adjacencia = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    if (x + dx, y + dy, z + dz) in posicoes_ocupadas:
                        bonus_adjacencia += 1
        
        score -= bonus_adjacencia * 2.0  # Forte incentivo à proximidade
        
        # 🧬 Bonus biomecânico por categoria (secundário)
        if categoria in ['Brinquedos', 'Organizadores']:
            score -= 3.0  # Prioriza itens acessíveis (menor que ABC)
        elif categoria == 'Utilidades':
            score += 1.0  # Pode ficar em locais menos acessíveis
            
        return score
    
    # 🎯 ETAPA 2: ALOCAÇÃO PRINCIPAL (ABC + BIOMECÂNICA + FÍSICA)
    for produto_idx, dims, peso, categoria, classe_abc, zona_ergonomica, demanda in produtos_com_abc:
        w, d, h = dims
        melhor_posicao = None
        melhor_score = float('inf')
        
        print(f"[DEBUG] 🎯 Processando produto {produto_idx}: {w}x{d}x{h}, {peso:.1f}kg, {classe_abc}, {categoria}")
        print(f"[DEBUG] 📐 Container disponível: {container.dx}x{container.dy}x{container.dz}")
        
        # 🏭 CHÃO DO GALPÃO: Força prioridade por camadas (Z crescente)
        for z in range(0, container.dz - h + 1):
            
            # 📊 ABC + 🧬 BIOMECÂNICO: Verifica adequação integrada
            zona_adequada = get_zona_abc_biomecanica(z, peso, classe_abc, zona_ergonomica)
            print(f"[DEBUG] 📊🧬 Z={z}: zona ABC+bio adequada para {classe_abc}({peso:.1f}kg)? {zona_adequada}")
            if not zona_adequada:
                print(f"[DEBUG] ❌ Zona ABC+biomecânica rejeitou Z={z} para {classe_abc}")
                continue
                
            # Busca posição na camada atual
            encontrou_nesta_camada = False
            posicoes_testadas = 0
            
            for x in range(0, container.dx - w + 1):
                for y in range(0, container.dy - d + 1):
                    posicoes_testadas += 1
                    
                    # Verifica colisões
                    colidiu = False
                    for check_x in range(x, x + w):
                        for check_y in range(y, y + d):
                            for check_z in range(z, z + h):
                                if (check_x, check_y, check_z) in posicoes_ocupadas:
                                    colidiu = True
                                    break
                            if colidiu:
                                break
                        if colidiu:
                            break
                    
                    if colidiu:
                        continue
                    
                    # 🏭 CHÃO DO GALPÃO: Verifica estabilidade (60% de suporte mínimo)
                    estavel = True
                    if z > 0:
                        area_com_suporte = 0
                        area_total = w * d
                        for check_x in range(x, x + w):
                            for check_y in range(y, y + d):
                                if (check_x, check_y, z - 1) in posicoes_ocupadas:
                                    area_com_suporte += 1
                        # 60% de suporte mínimo (equilibrio entre realismo e flexibilidade)
                        if (area_com_suporte / area_total) < 0.60:
                            estavel = False
                    
                    if not estavel:
                        suporte_percent = (area_com_suporte / area_total) * 100 if z > 0 else 100
                        print(f"[DEBUG] ⚠️ Posição ({x},{y},{z}) instável - suporte {suporte_percent:.1f}% (mín 60%)")
                        continue
                    
                    # 🚀 SCORE ABC INTELIGENTE: Calcula score integrado
                    score = calcular_score_abc_inteligente(x, y, z, w, d, h, peso, categoria, classe_abc, zona_ergonomica)
                    
                    if score < melhor_score:
                        melhor_score = score
                        melhor_posicao = (x, y, z)
                        encontrou_nesta_camada = True
                        print(f"[DEBUG] 🚀 Nova melhor posição: ({x},{y},{z}) - Score: {score:.2f}")
            
            print(f"[DEBUG] 📊 Z={z}: testadas {posicoes_testadas} posições, encontrou válida? {encontrou_nesta_camada}")
            
            # 🏭 CHÃO DO GALPÃO: Se encontrou posição nesta camada, para (prioriza camadas baixas)
            if encontrou_nesta_camada:
                break
        
        # Aloca na melhor posição encontrada
        if melhor_posicao:
            x, y, z = melhor_posicao
            
            # Marca posições como ocupadas
            for check_x in range(x, x + w):
                for check_y in range(y, y + d):
                    for check_z in range(z, z + h):
                        posicoes_ocupadas.add((check_x, check_y, check_z))
            
            alocacoes.append((x, y, z, produto_idx))
            zona = "chão" if z <= 5 else "baixa" if z <= 30 else "ideal" if z <= 120 else "alta" if z <= 180 else "crítica"
            print(f"[DEBUG] ✅ Produto {produto_idx} ({classe_abc}) alocado em ({x},{y},{z}) - Zona: {zona}, Score: {melhor_score:.2f}")
        else:
            # 🤖 ADICIONA À LISTA GREEDY
            produtos_nao_alocados.append((produto_idx, dims, peso, categoria, classe_abc, zona_ergonomica, demanda))
            print(f"[DEBUG] ⏳ Produto {produto_idx} ({classe_abc}) não alocado - será processado pelo GREEDY")
    
    print(f"[DEBUG] 📊 ETAPA 2 CONCLUÍDA: {len(alocacoes)} alocados, {len(produtos_nao_alocados)} para GREEDY")
    
    # 🤖 ETAPA 3: GREEDY INTELIGENTE (Recuperação + Otimização)
    if produtos_nao_alocados:
        print(f"[DEBUG] === 🤖 GREEDY INTELIGENTE: Processando {len(produtos_nao_alocados)} produtos ===")
        
        # Ordena produtos não alocados por prioridade (A > B > C, demanda alta > baixa)
        produtos_nao_alocados.sort(key=lambda x: (
            0 if x[4] == 'A' else 1 if x[4] == 'B' else 2,  # ABC primeiro
            -x[6],  # Demanda decrescente
            -x[2]   # Peso decrescente (estabilidade)
        ))
        
        alocacoes_greedy = aplicar_greedy_inteligente(
            container, produtos_nao_alocados, posicoes_ocupadas
        )
        
        alocacoes.extend(alocacoes_greedy)
        print(f"[DEBUG] 🤖 GREEDY recuperou: {len(alocacoes_greedy)} produtos adicionais")
    
    print(f"[DEBUG] === 🎯 HÍBRIDO INTELIGENTE CONCLUÍDO: {len(alocacoes)}/{len(block_dims)} produtos alocados ===")
    return alocacoes


def aplicar_greedy_inteligente(container: ContainerConfig, produtos_nao_alocados: List[tuple], posicoes_ocupadas: set) -> List[tuple]:
    """
    🤖 GREEDY INTELIGENTE: Recupera produtos rejeitados com flexibilidade adaptativa
    
    Args:
        container: Configuração do container
        produtos_nao_alocados: Lista de produtos que falharam na alocação ABC
        posicoes_ocupadas: Set de posições já ocupadas (modificado in-place)
        
    Returns:
        Lista de alocações recuperadas pelo Greedy
    """
    alocacoes_greedy = []
    
    for produto_idx, dims, peso, categoria, classe_abc, zona_ergonomica, demanda in produtos_nao_alocados:
        w, d, h = dims
        melhor_posicao = None
        melhor_score = float('inf')
        
        print(f"[DEBUG] 🤖 GREEDY processando {produto_idx} ({classe_abc}): {w}x{d}x{h}")
        
        # 🤖 GREEDY: Busca QUALQUER posição válida (sem restrições ABC)
        for z in range(0, container.dz - h + 1):
            for x in range(0, container.dx - w + 1):
                for y in range(0, container.dy - d + 1):
                    
                    # Verifica colisões
                    colidiu = False
                    for check_x in range(x, x + w):
                        for check_y in range(y, y + d):
                            for check_z in range(z, z + h):
                                if (check_x, check_y, check_z) in posicoes_ocupadas:
                                    colidiu = True
                                    break
                            if colidiu:
                                break
                        if colidiu:
                            break
                    
                    if colidiu:
                        continue
                    
                    # 🏭 Verifica estabilidade básica (mais flexível que ABC)
                    estavel = True
                    if z > 0:
                        area_com_suporte = 0
                        area_total = w * d
                        for check_x in range(x, x + w):
                            for check_y in range(y, y + d):
                                if (check_x, check_y, z - 1) in posicoes_ocupadas:
                                    area_com_suporte += 1
                        # 40% de suporte mínimo (mais flexível que os 60% do ABC)
                        if (area_com_suporte / area_total) < 0.40:
                            estavel = False
                    
                    if not estavel:
                        continue
                    
                    # 🤖 Score Greedy: prioriza proximidade + prefere zona ABC quando possível
                    score = x + y + z * 0.1
                    
                    # Bonus se conseguir ficar na zona ABC ideal (mas não obrigatório)
                    z_min, z_max = zona_ergonomica
                    if z_min <= z <= z_max:
                        score -= 10.0  # Bonus por zona correta
                    
                    # Bonus por classe (tenta salvar classe A)
                    if classe_abc == 'A':
                        score -= 5.0  # Prioriza classe A
                    elif classe_abc == 'B':
                        score -= 2.0  # Prioriza classe B
                    
                    if score < melhor_score:
                        melhor_score = score
                        melhor_posicao = (x, y, z)
        
        # Aloca se encontrou posição
        if melhor_posicao:
            x, y, z = melhor_posicao
            
            # Marca posições como ocupadas
            for check_x in range(x, x + w):
                for check_y in range(y, y + d):
                    for check_z in range(z, z + h):
                        posicoes_ocupadas.add((check_x, check_y, check_z))
            
            alocacoes_greedy.append((x, y, z, produto_idx))
            zona = "chão" if z <= 5 else "baixa" if z <= 30 else "ideal" if z <= 120 else "alta" if z <= 180 else "crítica"
            print(f"[DEBUG] 🤖 GREEDY salvou {produto_idx} ({classe_abc}) em ({x},{y},{z}) - Zona: {zona}")
        else:
            print(f"[DEBUG] 🤖 GREEDY falhou: {produto_idx} ({classe_abc}) sem espaço")
    
    return alocacoes_greedy


def gpu_optimize_packing_biomecanico(container: ContainerConfig, block_dims: List[Tuple[int, int, int]], produtos_df) -> List[tuple]:
    """
    Implementa algoritmo biomecânico baseado em zonas ergonômicas.
    """
    # Continuação da função existente...
ZONA_CRITICA = (0, 3)        # 0-30cm: Agachamento profundo (esforço máximo)
ZONA_ALTA = (18, 21)         # 180-210cm: Braço estendido (força reduzida)

# Zonas ajustadas para começar do chão (quando force_floor=True)
ZONA_PREMIUM_CHAO = (0, 6)   # 0-60cm: Primeira zona preferencial
ZONA_BOA_CHAO = (6, 12)      # 60-120cm: Segunda zona preferencial
ZONA_ACEITAVEL_CHAO = (12, 18)  # 120-180cm: Terceira zona
ZONA_RUIM_CHAO = (18, 24)    # 180-240cm: Zona de alcance difícil
ZONA_CRITICA_CHAO = (24, 30) # 240-300cm: Zona crítica alta
ZONA_ALTA_CHAO = (30, 36)    # 300-360cm: Zona muito alta


def classificar_abc_por_giro(demanda_mensal: int) -> str:
    """
    Classifica produto em classe ABC baseado na demanda mensal.
    Usa regra 80/15/5 da logística.
    
    Args:
        demanda_mensal: Previsão de demanda do próximo mês
        
    Returns:
        Classe ABC ('A', 'B', ou 'C')
    """
    if demanda_mensal >= 50:      # Alto giro: 80% dos picks
        return 'A'
    elif demanda_mensal >= 15:    # Médio giro: 15% dos picks  
        return 'B'
    else:                         # Baixo giro: 5% dos picks
        return 'C'


def calcular_fragilidade_por_categoria(categoria: str) -> float:
    """
    Calcula score de fragilidade baseado na categoria do produto.
    
    Args:
        categoria: Categoria do produto
        
    Returns:
        Score de fragilidade (0.0 = robusto, 1.0 = muito frágil)
    """
    fragilidade_por_categoria = {
        "Brinquedos": 0.6,        # Moderadamente frágil (plástico, eletrônicos)
        "Utilidades": 0.4,        # Robustos (uso doméstico)
        "Organizadores": 0.2      # Muito robustos (estruturais)
    }
    return fragilidade_por_categoria.get(categoria, 0.5)


def determinar_zona_biomecanica(demanda: int, peso_kg: float, categoria: str) -> Tuple[int, int]:
    """
    Determina a zona ergonômica ideal baseada em critérios biomecânicos.
    
    Args:
        demanda: Previsão de demanda mensal
        peso_kg: Peso do produto em kg
        categoria: Categoria do produto
        
    Returns:
        Tupla (z_min, z_max) da zona ergonômica em cm (convertida para nossa escala)
    """
    classe_abc = classificar_abc_por_giro(demanda)
    fragilidade = calcular_fragilidade_por_categoria(categoria)
    
    # Produtos classe A ou muito frágeis vão para zona premium
    if classe_abc == 'A' or fragilidade > 0.5:
        return ZONA_PREMIUM
    
    # Produtos pesados em baixo (física + biomecânica)
    elif peso_kg > 0.5:
        if classe_abc == 'B':
            return ZONA_ACEITAVEL
        else:
            return ZONA_RUIM
    
    # Produtos muito leves podem ir em cima
    elif peso_kg < 0.2:
        if classe_abc == 'B':
            return ZONA_BOA
        else:
            return ZONA_ALTA
    
    # Resto distribui por giro
    else:
        if classe_abc == 'B':
            return ZONA_BOA
        else:
            return ZONA_ACEITAVEL


def get_orientations(lx: int, ly: int, lz: int) -> List[Tuple[int, int, int]]:
    """Retorna todas as orientações possíveis de um bloco."""
    dims = [lx, ly, lz]
    return list(set(itertools.permutations(dims)))


def greedy_pack_biomecanico(container: ContainerConfig, produtos_data: List[Dict]) -> List[tuple]:
    """
    Empacotamento biomecânico otimizado: considera ergonomia, giro e peso.
    Aloca produtos nas zonas ergonômicas ideais baseado em critérios logísticos.
    
    Args:
        container: Configuração do container
        produtos_data: Lista de dicionários com dados completos dos produtos:
                      {'dims': (x,y,z), 'peso': float, 'demanda': int, 'categoria': str}
        
    Returns:
        Lista de alocações (x, y, z, block_index, orientation)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    # Etapa 1: Classifica produtos por zona biomecânica
    produtos_por_zona = {
        'premium': [], 'boa': [], 'aceitavel': [], 'ruim': [], 'critica': [], 'alta': []
    }
    
    for idx, produto in enumerate(produtos_data):
        zona_range = determinar_zona_biomecanica(
            produto['demanda'], 
            produto['peso'], 
            produto['categoria']
        )
        
        produto_info = {
            'index': idx,
            'dims': produto['dims'],
            'zona_range': zona_range,
            'peso': produto['peso'],
            'demanda': produto['demanda']
        }
        
        # Mapeia zona range para nome
        if zona_range == ZONA_PREMIUM:
            produtos_por_zona['premium'].append(produto_info)
        elif zona_range == ZONA_BOA:
            produtos_por_zona['boa'].append(produto_info)
        elif zona_range == ZONA_ACEITAVEL:
            produtos_por_zona['aceitavel'].append(produto_info)
        elif zona_range == ZONA_RUIM:
            produtos_por_zona['ruim'].append(produto_info)
        elif zona_range == ZONA_CRITICA:
            produtos_por_zona['critica'].append(produto_info)
        else:  # ZONA_ALTA
            produtos_por_zona['alta'].append(produto_info)
    
    print(f"[DEBUG] Distribuição por zona: Premium={len(produtos_por_zona['premium'])}, "
          f"Boa={len(produtos_por_zona['boa'])}, Aceitável={len(produtos_por_zona['aceitavel'])}, "
          f"Ruim={len(produtos_por_zona['ruim'])}, Crítica={len(produtos_por_zona['critica'])}, "
          f"Alta={len(produtos_por_zona['alta'])}")
    
    # Etapa 2: Empacota por ordem de prioridade ergonômica
    ordem_empacotamento = ['premium', 'boa', 'aceitavel', 'ruim', 'critica', 'alta']
    
    for zona_nome in ordem_empacotamento:
        produtos_zona = produtos_por_zona[zona_nome]
        if not produtos_zona:
            continue
            
        # Ordena por demanda (maior giro primeiro dentro da zona)
        produtos_zona.sort(key=lambda p: p['demanda'], reverse=True)
        
        print(f"[DEBUG] Empacotando zona {zona_nome}: {len(produtos_zona)} produtos")
        
        for produto in produtos_zona:
            colocado = False
            original_dims = produto['dims']
            zona_z_min, zona_z_max = produto['zona_range']
            
            orientations = get_orientations(*original_dims)
            
            # Tenta cada orientação
            for orientation in orientations:
                if colocado:
                    break
                lx, ly, lz = orientation
                
                # EMPACOTAMENTO BIOMECÂNICO: X → Y → Z dentro da zona ergonômica
                for z in range(zona_z_min, min(zona_z_max, container.dz - lz + 1)):
                    if colocado:
                        break
                    for y in range(0, container.dy - ly + 1):
                        if colocado:
                            break
                        for x in range(0, container.dx - lx + 1):
                            # Verifica se a posição está livre
                            if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                                # Marca como ocupado
                                ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                                # Adiciona à lista de alocações
                                placements.append((x, y, z, produto['index'], orientation))
                                colocado = True
                                print(f"[DEBUG] Produto {produto['index']} (zona {zona_nome}) colocado em ({x},{y},{z})")
                                break
            
            if not colocado:
                print(f"[DEBUG] Produto {produto['index']} não pôde ser alocado na zona {zona_nome}")
    
    # Debug: estatísticas finais
    z_positions = [p[2] for p in placements]
    if z_positions:
        z_unique = sorted(set(z_positions))
        print(f"[DEBUG] Camadas Z (altura) ocupadas: {z_unique}")
        for z in z_unique:
            count = sum(1 for pos in z_positions if pos == z)
            print(f"[DEBUG] Camada Z={z}: {count} blocos")
    
    return placements


def greedy_pack_floor_based(container: ContainerConfig, block_dims: List[Tuple[int, int, int]]) -> List[tuple]:
    """
    Empacotamento baseado no chão do galpão: preenche plano XY completamente antes de subir em Z.
    Simula um armazém real onde produtos são organizados em camadas no chão (XY) e empilhados em altura (Z).
    
    Convenção matemática:
    - X: Largura (esquerda-direita)
    - Y: Profundidade (frente-trás) 
    - Z: Altura (baixo-cima) - DIREÇÃO DO EMPILHAMENTO
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de alocações (x, y, z, block_index, orientation)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    # Debug: rastrear posições Z para verificar empacotamento por camadas (altura)
    z_positions = []
    
    for bloco_idx, original_dims in enumerate(block_dims):
        colocado = False
        orientations = get_orientations(*original_dims)
        
        # Tenta cada orientação
        for orientation in orientations:
            if colocado:
                break
            lx, ly, lz = orientation
            
            # REGRA DO GALPÃO: Preenche camadas Z (altura) de baixo para cima
            # Percorre camadas Z de baixo para cima (empilhamento em altura)
            for z in range(container.dz - lz + 1):
                if colocado:
                    break
                # Para cada camada Z, percorre todo o plano XY (chão do galpão)
                for x in range(container.dx - lx + 1):
                    if colocado:
                        break
                    for y in range(container.dy - ly + 1):
                        # Verifica se o espaço está livre
                        if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                            # Marca como ocupado
                            ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                            # Salva com a orientação usada
                            placements.append((x, y, z, bloco_idx, orientation))
                            z_positions.append(z)
                            colocado = True
                            break
        
        if not colocado:
            break
    
    # Debug: estatísticas das camadas Z (altura)
    if z_positions:
        unique_z = list(set(z_positions))
        unique_z.sort()
        print(f"[DEBUG] Camadas Z (altura) ocupadas: {unique_z}")
        for z_layer in unique_z:
            count = z_positions.count(z_layer)
            print(f"[DEBUG] Camada Z={z_layer}: {count} blocos")
    
    return placements


def greedy_pack_with_rotation(container: ContainerConfig, block_dims: List[Tuple[int, int, int]]) -> List[tuple]:
    """
    Empacotamento sequencial com ROTAÇÃO: maximiza preenchimento.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de alocações (x, y, z, block_index, orientation)
    """
    placements = []
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    
    for bloco_idx, original_dims in enumerate(block_dims):
        colocado = False
        orientations = get_orientations(*original_dims)
        
        # Tenta cada orientação
        for orientation in orientations:
            if colocado:
                break
            lx, ly, lz = orientation
            
            # Percorre o container sequencialmente
            for x in range(container.dx - lx + 1):
                if colocado:
                    break
                for y in range(container.dy - ly + 1):
                    if colocado:
                        break
                    for z in range(container.dz - lz + 1):
                        # Verifica se o espaço está livre
                        if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                            # Marca como ocupado
                            ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                            # Salva com a orientação usada
                            placements.append((x, y, z, bloco_idx, orientation))
                            colocado = True
                            break
        
        if not colocado:
            break
    
    return placements


def gpu_optimize_packing(container: ContainerConfig, block_dims: List[Tuple[int, int, int]], max_capacity: int, produtos_df=None, force_floor=False, hybrid_mode=False) -> List[tuple]:
    """
    Otimização de empacotamento com algoritmo biomecânico, GPU simulado, chão do galpão ou híbrido.
    
    Args:
        container: Configuração do container (pode ter múltiplos containers)
        block_dims: Lista de dimensões dos blocos
        max_capacity: Capacidade máxima de blocos
        produtos_df: DataFrame com dados dos produtos (opcional)
        force_floor: Se True, força empacotamento a partir do chão (Z=0)
        hybrid_mode: Se True, usa algoritmo híbrido (GPU + Biomecânico + Chão)
        
    Returns:
        Lista de alocações otimizadas com offset para múltiplos containers
    """
    # Limita aos blocos que cabem teoricamente
    target_blocks = min(max_capacity, len(block_dims))
    target_dims = block_dims[:target_blocks]
    
    # ALGORITMO HÍBRIDO: Combina os 3 métodos
    if hybrid_mode and produtos_df is not None and not produtos_df.empty:
        print("[DEBUG] Usando algoritmo HÍBRIDO INTELIGENTE")
        return hybrid_intelligent_packing(container, target_dims, produtos_df)
    
    # Se force_floor=True, usa algoritmo de chão do galpão
    if force_floor:
        print("[DEBUG] Usando algoritmo de chão do galpão (força Z=0)")
        if container.quantidade == 1:
            return greedy_pack_floor_based(container, target_dims)
        # Para múltiplos containers, distribui usando chão do galpão
        return distribute_multiple_containers_floor(container, target_dims)
    
    # Se temos dados dos produtos, usa algoritmo biomecânico
    if produtos_df is not None and not produtos_df.empty:
        print("[DEBUG] Usando algoritmo biomecânico com dados dos produtos")
        return gpu_optimize_packing_biomecanico(container, target_dims, produtos_df)
    
    # Senão, usa algoritmo original
    print("[DEBUG] Usando algoritmo original (sem dados de produtos)")
    
    if container.quantidade == 1:
        # Container único - algoritmo original
        placements = greedy_pack_floor_based(container, target_dims)
        return placements
    
    # Múltiplos containers - distribui os blocos
    all_placements = []
    blocks_per_container = len(target_dims) // container.quantidade
    remaining_blocks = len(target_dims) % container.quantidade
    
    print(f"[DEBUG] Distribuindo {len(target_dims)} blocos em {container.quantidade} containers:")
    print(f"[DEBUG] {blocks_per_container} blocos por container, {remaining_blocks} extras")
    
    start_idx = 0
    
    for container_idx in range(container.quantidade):
        # Calcula quantos blocos este container vai ter
        blocks_for_this = blocks_per_container
        if container_idx < remaining_blocks:
            blocks_for_this += 1
            
        if blocks_for_this == 0:
            continue
            
        # Pega os blocos para este container
        container_blocks = target_dims[start_idx:start_idx + blocks_for_this]
        
        # Cria container individual
        single_container = ContainerConfig(container.dx, container.dy, container.dz, 1)
        
        # Empacota neste container
        container_placements = greedy_pack_floor_based(single_container, container_blocks)
        
        # Aplica offset X para separar containers visualmente
        offset_x = container_idx * (container.dx + 10)  # 10 unidades de espaçamento
        
        # Adiciona offset nas coordenadas e ajusta índices dos blocos
        for placement in container_placements:
            if len(placement) == 5:
                x, y, z, block_idx, orientation = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + block_idx, orientation)
            else:
                x, y, z, block_idx = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + block_idx)
            
            all_placements.append(adjusted_placement)
        
        print(f"[DEBUG] Container {container_idx + 1}: {len(container_placements)} blocos colocados (offset X={offset_x})")
        start_idx += blocks_for_this
    
    print(f"[DEBUG] Total final: {len(all_placements)} blocos em {container.quantidade} containers")
    return all_placements


def distribute_multiple_containers_floor(container: ContainerConfig, target_dims: List[Tuple[int, int, int]]) -> List[tuple]:
    """
    Distribui blocos em múltiplos containers usando algoritmo de chão do galpão.
    
    Args:
        container: Configuração do container
        target_dims: Lista de dimensões dos blocos
        
    Returns:
        Lista de alocações com offset para múltiplos containers
    """
    all_placements = []
    blocks_per_container = len(target_dims) // container.quantidade
    remaining_blocks = len(target_dims) % container.quantidade
    
    print(f"[DEBUG] Distribuindo {len(target_dims)} blocos em {container.quantidade} containers (chão do galpão):")
    print(f"[DEBUG] {blocks_per_container} blocos por container, {remaining_blocks} extras")
    
    start_idx = 0
    
    for container_idx in range(container.quantidade):
        # Calcula quantos blocos este container vai ter
        blocks_for_this = blocks_per_container
        if container_idx < remaining_blocks:
            blocks_for_this += 1
            
        if blocks_for_this == 0:
            continue
            
        # Pega os blocos para este container
        container_blocks = target_dims[start_idx:start_idx + blocks_for_this]
        
        # Cria container individual
        single_container = ContainerConfig(container.dx, container.dy, container.dz, 1)
        
        # Empacota neste container usando chão do galpão
        container_placements = greedy_pack_floor_based(single_container, container_blocks)
        
        # Aplica offset X para separar containers visualmente
        offset_x = container_idx * (container.dx + 10)  # 10 unidades de espaçamento
        
        # Adiciona offset nas coordenadas e ajusta índices dos blocos
        for placement in container_placements:
            if len(placement) == 5:
                x, y, z, block_idx, orientation = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + block_idx, orientation)
            else:
                x, y, z, block_idx = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + block_idx)
            
            all_placements.append(adjusted_placement)
        
        print(f"[DEBUG] Container {container_idx + 1}: {len(container_placements)} blocos colocados (offset X={offset_x})")
        start_idx += blocks_for_this
    
    print(f"[DEBUG] Total final: {len(all_placements)} blocos em {container.quantidade} containers")
    return all_placements


def gpu_optimize_packing_biomecanico(container: ContainerConfig, target_dims: List[Tuple[int, int, int]], produtos_df) -> List[tuple]:
    """
    Versão biomecânica do algoritmo de empacotamento com múltiplos containers.
    
    Args:
        container: Configuração do container
        target_dims: Lista de dimensões dos blocos limitada
        produtos_df: DataFrame com dados dos produtos
        
    Returns:
        Lista de alocações otimizadas
    """
    # Prepara dados dos produtos para o algoritmo biomecânico
    produtos_data = []
    block_idx = 0
    
    for _, row in produtos_df.iterrows():
        demanda = int(row['Previsão Próx. Mês'])
        peso = float(row['Peso (kg)'])
        categoria = str(row['Categoria'])
        dims = (int(row['Comprimento']), int(row['Largura']), int(row['Profundidade']))
        
        # Adiciona produtos conforme a demanda (repetições)
        for _ in range(demanda):
            if block_idx >= len(target_dims):
                break
                
            produtos_data.append({
                'dims': target_dims[block_idx],  # Usa dimensões já processadas
                'peso': peso,
                'demanda': demanda,
                'categoria': categoria
            })
            block_idx += 1
            
        if block_idx >= len(target_dims):
            break
    
    if container.quantidade == 1:
        # Container único - algoritmo biomecânico
        return greedy_pack_biomecanico(container, produtos_data)
    
    # Múltiplos containers com algoritmo biomecânico
    all_placements = []
    products_per_container = len(produtos_data) // container.quantidade
    remaining_products = len(produtos_data) % container.quantidade
    
    print(f"[DEBUG] Distribuindo {len(produtos_data)} produtos biomecânicos em {container.quantidade} containers:")
    print(f"[DEBUG] {products_per_container} produtos por container, {remaining_products} extras")
    
    start_idx = 0
    
    for container_idx in range(container.quantidade):
        products_for_this = products_per_container
        if container_idx < remaining_products:
            products_for_this += 1
            
        if products_for_this == 0:
            continue
            
        # Pega produtos para este container
        container_products = produtos_data[start_idx:start_idx + products_for_this]
        
        # Cria container individual
        single_container = ContainerConfig(container.dx, container.dy, container.dz, 1)
        
        # Empacota neste container com algoritmo biomecânico
        container_placements = greedy_pack_biomecanico(single_container, container_products)
        
        # Aplica offset X para separar containers visualmente
        offset_x = container_idx * (container.dx + 10)
        
        # Adiciona offset e ajusta índices
        for placement in container_placements:
            if len(placement) == 5:
                x, y, z, product_idx, orientation = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + product_idx, orientation)
            else:
                x, y, z, product_idx = placement
                adjusted_placement = (x + offset_x, y, z, start_idx + product_idx)
            
            all_placements.append(adjusted_placement)
        
        print(f"[DEBUG] Container {container_idx + 1}: {len(container_placements)} produtos biomecânicos colocados (offset X={offset_x})")
        start_idx += products_for_this
    
    print(f"[DEBUG] Total final biomecânico: {len(all_placements)} produtos em {container.quantidade} containers")
    return all_placements


def hybrid_pack(container: ContainerConfig, block_dims: List[Tuple[int, int, int]], gpu_placements: List[tuple]) -> List[tuple]:
    """
    Algoritmo híbrido: usa resultado GPU e preenche buracos com Greedy.
    
    Args:
        container: Configuração do container
        block_dims: Lista de dimensões dos blocos
        gpu_placements: Alocações do algoritmo GPU
        
    Returns:
        Lista de alocações híbridas
    """
    ocupado = np.zeros((container.dx, container.dy, container.dz), dtype=bool)
    placements = []
    
    # Marca posições ocupadas pelo GPU
    for placement in gpu_placements:
        if len(placement) == 5:
            x0, y0, z0, o, orientation = placement
            lx, ly, lz = orientation
        else:
            x0, y0, z0, o = placement
            lx, ly, lz = block_dims[o]
            
        if x0 + lx <= container.dx and y0 + ly <= container.dy and z0 + lz <= container.dz:
            ocupado[x0:x0+lx, y0:y0+ly, z0:z0+lz] = True
            placements.append(placement)
    
    # Tenta encaixar blocos restantes nos buracos
    used_blocks = len(placements)
    for bloco_idx in range(used_blocks, len(block_dims)):
        lx, ly, lz = block_dims[bloco_idx]
        colocado = False
        
        for x in range(container.dx - lx + 1):
            if colocado: 
                break
            for y in range(container.dy - ly + 1):
                if colocado: 
                    break
                for z in range(container.dz - lz + 1):
                    if not ocupado[x:x+lx, y:y+ly, z:z+lz].any():
                        ocupado[x:x+lx, y:y+ly, z:z+lz] = True
                        placements.append((x, y, z, bloco_idx))
                        colocado = True
                        break
    
    return placements