#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

def main():
    data_dir = Path.home() / "Source" / "fcc_trainer" / "data"
    
    # Carregar slugs
    slugs_file = data_dir / "question_slugs.json"
    if not slugs_file.exists():
        print(f"❌ Arquivo de slugs não encontrado: {slugs_file}")
        print("Primeiro execute: node scripts/scraper-slug.js")
        return
    
    with open(slugs_file) as f:
        slugs = json.load(f)
    
    print(f"📂 Carregados {len(slugs)} slugs\n")
    
    # Mesclar com questões limpas
    for limpo_file in data_dir.glob("limpo_questoes_*.json"):
        print(f"📄 Processando {limpo_file.name}...")
        
        with open(limpo_file) as f:
            questoes = json.load(f)
        
        merged = 0
        for q in questoes:
            qid = q.get('question_id')
            if qid and qid in slugs:
                q['slug'] = slugs[qid]
                merged += 1
        
        # Salvar
        with open(limpo_file, 'w', encoding='utf-8') as f:
            json.dump(questoes, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ {merged} slugs adicionados")
    
    print(f"\n✅ Concluído!")

if __name__ == "__main__":
    main()
