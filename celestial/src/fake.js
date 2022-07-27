function nab(array) {
  return array[Math.floor(Math.random() * array.length)];
}

const cache = {};

let lastLoadId = 1000;
function loadGenerator() {
  lastLoadId += 1;
  return lastLoadId;
}

export function fake(driverId, entityName) {
  console.log(driverId);
  if (cache[driverId] && cache[driverId][entityName]) {
    return cache[driverId][entityName];
  }
  if (!cache[driverId]) {
    cache[driverId] = {};
  }
  cache[driverId][entityName] = _fake(entityName);
  return cache[driverId][entityName];
}

function _fake(entityName) {
  switch (entityName) {
    case "name":
      return (
        nab(["John", "Jane", "Bob", "Mary", "Tom", "Alice"]) +
        " " +
        nab(["Smith", "Jones", "Williams", "Brown", "Davis", "Miller"])
      );
    case "shipping":
      return nab(["UPS", "FedEx", "DHL", "TNT", "LTL"]);
    case "load":
      return loadGenerator();
  }
}

export function determineStatus(status) {
  if (status === "en_route") {
    return Math.random() < 0.001 ? "late" : "en_route";
  }
  if (status === "late") {
    return Math.random() < 0.999 ? "late" : "en_route";
  }
}
