const puppeteer = require('puppeteer');

const sites = [
  {
    name: 'mysimplestack.com',
    url: 'https://mysimplestack.com',
    expectedTitle: 'The Simple Company - AI Agents, Simply Built',
    requiredMeta: ['description', 'viewport', 'og:title', 'og:description'],
    minContentLength: 500,
    requiredElements: ['h1', 'h2', 'nav', 'footer']
  },
  {
    name: 'simple.company',
    url: 'https://simple.company',
    expectedTitle: 'The Simple Company - AI Agents, Simply Built',
    requiredMeta: ['description', 'viewport', 'og:title', 'og:description'],
    minContentLength: 500,
    requiredElements: ['h1', 'h2', 'nav', 'footer']
  },
  {
    name: 'textmaya.ai',
    url: 'https://textmaya.ai',
    expectedTitle: 'Maya - Your AI Friend via iMessage',
    requiredMeta: ['description', 'viewport', 'og:title', 'og:description'],
    minContentLength: 500,
    requiredElements: ['h1', 'h2']
  },
  {
    name: 'goodseeds.club',
    url: 'https://goodseeds.club',
    expectedTitle: 'GOOD SEEDS CLUB',
    requiredMeta: ['description', 'viewport', 'og:title', 'og:description'],
    minContentLength: 300,
    requiredElements: ['h1']
  },
  {
    name: 'thesimple.co',
    url: 'https://thesimple.co',
    expectedTitle: 'The Simple Company',
    requiredMeta: ['description', 'viewport', 'og:title', 'og:description'],
    minContentLength: 500,
    requiredElements: ['h1', 'h2']
  }
];

async function testSite(site) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  const results = {
    site: site.name,
    url: site.url,
    tests: {
      accessibility: false,
      title: false,
      metaTags: {},
      contentLength: false,
      mobileResponsive: false,
      pageSpeed: {},
      structuredData: false,
      robots: false,
      sitemap: false
    },
    errors: []
  };

  try {
    // Set viewport for mobile testing
    await page.setViewport({ width: 375, height: 667 });
    
    // Start timing
    const startTime = Date.now();
    
    // Navigate to site
    const response = await page.goto(site.url, { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    results.tests.accessibility = response.status() === 200;
    results.tests.pageSpeed.loadTime = Date.now() - startTime;
    
    // Check title
    const title = await page.title();
    results.tests.title = title.includes(site.expectedTitle.split(' - ')[0]);
    results.actualTitle = title;
    
    // Check meta tags
    for (const metaName of site.requiredMeta) {
      const metaContent = await page.$eval(
        `meta[name="${metaName}"], meta[property="${metaName}"]`,
        el => el ? el.getAttribute('content') : null
      ).catch(() => null);
      
      results.tests.metaTags[metaName] = !!metaContent;
      if (metaContent) {
        results[metaName] = metaContent;
      }
    }
    
    // Check content length
    const bodyText = await page.$eval('body', el => el.innerText);
    results.tests.contentLength = bodyText.length >= site.minContentLength;
    results.actualContentLength = bodyText.length;
    
    // Check required elements
    results.tests.requiredElements = {};
    for (const selector of site.requiredElements) {
      const element = await page.$(selector);
      results.tests.requiredElements[selector] = !!element;
    }
    
    // Check mobile responsiveness
    const hasViewportMeta = await page.$('meta[name="viewport"]');
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });
    results.tests.mobileResponsive = hasViewportMeta && !hasHorizontalScroll;
    
    // Check for structured data
    const structuredData = await page.$$eval('script[type="application/ld+json"]', 
      scripts => scripts.map(s => {
        try {
          return JSON.parse(s.innerHTML);
        } catch (e) {
          return null;
        }
      }).filter(Boolean)
    );
    results.tests.structuredData = structuredData.length > 0;
    results.structuredData = structuredData;
    
    // Check robots.txt
    const robotsResponse = await page.goto(`${site.url}/robots.txt`);
    results.tests.robots = robotsResponse.status() === 200;
    
    // Check sitemap
    const sitemapResponse = await page.goto(`${site.url}/sitemap.xml`);
    results.tests.sitemap = sitemapResponse.status() === 200;
    
    // Take screenshot
    await page.goto(site.url);
    await page.screenshot({ 
      path: `screenshots/${site.name}-mobile.png`,
      fullPage: true 
    });
    
    // Desktop screenshot
    await page.setViewport({ width: 1920, height: 1080 });
    await page.screenshot({ 
      path: `screenshots/${site.name}-desktop.png`,
      fullPage: true 
    });
    
  } catch (error) {
    results.errors.push(error.message);
  } finally {
    await browser.close();
  }
  
  return results;
}

async function runAllTests() {
  console.log('🔍 Starting SEO Test Suite\n');
  
  // Create screenshots directory
  const fs = require('fs');
  if (!fs.existsSync('screenshots')) {
    fs.mkdirSync('screenshots');
  }
  
  const allResults = [];
  
  for (const site of sites) {
    console.log(`Testing ${site.name}...`);
    const results = await testSite(site);
    allResults.push(results);
    
    // Print results
    console.log(`✓ Accessibility: ${results.tests.accessibility ? '✅' : '❌'}`);
    console.log(`✓ Title: ${results.tests.title ? '✅' : '❌'} "${results.actualTitle}"`);
    console.log(`✓ Meta Tags: ${Object.values(results.tests.metaTags).filter(v => v).length}/${site.requiredMeta.length}`);
    console.log(`✓ Content Length: ${results.tests.contentLength ? '✅' : '❌'} (${results.actualContentLength} chars)`);
    console.log(`✓ Mobile Responsive: ${results.tests.mobileResponsive ? '✅' : '❌'}`);
    console.log(`✓ Structured Data: ${results.tests.structuredData ? '✅' : '❌'}`);
    console.log(`✓ Robots.txt: ${results.tests.robots ? '✅' : '❌'}`);
    console.log(`✓ Sitemap: ${results.tests.sitemap ? '✅' : '❌'}`);
    console.log(`✓ Page Speed: ${results.tests.pageSpeed.loadTime}ms`);
    console.log('---\n');
  }
  
  // Save results
  fs.writeFileSync('seo-test-results.json', JSON.stringify(allResults, null, 2));
  console.log('📊 Full results saved to seo-test-results.json');
  console.log('📸 Screenshots saved to screenshots/');
  
  // Generate report
  generateReport(allResults);
}

function generateReport(results) {
  const report = `# SEO Test Report
Generated: ${new Date().toISOString()}

## Summary
${results.map(r => {
  const score = calculateScore(r);
  return `- **${r.site}**: ${score}/10 ${getEmoji(score)}`;
}).join('\n')}

## Detailed Results
${results.map(r => generateSiteReport(r)).join('\n\n')}
`;

  require('fs').writeFileSync('SEO-TEST-REPORT.md', report);
  console.log('\n📄 Report generated: SEO-TEST-REPORT.md');
}

function calculateScore(result) {
  let score = 0;
  if (result.tests.accessibility) score += 2;
  if (result.tests.title) score += 1;
  if (Object.values(result.tests.metaTags).filter(v => v).length >= 3) score += 2;
  if (result.tests.contentLength) score += 1;
  if (result.tests.mobileResponsive) score += 1;
  if (result.tests.structuredData) score += 1;
  if (result.tests.robots) score += 1;
  if (result.tests.sitemap) score += 1;
  return score;
}

function getEmoji(score) {
  if (score >= 8) return '🟢';
  if (score >= 5) return '🟡';
  return '🔴';
}

function generateSiteReport(result) {
  return `### ${result.site}
- URL: ${result.url}
- Title: ${result.actualTitle}
- Content Length: ${result.actualContentLength} chars
- Load Time: ${result.tests.pageSpeed.loadTime}ms
- Issues: ${result.errors.length > 0 ? result.errors.join(', ') : 'None'}`;
}

// Run tests
runAllTests().catch(console.error);