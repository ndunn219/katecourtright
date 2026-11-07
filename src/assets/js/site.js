const menu = document.querySelector('.mobile-menu');
const toggle = menu.querySelector('summary');
const mobile = window.matchMedia('(max-width: 640px)');
const background = [...document.querySelectorAll('.skip-link, .brand, .desktop-nav, main, .site-footer')];
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

// Native anchors retain history, deep links, and a no-script fallback. Move
// keyboard focus to the destination without interrupting native smooth scrolling.
document.querySelectorAll('.scroll-indicator').forEach(link => {
  link.addEventListener('click', () => {
    const destination = document.getElementById(link.hash.slice(1));
    if (destination) {
      destination.setAttribute('tabindex', '-1');
      destination.focus({ preventScroll: true });
    }
  });
});

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const heroes = [...document.querySelectorAll('.hero:not(.hero--short)')];
const intro = document.querySelector('.home-intro');
let scheduled = false;
function paintParallax() {
  scheduled = false;
  for (const hero of heroes) {
    const bounds = hero.getBoundingClientRect();
    const offset = reducedMotion.matches ? 0 : Math.max(0, Math.min(-bounds.top * .18, bounds.height * .18));
    hero.style.setProperty('--parallax-offset', `${offset}px`);
  }
  if (intro) {
    const bounds = intro.getBoundingClientRect();
    const offset = reducedMotion.matches ? 0 : Math.max(-60, Math.min(60, -bounds.top * .08));
    intro.style.setProperty('--background-offset', `${offset}px`);
  }
}
function scheduleParallax() {
  if (!scheduled) {
    scheduled = true;
    requestAnimationFrame(paintParallax);
  }
}
window.addEventListener('scroll', scheduleParallax, { passive: true });
window.addEventListener('resize', scheduleParallax);
reducedMotion.addEventListener('change', scheduleParallax);
paintParallax();
