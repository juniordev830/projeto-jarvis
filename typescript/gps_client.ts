export type Position = {
  latitude: number;
  longitude: number;
  timestamp: string;
};

export type GpsEvent = {
  type: "entered" | "exited";
  geofence: string;
  position: Position;
};

/** Cliente mínimo para enviar eventos do núcleo GPS a uma API futura. */
export async function sendGpsEvent(endpoint: string, event: GpsEvent): Promise<void> {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(event),
  });

  if (!response.ok) {
    throw new Error(`Falha ao enviar evento GPS: HTTP ${response.status}`);
  }
}
