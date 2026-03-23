const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://www.qconcursos.com/questoes-de-concursos/questoes?institute_ids%5B%5D=1&institute_ids%5B%5D=2&institute_ids%5B%5D=3&institute_ids%5B%5D=4&institute_ids%5B%5D=5&institute_ids%5B%5D=8&institute_ids%5B%5D=11&institute_ids%5B%5D=13&institute_ids%5B%5D=39&institute_ids%5B%5D=41&institute_ids%5B%5D=42&institute_ids%5B%5D=69&institute_ids%5B%5D=78&institute_ids%5B%5D=80&institute_ids%5B%5D=81&institute_ids%5B%5D=82&institute_ids%5B%5D=83&institute_ids%5B%5D=84&institute_ids%5B%5D=85&institute_ids%5B%5D=86&institute_ids%5B%5D=87&institute_ids%5B%5D=88&institute_ids%5B%5D=10607&knowledge_area_ids%5B%5D=13&publication_year%5B%5D=2020&publication_year%5B%5D=2021&publication_year%5B%5D=2022&publication_year%5B%5D=2023&publication_year%5B%5D=2024&publication_year%5B%5D=2025&publication_year%5B%5D=2026&scholarity_ids%5B%5D=3&sort=relevance';

const OUTPUT_FILE = path.join(__dirname, '..', 'data', 'question_slugs.json');

async function extrairSlugs() {
  let browser;
  try {
    console.log('🔗 Conectando ao Chromium...');
    
    browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:9222'
    });
    
    console.log('✓ Conectado!');
    
    const pages = await browser.pages();
    let page = pages[0];
    
    let slugs = {};
    let paginaAtual = 1;
    let temProxima = true;
    
    while (temProxima && paginaAtual <= 50) {
      console.log(`\n📄 Página ${paginaAtual}...`);
      
      const url = paginaAtual === 1 ? BASE_URL : `${BASE_URL}&page=${paginaAtual}`;
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 2000)));
      
      // Extrair slugs das questões
      const pageData = await page.evaluate(() => {
        const items = [];
        document.querySelectorAll('a[href*="/questoes-de-concursos/questoes/"]').forEach(link => {
          const href = link.getAttribute('href');
          const match = href.match(/\/questoes\/([a-f0-9\-]+)$/);
          if (match) {
            const qId = link.textContent.trim().match(/Q(\d+)/);
            if (qId) {
              items.push({
                qId: qId[1],
                slug: match[1]
              });
            }
          }
        });
        return items;
      });
      
      console.log(`✓ ${pageData.length} slugs extraídos`);
      
      pageData.forEach(item => {
        if (item.qId && item.slug) {
          slugs[item.qId] = item.slug;
        }
      });
      
      temProxima = await page.evaluate(() => {
        const nextBtn = document.querySelector('a[rel="next"]');
        return !!nextBtn && !nextBtn.disabled;
      });
      
      if (temProxima) paginaAtual++;
    }
    
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(slugs, null, 2));
    console.log(`\n✅ CONCLUÍDO!`);
    console.log(`📊 Total: ${Object.keys(slugs).length} slugs extraídos`);
    console.log(`💾 Salvo em: ${OUTPUT_FILE}`);
    
  } catch (error) {
    console.error('❌ Erro:', error.message);
  }
}

console.log('🚀 Iniciando extração de slugs...');
extrairSlugs();
