export default function () {
  const adobeProjectId = process.env.ADOBE_FONTS_PROJECT_ID || '';
  if (adobeProjectId && !/^[a-z0-9]{7}$/.test(adobeProjectId)) {
    throw new Error('ADOBE_FONTS_PROJECT_ID must be the seven-character ID from the owner’s Adobe Fonts embed URL.');
  }
  if (!adobeProjectId) console.warn('[fonts] Freight web project not configured; preview uses declared system fallbacks. See docs/FONTS.md.');
  return {
    title: 'Kate Courtright',
    description: 'Short stories, love stories, and musings on creativity and the writing journey by Kate Courtright.',
    adobeProjectId,
    // Enable indexing only after the remaining migration issues and font setup are complete.
    robots: 'noindex, nofollow',
    bookbub: 'https://www.bookbub.com/authors/kate-courtright',
    goodreads: 'https://www.goodreads.com/author/show/19932939.Kate_Courtright?from_search=true&from_srp=true',
  };
}
