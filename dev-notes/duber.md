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
  - "Do your best work"


July 15 2022
-------------

### Plans

- [X] Add a button for changing edit modes
- [ ] Draw shapes by routing API

### Progress

- [X] Add a button for changing edit modes

### Problems

- [X] Cut the overflow on the page

July 16 2022
------------

### Plans

- [X] Draw shapes by routing API
    - [ ] Can we get lasso working?

## Observations

- The sidebar could use an animation: https://tailwindui.com/components/application-ui/overlays/slide-overs 


July 18 2022
-------------

### Progress

- [X] Build a demo for Lily
  - [X] Draw a GPS trace
  - [X] Run the mapmatch API on it

- [X] Get the post-add flow working
  - [X] Add a shape
  - [X] Open the metadata editor box
  - [X] Let the user save the metadata


### Plans

- [ ] Support adding multiple properties
- [ ] Select multiple shapes and bulk edit their metadata
- [ ] Isochrone flow
- [ ] Select from OSM or Wikipedia, then draw isochrones or buffers around them
- [ ] Celestial/Heaven still needs a demo

## July 19 2022

### Progress

- [ ] Provide a way to edit the properties field for metadata edits

### Observations

- [ ] Might be useful to learn about Formik: https://youtu.be/vJtyp1YmOpc
- [ ] TODO need to support publishing versions of shapes
- Lean on examples from React Hook Form

July 20-21 2022
------------

### Progress

- [X] Support adding multiple properties

### Plans

- [X] Heaven

July 22 2022
------------

### Progress

- [X] Cleanup code in frontend
  - [X] Add style to JSON editor
- [X] OSM data -> buffer
  - [X] Command palette: "Pull OSM parks and draw a 10m meter buffer around them"
  - [X] Set up a FastAPI endpoint that grabs OSM demo data
  - [X] Render that data in the UI
  - [ ] ~~Add a one of those deck.gl demo option panel to set a radius~~
- [ ] Export shapes to a FeatureCollection file


July 23 2022
------------

- [ ] Export shapes to a FeatureCollection file
- [X] Bulk delete / bulk add

July 24 2022
------------

- [X] Smooth sidebar animation


July 25 2022
------------

## Outstanding features

### Backend / frontend

- [ ] publishing to a backend database
  - [ ] Create user organizations
    - [ ] Default users to a personal organization
      - [ ] If a new user appears, create a new organization with them. Each organization has one member by default
      - [ ] TODO add the ability to invite other members to your organization
  - [ ] Fill in DB manager page
    - [ ] Let user create a db for their organization
    - [ ] Let user read active dbs
    - [ ] Let user delete a db
  - [ ] Create DB manager Celery task
    - [ ] Test connection health to user db
    - [ ] Write to table in connection db
        - Schema: shape UUID, geojson, version
    - [ ] Read from table in connection db
- [ ] publishing via web hooks
- [ ] adding pagination to the shapes API
- [ ] letting the user upload their own geometries

### UI-only changes

- [ ] snap shape to map
- [ ] allow / disallow overlap
- [ ] bulk add: letting the user upload their own geometries
- [ ] bulk delete

July 26 2022
------------

## Progress

- [X] Mapbox analysis: Pull GPS traces

## Observations

- Pulumi is a Terraform replacement in JS

July 28 2022
------------

- [X] Finish refactor

Useful snippet for figuring out what function is the caller function:

```javascript
  // @ts-ignore
  console.log(new Error().stack.split("\n")[2].trim().split(" ")[1]);
```

July 30 2022
------------

## Progress

- [X] Add "Edit" mode to shapes UI
- [X] Add "Cut" mode to shapes UI

## Plans

- [ ] Allow export to GeoJSON

## Observations

- We could go one of two ways:
  - Prioritize sharing this with devs
  - Prioritize demo features

Aug 1 2022
-----------

- [X] CRUD for connections


- Creating a new user gives an organization called Personal, with a namespace called Personal
- Users can join organizations, with a default namespace called Shared and Personal

Aug 3 2022
----------

## Progress

- [X] Test for CRUD for connections

## Plans

- [ ] CRUD for namespaces
- [ ] Test for CRUD for namespaces

## Observations

- [Will need to get separate encryption keys per tenant](https://stackoverflow.com/questions/34199979/protecting-encrypting-data-in-a-shared-database-of-a-multitenant-cloud-applica)


Aug 4 2022
----------

## Progress

- [X] ~~Test for CRUD for connections~~ Refactored to prefer SqlAlchemy to raw SQL, preferred a "organization members" table.
  This unfortunately undid a lot of the db credentials / connections progress

## Plans

- [ ] CRUD for namespaces
- [ ] Test for CRUD for namespaces
- [ ] Bugfix for shape edit
- [ ] See user cursors in the same namespace.
  - [ ] [Copy Excalidraw maybe?](https://github.com/excalidraw/excalidraw/blob/dac8dda4d4f4b92471e3ae388206443dcb66fb78/src/excalidraw-app/collab/Collab.tsx#L204)
  - [ ] [LiveBlocks?](https://liveblocks.io/presence)
- [ ] Re-do landing page for Launch Bookface

Aug 5-7
-------

## Progress

- [X] Finished organizations flow

Aug 7-8

## Progress

- [X] Re-do landing page for Launch Bookface
- [X] Add to organization flow
- [ ] Write tests for organization flow
- [ ] Support publishing shapes to database

Aug 9
------

## Progress

- [X] Polish landing page

Aug 10
-------

## Progress

- [X] Add endpoints to manipulate credentials
- [X] Add endpoints to manipulate organizations
- [ ] Add create and read tests for organization flow

## Plans

- [ ] Need to make sure an organization always exists for a user. Another update trigger?
  - On org member soft delete, create a personal organization for a user

Aug 16-19 2022
-----------

## Progress
- [ ] Fix backlog tags
  - [ ] Editable shapes can't have points dragged back into the shape
  - [X] Right-click of a shape occasionally does not select the shape
  - [ ] Fix scroll
- [ ] Complete database publish
- [ ] Complete snap shape to roads
  - [ ] Break polygon into ring
  - [ ] Snap ring to roads
- [X] Make OSM searchable - demo copy
  - Used ``osm2pgsql`` with a ``flex`` argument and a [custom Lua script](https://github.com/openstreetmap/osm2pgsql/blob/master/flex-config/generic.lua)
  - Added a TSVector to pg tags column
- [ ] Pagination for shape results


# MVP

## Tier 0

- [X] Multitenancy
- ~~[ ] Snowflake publication~~
 - Possibly solved by [AirByte](https://airbyte.com/tutorials/postgresql-database-to-snowflake?utm_term=&utm_campaign=Airbyte+-+Nonbrand+-+Database+Transition&utm_source=adwords&utm_medium=ppc&hsa_acc=7542309003&hsa_cam=16651686687&hsa_grp=140090051201&hsa_ad=596994094959&hsa_src=g&hsa_tgt=aud-1637563966306:dsa-1720612594717&hsa_kw=&hsa_mt=&hsa_net=adwords&hsa_ver=3&gclid=CjwKCAjw6fyXBhBgEiwAhhiZsnMhxX_vU0BFWEH1upPto2BNLp0pXD85CZTIz62YZR9BAy1XK2aizxoCBh8QAvD_BwE#step-7)
 - ~~See branch ``ajd/add-a-database`` for WIP backend publication with Celery~~
 - [X] ~~DB credential creation flow [NOTE: Decided not to go with this approach]~~
   - [X] ~~Add UI for DB credential creation~~
   - [X] ~~Add health tests for DB credentials~~
   - [X] ~~Do an end to end test: Add credentials, do a health check~~
 - [ ] Copy data to a snowflake database
   - [X] Create an S3 bucket
     - [X] Verify can read from local machine (done at 10:37am Aug 27)
     - [X] Verify can read from Snowflake (done at 11:23am Aug 27)
   - [ ] Replicate the user's data to an S3 bucket
     - [X] Copy data from Postgres to S3 (done at 1:16am Aug 29)
     - [ ] Copy data from S3 to Snowflake
       - [X] Copy that S3 bucket to a stage
       - [X] Copy the stage to a table
       - [ ] Do this automatically: https://docs.snowflake.com/en/user-guide/tables-external-s3.html
             and maybe this, https://docs.snowflake.com/en/sql-reference/sql/create-external-table.html
     - [X] Configure a view for an organization on Snowflake
     - [ ] Share that to an external Snowflake organization
       - Docs for [setting up a snowflake data share](https://docs.snowflake.com/en/user-guide/data-sharing-gs.html#step-1-create-a-share)
       - Also this: https://docs.snowflake.com/en/user-guide/data-sharing-intro.html
     - [ ] Can we get some kind of a test on this??
- [X] Feature: Add button to trigger data copy (1:09am on Sep 5)
- [X] Feature: Button to download all JSON -- download all live shapes to JSON (1:09am on Sep 5)
- [X] Uploads of random data -- cap at 100 MB?
- [X] Finish the tentative shapes flow for publish
  - [X] Allow removal of tentative shapes (1:09am on Sep 5)
  - [X] Hide tentative shape on publish (1:09am on Sep 5)
  - [X] Cap upload of tentative shapes at 10MB (no-op)
  - [X] Enable zoom to tentative shapes (1:09am on Sep 5)
- [ ] UI bugs
  - [X] Drag / drop edits have odd jumps
    - Repro steps: Make a few of these, you'll see the shape doesn't always snap to the point
    - Post-mortem: Issue is that an edit of the shapes locally triggers a refresh of the shapes from the server
      and the shapes are ordered by updated timestamp
  - [X] "Tentative shape" shadow lingers
    - Repro steps: Draw a shape, alter it, delete the shape. Shadow is still there.
  - [X] Shape delete from right click does not work (1:59am on Sep 5)
    - Post-mortem: Frontend / backend client out of sync
  - [X] "The metadata editor needs a shape to edit" needs to be hidden
  - [X] Scroll on the shape bar needs to work
    - Repro steps: Add enough shapes for a scroll (10:36am on Sep 5)
    - [X] Virtual windows: https://react-window.vercel.app/#/examples/list/fixed-size
  - [ ] Weird properties count  -- no op for now
    - Repro steps: Add a property on a shape, the New Key will have an odd number
  - [ ] Double tooltip issue  -- no -op for now
    - Repro steps: Hover over multiple tooltip'd properties, the tooltips accumulate
- [X] Error snackbar needs to exist

## Tier 1

- [ ] Alerting on 400s/500s
- [ ] Organizations - Create an organization. For now, I can do this manually.
- [ ] Feature: Surface options to enable shape overlap (but deny by default)
- [ ] Feature: Snap to roads
- [ ] DataDog
- [ ] Feature: Ability to select multiple shapes for bulk edit, export, delete
- [ ] Feature: Ability to publish
- [ ] Feature: Arrange Z of shapes

## Tier 2

- [ ] OSM search / copy for all of North America
- [ ] Copy from Postgres to Snowflake using Fivetran: https://fivetran.com/docs/databases/connection-options#reversesshtunnel

## Tier 3

- [X] Add 403 page
  - Repro steps: Open up incognito browser to mercator.tech/geofencer
- [ ] Add error snackbar to landing page
  - Right now when you sign up with an unauthorized user, you don't receive any notice indicating that you are doing so

## Sep 7 2022


### Progress
- [X] Added edit-on-shape select


### Plans

- [ ] Swimply
  - [ ] Add Swimply organization to the database
  - [ ] Finish Snowflake datashare
- [X] UI bug: Make the shape edit actually work
- [X] UI bug: No mode selected after shape cut
- [ ] Move production of shapes to a tile server

### Problems

Complexity on the frontend has gotten quite high. Might need a new data model.

Allow selected shapes: Allow 1+ shapes to be selected
Groupings: Allow groupings of multiple shapes


## Sep 9 2022

### Progress

- [X] Debugging the inconsistent shape modification behavior
  - Some function internal to deck.gl gets interruped by the shape draw, though I'm not 100% sure yet on what
- [X] Require a click before a drag? This is a worse user experience (slightly) but guarantees consistent behavior


## Sep 10 2022

### Progress

- [X] Workably patched modify mode

## Sep 11 2022

- [X] [URGENT] Need to re-activate network requests for modify mode
  - [X] Make update return shapes?
  - [X] When the mode is switched or selection is changed or 5 seconds of inactivity are detected, fetch the latest shapes
- [X] [URGENT] Uploads are broken
- [X] Verify that property editor is not broken

## Sep 12 2022

- [ ] Send emails for users
- [X] Add parameter to toggle overlap (in context menu)
- [X] Add point-in-poly routes
- [X] Investigate options for API access

## Sep 14 2022

### Plans

- [ ] Add Usersnap to the frontend
- [ ] Search / sort for sidebar
- [ ] Support tiling
  - Create geometries on the backend
    - Create geojson features from properties and geometries for certain parts of the API
    - Index the geometeries
    - API needs to request tile
    - Load testing -- will this strategy work with many concurrent users?

### Progress

### Problems
