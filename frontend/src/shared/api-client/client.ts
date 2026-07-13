import createClient from "openapi-fetch";
import type { paths } from "./schema";

// Typed API client. Path keys already carry the /api/v1 prefix, so baseUrl is
// empty in dev (Vite proxies /api to the backend — see vite.config.ts).
export const api = createClient<paths>({ baseUrl: "" });
