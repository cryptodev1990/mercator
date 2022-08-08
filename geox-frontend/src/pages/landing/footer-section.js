export const FooterSection = () => {
  return (
    <footer className="text-white max-w-5xl mx-auto mt-12 relative h-[180px] snap-end border-t-2">
      <div className="absolute bottom-20 left-0 py-5 px-5 sm:px-0 flex flex-row justify-between items-end w-full">
        <ul className="flex flex-col">
          <li>
            <a href="mailto:support@mercator.tech" className="underline">
              Contact us
            </a>
          </li>
          <li>
            <p className="text-md">Made in San Francisco, California</p>
          </li>
        </ul>
        <div>
          <p className="text-sm">
            &copy; {new Date().getFullYear()} Mercator Technologies
          </p>
        </div>
      </div>
    </footer>
  );
};
