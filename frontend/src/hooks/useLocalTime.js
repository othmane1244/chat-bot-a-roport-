import { useEffect, useState } from "react";

export function useLocalTime() {
  const getTime = () =>
    new Date().toLocaleTimeString("en-GB", {
      timeZone: "Africa/Casablanca",
      hour: "2-digit",
      minute: "2-digit",
    });

  const [time, setTime] = useState(getTime());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(getTime());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return time;
}
