export const DEMO_MODE = true;

export const simulatedOperationalData = {
  AT5432: {
    flightNumber: "AT5432",
    airline: "Royal Air Maroc",
    origin: "Paris ORY",
    destination: "Agadir AGA",
    scheduledDeparture: "14:20",
    status: "Boarding",
    date: "25 May 2025",
    gate: "B12",
    terminal: "1",
    boardingZone: "B",
    source: "simulation",
  },

  AT7012: {
    flightNumber: "AT7012",
    airline: "Royal Air Maroc",
    origin: "Casablanca CMN",
    destination: "Agadir AGA",
    scheduledDeparture: "15:35",
    status: "On Time",
    date: "25 May 2025",
    gate: "A04",
    terminal: "1",
    boardingZone: "A",
    source: "simulation",
  },

  AT5433: {
    flightNumber: "AT5433",
    airline: "Royal Air Maroc",
    origin: "Agadir AGA",
    destination: "Paris ORY",
    scheduledDeparture: "16:45",
    status: "On Time",
    date: "25 May 2025",
    gate: "C08",
    terminal: "1",
    boardingZone: "C",
    source: "simulation",
  },

  FR6387: {
    flightNumber: "FR6387",
    airline: "Ryanair",
    origin: "Marseille MRS",
    destination: "Agadir AGA",
    scheduledDeparture: "15:10",
    status: "Delayed 15:40",
    date: "25 May 2025",
    gate: "A02",
    terminal: "1",
    boardingZone: "A",
    source: "simulation",
  },
};

export function getOperationalData(flightNumber) {
  if (!DEMO_MODE) return null;

  return (
    simulatedOperationalData[flightNumber?.toUpperCase()?.replace(/\s+/g, "")] || null
  );
}
