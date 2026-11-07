// Old Squarespace query URLs resolve to pre-rendered, bookmarkable author archives.
// Read the generated links so repository-path previews keep their hosting prefix.
const authorId = new URLSearchParams(window.location.search).get('author');
if (authorId) {
  const destination = [...document.querySelectorAll('a[data-author-id]')]
    .find(link => link.dataset.authorId === authorId);
  if (destination) window.location.replace(destination.href);
}
