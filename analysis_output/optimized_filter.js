// AUTO-GENERATED OPTIMIZED FILTER
// Generated from chat analysis
// 2026-03-15T19:32:57.751Z

const OPERATIONAL_KEYWORDS = [
  'cleaning', 'before', 'done', 'guest', 'guests', 'drive', 'after', 'next', 'hello', 'lockbox', 'upcoming', 'new', 'lavender'
];

const IRRELEVANT_KEYWORDS = [
  'yes', 'send', 'sure', 'thanks', 'just', 'bro', 'cleaner', 'thank', 'confirm', 'someone', 'ask', 'what', 'get', 'her', 'business', 'ridowan', 'rafin', 'thats', 'should', 'where', 'ill'
];

function filterMessage(message, hasImage = false) {
  const messageLower = (message || '').toLowerCase().trim();
  
  if (!messageLower || messageLower.length === 0) {
    return { shouldProcess: false, reason: 'empty' };
  }
  
  const hasOperational = OPERATIONAL_KEYWORDS.some(k => messageLower.includes(k));
  const hasIrrelevant = IRRELEVANT_KEYWORDS.some(k => messageLower.includes(k));
  
  if (hasImage || (hasOperational && !hasIrrelevant)) {
    return { 
      shouldProcess: true, 
      reason: 'operational',
      confidence: hasImage ? 'high' : 'medium'
    };
  }
  
  if (hasIrrelevant && !hasOperational) {
    return { shouldProcess: false, reason: 'irrelevant' };
  }
  
  return { 
    shouldProcess: messageLower.length > 20, 
    reason: 'uncertain',
    confidence: 'low'
  };
}

module.exports = { filterMessage };