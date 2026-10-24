const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Charger = {
  id: number; title: string; description: string; address: string; lat: number; lng: number;
  connector: string; power_kw: number; price_per_hour: number;
  avg_rating: number | null; distance_km: number | null;
};
export type Booking = {
  id: number; charger_id: number; start_time: string; end_time: string; total_price: number; status: string;
};

export const getToken = () => localStorage.getItem("token");
export const setToken = (t: string | null) => (t ? localStorage.setItem("token", t) : localStorage.removeItem("token"));

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
  const t = getToken();
  if (t) headers.Authorization = `Bearer ${t}`;
  const r = await fetch(BASE + path, { ...init, headers });
  if (!r.ok) {
    const d = (await r.json().catch(() => ({}))).detail;
    throw new Error(typeof d === "string" ? d : r.statusText);
  }
  return r.status === 204 ? (undefined as T) : r.json();
}
const json = (method: string, body: unknown): RequestInit => ({
  method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
});

export const api = {
  register: (b: { email: string; name: string; password: string; role: string }) => req("/auth/register", json("POST", b)),
  login: async (email: string, password: string) => {
    const r = await req<{ access_token: string }>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    });
    setToken(r.access_token);
  },
  me: () => req<{ id: number; name: string; role: "host" | "guest" }>("/auth/me"),
  search: (p: Record<string, string>) => req<Charger[]>("/chargers?" + new URLSearchParams(p)),
  createCharger: (b: unknown) => req<Charger>("/chargers", json("POST", b)),
  book: (b: { charger_id: number; start_time: string; end_time: string }) => req<Booking>("/bookings", json("POST", b)),
  myBookings: () => req<Booking[]>("/bookings/me"),
  cancel: (id: number) => req<Booking>(`/bookings/${id}/cancel`, { method: "POST" }),
};
