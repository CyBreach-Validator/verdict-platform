import api from "./api";

export interface Connector {
  id: number;
  name: string;
  status: string;
  version: string | null;
  last_seen: string | null;
}

export const getConnectors = async (): Promise<Connector[]> => {
  const response = await api.get("/connectors");
  return response.data;
};