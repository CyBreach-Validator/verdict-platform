import { WS_URL } from "./api";

class VerdictWebSocket {
  private socket: WebSocket | null = null;

  connect(
    onMessage: (data: any) => void,
    onOpen?: () => void,
    onClose?: () => void
  ) {
    // B11: the verdict feed is authenticated. The browser `WebSocket`
    // constructor cannot set an `Authorization` header, so the token is passed
    // as a query parameter, which is what the backend's `/ws/verdicts` verifies
    // before accepting the connection.
    //
    // Without this the server now closes the socket with code 1008 and the
    // dashboard receives no verdicts at all.
    const token = localStorage.getItem("access_token");

    if (!token) {
      console.error("No access token; not opening the verdict WebSocket.");
      onClose?.();
      return;
    }

    const url = `${WS_URL}?token=${encodeURIComponent(token)}`;

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      onOpen?.();
    };

    this.socket.onmessage = (event) => {
      onMessage(JSON.parse(event.data));
    };

    this.socket.onerror = (event) => {
      console.error("WebSocket Error", event);
    };

    this.socket.onclose = (event) => {
      // 1008 is the server's "policy violation" close: the token was missing,
      // expired or forged.
      if (event.code === 1008) {
        console.error(
          "Verdict WebSocket rejected by the server (unauthenticated)."
        );
      }
      onClose?.();
    };
  }

  disconnect() {
    this.socket?.close();
  }
}

export default new VerdictWebSocket();
