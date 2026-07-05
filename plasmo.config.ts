import { defineConfig } from "plasmo";

export default defineConfig({
  manifest: {
    host_permissions: [
      "https://*.sellercentral.amazon.com/*",
      "https://*.sellercentral.amazon.co.uk/*",
      "https://*.sellercentral.amazon.co.jp/*",
    ],
    permissions: ["storage"],
  },
});
