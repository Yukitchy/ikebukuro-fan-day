// Shared data + copy for d1–d5. Each design only styles and renders the items.
const ITEMS = [
  {id:'m36425879874', cat:'Cards', title:'Charizard ex SAR', sub:'Pokémon Card 151 (SV2a 201/165, JP)', range:'Raw ¥35,000–70,000 / PSA 10 ¥93,000–160,000', ex:40200},
  {id:'m14043988340', cat:'Cards', title:'Monkey D. Luffy SEC', sub:'One Piece Card OP05-119 (JP)', range:'Raw from ¥1,000 / Secret Parallel ¥9,000–25,000', ex:3300},
  {id:'m17630640437', cat:'Cards', title:'Pokémon Card 151', sub:'Sealed BOX (JP)', range:'¥39,000–60,000', ex:39800},
  {id:'m25932299194', cat:'Figures', title:'Monkey D. Luffy Gear 5', sub:'P.O.P WA-MAXIMUM', range:'¥13,000–28,000', ex:13500},
  {id:'m48700980297', cat:'Figures', title:'Roronoa Zoro "Asura"', sub:'P.O.P WA-MAXIMUM', range:'¥19,000–30,000', ex:19400},
  {id:'m69113118184', cat:'Figures', title:'Nagi Seishiro', sub:'Nendoroid 2056 (Blue Lock)', range:'Around ¥6,600 (prize figures ¥1,100–3,800)', ex:6666},
  {id:'m75254338953', cat:'Retro Games', title:'Pokémon Red', sub:'Game Boy, boxed (JP)', range:'Boxed ¥7,000–18,500 / cart only from ¥1,800', ex:9500},
  {id:'m84542502513', cat:'Retro Games', title:'Pokémon Crystal', sub:'Game Boy Color, boxed (JP)', range:'Boxed ¥9,000–18,000 / cart from ¥2,900', ex:14599},
  {id:'m35783849029', cat:'Retro Games', title:'Game Boy Color', sub:'Clear, tested', range:'¥6,500–13,000', ex:8480},
].map(it => ({...it, url:'https://jp.mercari.com/item/' + it.id, img:'img/' + it.id + '.jpg',
  price:'¥' + it.ex.toLocaleString('en-US'), name: it.title + ' — ' + it.sub, alt: (it.title + ' — ' + it.sub).replace(/"/g, '&quot;')}));
const CATS = ['Cards', 'Figures', 'Retro Games'];

const HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.3s-7.6-4.6-9.3-9.2C1.6 8 3.4 4.6 6.8 4.3c2.1-.2 3.9 1 5.2 2.8 1.3-1.8 3.1-3 5.2-2.8 3.4.3 5.2 3.7 4.1 6.8-1.7 4.6-9.3 9.2-9.3 9.2z"/></svg>';

const COPY = {
  intro: "Can't find it in the shops on tour day? We can buy it on Mercari, Japan's biggest second-hand marketplace, before the tour — and hand it to you in Ikebukuro on December 20.",
  steps: ['Send us the item and your max budget',
    'We send you the exact listing and the full total',
    'You approve and pay by card link',
    "We buy it and hand it over on Dec 20 — if it's sold out, we tell you. Never a silent substitute."],
  fee: 'No service fee for tour guests — you pay the item price + domestic shipping (usually ¥200–700).',
  honest: ['Every price here is a real Mercari listing, checked on November 19, 2026.',
    'The market moves. Prices go up and down, and listings sell out.',
    "If something sells out, we never buy a substitute on our own. We always tell you first."],
};

// Fill [data-slot] blocks with the fixed copy. Designs style the classes.
function huntCommon() {
  const fill = (k, html) => document.querySelectorAll('[data-slot="' + k + '"]').forEach(el => el.innerHTML = html);
  fill('intro', COPY.intro);
  fill('steps', '<ol class="steps">' + COPY.steps.map((s, i) => '<li><b>' + (i + 1) + '</b><span>' + s + '</span></li>').join('') + '</ol>');
  fill('fee', COPY.fee);
  fill('honest', '<ul class="honest">' + COPY.honest.map(s => '<li>' + s + '</li>').join('') + '</ul>');
  fill('form', `<form class="hunt-form" novalidate>
    <label>Item<input id="f-item" name="item" placeholder="e.g. Charizard ex SAR, raw"></label>
    <label>Max budget<input name="budget" inputmode="numeric" placeholder="e.g. ¥45,000"></label>
    <label>Name<input name="name" autocomplete="name" placeholder="Your name"></label>
    <label>Message<textarea name="message" rows="3" placeholder="Condition, size, anything we should know"></textarea></label>
    <button class="btn-red" type="submit">Send the hunt list</button>
    <p class="form-note" hidden>Preview only — this form doesn't send yet.</p>
  </form>`);
  document.querySelectorAll('.hunt-form').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault(); f.querySelector('.form-note').hidden = false;
  }));
}

// Build category tabs into `bar`; calls render(items, cat) on every switch.
function huntTabs(bar, render, label = c => c) {
  bar.setAttribute('role', 'tablist');
  bar.innerHTML = CATS.map((c, i) =>
    `<button type="button" role="tab" class="tab${i ? '' : ' on'}" aria-selected="${!i}" data-cat="${c}">${label(c)}</button>`).join('');
  const show = cat => {
    bar.querySelectorAll('.tab').forEach(b => { const on = b.dataset.cat === cat; b.classList.toggle('on', on); b.setAttribute('aria-selected', on); });
    render(ITEMS.filter(it => it.cat === cat), cat);
  };
  bar.addEventListener('click', e => { const b = e.target.closest('.tab'); if (b) show(b.dataset.cat); });
  show(CATS[0]);
}

// "Ask Yuuki to buy": prefill the form with the item and jump to it.
function huntAsk(id) {
  const it = ITEMS.find(x => x.id === id), f = document.getElementById('f-item');
  if (it && f) f.value = it.name;
  document.getElementById('ask').scrollIntoView({behavior: 'smooth'});
}
