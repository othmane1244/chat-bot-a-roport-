/**
 * Layer de simulation des portes et terminaux opérationnels.
 * 
 * REMARQUE IMPORTANTE :
 * Ces données sont des données d'exploitation simulées localement.
 * Elles sont distinctes des informations de vols réelles de l'iframe Avionio
 * et servent à démontrer les capacités de réponse du terminal digital.
 */

// Portes attribuées dynamiquement aux vols connus
const INITIAL_SIMULATED_GATES = {
  'AT5432': { gate: 'B12', terminal: '1', zone: 'Embarquement B', status: 'Boarding', desk: 'Desk 14-16' },
  'AT7012': { gate: 'A04', terminal: '1', zone: 'Embarquement A', status: 'On Time', desk: 'Desk 02-05' },
  'RAM800': { gate: 'A02', terminal: '1', zone: 'Embarquement A', status: 'On Time', desk: 'Desk 01-03' },
  'TO3420': { gate: 'B15', terminal: '1', zone: 'Embarquement B', status: 'Delayed', desk: 'Desk 18-20' },
  'FR4512': { gate: 'B10', terminal: '1', zone: 'Embarquement B', status: 'On Time', desk: 'Desk 08-10' },
  'HV5671': { gate: 'A06', terminal: '1', zone: 'Embarquement A', status: 'Landed', desk: 'Fermé' },
  'EJU782': { gate: 'B14', terminal: '1', zone: 'Embarquement B', status: 'On Time', desk: 'Desk 11-13' },
};

let currentGatesStore = { ...INITIAL_SIMULATED_GATES };
let lastUpdatedTime = new Date();

/**
 * Génère des portes aléatoires réalistes pour des numéros de vols non répertoriés
 */
export function getSimulatedGate(flightNumber) {
  const normalized = (flightNumber || '').toUpperCase().trim().replace(/\s+/g, '');
  
  if (currentGatesStore[normalized]) {
    return {
      ...currentGatesStore[normalized],
      flightNumber: normalized,
      isSimulated: true,
      lastUpdate: lastUpdatedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
  }

  // Si le vol est inconnu, générer un mapping déterministe basé sur le hash du numéro
  const hash = Array.from(normalized).reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const gatePrefix = hash % 2 === 0 ? 'A' : 'B';
  const gateNumber = String((hash % 12) + 1).padStart(2, '0');
  const gate = `${gatePrefix}${gateNumber}`;

  return {
    flightNumber: normalized,
    gate: gate,
    terminal: '1',
    zone: `Embarquement ${gatePrefix}`,
    status: 'Scheduled',
    desk: `Desk ${String((hash % 20) + 1).padStart(2, '0')}`,
    isSimulated: true,
    lastUpdate: lastUpdatedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  };
}

/**
 * Mise à jour périodique de la simulation (toutes les 30 minutes)
 */
export function refreshSimulatedGates() {
  lastUpdatedTime = new Date();
  // Simuler de petites variations de statut de porte
  Object.keys(currentGatesStore).forEach((fn) => {
    currentGatesStore[fn] = {
      ...currentGatesStore[fn],
      lastUpdate: lastUpdatedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
  });
  return currentGatesStore;
}
