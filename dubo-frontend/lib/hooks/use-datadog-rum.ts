import { datadogRum } from "@datadog/browser-rum";
import { useEffect } from "react";

const useDatadogRum = () => {
  useEffect(() => {
    const environment = process.env.NEXT_PUBLIC_VERCEL_ENV || "development";
    const isProduction = environment === "production";
    const applicationId = process.env.NEXT_PUBLIC_DATADOG_APP_ID;
    const clientToken = process.env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN;

    if (isProduction && applicationId && clientToken) {
      datadogRum.init({
        applicationId,
        clientToken,
        site: "datadoghq.com",
        service: "dubo",
        version:
          process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA || "local-development",
        sessionSampleRate: 100,
        sessionReplaySampleRate: 20,
        trackUserInteractions: true,
        trackResources: true,
        trackLongTasks: true,
        defaultPrivacyLevel: "mask-user-input",
      });

      datadogRum.startSessionReplayRecording();
    }
  }, []);
};

export default useDatadogRum;
