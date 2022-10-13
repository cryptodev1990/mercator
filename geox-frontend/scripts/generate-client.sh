#!/bin/bash
# TODO: replace this with a JS script
openapi --input ../geox-api/openapi.json --output ./autogen --client axios
# Uncomment to use options instead of arguments for services
# openapi --input ../geox-api/openapi.json --output ./autogen --client axios --useOptions
gsed -i "s/BASE: '',/BASE: process.env.REACT_APP_BACKEND_URL as string,/" ./autogen/core/OpenAPI.ts
