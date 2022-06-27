import logo from "./mercator-logo.svg";

const Navbar: React.FC = () => {
  const css =
    "relative max-w-5xl bg-red z-10 container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-24 font-semibold text-sm text-white";
  return (
    <header className={css}>
      <nav aria-label="Logo menu" className="relative z-50 flex">
        <a href="/">
          <img src={logo} alt="logo" className="h-10" />
        </a>
      </nav>
      <nav aria-label="Main menu" data-menu="" className="flex">
        {/* <a
          href="/blog/"
          className="text-center mx-auto lg:ml-auto lg:mr-3 transition-colors hover:text-violet-500"
          data-turbolinks="false"
        >
          Blog
        </a>
        <a
          href="/phoenix-files/"
          className="text-center mx-auto lg:mx-3 transition-colors hover:text-violet-500"
          data-turbolinks="false"
        >
          Phoenix Files
        </a>
        <a
          href="/docs/iii"
          className="text-center mx-auto lg:mx-3 transition-colors hover:text-violet-500"
          data-turbolinks="false"
        >
          Docs
        </a>
        <a
          href="https://community.fly.io"
          className="text-center mx-auto lg:mx-3 transition-colors hover:text-violet-500"
          data-turbolinks="false"
        ></a>
        <a
          href="/docs/about/pricing/"
          className="text-center mx-auto lg:ml-3 lg:mr-auto transition-colors hover:text-violet-500"
          data-turbolinks="false"
        >
          Pricing
        </a>
        */}

        <a
          href="/login"
          className="text-base sm:text-sm px-6 button lg:button-sm bg-ublue hover:bg-violet-600 text-white font-bold transition-all p-2 rounded"
          data-turbolinks="false"
        >
          Login
        </a>
      </nav>
    </header>
  );
};

export { Navbar };
