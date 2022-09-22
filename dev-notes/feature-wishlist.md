# Features

- [ ] Large data uploads with high fidelity
 - [ ] Tiling the data that gets uploaded
- [ ] Shape "namespaces" - provide a directory structure for shapes
  - [ ] Define a hierarchy of relationships between shapes
- [ ] Hosting OSM data?
- [ ] Snapping in the UI
 - [ ] Snap to roads
 - [ ] Snap to water
 - [ ] Snap to admin boundaries
- [ ] Search on shapes
- [ ] Metadata modification (e.g. setting the shape name)
- [ ] Shape transformations
 - [ ] Union/intersection/difference of shapes
- [ ] Command palette?
- [ ] API keys for access?
- [ ] Large scale isochrones support (drawing 10s or 100s at once)
- [ ] Incorporating real traffic?
- [ ] Point in poly for geofences

# Backlog

- Migrating state to Redux
- Integrate bug report tool
- Timeouts for DB sync failures and uploads
- Move sessions to sessions for FastAPI / Postgres
- Add exceptions to FastAPI / Swagger client

# Public release requirements

- Alerts (if the backend breaks, we should know about it)
- Error detection on the frontend
- Support automatic onboarding
- User docs
- Bug-filing: https://usersnap.com/


## What functionality of Figma makes sense for us to copy?

- [X] Edit on click
- [ ] Send to back / bring to front
- [ ] Setting colors of groups
- [ ] Grouping shapes

## Large conversations

- What should organizations/multitenancy look like?
- What should the frontend look like?
- How should NLP work?
- What data sets do we want?
- What could we build that's a novel entry?
  - ML-accelerated labeling
  - Pipelines for the text labeling, image labeling, geolabeling
