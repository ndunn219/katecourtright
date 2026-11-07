export default function () {
  const environment = process.env.SITE_ENV || 'preview';
  if (!['preview', 'production'].includes(environment)) throw new Error('SITE_ENV must be preview or production.');
  if (environment === 'production' && process.env.SITE_PATH_PREFIX && process.env.SITE_PATH_PREFIX !== '/') {
    throw new Error('Production must be built at the custom-domain root.');
  }
  return {
    title: 'Kate Courtright',
    description: 'Short stories, love stories, and musings on creativity and the writing journey by Kate Courtright.',
    // Production is an explicit launch choice; all ordinary builds remain previews.
    robots: environment === 'production' ? 'index, follow' : 'noindex, nofollow',
    bookbub: 'https://www.bookbub.com/authors/kate-courtright',
    goodreads: 'https://www.goodreads.com/author/show/19932939.Kate_Courtright?from_search=true&from_srp=true',
  };
}
