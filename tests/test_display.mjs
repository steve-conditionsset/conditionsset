import test from 'node:test';
import assert from 'node:assert/strict';
import { formatSnow, formatDate, isStale, validateDataset } from '../site/display.mjs';

test('snow display does not imply extra precision or hide traces', () => {
  assert.equal(formatSnow(0), '0″');
  assert.equal(formatSnow(0.05), '<0.1″');
  assert.equal(formatSnow(2), '2″');
  assert.equal(formatSnow(11.99), '12″'); // Signal still comes from unrounded Python calculation.
  assert.equal(formatSnow(8.34), '8.3″');
});

test('calendar dates stay on their Mountain date across DST', () => {
  assert.equal(formatDate('2026-03-08'), 'Sun, Mar 8');
  assert.equal(formatDate('2026-11-01'), 'Sun, Nov 1');
});

test('stale warning starts only after 36 hours', () => {
  const generated = '2026-10-23T08:17:00+00:00';
  const exact = Date.parse(generated) + 36 * 60 * 60 * 1000;
  assert.equal(isStale(generated, exact), false);
  assert.equal(isStale(generated, exact + 1), true);
});

test('malformed or incomplete datasets are not displayed', () => {
  for (const input of [null, {}, {schema_version: 2}, {locations: []}]) {
    assert.throws(() => validateDataset(input));
  }
  const place = {id: 'a', name: 'A', state: 'CO', snowfall_inches: 12, signal: 'green',
    storm_start: '2026-10-23', storm_end: '2026-10-24', bluebird_date: '2026-10-25'};
  const valid = {schema_version: 1, timezone: 'America/Denver', generated_at: '2026-10-23T08:17:00Z',
    evaluation_start: '2026-10-23', evaluation_end: '2026-10-29',
    locations: Array.from({length: 12}, (_, index) => ({...place, id: String(index)}))};
  assert.equal(validateDataset(valid), valid);
  for (const edit of [{signal: 'red'}, {snowfall_inches: -1}, {snowfall_inches: null},
                      {storm_start: '2026-02-31'}, {bluebird_date: undefined}]) {
    const data = structuredClone(valid);
    Object.assign(data.locations[0], edit);
    assert.throws(() => validateDataset(data));
  }
});
