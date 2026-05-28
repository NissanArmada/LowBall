import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, Image, ActivityIndicator, Alert, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { SymbolView } from 'expo-symbols';

import { Text, View } from '@/components/Themed';
import { ApiService } from '@/services/api';
import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';

export default function ScannerScreen() {
  const [image, setImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const router = useRouter();
  const colorScheme = useColorScheme() ?? 'light';

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const handleAnalyze = async () => {
    if (!image) return;

    setIsAnalyzing(true);
    try {
      const metadata = await ApiService.analyzeListing(image);
      
      router.push({
        pathname: '/chat',
        params: { 
          sessionId: metadata.session_id,
          itemName: metadata.item_name,
          askingPrice: metadata.original_listing_price
        }
      });
    } catch (error: any) {
      Alert.alert('Analysis Failed', error.message);
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <SymbolView name="chevron.left" size={20} tintColor={Colors[colorScheme].text} />
        </TouchableOpacity>
        <Text style={styles.title}>New Scan</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.mainContent}>
        <View style={styles.instructionContainer}>
          <Text style={styles.instructionTitle}>Analyze Marketplace Listing</Text>
          <Text style={styles.instructionText}>
            Upload a screenshot from Facebook Marketplace or OfferUp. Our Vision Agent will extract the details.
          </Text>
        </View>

        <View style={styles.uploadContainer}>
          {image ? (
            <View style={[styles.previewWrapper, { shadowColor: '#000' }]}>
              <Image source={{ uri: image }} style={styles.previewImage} resizeMode="cover" />
              <TouchableOpacity 
                style={styles.changeButton} 
                onPress={pickImage}
                disabled={isAnalyzing}
              >
                <View style={styles.changeButtonInner}>
                  <SymbolView name="arrow.triangle.2.circlepath" size={16} tintColor="white" />
                  <Text style={styles.changeButtonText}>Change</Text>
                </View>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.clearButton} 
                onPress={() => setImage(null)}
                disabled={isAnalyzing}
              >
                <SymbolView name="xmark" size={14} tintColor="white" />
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity 
              style={[styles.dropzone, { borderColor: Colors[colorScheme].border }]} 
              onPress={pickImage}
            >
              <View style={[styles.iconCircle, { backgroundColor: 'rgba(0,122,255,0.1)' }]}>
                <SymbolView name="arrow.up.doc.fill" size={32} tintColor={Colors[colorScheme].tint} />
              </View>
              <Text style={styles.dropzoneTitle}>Tap to select screenshot</Text>
              <Text style={styles.dropzoneSubtitle}>PNG or JPG supported</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[
            styles.primaryButton, 
            (!image || isAnalyzing) && styles.buttonDisabled,
            { backgroundColor: Colors[colorScheme].tint }
          ]}
          onPress={handleAnalyze}
          disabled={!image || isAnalyzing}
        >
          {isAnalyzing ? (
            <View style={styles.analyzingState}>
              <ActivityIndicator color="white" />
              <Text style={styles.primaryButtonText}>AI is analyzing...</Text>
            </View>
          ) : (
            <View style={styles.buttonInner}>
              <Text style={styles.primaryButtonText}>Analyze and Negotiate</Text>
              <SymbolView name="sparkles" size={18} tintColor="white" />
            </View>
          )}
        </TouchableOpacity>
        <Text style={styles.disclaimer}>Powered by Gemini 1.5 Flash Vision</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 24,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    marginBottom: 24,
    backgroundColor: 'transparent',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.05)',
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
  },
  mainContent: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  instructionContainer: {
    marginBottom: 32,
    backgroundColor: 'transparent',
  },
  instructionTitle: {
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 8,
  },
  instructionText: {
    fontSize: 16,
    opacity: 0.6,
    lineHeight: 24,
  },
  uploadContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  dropzone: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: 32,
    borderWidth: 2,
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.01)',
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  dropzoneTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
  },
  dropzoneSubtitle: {
    fontSize: 14,
    opacity: 0.4,
  },
  previewWrapper: {
    width: '100%',
    aspectRatio: 0.8,
    borderRadius: 24,
    overflow: 'hidden',
    position: 'relative',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 5,
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  changeButton: {
    position: 'absolute',
    bottom: 16,
    alignSelf: 'center',
  },
  changeButtonInner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 8,
  },
  changeButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  clearButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  footer: {
    paddingBottom: Platform.OS === 'ios' ? 40 : 24,
    backgroundColor: 'transparent',
  },
  primaryButton: {
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonInner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: 'transparent',
  },
  analyzingState: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: 'transparent',
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  disclaimer: {
    textAlign: 'center',
    fontSize: 12,
    opacity: 0.3,
    marginTop: 16,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
});
