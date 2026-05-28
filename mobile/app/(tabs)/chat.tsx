import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, TextInput, FlatList, TouchableOpacity, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';

import { Text, View } from '@/components/Themed';
import { useNegotiation } from '@/hooks/useNegotiation';
import { Message } from '@/constants/Types';
import { SymbolView } from 'expo-symbols';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function ChatScreen() {
  const { sessionId, itemName, askingPrice } = useLocalSearchParams<{ 
    sessionId: string; 
    itemName: string; 
    askingPrice: string;
  }>();
  
  const [inputText, setInputText] = useState('');
  const { messages, sendMessage, isConnecting, error, lastResponse } = useNegotiation(sessionId);
  const colorScheme = useColorScheme() ?? 'light';
  const flatListRef = useRef<FlatList>(null);
  const router = useRouter();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const handleSend = () => {
    if (inputText.trim()) {
      sendMessage(inputText.trim());
      setInputText('');
    }
  };

  const renderMessage = ({ item }: { item: Message }) => {
    const isAi = item.role === 'ai';
    return (
      <View style={[
        styles.messageBubble,
        isAi ? styles.aiBubble : styles.userBubble,
        { shadowColor: '#000' }
      ]}>
        <Text style={[
          styles.messageText,
          isAi ? styles.aiText : styles.userText
        ]}>
          {item.content}
        </Text>
        <Text style={[styles.timestamp, isAi ? styles.aiTimestamp : styles.userTimestamp]}>
          {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    );
  };

  if (!sessionId) {
    return (
      <View style={[styles.emptyContainer, { backgroundColor: Colors[colorScheme].background }]}>
        <View style={styles.emptyIconCircle}>
          <SymbolView name="bubble.left.and.bubble.right.fill" size={40} tintColor={Colors[colorScheme].tint} />
        </View>
        <Text style={styles.emptyText}>No Active Negotiation</Text>
        <Text style={styles.emptySubtext}>Start by scanning a marketplace listing to begin your deal.</Text>
        <TouchableOpacity 
          style={[styles.emptyButton, { backgroundColor: Colors[colorScheme].tint }]}
          onPress={() => router.push('/scanner')}
        >
          <Text style={styles.emptyButtonText}>Go to Scanner</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView 
      style={[styles.container, { backgroundColor: Colors[colorScheme].background }]} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <View style={[styles.chatHeader, { borderBottomColor: Colors[colorScheme].border }]}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerBack}>
          <SymbolView name="chevron.left" size={20} tintColor={Colors[colorScheme].text} />
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle} numberOfLines={1}>{itemName || 'Negotiation'}</Text>
          {askingPrice && <Text style={[styles.headerSubtitle, { color: Colors[colorScheme].tint }]}>Asking: ${askingPrice}</Text>}
        </View>
        <TouchableOpacity style={styles.headerMenu}>
          <SymbolView name="ellipsis" size={20} tintColor={Colors[colorScheme].text} />
        </TouchableOpacity>
      </View>

      {error && (
        <View style={[styles.errorBanner, { backgroundColor: Colors[colorScheme].error }]}>
          <SymbolView name="exclamationmark.triangle.fill" size={14} tintColor="white" />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item, index) => index.toString()}
        contentContainerStyle={styles.messageList}
        ListFooterComponent={isConnecting ? <ActivityIndicator style={{ marginTop: 20 }} color={Colors[colorScheme].tint} /> : null}
      />

      <View style={styles.intelligenceDashboard}>
        {lastResponse?.analytical_data && (
          <View style={[
            styles.researchPanel,
            lastResponse.analytical_data.is_researched ? styles.researchComplete : styles.researchPending,
            { borderColor: lastResponse.analytical_data.is_researched ? 'rgba(52, 199, 89, 0.2)' : 'rgba(0,0,0,0.05)' }
          ]}>
            <View style={styles.dashboardHeader}>
              <SymbolView 
                name={lastResponse.analytical_data.is_researched ? "checkmark.seal.fill" : "arrow.triangle.2.circlepath.circle.fill"} 
                size={14} 
                tintColor={lastResponse.analytical_data.is_researched ? "#34C759" : "#8E8E93"} 
              />
              <Text style={[styles.dashboardTitle, { color: lastResponse.analytical_data.is_researched ? "#34C759" : "#8E8E93" }]}>
                {lastResponse.analytical_data.is_researched ? "Market Data Synced" : "Market Research In Progress..."}
              </Text>
            </View>
            {lastResponse.analytical_data.is_researched && (
              <View style={styles.dataGrid}>
                <DataItem label="Avg Market" value={`$${lastResponse.analytical_data.calculated_fair_market_avg}`} />
                <DataItem label="Walk-away" value={`$${lastResponse.analytical_data.recommended_walk_away_price}`} />
                <DataItem label="Volatility" value={`${Math.round(lastResponse.analytical_data.price_volatility * 100)}%`} />
              </View>
            )}
          </View>
        )}

        {lastResponse?.synthesis && (
          <View style={[styles.thoughtPanel, { backgroundColor: Colors[colorScheme].card }]}>
            <View style={styles.dashboardHeader}>
               <SymbolView name="brain.fill" size={14} tintColor={Colors[colorScheme].tint} />
               <Text style={[styles.dashboardTitle, { color: Colors[colorScheme].text }]}>Council Rationale</Text>
            </View>
            <Text style={styles.thoughtText}>
              {lastResponse.synthesis.rationale}
            </Text>
          </View>
        )}
      </View>

      <View style={[styles.inputWrapper, { backgroundColor: Colors[colorScheme].card, borderTopColor: Colors[colorScheme].border }]}>
        <View style={styles.inputContainer}>
          <TextInput
            style={[styles.input, { color: Colors[colorScheme].text }]}
            placeholder={messages.length === 0 ? "Analyzing..." : "Type your message..."}
            placeholderTextColor="rgba(0,0,0,0.3)"
            value={inputText}
            onChangeText={setInputText}
            multiline
            editable={messages.length > 0}
          />
          <TouchableOpacity 
            style={[
              styles.sendButton,
              { backgroundColor: Colors[colorScheme].tint },
              (!inputText.trim() || messages.length === 0) && styles.sendButtonDisabled
            ]} 
            onPress={handleSend}
            disabled={!inputText.trim() || messages.length === 0}
          >
            <SymbolView name="arrow.up" size={18} tintColor="white" />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

function DataItem({ label, value }: { label: string, value: string }) {
  return (
    <View style={styles.dataItem}>
      <Text style={styles.dataLabel}>{label}</Text>
      <Text style={styles.dataValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    borderBottomWidth: 1,
    backgroundColor: 'transparent',
  },
  headerBack: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.03)',
  },
  headerInfo: {
    flex: 1,
    marginLeft: 12,
    backgroundColor: 'transparent',
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: '700',
  },
  headerSubtitle: {
    fontSize: 13,
    fontWeight: '600',
    marginTop: 2,
  },
  headerMenu: {
    width: 36,
    height: 36,
    justifyContent: 'center',
    alignItems: 'center',
  },
  messageList: {
    padding: 16,
    paddingBottom: 24,
  },
  messageBubble: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    marginBottom: 12,
    maxWidth: '80%',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#E9E9EB',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: 'white',
  },
  aiText: {
    color: '#1C1C1E',
  },
  timestamp: {
    fontSize: 10,
    marginTop: 4,
    opacity: 0.5,
  },
  userTimestamp: {
    textAlign: 'right',
    color: 'rgba(255,255,255,0.7)',
  },
  aiTimestamp: {
    textAlign: 'left',
    color: 'rgba(0,0,0,0.5)',
  },
  intelligenceDashboard: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    gap: 8,
    backgroundColor: 'transparent',
  },
  researchPanel: {
    padding: 12,
    borderRadius: 16,
    borderWidth: 1,
  },
  researchComplete: {
    backgroundColor: 'rgba(52, 199, 89, 0.05)',
  },
  researchPending: {
    backgroundColor: 'rgba(0,0,0,0.02)',
  },
  dashboardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
    backgroundColor: 'transparent',
  },
  dashboardTitle: {
    fontSize: 11,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  dataGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: 'transparent',
  },
  dataItem: {
    backgroundColor: 'transparent',
  },
  dataLabel: {
    fontSize: 10,
    opacity: 0.5,
    marginBottom: 2,
  },
  dataValue: {
    fontSize: 14,
    fontWeight: '700',
  },
  thoughtPanel: {
    padding: 12,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 5,
    elevation: 2,
  },
  thoughtText: {
    fontSize: 13,
    lineHeight: 18,
    opacity: 0.7,
    fontStyle: 'italic',
  },
  inputWrapper: {
    padding: 12,
    paddingBottom: Platform.OS === 'ios' ? 34 : 12,
    borderTopWidth: 1,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.05)',
    borderRadius: 24,
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 8,
  },
  input: {
    flex: 1,
    fontSize: 16,
    maxHeight: 100,
    paddingTop: 8,
    paddingBottom: 8,
  },
  sendButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.3,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyIconCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(0,122,255,0.05)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  emptyText: {
    fontSize: 22,
    fontWeight: '800',
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 16,
    opacity: 0.5,
    textAlign: 'center',
    marginTop: 12,
    lineHeight: 22,
  },
  emptyButton: {
    marginTop: 32,
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 24,
  },
  emptyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '700',
  },
  errorBanner: {
    flexDirection: 'row',
    padding: 10,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  errorText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
});
