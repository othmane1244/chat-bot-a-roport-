import { useEffect, useState } from "react";
import { getOperationalData } from "../services/operationalService";

export function useOperationalData(flightNumber) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!flightNumber) {
      setData(null);
      return;
    }

    const updateData = () => {
      const operationalData = getOperationalData(flightNumber);
      setData(operationalData);
    };

    updateData();

    const interval = setInterval(
      updateData,
      30 * 60 * 1000
    );

    return () => clearInterval(interval);
  }, [flightNumber]);

  return data;
}
