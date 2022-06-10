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

## Plans / Progress

- [X] Deploy a basic hello world app with fly.io and FastAPI
  - Why Fly.io? Why not? Easy PaaS with a YC deal.
  - Why FastAPI? Get free OpenAPI / Swagger bindings for the frontend, seems easy to use
- [ ] Run a React application out of the app

## Observations

- The docker command to build and run a Dockerfile, ``docker build . -t geox-web && docker run -p 3000:80 geox-web``
