# Sep 26 2022

## Progress

1. Sent PR for frontend Datadog RUM

## Plans

1. Add Datadog APM integration for API server
2. Connect RUM + APM traces

## Problems

1. Spent some time yak shaving strongly typed env config setup but abandoned for
now and just made it a TODO. Probably best to use this: https://app-config.dev/
2. Wanted to add source uploads for frontend but didn't because it seems we
   don't have any CI set up for it and just purely rely on Vercel right now.
