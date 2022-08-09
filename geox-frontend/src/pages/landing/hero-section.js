import { EmailBox } from "./email-box";
import ycLogo from "./yc-logo.png";

import { Globe } from "./globe";
import { useEffect, useRef } from "react";

export const HeroSection = () => {
  const ref = useRef(null);

  useEffect(() => {
    if (ref) {
      ref.current.focus();
    }
  }, []);

  return (
    <section ref={ref} className="m-1">
      <div className="grid max-w-5xl md:grid-cols-2 gap-20 mx-auto px-4 text-white">
        <div className="h-fit-content">
          <div className="relative max-w-none xl:max-w-md">
            <div className="font-heading mb-5 text-4xl font-extrabold leading-none lg:leading-tight xl:text-5xl">
              <div>
                <span className="text-white">Manage your logistics</span>
              </div>
            </div>
            <p className="text-base lg:text-lg xl:text-xl text-white-200 mb-9 leading-snug">
              Empower your operations team with fleet management tools inspired
              by the best practices from companies like Uber and Instacart.
            </p>
            <EmailBox />
            <div className="">
              <div className="py-5 flex flex-row gap-x-10">
                <div className="text-xs font-bold">
                  <p className="py-2">Backed by</p>
                  <a
                    href="https://www.ycombinator.com/"
                    target="_blank"
                    rel="noreferrer"
                    className="select-none cursor-default"
                    style={{
                      display: "inline-block",
                      width: "60px",
                      height: "60px",
                    }}
                  >
                    <img
                      src={ycLogo}
                      title={`Y Combinator`}
                      className="h-[60px] w-[60px] cursor-pointer"
                      alt="Y Combinator"
                    ></img>
                  </a>
                </div>
                <div className="text-xs font-bold ">
                  <p className="py-2">With experience from</p>
                  <div className="flex flex-row gap-x-3">
                    <div className="flex flex-col items-center">
                      <img
                        src={
                          "https://xmwdyaolhaobykjycchu.supabase.co/storage/v1/object/public/landing-page/uber-square.jpeg?t=2022-08-08T22%3A15%3A58.737Z"
                        }
                        className="h-[60px] w-[60px]"
                        title={`Uber`}
                        style={{
                          filter: "grayscale(100%)",
                        }}
                        alt="Uber"
                      ></img>
                    </div>
                    <div className="flex flex-col items-center">
                      <img
                        src={
                          "https://xmwdyaolhaobykjycchu.supabase.co/storage/v1/object/public/landing-page/Berkeley-logo.jpeg?t=2022-08-08T22%3A15%3A22.718Z"
                        }
                        className="h-[60px] w-[90px]"
                        alt="University of California, Berkeley"
                        title={`University of California, Berkeley`}
                      ></img>
                    </div>
                    <div className="flex flex-col items-center text-gray-300">
                      <img
                        src={
                          "https://xmwdyaolhaobykjycchu.supabase.co/storage/v1/object/public/landing-page/instacart-square.png?t=2022-08-08T22%3A15%3A40.046Z"
                        }
                        className="h-[60px] w-[60px]"
                        alt="Instacart"
                        title={`Instacart`}
                      ></img>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="relative hidden sm:block h-[90%]">
          <Globe />
        </div>
      </div>
    </section>
  );
};
