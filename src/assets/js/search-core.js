export const normalize = value => value.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase();

export function search(documents, query) {
  const phrase = normalize(query.trim());
  const terms = [...new Set(phrase.match(/[\p{L}\p{N}]+/gu) || [])];
  if (!terms.length) return [];
  return documents.map(document => {
    const title = normalize(document.title);
    const text = normalize(document.text);
    const haystack = `${title} ${text}`;
    if (!terms.every(term => haystack.includes(term))) return null;
    const score = (title.includes(phrase) ? 20 : 0)
      + terms.reduce((sum, term) => sum + (title.includes(term) ? 5 : 0), 0)
      + (text.includes(phrase) ? 2 : 0);
    const match = text.indexOf(terms[0]);
    const start = Math.max(0, match - 65);
    const snippet = `${start ? '…' : ''}${document.text.slice(start, start + 230).trim()}${document.text.length > start + 230 ? '…' : ''}`;
    return { ...document, score, snippet };
  }).filter(Boolean).sort((a, b) => b.score - a.score || a.title.localeCompare(b.title));
}
