import { search } from './search-core.js';

const form = document.querySelector('.search-form');
const input = document.querySelector('#search-query');
const status = document.querySelector('#search-status');
const results = document.querySelector('#search-results');
let index;
let request = 0;

function loadIndex() {
  if (!index) {
    index = fetch(new URL('../../search-index.json', import.meta.url))
      .then(response => {
        if (!response.ok) throw new Error('Search index unavailable');
        return response.json();
      }).catch(error => { index = undefined; throw error; });
  }
  return index;
}

async function showResults() {
  const currentRequest = ++request;
  const query = input.value.trim();
  results.replaceChildren();
  results.removeAttribute('aria-busy');
  if (!query || !/[\p{L}\p{N}]/u.test(query)) {
    status.textContent = 'Enter a word or phrase, or browse below.';
    return;
  }
  status.textContent = 'Searching…';
  results.setAttribute('aria-busy', 'true');
  try {
    const matches = search(await loadIndex(), query);
    if (currentRequest !== request) return;
    for (const match of matches) {
      const item = document.createElement('li');
      const heading = document.createElement('h2');
      const link = document.createElement('a');
      const excerpt = document.createElement('p');
      link.href = match.url;
      link.textContent = match.title;
      excerpt.textContent = match.snippet;
      heading.append(link);
      item.append(heading, excerpt);
      results.append(item);
    }
    status.textContent = matches.length
      ? `${matches.length} ${matches.length === 1 ? 'result' : 'results'} for “${query}”.`
      : `No results for “${query}”. Try another word or browse below.`;
  } catch {
    if (currentRequest !== request) return;
    status.textContent = 'Search is temporarily unavailable. Try again or browse below.';
  } finally {
    if (currentRequest === request) results.removeAttribute('aria-busy');
  }
}

function readQuery() {
  input.value = (new URLSearchParams(location.search).get('q') || '').slice(0, 200);
  showResults();
}
form.addEventListener('submit', event => {
  event.preventDefault();
  const url = new URL(location.href);
  if (input.value.trim()) url.searchParams.set('q', input.value.trim());
  else url.searchParams.delete('q');
  history.pushState(null, '', url);
  showResults();
});
window.addEventListener('popstate', readQuery);
readQuery();
