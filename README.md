# 📚 FCC Trainer - Questões TRT (Informática)

App interativo para estudar questões dos Tribunais Regionais do Trabalho (TRT) elaboradas pela FCC, com foco em Informática/Computação.

## 📊 Dados

- **Total de Questões:** 334
- **Questões com Alternativas:** 139 (estruturadas)
- **Período:** 2020-2026
- **Cargos:** Analista Judiciário - Área Apoio Especializado - Especialidade Tecnologia da Informação
- **Fonte:** QConcursos

## 🎯 Distribuição por Dificuldade

- 🔴 **CRÍTICO:** ~490 questões
- 🟠 **MUITO IMPORTANTE:** ~464 questões
- 🟡 **IMPORTANTE:** ~261 questões
- 🟢 **RECOMENDADO:** ~542 questões
- ⚪ **NÃO CATEGORIZADO:** ~426 questões

## ✨ Recursos

### App Interativo (GUI)
- ✅ Filtros por dificuldade (checkboxes)
- ✅ Navegação entre questões
- ✅ Enunciado estruturado
- ✅ Alternativas extraídas (quando disponíveis)
- ✅ Link direto para QConcursos (para ver versão completa)
- ✅ Barra de progresso

### Temas Cobertos
- Segurança da Informação
- Redes de Computadores (TCP/IP, LACP, etc)
- Banco de Dados (SQL, Oracle, PostgreSQL)
- Desenvolvimento de Software (Java, JavaScript, Python)
- Cloud Computing (AWS, Azure, NIST)
- DevOps (Docker, Kubernetes, CI/CD)
- Engenharia de Software
- E muito mais...

## 🚀 Uso

### Executar App GUI

```bash
python3 app/qconcursos_app_v2.py
```

**Requisitos:**
- Python 3.7+
- tkinter (geralmente incluído no Python)
- Display gráfico (X11/Wayland)

### Estrutura de Dados

```json
{
  "numero": "1",
  "enunciado": "texto do enunciado...",
  "alternativas": {
    "A": "opção A",
    "B": "opção B",
    "C": "opção C",
    "D": "opção D",
    "E": "opção E"
  },
  "tema": "segurança da informação",
  "ano": "2025",
  "pagina": 1,
  "idGlobal": 1
}
```

## 🔧 Scraper

Usar Puppeteer para extrair questões:

```bash
cd scripts
npm install puppeteer
node scraper-completo.js
```

**Requisitos:**
- Node.js 14+
- Chromium com `--remote-debugging-port=9222`

## 📁 Estrutura do Projeto

```
fcc_trainer/
├── data/                    # Dados das questões (JSON)
├── app/                     # App GUI
│   └── qconcursos_app_v2.py
├── scripts/                 # Scrapers e utilitários
│   └── scraper-completo.js
└── README.md
```

## 🎓 Como Estudar

1. **Filtro por Dificuldade:** Começar com 🟢 RECOMENDADO
2. **Progressão:** RECOMENDADO → IMPORTANTE → MUITO_IMPORTANTE → CRÍTICO
3. **Alternativas:** Clique em "Ver no QConcursos" para ver respostas completas
4. **Revisão:** Use os filtros para revisar temas específicos

## ⚠️ Notas

- Algumas questões podem ter alternativas incompletas (limitation do scraper)
- Para questões sem alternativas estruturadas, consulte o site original via link
- Dados extraídos automaticamente de https://www.qconcursos.com/

## 📝 Licença

MIT

## 👤 Autor

Criado com Claude Code durante preparação para concursos TRT.

---

**Quer contribuir?** Abra uma issue ou PR para melhorias no scraper ou app!
