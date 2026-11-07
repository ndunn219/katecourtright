const menu = document.querySelector('.mobile-menu');
const toggle = menu.querySelector('summary');
const mobile = window.matchMedia('(max-width: 1000px)');
const background = [...document.querySelectorAll('.skip-link, .brand, main, .site-footer')];
const inertBeforeOpen = new Map();
menu.dataset.enhanced = 'true';

function syncMenu() {
  const open = menu.open && mobile.matches;
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  for (const element of background) {
    if (open) {
      if (!inertBeforeOpen.has(element)) inertBeforeOpen.set(element, element.inert);
      element.inert = true;
    } else if (inertBeforeOpen.has(element)) {
      element.inert = inertBeforeOpen.get(element);
      inertBeforeOpen.delete(element);
    }
  }
  if (open && !menu.contains(document.activeElement)) toggle.focus();
}

function closeMenu(restoreFocus = true) {
  menu.open = false;
  syncMenu();
  if (restoreFocus) toggle.focus();
}
menu.addEventListener('toggle', syncMenu);
menu.querySelector('nav').addEventListener('click', event => {
  if (event.target.closest('a')) closeMenu();
});
document.addEventListener('keydown', event => {
  if (!menu.open || !mobile.matches) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    closeMenu();
  } else if (event.key === 'Tab') {
    const focusable = [toggle, ...menu.querySelectorAll('a[href]')];
    const first = focusable[0];
    const last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
});
document.addEventListener('focusin', event => {
  if (menu.open && mobile.matches && !menu.contains(event.target)) toggle.focus();
});
mobile.addEventListener('change', () => {
  if (!mobile.matches) {
    const hadFocus = menu.contains(document.activeElement);
    closeMenu(false);
    if (hadFocus) document.querySelector('.brand').focus();
  }
});
window.addEventListener('pageshow', () => {
  const hadFocus = menu.contains(document.activeElement);
  closeMenu(false);
  if (hadFocus) (mobile.matches ? toggle : document.querySelector('.brand')).focus();
});
syncMenu();
