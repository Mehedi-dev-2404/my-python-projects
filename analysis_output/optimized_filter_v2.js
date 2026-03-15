// AUTO-GENERATED OPTIMIZED FILTER v2
// Generated from comprehensive chat analysis
// 2026-03-15T19:35:18.913Z

const OPERATIONAL_KEYWORDS = [
  'done', 'finished', 'complete', 'housekeeping', 'cleaning', 'before', 'after', 'broken', 'damage', 'damaged', 'stain', 'stains', 'blood', 'dirty', 'dust', 'bedbugs', 'bugs', 'issue', 'problem', 'urgent', 'asap', 'emergency', 'lockbox', 'code', 'key', 'unlock', 'access', 'arrive', 'arriving', 'on the way', 'guest', 'check in', 'checkout', 'cleaning done', 'finished cleaning', 'found broken', 'not cleaned', 'missed', 'incomplete', 'inspect', 'verify', 'descale', 'vacuum', 'hoover', 'mop', 'spray', 'wash', 'wipe', 'disinfect', 'the', 'you', 'please', 'and', 'can', 'for', '@⁨~mumen⁩', 'clayton', 'will', 'tomorrow', 'there', 'was', 'send', 'are', 'just', 'this', 'she', 'they', 'check', 'have', 'cleaner', 'know', 'not', 'confirm', 'let', 'message', 'that', 'someone', '‎<this', 'edited>', 'need', 'lane', 'all', 'with', 'centurion', 'time', 'linens', 'any', 'out', 'it’s', 'today', 'clean', 'them', 'also', 'mumen', 'ask', 'from', 'what', 'get', 'property', 'but', 'keys', 'when', 'back', 'her', 'guests'
];

const IRRELEVANT_KEYWORDS = [
  'ok', 'okay', 'yes', 'no', 'sure', 'thanks', 'thank', 'hi', 'hello', 'hey', 'bye', 'see you', 'goodbye', 'great', 'good', 'perfect', 'awesome', 'noted', 'understood', 'got it', 'will do', 'no problem', 'how are you', 'hope you', 'keeping well', 'let me check', 'let me know', 'bro', 'shopping', 'receipt', 'worries', 'mins', '👍🏽', 'paid', 'mean', 'informing', 'welcome', 'throw', 'opening', 'he’s', 'argos', 'yup', 'spoke', 'thats', 'ringing', 'responding', 'reach', 'updates', 'calling', 'almost'
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

module.exports = { filterMessage };