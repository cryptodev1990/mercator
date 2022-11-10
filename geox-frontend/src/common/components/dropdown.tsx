import { Menu } from "@headlessui/react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router";
import { GearFillIcon } from "../../common/components/icons";
import { SmoothTransition } from "./smooth-transition";
import { useUiModals } from "../../features/geofence-map/hooks/use-ui-modals";
import { UIModalEnum } from "../../features/geofence-map/types";

function classNames(...classes: any[]) {
  return classes.filter(Boolean).join(" ");
}

export default function Dropdown() {
  const { user } = useAuth0();
  const nav = useNavigate();
  const { openModal } = useUiModals();
  // check if on geofencer page
  const isGeofencerPage = window.location.pathname.includes("geofencer");

  return (
    <Menu as="div" className="relative z-40 inline-block text-left">
      <div>
        <Menu.Button className="btn btn-square bg-slate-600 text-white">
          <GearFillIcon size={17} />
        </Menu.Button>
      </div>

      <SmoothTransition>
        <Menu.Items className="origin-top-right z-50 absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none">
          <div className="px-4 py-3">
            <p className="text-sm text-slate-400">Signed in as</p>
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.email}
            </p>
          </div>
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <a
                  href="/account"
                  className={classNames(
                    active ? "bg-gray-100 text-gray-900" : "text-gray-700",
                    "block px-4 py-2 text-sm"
                  )}
                >
                  Account Settings
                </a>
              )}
            </Menu.Item>
            {isGeofencerPage && (
              <Menu.Item>
                {({ active }) => (
                  <button
                    className={classNames(
                      active ? "bg-gray-100 text-gray-900" : "text-gray-700",
                      "block px-4 py-2 text-sm w-full text-left"
                    )}
                    onClick={() => {
                      openModal(UIModalEnum.SupportModal);
                    }}
                  >
                    Support
                  </button>
                )}
              </Menu.Item>
            )}
            <Menu.Item>
              {({ active }) => (
                <a
                  href="/terms"
                  className={classNames(
                    active ? "bg-gray-100 text-gray-900" : "text-gray-700",
                    "block px-4 py-2 text-sm"
                  )}
                >
                  Terms of Service
                </a>
              )}
            </Menu.Item>
            <Menu.Item>
              {({ active }) => (
                <a
                  href="/privacy"
                  className={classNames(
                    active ? "bg-gray-100 text-gray-900" : "text-gray-700",
                    "block px-4 py-2 text-sm"
                  )}
                >
                  Privacy Policy
                </a>
              )}
            </Menu.Item>
          </div>
          <div className="py-1">
            <form method="POST" action="#">
              <Menu.Item>
                {({ active }) => (
                  <button
                    type="submit"
                    onClick={() => {
                      nav("/logout");
                    }}
                    className={classNames(
                      active ? "bg-gray-100 text-gray-900" : "text-gray-700",
                      "block w-full text-left px-4 py-2 text-sm"
                    )}
                  >
                    Sign out
                  </button>
                )}
              </Menu.Item>
            </form>
          </div>
        </Menu.Items>
      </SmoothTransition>
    </Menu>
  );
}
