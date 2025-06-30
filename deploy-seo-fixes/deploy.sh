#!/bin/bash
# SEO Deployment Script

echo "🚀 SEO Deployment Suite"
echo "======================="
echo ""

# Create directories
mkdir -p sites/mysimplestack
mkdir -p sites/textmaya
mkdir -p sites/goodseeds
mkdir -p sites/thesimple

# Copy SEO files
cp ../sitemap_*.xml ./
cp ../robots_*.txt ./

# Create a simple test server
cat > server.js << 'EOF'
const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Serve robots.txt and sitemap.xml
app.get('/robots.txt', (req, res) => {
  const host = req.get('host');
  let robotsFile = 'robots_mysimplestack_com.txt';
  
  if (host.includes('textmaya')) robotsFile = 'robots_textmaya_ai.txt';
  else if (host.includes('goodseeds')) robotsFile = 'robots_goodseeds_club.txt';
  else if (host.includes('thesimple')) robotsFile = 'robots_thesimple_co.txt';
  else if (host.includes('simple.company')) robotsFile = 'robots_simple_company.txt';
  
  res.type('text/plain');
  res.sendFile(path.join(__dirname, robotsFile));
});

app.get('/sitemap.xml', (req, res) => {
  const host = req.get('host');
  let sitemapFile = 'sitemap_mysimplestack_com.xml';
  
  if (host.includes('textmaya')) sitemapFile = 'sitemap_textmaya_ai.xml';
  else if (host.includes('goodseeds')) sitemapFile = 'sitemap_goodseeds_club.xml';
  else if (host.includes('thesimple')) sitemapFile = 'sitemap_thesimple_co.xml';
  else if (host.includes('simple.company')) sitemapFile = 'sitemap_simple_company.xml';
  
  res.type('application/xml');
  res.sendFile(path.join(__dirname, sitemapFile));
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'seo-fixes' });
});

app.listen(PORT, () => {
  console.log(`SEO service running on port ${PORT}`);
});
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 8080

CMD ["node", "server.js"]
EOF

# Create .gcloudignore
cat > .gcloudignore << 'EOF'
.gcloudignore
.git
.gitignore
node_modules/
*.md
screenshots/
*.test.js
EOF

echo "📦 Files prepared for deployment"
echo ""
echo "To deploy:"
echo "1. Review SEO changes in *-seo.html files"
echo "2. Add the meta tags to your actual sites"
echo "3. Deploy this service: gcloud run deploy seo-service --source . --region us-central1"
echo ""
echo "Or deploy individually:"
echo "- npm run deploy:mysimplestack"
echo "- npm run deploy:textmaya"
echo "- npm run deploy:goodseeds"