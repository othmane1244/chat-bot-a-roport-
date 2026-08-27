export const AVIONIO_CONFIG = {
  iframeUrl: import.meta.env.VITE_AVIONIO_IFRAME_URL || "https://www.avionio.com/en/aga/departures",

  enabled: Boolean(
    import.meta.env.VITE_AVIONIO_IFRAME_URL || true
  ),
};
