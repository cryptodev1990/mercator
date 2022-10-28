import { Navbar } from "../../common/components/navbar";
import geofencer from "./icons/geofencer-logo.svg";
import { useNavigate } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";

interface AppCardProps {
  css?: string;
  hidden?: boolean;
  svg: string;
  name: string;
  navlink: string;
  tabindex: number;
  description: string;
}

const AppCard: React.FC<AppCardProps> = (props: AppCardProps) => {
  const navigate = useNavigate();
  if (props.hidden) {
    return null;
  }
  return (
    <div
      onClick={() => navigate(props.navlink)}
      tabIndex={props.tabindex}
      className="max-w-sm cursor-pointer rounded overflow-hidden shadow-lg bg-slate-100 focus:shadow-none"
    >
      <div>
        <div className="bg-slate-600 text-white">
          <img src={props.svg} alt="logo" className="h-[300px] mx-auto" />
        </div>
        <div className="px-6 py-4 bg-swiss-coffee overflow-hidden">
          <div className="font-bold text-xl pb-2">{props.name}</div>
          <p className="text-gray-700 text-base">{props.description}</p>
        </div>
      </div>
    </div>
  );
};

const DashboardPage = () => {
  const { user } = useAuth0();
  return (
    <main
      className="max-w-full h-screen bg-gray-200 overflow-scroll"
      role="main"
    >
      <section className="max-w-full bg-slate-700">
        <div className="max-w-5xl mx-auto h-fit p-3">
          <Navbar />
        </div>
      </section>
      <section className="grid grid-cols-3 grid-rows-3 gap-3 max-w-5xl mx-auto my-10">
        <AppCard
          tabindex={1}
          svg={geofencer}
          name="Geofencer"
          navlink={"/geofencer"}
          description="Draw geofences or edit existing ones"
        />
      </section>
    </main>
  );
};

export default DashboardPage;
