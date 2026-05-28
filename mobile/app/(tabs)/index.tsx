import React from 'react';
import { StyleSheet, TouchableOpacity, ScrollView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { SymbolView } from 'expo-symbols';

import { Text, View } from '@/components/Themed';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function HomeScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme() ?? 'light';

  return (
    <ScrollView style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.greeting}>Lowball.ai</Text>
          <TouchableOpacity style={styles.profileButton}>
            <SymbolView name="person.circle.fill" size={32} tintColor={Colors[colorScheme].tint} />
          </TouchableOpacity>
        </View>
        <Text style={styles.headline}>Negotiate smarter, not harder.</Text>
      </View>

      <View style={styles.actionCard}>
        <View style={styles.actionIconContainer}>
          <SymbolView name="camera.viewfinder" size={40} tintColor="white" />
        </View>
        <View style={styles.actionTextContainer}>
          <Text style={styles.actionTitle}>New Negotiation</Text>
          <Text style={styles.actionSubtitle}>Scan a listing to start saving money.</Text>
        </View>
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => router.push('/scanner')}
        >
          <SymbolView name="plus" size={20} tintColor="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>How it works</Text>
        <View style={styles.stepsContainer}>
          <Step 
            number="1" 
            title="Upload" 
            desc="Take a screenshot of any Marketplace or OfferUp listing." 
            icon="photo.fill"
          />
          <Step 
            number="2" 
            title="Analyze" 
            desc="Our Vision Agent extracts the details and researches market prices." 
            icon="magnifyingglass"
          />
          <Step 
            number="3" 
            title="Negotiate" 
            desc="The Council-of-Thought generates the perfect lowball strategy." 
            icon="bubble.left.and.bubble.right.fill"
          />
        </View>
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Scans</Text>
          <TouchableOpacity>
            <Text style={[styles.seeAll, { color: Colors[colorScheme].tint }]}>See All</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.recentList}>
          <RecentItem 
            title="Gaming PC" 
            price="$650" 
            status="Researched" 
            date="Today"
            colorScheme={colorScheme}
          />
          <RecentItem 
            title="Mountain Bike" 
            price="$1,200" 
            status="In Progress" 
            date="Yesterday"
            colorScheme={colorScheme}
          />
        </View>
      </View>
    </ScrollView>
  );
}

function Step({ number, title, desc, icon }: { number: string, title: string, desc: string, icon: any }) {
  const colorScheme = useColorScheme() ?? 'light';
  return (
    <View style={styles.stepCard}>
      <View style={[styles.stepNumber, { backgroundColor: Colors[colorScheme].tint }]}>
        <SymbolView name={icon} size={16} tintColor="white" />
      </View>
      <View style={styles.stepContent}>
        <Text style={styles.stepTitle}>{title}</Text>
        <Text style={styles.stepDesc}>{desc}</Text>
      </View>
    </View>
  );
}

function RecentItem({ title, price, status, date, colorScheme }: { title: string, price: string, status: string, date: string, colorScheme: 'light' | 'dark' }) {
  return (
    <View style={[styles.recentItem, { backgroundColor: Colors[colorScheme].card }]}>
      <View style={styles.recentIcon}>
        <SymbolView name="doc.text.fill" size={20} tintColor={Colors[colorScheme].tint} />
      </View>
      <View style={styles.recentInfo}>
        <Text style={styles.recentTitle}>{title}</Text>
        <Text style={styles.recentDate}>{date} • {price}</Text>
      </View>
      <View style={[styles.statusBadge, { backgroundColor: status === 'Researched' ? 'rgba(52, 199, 89, 0.1)' : 'rgba(255, 149, 0, 0.1)' }]}>
        <Text style={[styles.statusText, { color: status === 'Researched' ? '#34C759' : '#FF9500' }]}>{status}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 24,
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    backgroundColor: 'transparent',
  },
  greeting: {
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: -0.5,
  },
  headline: {
    fontSize: 32,
    fontWeight: 'bold',
    lineHeight: 38,
    marginTop: 8,
  },
  profileButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionCard: {
    margin: 24,
    marginTop: 0,
    padding: 20,
    backgroundColor: '#1C1C1E',
    borderRadius: 24,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    elevation: 10,
  },
  actionIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionTextContainer: {
    flex: 1,
    marginLeft: 16,
    backgroundColor: 'transparent',
  },
  actionTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  actionSubtitle: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 14,
    marginTop: 4,
  },
  actionButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    paddingHorizontal: 24,
    marginBottom: 32,
    backgroundColor: 'transparent',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    backgroundColor: 'transparent',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
  },
  seeAll: {
    fontSize: 15,
    fontWeight: '600',
  },
  stepsContainer: {
    gap: 12,
    marginTop: 12,
    backgroundColor: 'transparent',
  },
  stepCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: 'transparent',
  },
  stepNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 2,
  },
  stepContent: {
    flex: 1,
    marginLeft: 16,
    backgroundColor: 'transparent',
  },
  stepTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  stepDesc: {
    fontSize: 14,
    opacity: 0.6,
    lineHeight: 20,
    marginTop: 2,
  },
  recentList: {
    gap: 12,
    backgroundColor: 'transparent',
  },
  recentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  recentIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(0,122,255,0.05)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  recentInfo: {
    flex: 1,
    marginLeft: 12,
    backgroundColor: 'transparent',
  },
  recentTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  recentDate: {
    fontSize: 13,
    opacity: 0.5,
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
});
