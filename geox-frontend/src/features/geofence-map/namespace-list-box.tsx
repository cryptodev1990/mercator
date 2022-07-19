import { useEffect, useState } from "react";
import { Listbox } from "@headlessui/react";
import { BsCheck } from "react-icons/bs";
import { HiSelector } from "react-icons/hi";
import { useAuth0 } from "@auth0/auth0-react";
import { SmoothTransition } from "../../common/components/smooth-transition";

export function NamespaceListBox() {
  const { user } = useAuth0();
  const emailDomain = user?.email?.split("@")[1];
  const [namespace, setNamespace] = useState<string | undefined>(user?.email);

  const options = [user?.email, emailDomain];

  useEffect(() => {
    if (user?.email) {
      setNamespace(user.email);
    }
  }, [user]);

  return (
    <div className="text-white z-40">
      <Listbox value={namespace} onChange={setNamespace}>
        <input name="listbox" className="hidden"></input>
        <div className="relative w-[13rem]">
          <Listbox.Button className="cursor-pointer relative w-full rounded-lg bg-slate-500 py-2 pl-3 pr-10 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm">
            <span className="block truncate">{namespace}</span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <HiSelector
                className="h-5 w-5 text-gray-400"
                aria-hidden="true"
              />
            </span>
          </Listbox.Button>
          <SmoothTransition>
            <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              <p className="text-slate-500 px-3 py-1">Namespaces</p>
              <hr />
              {options.map((namespace, i) => (
                <Listbox.Option
                  key={i}
                  className={({ active }) =>
                    `relative cursor-default select-none py-2 pl-10 pr-4 ${
                      active ? "bg-amber-100 text-amber-900" : "text-gray-900"
                    }`
                  }
                  value={namespace}
                >
                  {({ selected }) => (
                    <>
                      <span
                        className={`block truncate ${
                          selected ? "font-medium" : "font-normal"
                        }`}
                      >
                        {namespace}
                      </span>
                      {selected ? (
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-amber-600">
                          <BsCheck className="h-5 w-5" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </SmoothTransition>
        </div>
      </Listbox>
    </div>
  );
}
