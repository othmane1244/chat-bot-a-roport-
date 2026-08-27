import { APP_CONFIG } from "../config/appConfig";
import { simulatedOperationalData } from "../data/simulatedOperationalData";

export function getOperationalData(flightNumber) {
  if (!APP_CONFIG.DEMO_MODE || !flightNumber) {
    return null;
  }

  const cleanNumber = String(flightNumber).toUpperCase().replace(/\s+/g, "");
  return simulatedOperationalData[cleanNumber] || null;
}
