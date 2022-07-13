import { GeofencerNavbar } from "../../features/geofence-map/geofencer-navbar";
import { GeofenceMap } from "../../features/geofence-map/geofence-map";
import { GeofenceSidebar } from "../../features/geofence-map/geofence-sidebar";

const GeofencerPage = () => {
  return (
    <div className="text-white">
      <div className="h-fit w-screen p-4 bg-gradient-to-r from-slate-800 to-slate-900">
        <GeofencerNavbar />
      </div>
      <div className="h-screen w-screen relative">
        <div className="h-[90%] px-5 py-5 flex flex-row relative">
          <GeofenceSidebar />
        </div>
        <GeofenceMap />
      </div>
    </div>
  );
};

export default GeofencerPage;
