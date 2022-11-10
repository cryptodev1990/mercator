import { Navbar } from "../../common/components/navbar";
import { AccountSupportCard } from "./components/account-support-card";
import { AccountUserCard } from "./components/account-user-card";

const AccountPage = (): JSX.Element => (
  <main className="h-screen bg-blue-400 overflow-none" role="main">
    <section className="max-w-full bg-blue-700">
      <div className="max-w-5xl mx-auto h-fit p-3">
        <Navbar />
      </div>
    </section>
    <section className="max-w-4xl m-auto pt-9 flex flex-col space-y-5">
      <h2 className="text-white font-bold text-2xl">Account</h2>
      <AccountUserCard />
      <AccountSupportCard />
    </section>
  </main>
);

export default AccountPage;
