# Extrair Slugs do QConcursos

Para que o link abra a questão correta, preciso extrair o slug (ID único da URL) de cada questão.

## Passo 1: Iniciar Chromium com debugger

```bash
chromium --remote-debugging-port=9222
```

## Passo 2: Acessar o site

Abra o Firefox/Chrome manualmente e acesse:
```
https://www.qconcursos.com/questoes-de-concursos/questoes?institute_ids%5B%5D=1&...
```

(O Chromium do debugger não precisa carregar visualmente)

## Passo 3: Executar script de extração

```bash
cd ~/Source/fcc_trainer
node scripts/scraper-slug.js
```

Isso vai criar `data/question_slugs.json` com todos os slugs.

## Passo 4: Mesclar slugs com os dados

```bash
python3 scripts/merge_slugs.py
```

Isso adiciona o slug a cada questão.

## Passo 5: Pronto!

Agora o app abre a questão correta quando você clica em "🔗 QConcursos"

---

**Tempo estimado**: ~5 minutos

Quer executar agora?
