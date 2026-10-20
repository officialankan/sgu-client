# sgu-client

A Python client for the open groundwater data published by SGU (Geological Survey of Sweden).

## Language

### How SGU publishes data

**Dataset**:
One of SGU's open data APIs, such as observed groundwater levels, modeled groundwater levels or groundwater chemistry.
_Avoid_: API, endpoint, service

**Collection**:
One kind of feature within a dataset, such as `stationer` or `nivaer` in the observed levels dataset.
_Avoid_: endpoint, table, layer

**Feature**:
One item in a collection: a station, a measurement, an area, and so on.
_Avoid_: record, row, item

**Feature id**:
SGU's technical id for a feature, made of the collection name and a number (e.g. `stationer.4086`). Rarely what a user means by "id".
_Avoid_: station id, ID

### Groundwater levels

**Station**:
A place where groundwater levels are observed.
_Avoid_: well, site, monitoring point

**Station id**:
A station's domain identifier (`platsbeteckning`, e.g. `95_2`), the one users know a station by.
_Avoid_: feature id, platsbeteckning (in client code)

**Measurement**:
One observed groundwater level at a station at a point in time.
_Avoid_: observation, reading, level

**Area**:
A region for which SGU models groundwater levels (`omrade`).
_Avoid_: zone, region, omrade (in client code)

**Modeled level**:
A modeled groundwater level for an area on a date.
_Avoid_: prediction, level (alone)

### Groundwater chemistry

**Sampling site**:
A place where groundwater is sampled for chemical analysis.
_Avoid_: station, well

**Site id**:
A sampling site's domain identifier (`platsbeteckning`, e.g. `TTK-442-M`).
_Avoid_: feature id

**National site id**:
A sampling site's national numeric identifier (`nationellt_provplatsid`). Analysis results refer to their sampling site by this id only.
_Avoid_: site id, provplatsid

**Analysis result**:
One measured value of one parameter in one sample from a sampling site.
_Avoid_: measurement, sample
