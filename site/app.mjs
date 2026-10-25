import { formatSnow, formatDate, isStale, validateDataset, sortLocations, SIGNAL_LABELS } from './display.mjs';

const board = document.querySelector('#locations');
const message = document.querySelector('#load-message');

function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function locationCard(place, index) {
  const item = element('li', `location ${place.signal}`);
  const top = element('div', 'card-top');
  top.append(element('span', 'state', place.state), element('span', 'rank', String(index + 1).padStart(2, '0')));
  const heading = element('h3', '', place.name);
  const snow = element('div', 'snow-row');
  snow.append(element('span', 'snow', formatSnow(place.snowfall_inches)), element('span', 'snow-unit', '2-day snow'));
  const dates = element('p', 'storm-dates', place.snowfall_inches > 0
    ? `${formatDate(place.storm_start)} – ${formatDate(place.storm_end)}` : 'No notable snow this week');
  const bottom = element('div', 'card-bottom');
  const signal = element('span', 'signal');
  const dot = element('i', `dot ${place.signal}`);
  dot.setAttribute('aria-hidden', 'true');
  signal.append(dot, document.createTextNode(SIGNAL_LABELS[place.signal]));
  bottom.append(signal);
  if (place.bluebird_date) {
    const clearing = element('span', 'clearing');
    const sun = element('span', 'sun', '☀');
    sun.setAttribute('aria-hidden', 'true');
    clearing.append(sun, document.createTextNode(`Clearing ${formatDate(place.bluebird_date, { weekday: 'short', month: 'short', day: 'numeric' })}`));
    bottom.append(clearing);
  }
  item.append(top, heading, snow, dates, bottom);
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
    document.querySelector('#updated').textContent = `Last updated ${updateTime}`;
    document.querySelector('#outlook-title').textContent = `${formatDate(data.evaluation_start, { month: 'short', day: 'numeric', year: 'numeric' })} – ${formatDate(data.evaluation_end, { month: 'short', day: 'numeric', year: 'numeric' })}`;
    document.querySelector('#example-warning').hidden = data.example !== true;
    const updateStaleness = () => { document.querySelector('#stale-warning').hidden = !isStale(data.generated_at); };
    updateStaleness();
    setInterval(updateStaleness, 60_000);
    board.replaceChildren(...sortLocations(data.locations).map(locationCard));
    message.textContent = '';
  } catch {
    document.querySelector('#updated').textContent = 'Forecast unavailable';
    message.textContent = 'The forecast is temporarily unavailable. Please check back after the next daily update.';
    board.replaceChildren();
  } finally {
    document.querySelector('#outlook').setAttribute('aria-busy', 'false');
  }
}

loadForecast();
