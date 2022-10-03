import { datadogRum } from '@datadog/browser-rum';

/**
 * Configuration for Datadog RUM
 * @see https://app.datadoghq.com/rum/list
 */
export interface DatadogRUMConfig {
  /**
   * Environment we're running in
   *
   * @example production
   */
  environment: string;
  /**
   * SHA of git commit that's currently running.
   * We use gitSha inside of Datadog RUM as the `version` field.
   */
  gitSha: string;
}

/**
 * Start running Datadog RUM
 * @see https://app.datadoghq.com/rum/list
 *
 * @param config @see {@link DatadogRUMConfig}
 */
export function startDatadogRUM(config: DatadogRUMConfig): void {
  /**
   * Only run Datadog RUM in production
   */
  if (config.environment !== 'production') {
    return;
  }

  /**
   * @TODO Move all these to env variables
   */
  datadogRum.init({
    applicationId: 'ce6f2047-3a48-4c2c-9999-de08116763f8',
    clientToken: 'pub6873a27f34bce710d17e450941f1af29',
    site: 'datadoghq.com',
    service: 'geofencer',
    env: config.environment,
    // Specify a version number to identify the deployed version of your application in Datadog
    version: config.gitSha,
    sampleRate: 100,
    premiumSampleRate: 100,
    trackInteractions: true,
    defaultPrivacyLevel: 'mask-user-input'
  });

  datadogRum.startSessionReplayRecording();
}
