import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { Parser } from 'htmlparser2';

// Index rendered main content, including decoded entities, never shared navigation,
// scripts or footer copy. This runs on ordinary builds and Eleventy watch rebuilds.
export function searchDocument(html) {
  const stack = [];
  const body = [];
  const heading = [];
  const parser = new Parser({
    onopentag(tag) {
      stack.push(tag);
      if (['p', 'br', 'div', 'li', 'h1', 'h2', 'h3'].includes(tag)) body.push(' ');
    },
    ontext(text) {
      if (!stack.includes('main') || stack.some(tag => ['script', 'style', 'nav'].includes(tag))) return;
      body.push(text);
      if (stack.includes('h1')) heading.push(text);
    },
    onclosetag() { stack.pop(); body.push(' '); },
  }, { decodeEntities: true });
  parser.end(html);
  const compact = parts => parts.join('').replace(/\s+/g, ' ').trim();
  return { title: compact(heading), text: compact(body) };
}

export async function writeSearchIndex({ dir, results }) {
  const prefix = process.env.SITE_PATH_PREFIX || '/';
  const excluded = new Set(['/welcome/', '/search/', '/404.html', '/newsletter/']);
  const documents = results.filter(result => result.outputPath?.endsWith('.html') && !excluded.has(result.url))
    .map(result => {
      const { title, text } = searchDocument(result.content);
      return { title, text, url: `${prefix.replace(/\/$/, '')}${result.url}` };
    }).sort((a, b) => a.url.localeCompare(b.url));
  const destination = path.join(dir.output, 'search-index.json');
  await mkdir(path.dirname(destination), { recursive: true });
  await writeFile(destination, JSON.stringify(documents));
}
