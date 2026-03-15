// ============================================
// ASSISTOSPHERE CHAT ANALYSIS SCRIPT v2
// Improved classification logic
// ============================================

const fs = require('fs');
const path = require('path');

/**
 * MANUAL OPERATIONAL SEED KEYWORDS
 * These are definitely operational - use to train classifier
 */
const OPERATIONAL_SEED = [
  'done', 'finished', 'complete', 'housekeeping', 'cleaning', 'before', 'after',
  'broken', 'damage', 'damaged', 'stain', 'stains', 'blood', 'dirty', 'dust',
  'bedbugs', 'bugs', 'issue', 'problem', 'urgent', 'asap', 'emergency',
  'lockbox', 'code', 'key', 'unlock', 'access', 'arrive', 'arriving', 'on the way',
  'guest', 'check in', 'checkout', 'cleaning done', 'finished cleaning',
  'found broken', 'not cleaned', 'missed', 'incomplete', 'inspect', 'verify',
  'descale', 'vacuum', 'hoover', 'mop', 'spray', 'wash', 'wipe', 'disinfect'
];

/**
 * MANUAL IRRELEVANT SEED KEYWORDS
 * These are definitely irrelevant - use to train classifier
 */
const IRRELEVANT_SEED = [
  'ok', 'okay', 'yes', 'no', 'sure', 'thanks', 'thank', 'hi', 'hello', 'hey',
  'bye', 'see you', 'goodbye', 'great', 'good', 'perfect', 'awesome',
  'noted', 'understood', 'got it', 'will do', 'no problem',
  'how are you', 'hope you', 'keeping well', 'let me check', 'let me know'
];

/**
 * STEP 1: Read all chat files
 */
function readChatFiles(dirPath) {
  console.log(`\n📁 Reading chat files from: ${dirPath}`);
  
  let allMessages = [];
  
  try {
    const files = fs.readdirSync(dirPath);
    const chatFiles = files.filter(f => f.endsWith('.txt') || f.endsWith('.docx'));
    
    console.log(`Found ${chatFiles.length} chat files\n`);
    
    chatFiles.forEach(file => {
      console.log(`  Processing: ${file}`);
      const filePath = path.join(dirPath, file);
      const content = fs.readFileSync(filePath, 'utf-8');
      
      const messages = parseWhatsAppMessages(content);
      allMessages = allMessages.concat(messages);
      console.log(`    → Extracted ${messages.length} messages`);
    });
  } catch (err) {
    console.error('Error reading chat files:', err.message);
    return [];
  }
  
  console.log(`\n✅ Total messages extracted: ${allMessages.length}\n`);
  return allMessages;
}

/**
 * STEP 2: Parse WhatsApp messages
 */
function parseWhatsAppMessages(content) {
  const messages = [];
  
  const messageRegex = /\[.*?\]\s+(.+?):\s+(.+?)(?=\n\[|$)/gs;
  let match;
  
  while ((match = messageRegex.exec(content)) !== null) {
    const sender = match[1].trim();
    let text = match[2].trim();
    
    // Skip system messages
    if (text.includes('changed') || text.includes('added') || text.includes('removed') || 
        text.includes('left') || text.includes('message was deleted') || 
        text.includes('video omitted') || text.includes('audio omitted') ||
        text.includes('document omitted')) {
      continue;
    }
    
    messages.push({
      sender: sender,
      text: text.toLowerCase().trim(),
      length: text.length,
      hasImage: text.includes('before') || text.includes('after') || text.includes('video'),
      timestamp: new Date()
    });
  }
  
  return messages;
}

/**
 * STEP 3: Smart classification using seed words
 */
function classifyMessages(messages) {
  console.log('🔍 Classifying messages with improved logic...\n');
  
  const classified = [];
  let operationalCount = 0;
  let irrelevantCount = 0;
  let uncertainCount = 0;
  
  messages.forEach(msg => {
    const text = msg.text;
    
    // Count seed keyword matches
    let operationalMatches = 0;
    let irrelevantMatches = 0;
    
    OPERATIONAL_SEED.forEach(keyword => {
      if (text.includes(keyword)) operationalMatches++;
    });
    
    IRRELEVANT_SEED.forEach(keyword => {
      if (text.includes(keyword)) irrelevantMatches++;
    });
    
    // Decision logic
    let classification = 'uncertain';
    
    if (msg.hasImage) {
      classification = 'operational'; // Images are always operational context
      operationalCount++;
    } else if (operationalMatches > irrelevantMatches && operationalMatches > 0) {
      classification = 'operational';
      operationalCount++;
    } else if (irrelevantMatches > operationalMatches && irrelevantMatches > 0 && text.length < 50) {
      classification = 'irrelevant';
      irrelevantCount++;
    } else if (text.length > 30) {
      classification = 'operational'; // Longer messages likely operational
      operationalCount++;
    } else {
      uncertainCount++;
    }
    
    classified.push({
      text: text,
      classification: classification,
      sender: msg.sender,
      length: msg.length,
      hasImage: msg.hasImage,
      operationalMatches: operationalMatches,
      irrelevantMatches: irrelevantMatches
    });
  });
  
  console.log(`  Operational: ${operationalCount}`);
  console.log(`  Irrelevant: ${irrelevantCount}`);
  console.log(`  Uncertain: ${uncertainCount}\n`);
  
  return classified;
}

/**
 * STEP 4: Extract keywords from classified messages
 */
function analyzeKeywords(messages) {
  console.log('🔑 Analyzing keyword frequency...\n');
  
  const keywordStats = {};
  
  messages.forEach(msg => {
    const words = msg.text.split(/[\s\-,.:!?;'"()]+/).filter(w => w.length > 2);
    
    words.forEach(word => {
      if (!keywordStats[word]) {
        keywordStats[word] = { 
          total: 0, 
          operational: 0, 
          irrelevant: 0, 
          uncertain: 0,
          senders: new Set()
        };
      }
      
      keywordStats[word].total++;
      keywordStats[word][msg.classification]++;
      keywordStats[word].senders.add(msg.sender);
    });
  });
  
  // Calculate operational ratio
  const ranked = Object.entries(keywordStats)
    .map(([word, stats]) => ({
      word,
      ...stats,
      senders: Array.from(stats.senders),
      operationalRatio: stats.total > 0 ? (stats.operational / stats.total * 100).toFixed(1) : 0,
      frequency: stats.total
    }))
    .sort((a, b) => b.frequency - a.frequency);
  
  // Extract operational and irrelevant keywords
  const operational = ranked
    .filter(item => item.operationalRatio > 60 && item.frequency > 2)
    .slice(0, 60)
    .map(item => item.word);
  
  const irrelevant = ranked
    .filter(item => item.operationalRatio < 40 && item.frequency > 3)
    .slice(0, 40)
    .map(item => item.word);
  
  console.log(`Top Operational Keywords (>60% ratio):`);
  ranked.filter(i => i.operationalRatio > 60).slice(0, 20).forEach(item => {
    console.log(`  ${item.word}: ${item.frequency} (${item.operationalRatio}%)`);
  });
  
  console.log(`\nTop Irrelevant Keywords (<40% ratio):`);
  ranked.filter(i => i.operationalRatio < 40).slice(0, 20).forEach(item => {
    console.log(`  ${item.word}: ${item.frequency} (${item.operationalRatio}%)`);
  });
  
  return { 
    operational: [...new Set([...OPERATIONAL_SEED, ...operational])],
    irrelevant: [...new Set([...IRRELEVANT_SEED, ...irrelevant])],
    allStats: ranked
  };
}

/**
 * STEP 5: Generate optimized filter
 */
function generateOptimizedFilter(keywords) {
  console.log('\n📝 Generating optimized filter...\n');
  
  const filterCode = `// AUTO-GENERATED OPTIMIZED FILTER v2
// Generated from comprehensive chat analysis
// ${new Date().toISOString()}

const OPERATIONAL_KEYWORDS = [
  ${keywords.operational.map(k => `'${k}'`).join(', ')}
];

const IRRELEVANT_KEYWORDS = [
  ${keywords.irrelevant.map(k => `'${k}'`).join(', ')}
];

const ESCALATION_KEYWORDS = [
  'broken', 'bedbugs', 'blood', 'stain', 'damage', 'urgent', 'asap', 
  'emergency', 'not cleaned', 'missed', 'incomplete', 'issue'
];

function filterMessage(message, hasImage = false) {
  const messageLower = (message || '').toLowerCase().trim();
  
  if (!messageLower || messageLower.length === 0) {
    return { shouldProcess: false, reason: 'empty' };
  }
  
  const hasOperational = OPERATIONAL_KEYWORDS.some(k => messageLower.includes(k));
  const hasIrrelevant = IRRELEVANT_KEYWORDS.some(k => messageLower.includes(k));
  const needsEscalation = ESCALATION_KEYWORDS.some(k => messageLower.includes(k));
  
  // Always process images in operational context
  if (hasImage || (hasOperational && !hasIrrelevant)) {
    return { 
      shouldProcess: true, 
      reason: 'operational',
      confidence: hasImage ? 'high' : 'medium',
      priority: needsEscalation ? 'urgent' : 'normal',
      requiresEscalation: needsEscalation
    };
  }
  
  // Block pure irrelevant
  if (hasIrrelevant && !hasOperational && messageLower.length < 50) {
    return { shouldProcess: false, reason: 'irrelevant' };
  }
  
  // Uncertain: process if longer message (likely operational)
  return { 
    shouldProcess: messageLower.length > 30, 
    reason: 'uncertain',
    confidence: 'low',
    priority: 'medium'
  };
}

module.exports = { filterMessage };`;
  
  return filterCode;
}

/**
 * STEP 6: Save results
 */
function saveResults(filterCode, keywords, outputDir = './analysis_output') {
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Save filter
  const filterPath = path.join(outputDir, 'optimized_filter_v2.js');
  fs.writeFileSync(filterPath, filterCode);
  console.log(`✅ Filter saved to: ${filterPath}`);
  
  // Save detailed analysis
  const analysisPath = path.join(outputDir, 'detailed_analysis.json');
  fs.writeFileSync(analysisPath, JSON.stringify({
    operationalKeywords: keywords.operational,
    irrelevantKeywords: keywords.irrelevant,
    topKeywords: keywords.allStats.slice(0, 100)
  }, null, 2));
  console.log(`✅ Analysis saved to: ${analysisPath}`);
  
  // Save summary
  const summaryPath = path.join(outputDir, 'ANALYSIS_SUMMARY.txt');
  const summary = `ASSISTOSPHERE CHAT ANALYSIS v2 SUMMARY
Generated: ${new Date().toISOString()}

OPERATIONAL KEYWORDS (${keywords.operational.length}):
${keywords.operational.slice(0, 30).join(', ')}

IRRELEVANT KEYWORDS (${keywords.irrelevant.length}):
${keywords.irrelevant.slice(0, 30).join(', ')}

ESCALATION KEYWORDS:
broken, bedbugs, blood, stain, damage, urgent, asap, emergency, not cleaned, missed

FILES GENERATED:
1. optimized_filter_v2.js - Use this in n8n
2. detailed_analysis.json - Full keyword stats
3. ANALYSIS_SUMMARY.txt - This file

NEXT STEPS:
1. Copy optimized_filter_v2.js into n8n Function node
2. Test with real messages
3. Adjust keyword lists if needed
`;
  fs.writeFileSync(summaryPath, summary);
  console.log(`✅ Summary saved to: ${summaryPath}`);
}

/**
 * MAIN EXECUTION
 */
async function main() {
  console.log('════════════════════════════════════════');
  console.log('  ASSISTOSPHERE CHAT ANALYSIS v2');
  console.log('════════════════════════════════════════');
  
  const chatDirectory = process.argv[2] || './chats';
  const outputDirectory = './analysis_output';
  
  const messages = readChatFiles(chatDirectory);
  if (messages.length === 0) {
    console.error('❌ No messages found. Check directory path.');
    process.exit(1);
  }
  
  const classified = classifyMessages(messages);
  const keywords = analyzeKeywords(classified);
  const filterCode = generateOptimizedFilter(keywords);
  saveResults(filterCode, keywords, outputDirectory);
  
  console.log('\n✅ Analysis complete!');
  console.log(`📍 Output directory: ${outputDirectory}`);
  console.log('\n📋 Next: Copy optimized_filter_v2.js into n8n');
}

main().catch(console.error);