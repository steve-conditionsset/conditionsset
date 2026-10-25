// Presentation helpers only. Weather calculations remain in Python.
export const STALE_HOURS = 36;
export const SIGNAL_LABELS = { green: 'Significant snow', yellow: 'Moderate snow', neutral: 'No notable snow' };

export function sortLocations(locations) {
  const stateMax = new Map();
  for (const place of locations) {
    stateMax.set(place.state, Math.max(stateMax.get(place.state) ?? 0, place.snowfall_inches));
  }
  const compareText = (a, b) => a < b ? -1 : a > b ? 1 : 0;
  return [...locations].sort((a, b) =>
    stateMax.get(b.state) - stateMax.get(a.state)
    || compareText(a.state, b.state)
    || b.snowfall_inches - a.snowfall_inches
    || compareText(a.name.toLowerCase(), b.name.toLowerCase())
    || compareText(a.id, b.id));
}

export function formatSnow(inches) {
  if (inches > 0 && inches < 0.1) return '<0.1″';
  return `${Number(inches.toFixed(1))}″`;
}

export function formatDate(date, options = { weekday: 'short', month: 'short', day: 'numeric' }) {
  // Noon UTC keeps a calendar date on the same day in Mountain time.
  return new Intl.DateTimeFormat('en-US', { ...options, timeZone: 'America/Denver' })
    .format(new Date(`${date}T12:00:00Z`));
}

export function isStale(generatedAt, now = Date.now()) {
  return now - Date.parse(generatedAt) > STALE_HOURS * 60 * 60 * 1000;
}

function validDate(value) {
  return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)
    && Number.isFinite(Date.parse(`${value}T12:00:00Z`))
    && new Date(`${value}T12:00:00Z`).toISOString().slice(0, 10) === value;
}

export function validateDataset(data) {
  if (!data || data.schema_version !== 1 || data.timezone !== 'America/Denver'
      || typeof data.generated_at !== 'string' || !Number.isFinite(Date.parse(data.generated_at))
      || !validDate(data.evaluation_start) || !validDate(data.evaluation_end)
      || !Array.isArray(data.locations) || data.locations.length !== 12) {
    throw new Error('Published forecast is unavailable or invalid.');
  }
  const ids = new Set();
  for (const place of data.locations) {
    if (!place || typeof place.id !== 'string' || !place.id || ids.has(place.id)
        || typeof place.name !== 'string' || !place.name
        || !['CO', 'UT', 'WY', 'NM'].includes(place.state)
        || typeof place.snowfall_inches !== 'number' || !Number.isFinite(place.snowfall_inches)
        || place.snowfall_inches < 0 || !Object.hasOwn(SIGNAL_LABELS, place.signal)
        || !validDate(place.storm_start) || !validDate(place.storm_end)
        || (place.bluebird_date !== null && !validDate(place.bluebird_date))) {
      throw new Error('Published forecast is unavailable or invalid.');
    }
    ids.add(place.id);
  }
  return data;
}
