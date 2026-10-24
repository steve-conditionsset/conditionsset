# Representative mountain points

The configuration preserves the twelve approved coordinates. Map references below allow
placement verification without adding a mapping feature to the product. Points represent
mountain weather, not slope suitability, summit-specific forecasts, elevation corrections,
or access advice. Round-off precision is not a guarantee of forecast accuracy.

| Point | Map centered on configured coordinate |
| --- | --- |
| Berthoud Pass | https://www.openstreetmap.org/?mlat=39.798&mlon=-105.777#map=14/39.798/-105.777 |
| Steamboat | https://www.openstreetmap.org/?mlat=40.457&mlon=-106.743#map=14/40.457/-106.743 |
| Crested Butte | https://www.openstreetmap.org/?mlat=38.900&mlon=-106.943#map=14/38.900/-106.943 |
| Wolf Creek Pass | https://www.openstreetmap.org/?mlat=37.485&mlon=-106.793#map=14/37.485/-106.793 |
| Little Cottonwood Canyon | https://www.openstreetmap.org/?mlat=40.581&mlon=-111.638#map=14/40.581/-111.638 |
| Powder Mountain | https://www.openstreetmap.org/?mlat=41.379&mlon=-111.781#map=14/41.379/-111.781 |
| La Sal Mountains | https://www.openstreetmap.org/?mlat=38.439&mlon=-109.260#map=14/38.439/-109.260 |
| Jackson Hole / Tetons | https://www.openstreetmap.org/?mlat=43.597&mlon=-110.871#map=14/43.597/-110.871 |
| Snowy Range | https://www.openstreetmap.org/?mlat=41.360&mlon=-106.317#map=14/41.360/-106.317 |
| Taos Ski Valley | https://www.openstreetmap.org/?mlat=36.558&mlon=-105.417#map=14/36.558/-105.417 |
| Ski Santa Fe | https://www.openstreetmap.org/?mlat=35.796&mlon=-105.802#map=14/35.796/-105.802 |
| Ski Apache | https://www.openstreetmap.org/?mlat=33.397&mlon=-105.788#map=14/33.397/-105.788 |

The older reference workbook was inspected, not modified. It includes general-weather
locations and coordinates that differ from the approved winter list, including positive
western longitudes. Its date conversion also does not establish local calendar-day handling.
The winter implementation therefore uses the approved configuration and explicit Mountain time.

## Map verification

All twelve points were visually checked against USGS topographic map exports on
October 23, 2026, before any live weather request. Each lies in the intended mountain
area. The approved coordinates were retained without adjustment.

Source: [USGS Topo map service](https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer).
Local QA images are kept under ignored `.local/maps/`, with a contact sheet at
`.local/coordinate-review.png`; they are not website assets.

The labels "upper mountain" are approximate descriptions, not elevations: the Ski Santa Fe
and Ski Apache points are around their mountain base facilities; the Crested Butte point
is on its northern mountain terrain. No claim that all twelve points are summits is made.
