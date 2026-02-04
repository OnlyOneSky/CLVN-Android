/**
 * Expo Config Plugin — enables cleartext HTTP traffic for Android.
 *
 * This adds a network_security_config.xml that allows cleartext to all hosts
 * and references it from the AndroidManifest.xml. Required for release builds
 * that need to reach WireMock over HTTP during testing.
 */
const { withAndroidManifest, withDangerousMod } = require("expo/config-plugins");
const fs = require("fs");
const path = require("path");

const NETWORK_SECURITY_CONFIG = `<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>`;

function withNetworkSecurityConfig(config) {
  // Step 1: Write network_security_config.xml
  config = withDangerousMod(config, [
    "android",
    async (cfg) => {
      const resDir = path.join(
        cfg.modRequest.platformProjectRoot,
        "app",
        "src",
        "main",
        "res",
        "xml"
      );
      fs.mkdirSync(resDir, { recursive: true });
      fs.writeFileSync(
        path.join(resDir, "network_security_config.xml"),
        NETWORK_SECURITY_CONFIG
      );
      return cfg;
    },
  ]);

  // Step 2: Reference it in AndroidManifest.xml
  config = withAndroidManifest(config, (cfg) => {
    const app = cfg.modResults.manifest.application?.[0];
    if (app) {
      app.$["android:networkSecurityConfig"] =
        "@xml/network_security_config";
      app.$["android:usesCleartextTraffic"] = "true";
    }
    return cfg;
  });

  return config;
}

module.exports = withNetworkSecurityConfig;
