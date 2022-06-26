Jun 9 2022
----------

## Plans
## Problems
## Progress
## Observations

- What are we building?
  - UI for power analysis
    - Input:
    	- Time series of the metric you're interested in (as much as you can give us)
        - "I want an experiment that achieves this X% effect size in Y time"
    - Output:
          - Curve that gives the tradeoff between power and time, based on the data you've given us
  - Python wrapper for GeoLift
  - Some sort of API that some developers can call


- TODO do we build some sort of CMS for geo experiment management?

  - List of experiments
    - Treatment and control
    - Live dates
    - Input data
    - Experiment status: Planned, live, archived

1) Designing an experiment -> Some sort of assignments
2) Defining an experiment
3) Analysis and management
4) Developer integration (TBD)

We develop a richer understanding of where to run your experiments over time
We can best choose the locations where your geographies

Jun 10 2022
-----------

## Progress

- [X] Deploy a basic hello world app with fly.io and FastAPI
  - Why Fly.io? Why not? Easy PaaS with a YC deal.
  - Why FastAPI? Get free OpenAPI / Swagger bindings for the frontend, seems easy to use
- [X] Run a React application out of the app

## Plans

- [ ] Work with advisors to figure out the data model
- [ ] Figma to figure out what the UX is

## Observations

- The docker command to build and run a Dockerfile, ``docker build . -t geox-web && docker run -p 3000:80 geox-web``
- ``fly launch`` builds the project the first time; ``flyctl deploy`` runs the current configuration. ``fly open`` opens the current web URL for fly.
- Deployed the frontend to Vercel and the backend to Fly
- Fly URL: https://restless-rain-538.fly.dev/
- FE Vercel URL: https://geox.vercel.app

June 18 2022
------------

## Plans / Progress

- [X] Get pygeolift into the FastAPI Docker container

## Observations

```R
market_selections <- geolift.geo_lift_market_selection(
  data = geo_test_data_pre_test,  # This is a data.frame of location, serial time ID, and a Y value. Optionally additional X's (skip for now)
  treatment_periods = [10,15], # This is the length of time the experiment runs (10 time units and 15 time units)
  N = [2,3,4,5], # Try several different units (2 == 2 items in treatment, 3 == 3 items in treatment, etc)
  Y_id = "Y", # This is our Y
  location_id = "location", # This is our location ID
  time_id = "time", # This is our time period as a monotonically increasing ID
  effect_size = list(np.arange(-0.25, 0.25, 0.05)), # Check a range of effect sizes in the treatment
  lookback_window = 1, # When running simulation, run one at a time. Might skip this for?
  include_markets = ["chicago"], # Skip for now?
  exclude_markets = ["honolulu"], # Skip for now?
  cpic = 7.50, # Cost per incremental click. Library assumes Y is always a number of conversions
  budget = 100000, # Budget is the upper bound of what I want to spend
  alpha = 0.1,
  Correlations = True, # Output specification
  fixed_effects = True,
  side_of_test = "one_sided"
)
```

Options
- Create a new experiment
- Analyze an existing experiment

Landing page
- Intelligently choose where to run your experiments
- Run your experiments faster and better

```text
Based on your data, Bethesda, MD, and Portland, Oregon are the best places
for your

We look at your DV across regions
```

June 19 2022
------------

## Plans / Progress

- [X] Deploy FastAPI with a the GeoLift validator for Jeff to approve of
- [X] Add tests / build commands in a Makefile

## Observations

- The computation for GeoLift takes a bit of time, so we might need a worker queue ([example here](https://testdriven.io/blog/fastapi-and-celery/)).
- [We might need to move off of Fly, if we need a worker queue.](https://community.fly.io/t/preview-multi-process-apps-get-your-workers-here/2316/13)


June 21 2022
-------------

## Plans / Progress

- [ ] Add basic CRUD for experiments
- [X] Add worker queue
    - [X] Worker queue works on Fly / in prod
    - [X] Worker queue works in local Dockerfile
    - [X] Worker queue works on local metal

## Observations

- Had to set up Redis on Fly as its own app. Still easier than AWS but if this becomes a frequent pattern it's probably not worth using Fly
- Eugene recommended using Auth0 and Stripe for user accounts and billing
- [FastAPI with Auth0 post](https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/)


June 24 2022
------------

## Progress

- [X] Added Auth0 login
- [X] Added Alembic
- [X] Added SQLAlchemy

Need to get frontend working with the backend auth.

TODO Can I have api.mercator.tech route to Fly and mercator.tech otherwise be the frontend?

## Plans

- Write a shape drawing frontend. Desired functionality:
  - User can CRUD manage a database connection, with a target table. Hashicorp Vault for storing this?
  - Given a database and a target table, the user gets a list of shapes in that table, filtered to the current viewport
  - The user can draw new shapes by clicking a draw tool, or edit existing shapes by clicking an edit tool
  - All shapes by default are GeoJSON Features
  - User flow: Login >> Apps >> Mercator


Login
```
------------------------
|
|   MERCATOR  Geospatial intelligence for Business Operations
|
|                  Early Access User Login
|
|                  EMAIL_______
|                  PASSWORD___
|

```

Apps
```
 Imagine this page looks like toolshed.uberinternal.com or Okta
```

Mercator

````
HEADER BAR which contains a DB CONNECTIONS DROPDOWN

  TOOL BANK which is fully draggable
 
SIDE BAR with list of shapes in db
    |
    |xxxxxxxxxxxxxxxxxxxxxxxxxx
    |xxxxxx MAP   xxxxxxxxxxxxx
    |xxxxxxxxxxxxxxxxxxxxxxxxxx
    |xxxxxxxxxxxxxxxxxxxxxxxxxx
    |xxxxxxxxxxxxxxxxxxxxxxxxxx


```

## Observations

- Could use [OpenAPI TypeScript CodeGen](https://github.com/ferdikoomen/openapi-typescript-codegen) with FastAPI

June 25 2022
------------

## Progress

- [X] Set up api.mercator.tech and mercator.tech to pair with fly and vercel
- [X] Updated the landing page for mercator.tech

## Plans

- [ ] Set up login with current landing page
- [ ] Write database connector app
- [ ] Write GeoJSON app on top of database connector

## Observations

-  ``fly certs --app restless-rain-538 add api.mercator.tech`` let me add certs
- DNS records look like:

TYPE | HOST | VALUE
---------------------------------
CNAME | wwww | geox.vercel.app
TXT | @ | google-site-verification...
A Record | @ | IP-address-for-vercel
CNAME | api | restless-rain-538.fly.dev

June 26 2022
------------

## Progress

- [ ] Write GeoJSON app
  1) Create a deck container
  2) Create polygon fixtures
  3) Add new polygons
    - "Publish" on add
  4) Edit existing polygons
    - "Publish" on edit
  State to track:
    - Polygons currently on map
    - Data source currently being used
- [ ] 

