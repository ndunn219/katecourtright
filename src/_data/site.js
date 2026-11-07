export default function () {
  const environment = process.env.SITE_ENV || 'preview';
  if (!['preview', 'production'].includes(environment)) throw new Error('SITE_ENV must be preview or production.');
  if (environment === 'production' && process.env.SITE_PATH_PREFIX && process.env.SITE_PATH_PREFIX !== '/') {
    throw new Error('Production must be built at the custom-domain root.');
  }
  const adobeProjectId = process.env.ADOBE_FONTS_PROJECT_ID || '';
  if (adobeProjectId && !/^[a-z0-9]{7}$/.test(adobeProjectId)) {
    throw new Error('ADOBE_FONTS_PROJECT_ID must be the seven-character ID from the owner’s Adobe Fonts embed URL.');
  }
  if (!adobeProjectId) console.warn('[fonts] Freight web project not configured; preview uses declared system fallbacks. See docs/FONTS.md.');
  return {
    title: 'Kate Courtright',
    description: 'Short stories, love stories, and musings on creativity and the writing journey by Kate Courtright.',
    adobeProjectId,
    // Production is an explicit launch choice; all ordinary builds remain previews.
    robots: environment === 'production' ? 'index, follow' : 'noindex, nofollow',
    bookbub: 'https://www.bookbub.com/authors/kate-courtright',
    goodreads: 'https://www.goodreads.com/author/show/19932939.Kate_Courtright?from_search=true&from_srp=true',
  };
}
