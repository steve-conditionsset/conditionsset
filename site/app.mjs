import { formatSnow, formatDate, formatStormRange, isStale, validateDataset, sortLocations, SIGNAL_LABELS } from './display.mjs';

const board = document.querySelector('#locations');
const message = document.querySelector('#load-message');

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function locationCard(place) {
  const item = element('li', `location ${place.signal}`);
  const top = element('div', 'card-top');
  const heading = element('h3', 'area-name');
  heading.append(document.createTextNode(place.name), document.createTextNode(' '), element('span', 'state', place.state));
  const dot = element('span', `dot ${place.signal}`);
  dot.setAttribute('role', 'img');
  dot.setAttribute('aria-label', SIGNAL_LABELS[place.signal]);
  top.append(heading, dot);
  const snow = element('div', 'snow-row');
  snow.append(element('span', 'snow', formatSnow(place.snowfall_inches)));
  const dates = element('p', 'storm-dates', `${formatStormRange(place.storm_start, place.storm_end)} · 2-DAY SNOW`);
  item.append(top, snow, dates);
  if (place.bluebird_date) {
    const clearing = element('span', 'clearing');
    const sun = element('span', 'sun', '☀');
    sun.setAttribute('aria-hidden', 'true');
    clearing.append(sun, document.createTextNode(`Clearing ${formatDate(place.bluebird_date, { weekday: 'short', month: 'short', day: 'numeric' })}`));
    item.append(clearing);
  }
  return item;
}

async function loadForecast() {
  try {
    const response = await fetch('./data/forecast.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('No published forecast.');
    const data = validateDataset(await response.json());
    const updateTime = new Intl.DateTimeFormat('en-US', {
      month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit',
      timeZone: 'America/Denver', timeZoneName: 'short',
    }).format(new Date(data.generated_at));
    document.querySelector('#updated').textContent = `Last successful update ${updateTime}`;
    document.querySelector('#outlook-title').textContent = `${formatDate(data.evaluation_start, { month: 'short', day: 'numeric', year: 'numeric' })} – ${formatDate(data.evaluation_end, { month: 'short', day: 'numeric', year: 'numeric' })}`;
    document.querySelector('#example-warning').hidden = data.example !== true;
    const updateStaleness = () => { document.querySelector('#stale-warning').hidden = !isStale(data.generated_at); };
    updateStaleness();
    setInterval(updateStaleness, 60_000);
    // Separate grids keep state groups together without filling partial rows from the next state.
    const groups = [];
    let currentState;
    let cards;
    for (const place of sortLocations(data.locations)) {
      if (place.state !== currentState) {
        currentState = place.state;
        const group = element('li', 'state-group');
        cards = element('ol', 'state-cards');
        cards.setAttribute('aria-label', `${place.state} areas in snowfall order`);
        group.append(cards);
        groups.push(group);
      }
      cards.append(locationCard(place));
    }
    board.replaceChildren(...groups);
    message.textContent = '';
  } catch {
    document.querySelector('#outlook-title').textContent = 'Forecast period unavailable';
    document.querySelector('#updated').textContent = 'Forecast unavailable';
    message.textContent = 'The forecast is temporarily unavailable. Please check back after the next daily update.';
    board.replaceChildren();
  } finally {
    document.querySelector('#outlook').setAttribute('aria-busy', 'false');
  }
}

loadForecast();
