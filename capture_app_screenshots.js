const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

async function capture() {
  const outputDir = path.join(__dirname, 'presentation_assets');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: "new",
    defaultViewport: { width: 1440, height: 900 }
  });

  const page = await browser.newPage();
  console.log('Navigating to http://localhost:5173 ...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1000));

  // Find and click "Instant One-Click Demo Access" button
  console.log('Clicking "Instant One-Click Demo Access"...');
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Instant One-Click Demo Access')) {
      await btn.click();
      break;
    }
  }

  // Wait for sidebar
  console.log('Waiting for application shell...');
  await page.waitForSelector('aside select', { timeout: 10000 });
  await new Promise(r => setTimeout(r, 2000));

  // Select project 6 which has the full dataset
  console.log('Selecting Project 6 with complete data...');
  try {
    await page.select('aside select', '6');
    await new Promise(r => setTimeout(r, 2000));
  } catch (err) {
    console.log('Could not select project 6, continuing with current');
  }

  const navigateTo = async (tabLabel) => {
    const navButtons = await page.$$('aside nav button');
    for (const b of navButtons) {
      const txt = await page.evaluate(el => el.textContent, b);
      if (txt && txt.toLowerCase().includes(tabLabel.toLowerCase())) {
        await b.click();
        await new Promise(r => setTimeout(r, 2000));
        return true;
      }
    }
    return false;
  };

  // 1. Dashboard
  console.log('Capturing Dashboard...');
  await page.screenshot({ path: path.join(outputDir, '1_dashboard.png') });

  // 2. Paper Library
  console.log('Navigating to Paper Library...');
  await navigateTo('Paper Library');
  await page.screenshot({ path: path.join(outputDir, '2_library.png') });

  // 3. AI Assistant
  console.log('Navigating to AI Assistant...');
  await navigateTo('AI Research Assistant');
  await new Promise(r => setTimeout(r, 2000));
  // Select first session in session list
  const sessionItem = await page.$('.space-y-1 button, div[role="button"]');
  if (sessionItem) {
    await sessionItem.click();
    await new Promise(r => setTimeout(r, 2000));
  }
  await page.screenshot({ path: path.join(outputDir, '3_assistant.png') });

  // 4. Comparison
  console.log('Navigating to Paper Comparison...');
  await navigateTo('Paper Comparison');
  await new Promise(r => setTimeout(r, 2000));
  // Click on past comparison in history sidebar if present
  const compButtons = await page.$$('button');
  for (const cb of compButtons) {
    const txt = await page.evaluate(el => el.textContent, cb);
    if (txt && txt.includes('Methodology Comparison')) {
      await cb.click();
      await new Promise(r => setTimeout(r, 1500));
      break;
    }
  }
  await page.screenshot({ path: path.join(outputDir, '4_comparison.png') });

  // 5. Research Gap Analyzer
  console.log('Navigating to Research Gap Analyzer...');
  await navigateTo('Research Gap');
  await new Promise(r => setTimeout(r, 2000));
  const gapButtons = await page.$$('button');
  for (const gb of gapButtons) {
    const txt = await page.evaluate(el => el.textContent, gb);
    if (txt && txt.includes('Cross-Corpus')) {
      await gb.click();
      await new Promise(r => setTimeout(r, 1500));
      break;
    }
  }
  await page.screenshot({ path: path.join(outputDir, '5_gap_analyzer.png') });

  // 6. Literature Reviews
  console.log('Navigating to Literature Reviews...');
  await navigateTo('Literature Review');
  await new Promise(r => setTimeout(r, 2000));
  const reviewButtons = await page.$$('button');
  for (const rb of reviewButtons) {
    const txt = await page.evaluate(el => el.textContent, rb);
    if (txt && txt.includes('Advances in Retrieval')) {
      await rb.click();
      await new Promise(r => setTimeout(r, 1500));
      break;
    }
  }
  await page.screenshot({ path: path.join(outputDir, '6_literature_review.png') });

  console.log('All screenshots captured successfully!');
  await browser.close();
}

capture().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
