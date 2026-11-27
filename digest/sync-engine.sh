#!/bin/sh
# Copy the open-data fetchers from the public-tenders-feed actor (apify-actors/tenders/src) into digest/engine/.
set -e
SRC="${1:-../../apify-actors/tenders/src}"
cp "$SRC/common.js" "$SRC/pipeline.js" engine/
cp "$SRC"/sources/*.js engine/sources/
