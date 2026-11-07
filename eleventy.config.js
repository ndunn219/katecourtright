import { HtmlBasePlugin } from '@11ty/eleventy';

export default function (config) {
  config.addPlugin(HtmlBasePlugin);
  config.addPassthroughCopy('src/assets');
  config.addPassthroughCopy({ 'src/static': '/' });
  config.watchIgnores.add('reference/**');
  config.setNunjucksEnvironmentOptions({ autoescape: true });
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
