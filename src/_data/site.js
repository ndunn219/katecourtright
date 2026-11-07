export default function () {
  const environment = process.env.SITE_ENV || 'preview';
  if (!['preview', 'production'].includes(environment)) throw new Error('SITE_ENV must be preview or production.');
  if (environment === 'production' && process.env.SITE_PATH_PREFIX && process.env.SITE_PATH_PREFIX !== '/') {
    throw new Error('Production must be built at the custom-domain root.');
  }
  const links = {
    bookbub: 'https://www.bookbub.com/authors/kate-courtright',
    goodreads: 'https://www.goodreads.com/author/show/19932939.Kate_Courtright?from_search=true&from_srp=true',
    instagram: 'https://www.instagram.com/kate_courtright_/',
    facebook: 'https://www.facebook.com/kate.courtright.nyc',
  };
  return {
    title: 'Kate Courtright',
    description: 'Short stories, love stories, and musings on creativity and the writing journey by Kate Courtright.',
    tagline: 'Short stories, love stories, and musings on creativity and the writing journey.',
    // Production is an explicit launch choice; all ordinary builds remain previews.
    robots: environment === 'production' ? 'index, follow' : 'noindex, nofollow',
    ...links,
    // Shared "Follow Kate" destinations for the mobile menu, footer and pages.
    social: [
      { name: 'BookBub', url: links.bookbub },
      { name: 'Goodreads', url: links.goodreads },
      { name: 'Instagram', url: links.instagram },
      { name: 'Facebook', url: links.facebook },
    ],
  };
}
