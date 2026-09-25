const fs = require('fs');
const path = require('path');

const filePath = `D:\\DATN\\he_thong_phat_hien_khong_doi_mu_VSCode_scrollfix\\frontend\\src\\services\\api.ts`;

let content = fs.readFileSync(filePath, 'utf-8');

// Fix the broken Authorization header
// Replace malformed backtick pattern with proper Bearer token template
const oldLine = "        ...(token ? { Authorization: `****** } : {}),";
const newLine = "        ...(token ? { Authorization: `Bearer ${token}` } : {}),";

if (content.includes(oldLine)) {
  content = content.replace(oldLine, newLine);
  console.log('✅ Fixed Authorization header in api.ts');
} else {
  console.log('❌ Could not find exact string to replace');
  console.log('Looking for pattern with Authorization...');
  const match = content.match(/Authorization: `[^`]*`/);
  if (match) {
    console.log('Found:', match[0]);
    content = content.replace(/Authorization: `[^`]*`/g, "Authorization: `Bearer ${token}`");
    console.log('✅ Fixed with pattern replacement');
  }
}

fs.writeFileSync(filePath, content, 'utf-8');

// Verify
const lines = content.split('\n');
lines.slice(50, 60).forEach((line, i) => {
  if (line.includes('Authorization')) {
    console.log(`Line ${i+51}: ${line.trim()}`);
  }
});
