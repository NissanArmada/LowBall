import { useState, useEffect, useCallback, useRef } from 'react';
import { Platform } from 'react-native';
import { Config } from '../constants/Config';
import { Message, ChatResponse } from '../constants/Types';

/**
 * Custom hook to manage the real-time negotiation chat via WebSockets.
 */
export function useNegotiation(sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const connect = () => {
      setIsConnecting(true);
      setError(null);

      // 1. Build the authenticated URL (Required for Web)
      const url = `${Config.WS_BASE_URL}${Config.API_V1_STR}/chat/${sessionId}?token=${Config.API_TOKEN}`;
      
      let socket: WebSocket;

      if (Platform.OS === 'web') {
        // Standard Web browser connection
        socket = new WebSocket(url);
      } else {
        // Native React Native connection (Allows custom headers)
        // @ts-ignore - React Native WebSocket supports a third options argument
        socket = new WebSocket(url, null, {
          headers: { 'X-API-Token': Config.API_TOKEN }
        });
      }

      socketRef.current = socket;

      socket.onopen = () => {
        console.log('Successfully connected to Lowball.ai Engine');
        setIsConnecting(false);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.error) {
            setError(data.error);
            // If it's an auth error, we know exactly what happened
            if (data.error === 'Unauthorized') {
              console.error('CRITICAL: Authentication failed. Check your API tokens.');
            }
            return;
          }

          const chatRes: ChatResponse = data;
          setLastResponse(chatRes);
          
          if (chatRes.synthesis && chatRes.synthesis.final_response) {
            setMessages((prev) => {
              // Prevent duplicate messages if the backend pushes a status update
              const lastMsg = prev.length > 0 ? prev[prev.length - 1] : null;
              if (lastMsg && lastMsg.role === 'ai' && lastMsg.content === chatRes.synthesis.final_response) {
                return prev;
              }
              
              const aiMessage: Message = {
                role: 'ai',
                content: chatRes.synthesis.final_response,
                timestamp: new Date().toISOString(),
              };
              return [...prev, aiMessage];
            });
          }
        } catch (err) {
          console.error('Failed to parse message:', err);
        }
      };

      socket.onerror = (e) => {
        setError('Connection error. Is the backend running?');
        setIsConnecting(false);
      };

      socket.onclose = (e) => {
        console.log(`Connection closed (Code: ${e.code})`);
        setIsConnecting(false);
      };
    };

    connect();

    return () => {
      socketRef.current?.close();
    };
  }, [sessionId]);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current?.readyState !== WebSocket.OPEN) {
      setError('Not connected to server.');
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    socketRef.current.send(JSON.stringify({ user_message: content }));
  }, []);

  return {
    messages,
    sendMessage,
    isConnecting,
    error,
    lastResponse,
  };
}
