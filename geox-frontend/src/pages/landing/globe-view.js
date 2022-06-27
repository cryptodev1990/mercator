import {
  _GlobeView as GlobeView,
  _GlobeController as GlobeController,
} from "@deck.gl/core";

class CustomGlobeController extends GlobeController {
  handleEvent(event) {
    if (event.type === "pan") {
      // do something
    } else {
      super.handleEvent(event);
    }
  }
}

export { GlobeView, CustomGlobeController };
