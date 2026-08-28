import { useEffect, useState } from "react";
import { getOperationalData } from "../services/operationalService";

export function useOperationalData(flightNumber) {
  const [data, setData] = useState(() => (flightNumber ? getOperationalData(flightNumber) : null));

  useEffect(() => {
    const updateData = () => {
      setData(flightNumber ? getOperationalData(flightNumber) : null);
    };

    const interval = setInterval(updateData, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, [flightNumber]);

  return flightNumber ? (data || getOperationalData(flightNumber)) : null;
}
