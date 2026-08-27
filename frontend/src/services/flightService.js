import { getSimulatedGate } from '../data/simulatedGates';

/**
 * Service d'information de vols.
 * Combine les informations de vol et les données d'exploitation d'embarquement (Porte, Terminal).
 */

export function extractFlightNumber(text) {
  const match = (text || '').match(/\b([A-Z0-9]{2,3}\s?\d{2,4})\b/i);
  return match ? match[1].replace(/\s+/g, '').toUpperCase() : null;
}

export function getFlightInfo(flightNumber) {
  const normalizedNumber = (flightNumber || '').toUpperCase().trim();
  const simulated = getSimulatedGate(normalizedNumber);

  // Mapping simple pour les compagnies connues
  let airline = 'Royal Air Maroc';
  let origin = 'Paris (CDG)';
  let destination = 'Agadir (AGA)';
  let time = '14:20';

  if (normalizedNumber.startsWith('TO')) {
    airline = 'Transavia';
    origin = 'Orly (ORY)';
    time = '16:45';
  } else if (normalizedNumber.startsWith('FR')) {
    airline = 'Ryanair';
    origin = 'Marseille (MRS)';
    time = '11:10';
  } else if (normalizedNumber.startsWith('HV')) {
    airline = 'Transavia Holland';
    origin = 'Amsterdam (AMS)';
    time = '09:30';
  } else if (normalizedNumber.startsWith('EJU')) {
    airline = 'easyJet Europe';
    origin = 'Lyon (LYS)';
    time = '18:15';
  }

  return {
    flightNumber: normalizedNumber,
    airline: airline,
    origin: origin,
    destination: destination,
    scheduledDeparture: time,
    status: simulated.status || 'Boarding',
    gate: simulated.gate,
    terminal: simulated.terminal,
    zone: simulated.zone,
    desk: simulated.desk,
    isSimulatedData: true,
  };
}
