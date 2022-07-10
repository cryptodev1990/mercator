import { Navbar } from "../../components/navbar";
import geofencer from "./icons/geofencer-logo.svg";
import blank from "./icons/dbconfig-logo.svg";
import { useNavigate } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { isAdmin } from "../../common";

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
      className="max-w-sm rounded overflow-hidden shadow-lg bg-swiss-coffee focus:shadow-none"
    >
      <div className="bg-porsche">
        <img src={props.svg} alt="logo" />
      </div>
      <div className="px-6 py-4 bg-swiss-coffee overflow-hidden">
        <div className="font-bold text-xl pb-2">{props.name}</div>
        <p className="text-gray-700 text-base">{props.description}</p>
      </div>
    </div>
  );
};

const DashboardPage = () => {
  const { user } = useAuth0();
  console.log(user);
  return (
    <main
      className="max-w-full h-screen bg-gray-200 overflow-scroll"
      role="main"
    >
      <section className="max-w-full bg-tuna">
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
        <AppCard
          tabindex={2}
          svg={blank}
          navlink={"/db-config"}
          name="DBConfig"
          description="Configure database connections for your team"
        />
        <AppCard
          hidden={!isAdmin(user)}
          tabindex={3}
          svg={blank}
          navlink={"/admin"}
          name="Admin"
          description="Admin"
        />
        <AppCard
          tabindex={3}
          svg={blank}
          navlink={"/"}
          name="Other application"
          description="Lorem ipsum dolores"
        />
      </section>
    </main>
  );
};

export default DashboardPage;
