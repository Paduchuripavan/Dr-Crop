import { useState } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, Image,
  ScrollView, ActivityIndicator, Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../../constants/colors';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../utils/api';

export default function Detect() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [image, setImage] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const requestPermissions = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(t('permission_required'), t('camera_permission'));
      return false;
    }
    return true;
  };

  const takePicture = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;
    const res = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true, aspect: [4, 3], quality: 0.8, base64: true,
    });
    if (!res.canceled && res.assets[0].base64) {
      setImage(`data:image/jpeg;base64,${res.assets[0].base64}`);
      setResult(null);
    }
  };

  const pickImage = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true, aspect: [4, 3], quality: 0.8, base64: true,
    });
    if (!res.canceled && res.assets[0].base64) {
      setImage(`data:image/jpeg;base64,${res.assets[0].base64}`);
      setResult(null);
    }
  };

  const analyzeImage = async () => {
    if (!image || !user) return;
    setAnalyzing(true);
    try {
      const base64Data = image.split(',')[1];
      const response = await api.post('/diagnose', {
        user_id: user.id, image_base64: base64Data, location: user.location,
      });
      setResult(response.data);
    } catch (error: any) {
      Alert.alert(t('analysis_failed'), error.response?.data?.detail || 'Failed to analyze image');
    } finally { setAnalyzing(false); }
  };

  const reset = () => { setImage(null); setResult(null); };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{t('disease_detection')}</Text>
        <Text style={styles.subtitle}>{t('take_upload_photo')}</Text>
      </View>
      <ScrollView style={styles.content}>
        {!image ? (
          <View style={styles.uploadSection}>
            <View style={styles.iconContainer}>
              <Ionicons name="camera-outline" size={80} color={Colors.primary} />
            </View>
            <Text style={styles.uploadText}>{t('capture_select')}</Text>
            <TouchableOpacity testID="take-photo-btn" style={styles.primaryButton} onPress={takePicture}>
              <Ionicons name="camera" size={24} color={Colors.textLight} />
              <Text style={styles.primaryButtonText}>{t('take_photo')}</Text>
            </TouchableOpacity>
            <TouchableOpacity testID="choose-gallery-btn" style={styles.secondaryButton} onPress={pickImage}>
              <Ionicons name="images" size={24} color={Colors.primary} />
              <Text style={styles.secondaryButtonText}>{t('choose_gallery')}</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.analysisSection}>
            <Image source={{ uri: image }} style={styles.image} />
            {!result && !analyzing && (
              <View style={styles.actions}>
                <TouchableOpacity testID="analyze-btn" style={styles.primaryButton} onPress={analyzeImage}>
                  <Ionicons name="search" size={24} color={Colors.textLight} />
                  <Text style={styles.primaryButtonText}>{t('analyze_plant')}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.secondaryButton} onPress={reset}>
                  <Text style={styles.secondaryButtonText}>{t('take_another')}</Text>
                </TouchableOpacity>
              </View>
            )}
            {analyzing && (
              <View style={styles.analyzingContainer}>
                <ActivityIndicator size="large" color={Colors.primary} />
                <Text style={styles.analyzingText}>{t('analyzing')}</Text>
                <Text style={styles.analyzingSubtext}>{t('analyzing_wait')}</Text>
              </View>
            )}
            {result && (
              <View style={styles.resultContainer}>
                <View style={styles.resultHeader}>
                  <Ionicons
                    name={result.disease_name === 'Healthy' ? 'checkmark-circle' : 'warning'}
                    size={48}
                    color={result.disease_name === 'Healthy' ? Colors.success : Colors.warning}
                  />
                  <Text style={styles.resultTitle}>{result.disease_name}</Text>
                </View>
                {result.confidence && (
                  <View style={styles.confidenceContainer}>
                    <Text style={styles.label}>{t('confidence')}:</Text>
                    <Text style={[styles.confidence,
                      result.confidence === 'High' ? styles.confHigh :
                      result.confidence === 'Medium' ? styles.confMed : styles.confLow
                    ]}>{result.confidence}</Text>
                  </View>
                )}
                {result.crop_name && (
                  <View style={styles.infoCard}>
                    <Text style={styles.label}>{t('crop_identified')}:</Text>
                    <Text style={styles.value}>{result.crop_name}</Text>
                  </View>
                )}
                {result.treatment && (
                  <View style={styles.infoCard}>
                    <Text style={styles.label}>{t('recommended_treatment')}:</Text>
                    <Text style={styles.value}>{result.treatment}</Text>
                  </View>
                )}
                {result.diagnosis_text && (
                  <View style={styles.infoCard}>
                    <Text style={styles.label}>{t('full_diagnosis')}:</Text>
                    <Text style={styles.value}>{result.diagnosis_text}</Text>
                  </View>
                )}
                <TouchableOpacity style={styles.primaryButton} onPress={reset}>
                  <Ionicons name="camera" size={24} color={Colors.textLight} />
                  <Text style={styles.primaryButtonText}>{t('scan_another')}</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: { padding: 20, backgroundColor: Colors.surface },
  title: { fontSize: 28, fontWeight: 'bold', color: Colors.text, marginBottom: 4 },
  subtitle: { fontSize: 16, color: Colors.textSecondary },
  content: { flex: 1 },
  uploadSection: { padding: 20, alignItems: 'center' },
  iconContainer: {
    width: 160, height: 160, borderRadius: 80, backgroundColor: Colors.primary + '20',
    alignItems: 'center', justifyContent: 'center', marginTop: 40, marginBottom: 24,
  },
  uploadText: { fontSize: 18, color: Colors.textSecondary, textAlign: 'center', marginBottom: 32 },
  primaryButton: {
    flexDirection: 'row', backgroundColor: Colors.primary, borderRadius: 12, padding: 16,
    alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: 12, gap: 8,
  },
  primaryButtonText: { color: Colors.textLight, fontSize: 18, fontWeight: 'bold' },
  secondaryButton: {
    flexDirection: 'row', backgroundColor: Colors.surface, borderRadius: 12, padding: 16,
    alignItems: 'center', justifyContent: 'center', width: '100%', borderWidth: 2, borderColor: Colors.primary, gap: 8,
  },
  secondaryButtonText: { color: Colors.primary, fontSize: 18, fontWeight: 'bold' },
  analysisSection: { padding: 20 },
  image: { width: '100%', height: 300, borderRadius: 12, marginBottom: 20 },
  actions: { marginBottom: 20 },
  analyzingContainer: { alignItems: 'center', padding: 40 },
  analyzingText: { fontSize: 18, fontWeight: 'bold', color: Colors.text, marginTop: 16 },
  analyzingSubtext: { fontSize: 14, color: Colors.textSecondary, marginTop: 8 },
  resultContainer: { backgroundColor: Colors.surface, borderRadius: 12, padding: 20 },
  resultHeader: { alignItems: 'center', marginBottom: 20 },
  resultTitle: { fontSize: 24, fontWeight: 'bold', color: Colors.text, marginTop: 12, textAlign: 'center' },
  confidenceContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginBottom: 20, gap: 8 },
  confidence: { fontSize: 16, fontWeight: 'bold' },
  confHigh: { color: Colors.success }, confMed: { color: Colors.warning }, confLow: { color: Colors.error },
  infoCard: { backgroundColor: Colors.background, borderRadius: 8, padding: 16, marginBottom: 12 },
  label: { fontSize: 14, fontWeight: 'bold', color: Colors.textSecondary, marginBottom: 8 },
  value: { fontSize: 16, color: Colors.text, lineHeight: 24 },
});
