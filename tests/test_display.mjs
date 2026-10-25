import test from 'node:test';
import assert from 'node:assert/strict';
import { formatSnow, formatDate, formatStormRange, isStale, validateDataset, sortLocations } from '../site/display.mjs';

const place = (id, state, snowfall_inches, name = id) => ({ id, state, snowfall_inches, name });
const sortedIds = locations => sortLocations(locations).map(location => location.id);

test('states rank by maximum rather than total; each state stays together in snowfall order', () => {
  const locations = [place('ut-low', 'UT', 7), place('co-low', 'CO', 1),
    place('wy', 'WY', 9), place('co-high', 'CO', 10), place('ut-high', 'UT', 8)];
  assert.deepEqual(sortedIds(locations), ['co-high', 'co-low', 'wy', 'ut-high', 'ut-low']);
});

test('tied state maxima use abbreviation before comparing individual locations', () => {
  assert.deepEqual(sortedIds([place('ut-high', 'UT', 10), place('co-low', 'CO', 0),
    place('ut-low', 'UT', 9), place('co-high', 'CO', 10)]),
  ['co-high', 'co-low', 'ut-high', 'ut-low']);
});

test('tied locations sort by case-insensitive name, then ID', () => {
  assert.deepEqual(sortedIds([place('z', 'CO', 2, 'Beta'), place('b', 'CO', 2, 'alpha'),
    place('a', 'CO', 2, 'Alpha')]), ['a', 'b', 'z']);
});

test('all-zero forecasts sort deterministically by state and name', () => {
  assert.deepEqual(sortedIds([place('z', 'WY', 0), place('b', 'CO', 0),
    place('a', 'CO', 0), place('n', 'NM', 0)]), ['a', 'b', 'n', 'z']);
});

test('state and location comparisons use unrounded snowfall', () => {
  const locations = [place('co', 'CO', 8.31), place('ut-low', 'UT', 8.32),
    place('ut-high', 'UT', 8.34)];
  assert.equal(new Set(locations.map(p => formatSnow(p.snowfall_inches))).size, 1);
  assert.deepEqual(sortedIds(locations), ['ut-high', 'ut-low', 'co']);
});

test('sorter accepts empty input and arbitrary states and location counts', () => {
  assert.deepEqual(sortLocations([]), []);
  const locations = Array.from({ length: 17 }, (_, i) => place(String(i), i % 2 ? 'AK' : 'CA', i));
  assert.deepEqual(sortedIds(locations), ['16', '14', '12', '10', '8', '6', '4', '2', '0',
    '15', '13', '11', '9', '7', '5', '3', '1']);
  assert.deepEqual(sortedIds([place('one', 'VT', 0)]), ['one']);
});

test('sorting returns a new array without mutating locations or their records', () => {
  const locations = Object.freeze([Object.freeze(place('low', 'CO', 1)),
    Object.freeze(place('high', 'CO', 2))]);
  const before = structuredClone(locations);
  const sorted = sortLocations(locations);
  assert.notEqual(sorted, locations);
  assert.equal(sorted[0], locations[1]);
  assert.deepEqual(locations, before);
});

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

test('compact storm ranges distinguish month and year boundaries', () => {
  assert.equal(formatStormRange('2026-11-02', '2026-11-03'), 'NOV 02–03');
  assert.equal(formatStormRange('2026-10-31', '2026-11-01'), 'OCT 31–NOV 01');
  assert.equal(formatStormRange('2026-12-31', '2027-01-01'), 'DEC 31, 2026–JAN 01, 2027');
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
