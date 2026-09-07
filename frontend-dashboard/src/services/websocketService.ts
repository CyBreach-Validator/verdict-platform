class VerdictWebSocket {
  private socket: WebSocket | null = null;

  connect(
    onMessage: (data: any) => void,
    onOpen?: () => void,
    onClose?: () => void
  ) {

    this.socket = new WebSocket("ws://127.0.0.1:8000/ws/verdicts");
    this.socket.onopen = () => {

      console.log("✅ Connected to Verdict WebSocket");

      this.socket?.send("Hello Server");

      onOpen?.();

    };

    this.socket.onmessage = (event) => {

      const data = JSON.parse(event.data);

      console.log("Received:", data);

      onMessage(data);

    };

    this.socket.onerror = (event) => {
      console.error("WebSocket Error", event);
    };

    this.socket.onclose = () => {

      console.log("❌ WebSocket Closed");

      onClose?.();

    };
  }

  disconnect() {
    this.socket?.close();
  }
}

export default new VerdictWebSocket();