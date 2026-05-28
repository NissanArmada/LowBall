import { SymbolView } from 'expo-symbols';
import { Link, Tabs } from 'expo-router';
import { Platform, Pressable } from 'react-native';

import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import { useClientOnlyValue } from '@/components/useClientOnlyValue';

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme].tint,
        headerShown: useClientOnlyValue(false, true),
        }}>
        <Tabs.Screen
        name="index"
        options={{
        title: 'Home',
        tabBarIcon: ({ color }) => (
          <SymbolView
            name={{
              ios: 'house.fill',
              android: 'home',
              web: 'home',
            }}
            tintColor={color}
            size={28}
          />
        ),
        }}
        />
        <Tabs.Screen        name="scanner"
        options={{
          title: 'Scanner',
          tabBarIcon: ({ color }) => (
            <SymbolView
              name={{
                ios: 'barcode.viewfinder',
                android: 'qr_code_scanner',
                web: 'qr_code_scanner',
              }}
              tintColor={color}
              size={28}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Chat',
          tabBarIcon: ({ color }) => (
            <SymbolView
              name={{
                ios: 'bubble.left.and.bubble.right.fill',
                android: 'chat',
                web: 'chat',
              }}
              tintColor={color}
              size={28}
            />
          ),
        }}
      />
    </Tabs>
  );
}
