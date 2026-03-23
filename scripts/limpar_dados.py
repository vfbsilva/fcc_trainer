#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path

def limpar_agressivo(texto):
    """Limpeza MUITO agressiva de enunciado"""
    if not texto:
        return ""

    # Remover HTML
    texto = re.sub(r'<[^>]+>', '', texto)

    # Encontrar onde começa o enunciado real (primeira frase com maiúscula)
    # Remove números iniciais e metadados
    linhas = texto.split('\n')
    enunciado_start = -1

    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        if linha_limpa and len(linha_limpa) > 10:
            # Pular linhas com metadados conhecidos
            if any(keyword in linha_limpa.upper() for keyword in ['BANCA', 'ÓRGÃO', 'PROVA', 'ALTERNATIVAS', 'RESPONDER', 'VOCÊ']):
                continue
            # Pular linhas que são apenas tópicos/assuntos
            if ',' in linha_limpa and len(linha_limpa) < 50:
                continue
            # Se chegou aqui, é o início do enunciado
            enunciado_start = i
            break

    if enunciado_start >= 0:
        texto = '\n'.join(linhas[enunciado_start:])

    # Remover tudo depois de "Responder", "Você errou", etc (artefatos da página)
    texto = re.split(r'(?:Responder|Você errou|Parabéns|Clique|Ver|gabarito)', texto, flags=re.IGNORECASE)[0]

    # Remover linhas que parecem ser metadados
    texto = re.sub(r'(?:Banca|Órgão|Prova|Ano):\s*.*$', '', texto, flags=re.MULTILINE | re.IGNORECASE)

    # Remover espaços excessivos
    texto = re.sub(r'\s+', ' ', texto).strip()

    # Remover "Alternativas" ou similar no final
    texto = re.sub(r'(Alternativas|alternativas).*$', '', texto)

    return texto.strip()


def extrair_question_id(html):
    """Extrair ID da questão do HTML"""
    if not html:
        return None

    # Procurar por data-question-id="XXXXX"
    match = re.search(r'data-question-id=["\'](\d+)["\']', html)
    if match:
        return match.group(1)
    return None


def extrair_orgao(enunciado):
    """Extrair órgão do enunciado"""
    if not enunciado:
        return None

    # Procurar por "Órgão: ..."
    match = re.search(r'Órgão:\s*([^\n]+)', enunciado)
    if match:
        return match.group(1).strip()
    return None


def extrair_banca(enunciado):
    """Extrair banca do enunciado"""
    if not enunciado:
        return None

    # Procurar por "Banca: ..."
    match = re.search(r'Banca:\s*([^\n]+)', enunciado)
    if match:
        return match.group(1).strip()
    return None


def extrair_alternativas(texto_raw):
    """Extrair alternativas de forma inteligente"""
    if not texto_raw:
        return {}

    alternativas = {}

    # Se já é dict, processar direto
    if isinstance(texto_raw, dict):
        for letra in ['A', 'B', 'C', 'D', 'E']:
            alt = texto_raw.get(letra, '').strip()
            if not alt:
                continue
            # Remover artefatos
            alt = re.sub(r'(?:Responder|Você errou|gabarito|Parabéns).*', '', alt, flags=re.IGNORECASE)
            alt = re.sub(r'\s+', ' ', alt).strip()
            if alt and len(alt) > 3:
                alternativas[letra] = alt
        return alternativas

    # Se é string, tentar extrair padrão
    if not isinstance(texto_raw, str):
        return {}

    # Padrão: A) texto B) texto
    pattern1 = r'([A-E])\s*[\)\-]?\s*([^A-E]*?)(?=[A-E]\s*[\)\-]|\s*$)'
    matches = re.findall(pattern1, texto_raw, re.DOTALL)

    if matches:
        for letra, texto in matches:
            texto_limpo = texto.strip()
            texto_limpo = re.sub(r'(?:Responder|Você errou|gabarito).*', '', texto_limpo, flags=re.IGNORECASE)
            texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()

            if texto_limpo and len(texto_limpo) > 3:
                alternativas[letra] = texto_limpo

    return alternativas


def processar_questoes(json_file):
    """Processar um arquivo JSON completo"""
    print(f"\n📄 Processando {json_file.name}...")

    with open(json_file) as f:
        questoes = json.load(f)

    questoes_limpas = []

    for i, q in enumerate(questoes):
        if (i + 1) % 100 == 0:
            print(f"  ... {i+1}/{len(questoes)}")

        enunciado = limpar_agressivo(q.get('enunciado', ''))

        if not enunciado or len(enunciado) < 30:
            continue

        # Extrair alternativas
        alternativas = extrair_alternativas(q.get('alternativas', {}))

        # Extrair ID da questão do HTML
        question_id = extrair_question_id(q.get('html', ''))

        # Extrair informações do enunciado original
        enunciado_original = q.get('enunciado', '')
        orgao = extrair_orgao(enunciado_original)
        banca = extrair_banca(enunciado_original)

        questoes_limpas.append({
            'numero': q.get('numero', ''),
            'enunciado': enunciado,
            'alternativas': alternativas,
            'tema': q.get('tema', 'N/A'),
            'ano': q.get('ano', 'N/A'),
            'tem_alternativas': len(alternativas) >= 4,
            'pagina': q.get('pagina', 'N/A'),
            'question_id': question_id,
            'orgao': orgao,
            'banca': banca,
        })

    # Salvar arquivo limpo
    output_file = json_file.parent / f"limpo_{json_file.name}"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questoes_limpas, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(questoes_limpas)} questões limpas (de {len(questoes)})")
    print(f"   Salvo em: {output_file.name}")

    return questoes_limpas


def main():
    data_dir = Path.home() / "Source" / "fcc_trainer" / "data"

    if not data_dir.exists():
        print(f"❌ Pasta não encontrada: {data_dir}")
        return

    json_files = list(data_dir.glob("questoes_*.json"))

    if not json_files:
        print(f"❌ Nenhum arquivo questoes_*.json em {data_dir}")
        return

    total_limpas = 0

    for json_file in sorted(json_files):
        limpas = processar_questoes(json_file)
        total_limpas += len(limpas)

    print(f"\n🎉 TOTAL: {total_limpas} questões limpas e prontas para usar!")


if __name__ == "__main__":
    main()
