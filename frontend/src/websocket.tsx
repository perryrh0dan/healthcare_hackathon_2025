type WebSocketMessagePayload = {
  message: string;
};

interface WebSocketResponse {
  history: Array<{
    role: string;
    content: string;
    steps?: number;
    id?: string;
    name?: string;
  }>;
  conversation_id: string;
  error?: string;
  type?: string;
  step?: number;
  description?: string;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private onMessageCallback?: (data: WebSocketResponse) => void;
  private onStepCallback?: (step: {step: number; description: string}) => void;
  private onErrorCallback?: (error: string) => void;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000; // ms
  private intentionalDisconnect = false;

  constructor(url: string) {
    this.url = url;
  }

  connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
      this.intentionalDisconnect = false;
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WebSocketResponse = JSON.parse(event.data);
        if (data.type === "step" && this.onStepCallback) {
          this.onStepCallback({step: data.step || 0, description: data.description || ""});
        } else if (this.onMessageCallback) {
          this.onMessageCallback(data);
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
        if (this.onErrorCallback) {
          this.onErrorCallback("Invalid message format");
        }
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (this.onErrorCallback) {
        this.onErrorCallback("WebSocket connection error");
      }
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      if (!this.intentionalDisconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, this.reconnectInterval);
      }
    };
  }

  sendMessage(payload: WebSocketMessagePayload): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    } else {
      console.warn("WebSocket not connected, message not sent");
      if (this.onErrorCallback) {
        this.onErrorCallback("WebSocket not connected");
      }
    }
  }

  onMessage(callback: (data: WebSocketResponse) => void): void {
    this.onMessageCallback = callback;
  }

  onStep(callback: (step: {step: number; description: string}) => void): void {
    this.onStepCallback = callback;
  }

  onError(callback: (error: string) => void): void {
    this.onErrorCallback = callback;
  }

  disconnect(): void {
    this.intentionalDisconnect = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const createWebSocketClient = (url: string): WebSocketClient => {
  return new WebSocketClient(url);
};
