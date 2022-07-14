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
 Imagine this page looks like toolshed.uberinternal.com or Okta


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

## Plans

- [ ] Pass auth token from API to frontend
  - [ ] Use OpenAPI TypeScript CodeGen on api.mercator
  - [ ] Ping auth API endpoint from frontend
  - [ ] Store auth cookie and use on all requests
  - [ ] Verify that frontend can access authenticated material
    - [ ] Create a restricted endpoint
    - [ ] Create a restricted view
    - [ ] Verify that neither are accessible if logged out
    - [ ] Verify that both are accessible if logged in
    - [ ] Verify that accessible assets are unique to the logged-in user (e.g. user A can't see user B's material)

- [ ] Set up database connector
  - [ ] Web form for connection string info
  - [ ] Backend endpoint to pass connection string info
  - [ ] Connect backend to [Hashicorp Vault](https://www.vaultproject.io/api-docs/secret/databases)
     - Use the [Vault Docker image](https://hub.docker.com/_/vault)?

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
    - Live database connection
    - User logged in or not

June 27 2022
------------

- [X] Finish landing page globe
- [ ] Pass auth token from API to frontend
  - [ ] Use OpenAPI TypeScript CodeGen on api.mercator
  - [ ] Ping auth API endpoint from frontend
  - [ ] Store auth cookie and use on all requests
  - [ ] Verify that frontend can access authenticated material
    - [ ] Create a restricted endpoint
    - [ ] Create a restricted view
    - [ ] Verify that neither are accessible if logged out
    - [ ] Verify that both are accessible if logged in
    - [ ] Verify that accessible assets are unique to the logged-in user (e.g. user A can't see user B's material)

June 28 2022 & June 29 2022
------------------------------

- [X] Test client bearer token against API
  The access token sent to the client works for the API...huge.
- [X] Construct bearer token flow. Frontend calls Auth0, receives bearer token, uses bearer token with backend.
- [ ] ~~Use /auth callback creating user profiles~~
  - [ ] ~~Configure redirect in https://manage.auth0.com/dashboard/us/dev-w40e3mxg/applications/qjRNVRmw9ZIkDWDAkubz6iXxUIhwh5AO/settings~~

June 30 2022
-------------
- [X] Wrote middleware to protect routes
- [X] Wrote middleware to pull user out of JWT

July 1 2022
-------------
- [X] Make the post login page


July 2 2022
-------------
- [ ] Draw geofences

### Dare we PAMstack?

Roles:
  - Anon. Can write notebooks but not save them (unless signed in). Can read any public notebook.
  - Author. Can save notebooks + anon permissions. Can view/edit own notebooks that are private.
      Can edit own notebooks.
      Can "fork" other notebooks.

Usage:

0. The modes
  - Edit mode. Locked down to the author.
  - Read mode. Allowed for anyone
  - Sharing.
  	- Public
	- Private
	- User-specific
1. The cells
  - A + creates a new cell
  - A garbage can icon deletes
  - Cells are draggable / droppable
  - Cell modes:
    - Markdown
    - Rich text editor
    - Python
2. Notebook config
  - Read modes
    - Show code
    - Hide code
3. API Keys
  - Keep in mind these keys are shared with your client.
    Never put a key here that is essential for security.
    There are keys shared on clients all the time (e.g. Google Maps API keys
    or keys for the backend Firebase)

Python syscalls to patch

What's a syscall? A syscall is a "system call" to the operating system--any I/O is here, for example.
All programming languages support this.

Example syscall issues:

`os.environ` -- reading an environment variable (no OS kernel the browser)
`open('filename.txt')` -- reading a file (no file system in the browser)

Q: Yikes are we the first to do this?
A: No. And keep in mind someone did this for JavaScript in the other direction -- made the browser language of JS run
  as Node on your machine.

Other issues:

- Disable multiprocessing (since there's only one OS process for the browser...for now...)
- Disable threading (for now, though we can add webworkers in for this later)


July 6 2022
-----------

### Plans / Progress
- [X] Generate OpenAPI backend for drawing geofences
- [X] Write shapes CRUD

### Observations
- Email whitelist link: `https://manage.auth0.com/dashboard/us/dev-w40e3mxg/rules/rul_ENuEAhENBhP7OB1R`


July 7 2022
-----------

### Progress
- [X] Write test for shape CRUD

### Plans
- [ ] Test backend / frontend connection

### Observations
- Need to figure out how to pass bearer token in the api.mercator.tech/docs 
- Need CI tests still. We're fine now but that won't last.
- Need to verify this all works in prod. But to start with let's just get it working locally.
- Need to add a concept of user groups or organizations, as well as who's allowed to do what
- Versioning would be nice-to-have


July 8 2022
-----------

### Progress

- [X] Finish tests
- [X] Add bearer token to the function signature and therefore redocs/docs/OpenAPI codegen
- [X] Generate latest OpenAPI codegen for drawing geofences
- [X] Test backend / frontend connection with clients from OpenAPI
  - [X] plan to use react-query. Line 6 in pages/admin/index.tsx
- [X] Incorporate types in react query

### Plans

### Observations

July 9/10 2022
-----------

### Progress

- [X] Basic map UI
- [ ] Add read flow - open up page and read polygons for current user
- [ ] Add create flow
  - [ ] Let a user draw a geofence and publish it to the backend

### Observations

- **TODO** Need to add a ``created_at`` field to the ``users`` table, somehow missing
- **TODO** Need a 404 page
- **TODO** Need a 500 page
- **TODO** Need an error snackbar
- [EditableGeoJsonLayer docs contain mention of](https://nebula.gl/docs/api-reference/layers/editable-geojson-layer) of GeoJSON that can be snapped to

July 11 2022
-------------

### Progress

- [X] Add read flow
- [X] Add create flow

### Plans

- Edit: Transform
- Edit: Remove points
- Read: See list of active shapes in the UI
- Edit: Edit names of shapes in the UI
- Use MVTLayer to snap points to objects?

July 12 2022
------------

- [X] Add list of active shapes in the UI
- [X] Add header that includes Geofencer logo and current user
   - [ ] Settings button provide a dropdown that supports logout
- [X] Delete shapes

### Observations

- Will need to upgrade to the latest nebula.gl and at least deck 8.6 to support shape cancellations. See [here](https://github.com/uber/nebula.gl/blob/master/CHANGELOG.md)

- User interview for Yummy
  - Population in those areas
    - Enrichment for this data (e.g. who's here?)
  - [Overlapping](https://stackoverflow.com/questions/71738629/expand-polygons-in-geopandas-so-that-they-do-not-overlap-each-other)
  - Polygon area

- More PAMstack thoughts:
  - The real sell: This is the easiest-to-deploy Jupyter notebook there could possibly be
  - The risk, people use it as a proof of concept for notebooks internally then churn
