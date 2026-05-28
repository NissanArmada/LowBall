import { Platform } from 'react-native';

/**
 * Lowball.ai Mobile Configuration
 */
export const Config = {
  // Use your machine's local IP address for physical device testing
  // Android Emulator uses 10.0.2.2, iOS Simulator uses localhost
  API_BASE_URL: Platform.select({
    android: 'http://10.0.2.2:8000',
    ios: 'http://localhost:8000',
    default: 'http://localhost:8000',
  }),

  WS_BASE_URL: Platform.select({
    android: 'ws://10.0.2.2:8000',
    ios: 'ws://localhost:8000',
    default: 'ws://localhost:8000',
  }),

  // This is injected from mobile/.env via EXPO_PUBLIC_ prefix
  // It ensures your secret stays out of your source code/Git
  API_TOKEN: process.env.EXPO_PUBLIC_API_TOKEN || '',
  
  API_V1_STR: '/api/v1',
};
