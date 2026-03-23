const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://www.qconcursos.com/questoes-de-concursos/questoes?examining_board_ids%5B%5D=1&institute_ids%5B%5D=1&institute_ids%5B%5D=2&institute_ids%5B%5D=3&institute_ids%5B%5D=4&institute_ids%5B%5D=5&institute_ids%5B%5D=8&institute_ids%5B%5D=11&institute_ids%5B%5D=13&institute_ids%5B%5D=39&institute_ids%5B%5D=41&institute_ids%5B%5D=42&institute_ids%5B%5D=69&institute_ids%5B%5D=78&institute_ids%5B%5D=80&institute_ids%5B%5D=81&institute_ids%5B%5D=82&institute_ids%5B%5D=83&institute_ids%5B%5D=84&institute_ids%5B%5D=85&institute_ids%5B%5D=86&institute_ids%5B%5D=87&institute_ids%5B%5D=88&institute_ids%5B%5D=10607&knowledge_area_ids%5B%5D=13&publication_year%5B%5D=2020&publication_year%5B%5D=2021&publication_year%5B%5D=2022&publication_year%5B%5D=2023&publication_year%5B%5D=2024&publication_year%5B%5D=2025&publication_year%5B%5D=2026&scholarity_ids%5B%5D=3&sort=relevance';

const OUTPUT_DIR = path.join(__dirname, 'questoes_completas');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function extrairQuestaoCompleta(page) {
  // Extrair questão com HTML estruturado
  return await page.evaluate(() => {
    const questoes = [];

    // Procurar por cards de questões (tenta múltiplos seletores)
    const possibleSelectors = [
      '.question-container',
      '.card-questao',
      '[data-qa*="question"]',
      'article',
      '.questao',
      '[class*="questao"]'
    ];

    let elements = [];
    for (const selector of possibleSelectors) {
      elements = document.querySelectorAll(selector);
      if (elements.length > 0) break;
    }

    // Se ainda não encontrou, tenta procurar pela estrutura geral
    if (elements.length === 0) {
      const allDivs = Array.from(document.querySelectorAll('[class*="item"]'));
      elements = allDivs.filter(div => {
        const text = div.textContent;
        return text && text.length > 200 && (
          text.includes('A)') || text.includes('B)') ||
          text.match(/^A\s/) || text.match(/\sB\s/)
        );
      });
    }

    console.log(`Elementos encontrados: ${elements.length}`);

    elements.forEach((elem, idx) => {
      try {
        const html = elem.innerHTML;
        const texto = elem.textContent || '';

        // Extrair número da questão
        const numeroMatch = texto.match(/Questão\s*(\d+)|^(\d+)|#(\d+)/i);
        const numero = numeroMatch ? (numeroMatch[1] || numeroMatch[2] || numeroMatch[3]) : idx + 1;

        // Extrair tema
        const temaMatch = texto.match(/(?:Tema|Assunto|Disciplina):\s*([^\n]+)/i);
        const tema = temaMatch ? temaMatch[1].trim() : 'N/A';

        // Extrair ano
        const anoMatch = texto.match(/Ano:\s*(\d{4})/);
        const ano = anoMatch ? anoMatch[1] : 'N/A';

        // Procurar por enunciado e alternativas
        let enunciado = '';
        const alternativas = {};

        // Tenta várias estratégias para extrair
        const paragraphs = elem.querySelectorAll('p');
        if (paragraphs.length > 0) {
          // Se tem parágrafos, primeiro é geralmente enunciado
          enunciado = paragraphs[0]?.textContent || '';

          // Procurar alternativas nos parágrafos seguintes
          for (let i = 1; i < Math.min(7, paragraphs.length); i++) {
            const p = paragraphs[i].textContent.trim();
            const match = p.match(/^([A-E])\s+(.+)/);
            if (match) {
              alternativas[match[1]] = match[2];
            }
          }
        }

        // Se não encontrou por parágrafo, tenta regex no texto
        if (Object.keys(alternativas).length === 0) {
          const textoLimpo = texto.substring(0, 2000);

          // Procura enunciado até primeira alternativa
          const primeiraAlt = /\n?A\s+/.exec(textoLimpo);
          if (primeiraAlt) {
            enunciado = textoLimpo.substring(0, primeiraAlt.index).trim();

            // Extrair alternativas
            const altRegex = /([A-E])\s+([^A-E]*?)(?=[A-E]\s+|$)/g;
            let altMatch;
            while ((altMatch = altRegex.exec(textoLimpo)) !== null) {
              alternativas[altMatch[1]] = altMatch[2].trim().substring(0, 200);
            }
          } else {
            enunciado = textoLimpo.substring(0, 500);
          }
        }

        // Remover metadados do enunciado
        enunciado = enunciado
          .replace(/Ano:\s*\d{4}.*/i, '')
          .replace(/Banca:.*?Prova:/i, '')
          .replace(/TRT.*?Especialidade/i, '')
          .replace(/Q\d+/g, '')
          .trim();

        if (enunciado.length > 30) {
          questoes.push({
            numero: numero,
            enunciado: enunciado,
            alternativas: alternativas,
            tema: tema,
            ano: ano,
            html: html.substring(0, 1000)
          });
        }
      } catch (e) {
        // Ignorar erros individuais
      }
    });

    return questoes;
  });
}

async function scrapeCompleto() {
  let browser;
  try {
    console.log('🔗 Conectando ao Chromium...');

    browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:9222'
    });

    console.log('✓ Conectado!');

    const pages = await browser.pages();
    let page = null;

    // Procurar aba qconcursos
    for (const p of pages) {
      if (p.url().includes('qconcursos')) {
        page = p;
        console.log('✓ Aba QConcursos encontrada');
        break;
      }
    }

    if (!page) {
      page = pages[0];
    }

    let allQuestoes = [];
    let paginaAtual = 1;
    let temProxima = true;
    const maxPaginas = 50;

    while (temProxima && paginaAtual <= maxPaginas) {
      console.log(`\n📄 Página ${paginaAtual}...`);

      const url = paginaAtual === 1 ? BASE_URL : `${BASE_URL}&page=${paginaAtual}`;
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 3000)));

      // Extrair questões
      const questoes = await extrairQuestaoCompleta(page);
      console.log(`✓ ${questoes.length} questões extraídas`);

      allQuestoes = allQuestoes.concat(questoes.map((q, i) => ({
        ...q,
        pagina: paginaAtual,
        idGlobal: allQuestoes.length + i + 1
      })));

      // Verificar próxima
      temProxima = await page.evaluate(() => {
        const nextBtn = document.querySelector('a[rel="next"], [aria-label*="next"]');
        return !!nextBtn && !nextBtn.disabled;
      });

      if (temProxima) {
        paginaAtual++;
        await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 2000)));
      }
    }

    // Salvar
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const jsonFile = path.join(OUTPUT_DIR, `questoes_completas_${timestamp}.json`);

    fs.writeFileSync(jsonFile, JSON.stringify(allQuestoes, null, 2));

    console.log(`\n✅ CONCLUÍDO!`);
    console.log(`📊 Total: ${allQuestoes.length} questões`);
    console.log(`💾 Salvo em: ${jsonFile}`);

    // Estatísticas
    const comAlternativas = allQuestoes.filter(q => Object.keys(q.alternativas).length >= 4).length;
    console.log(`📈 Com alternativas completas: ${comAlternativas}`);

  } catch (error) {
    console.error('❌ Erro:', error.message);
  }
}

console.log('🚀 Iniciando scrape COMPLETO...');
scrapeCompleto();
