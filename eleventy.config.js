import { HtmlBasePlugin } from '@11ty/eleventy';
import { writeSearchIndex } from './scripts/search-index.mjs';

const postsByDate = collection => collection.getFilteredByTag('posts')
  .sort((a, b) => b.data.published.localeCompare(a.data.published));
const categoryUrl = name => `/musings/category/${encodeURIComponent(name).replaceAll('%20', '+')}/`;
const authorUrl = id => `/musings/author/${encodeURIComponent(id)}/`;

export default function (config) {
  config.addPlugin(HtmlBasePlugin);
  config.on('eleventy.after', writeSearchIndex);
  config.addPassthroughCopy('src/assets');
  config.addPassthroughCopy({ 'src/static': '/' });
  config.watchIgnores.add('reference/**');
  config.setNunjucksEnvironmentOptions({ autoescape: true });
  config.addCollection('posts', postsByDate);
  config.addCollection('categories', collection => {
    const posts = postsByDate(collection);
    return [...new Set(posts.flatMap(post => post.data.categories))].sort().map(name => ({
      name, url: categoryUrl(name), posts: posts.filter(post => post.data.categories.includes(name)),
    }));
  });
  // Every post is by Kate Courtright (redesign #13). The two legacy Squarespace
  // author IDs remain as archive URLs; each now lists all of Kate's posts.
  config.addCollection('authors', collection => {
    const posts = postsByDate(collection);
    return [...new Set(posts.map(post => post.data.authorId))].sort().map(id => {
      const name = posts.find(post => post.data.authorId === id).data.author;
      return { id, name, url: authorUrl(id), posts: posts.filter(post => post.data.author === name) };
    });
  });
  config.addCollection('postsByYear', collection => {
    const years = new Map();
    for (const post of postsByDate(collection)) {
      const year = post.data.published.slice(0, 4);
      if (!years.has(year)) years.set(year, []);
      years.get(year).push(post);
    }
    return [...years].map(([year, posts]) => ({ year, posts }));
  });
  config.addFilter('categoryUrl', categoryUrl);
  config.addFilter('authorUrl', authorUrl);
  config.addFilter('adjacentPosts', (posts, url) => {
    const index = posts.findIndex(post => post.url === url);
    return { newer: posts[index - 1], older: posts[index + 1] };
  });
  config.addFilter('canonicalUrl', path => new URL(path, 'https://katecourtright.com').href);
  config.addFilter('encodeURIComponent', encodeURIComponent);
  config.addFilter('monthYear', value => new Intl.DateTimeFormat('en-US', {
    month: 'long', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(value)));
  config.addFilter('readableDate', value => new Intl.DateTimeFormat('en-US', {
    month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(value)));
  return {
    dir: { input: 'src', output: '_site', includes: '_includes', data: '_data' },
    templateFormats: ['njk', 'md'],
    markdownTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk',
    pathPrefix: process.env.SITE_PATH_PREFIX || '/',
  };
}
