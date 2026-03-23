#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

def categorizar_por_enunciado(enunciado):
    """Categorizar pela qualidade do enunciado e alternativas"""
    if not enunciado:
        return 'NAO_CATEGORIZADO'

    enunciado_lower = enunciado.lower()

    # Palavras-chave por dificuldade
    critico_palavras = [
        'segurança', 'criptografia', 'ssl', 'tls', 'firewall', 'vpn',
        'lacp', 'link aggregation', 'tcp/ip', 'protocolo', 'switch',
        'docker', 'kubernetes', 'container', 'orchestration',
        'git', 'versionamento', 'merge', 'rebase'
    ]

    muito_importante_palavras = [
        'spring', 'framework', 'java', 'jee', 'servlet',
        'python', 'django', 'flask',
        'javascript', 'node.js', 'react', 'angular',
        'sql', 'oracle', 'mysql', 'postgresql', 'database',
        'api', 'rest', 'soap', 'web service',
        'cloud', 'aws', 'azure', 'gcp',
        'microserviço', 'microservices',
        'json', 'xml'
    ]

    importante_palavras = [
        'engenharia', 'software',
        'scrum', 'agile', 'metodologia',
        'design pattern', 'padrão',
        'oop', 'orientado',
        'arquitetura', 'architecture',
        'teste', 'testing', 'unitário'
    ]

    recomendado_palavras = [
        'internet', 'protocolo', 'http', 'https',
        'email', 'smtp', 'pop3', 'imap',
        'web', 'html', 'css', 'javascript',
        'navegador', 'browser'
    ]

    # Verificar categorias
    for palavra in critico_palavras:
        if palavra in enunciado_lower:
            return 'CRITICO'

    for palavra in muito_importante_palavras:
        if palavra in enunciado_lower:
            return 'MUITO_IMPORTANTE'

    for palavra in importante_palavras:
        if palavra in enunciado_lower:
            return 'IMPORTANTE'

    for palavra in recomendado_palavras:
        if palavra in enunciado_lower:
            return 'RECOMENDADO'

    return 'NAO_CATEGORIZADO'


def main():
    data_dir = Path.home() / "Source" / "fcc_trainer" / "data"

    for json_file in sorted(data_dir.glob("limpo_questoes_*.json")):
        print(f"\n📄 Recategorizando {json_file.name}...")

        with open(json_file) as f:
            questoes = json.load(f)

        # Recategorizar
        for q in questoes:
            dificuldade = categorizar_por_enunciado(q.get('enunciado', ''))
            q['dificuldade'] = dificuldade

        # Salvar
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(questoes, f, indent=2, ensure_ascii=False)

        # Estatísticas
        diffs = {}
        for q in questoes:
            d = q.get('dificuldade', 'NAO_CATEGORIZADO')
            diffs[d] = diffs.get(d, 0) + 1

        print(f"✅ Salvo. Distribuição:")
        for d, count in sorted(diffs.items()):
            print(f"   {d}: {count}")


if __name__ == "__main__":
    main()
