import { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Colors } from '../../constants/colors';
import { useLanguage } from '../../contexts/LanguageContext';
import { Ionicons } from '@expo/vector-icons';
import api from '../../utils/api';

export default function Crops() {
  const { t } = useLanguage();
  const [crops, setCrops] = useState<any[]>([]);
  const [selectedCrop, setSelectedCrop] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { loadCrops(); }, []);

  const loadCrops = async () => {
    try {
      const response = await api.get('/crops');
      setCrops(response.data);
    } catch (error) {
      console.error('Error loading crops:', error);
    } finally { setLoading(false); setRefreshing(false); }
  };

  const onRefresh = () => { setRefreshing(true); loadCrops(); };

  if (loading) {
    return <View style={styles.loadingContainer}><ActivityIndicator size="large" color={Colors.primary} /></View>;
  }

  if (selectedCrop) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.detailHeader}>
          <TouchableOpacity style={styles.backButton} onPress={() => setSelectedCrop(null)}>
            <Ionicons name="arrow-back" size={24} color={Colors.text} />
          </TouchableOpacity>
          <Text style={styles.detailTitle}>{selectedCrop.name}</Text>
        </View>
        <ScrollView style={styles.detailContent}>
          <View style={styles.cropIcon}><Text style={styles.cropIconText}>{selectedCrop.icon}</Text></View>
          <Text style={styles.scientificName}>{selectedCrop.scientific_name}</Text>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('description')}</Text>
            <Text style={styles.sectionText}>{selectedCrop.description}</Text>
          </View>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('growing_tips')}</Text>
            <Text style={styles.sectionText}>{selectedCrop.growing_tips}</Text>
          </View>
          <View style={styles.bottomSpace} />
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{t('crop_library_title')}</Text>
        <Text style={styles.subtitle}>{t('learn_crops')}</Text>
      </View>
      <ScrollView style={styles.content} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        <View style={styles.grid}>
          {crops.map((crop) => (
            <TouchableOpacity key={crop.id} style={styles.cropCard} onPress={() => setSelectedCrop(crop)}>
              <Text style={styles.cropCardIcon}>{crop.icon}</Text>
              <Text style={styles.cropCardName}>{crop.name}</Text>
              <Text style={styles.cropCardScientific} numberOfLines={1}>{crop.scientific_name}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <View style={styles.bottomSpace} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { padding: 20, backgroundColor: Colors.surface },
  title: { fontSize: 28, fontWeight: 'bold', color: Colors.text, marginBottom: 4 },
  subtitle: { fontSize: 16, color: Colors.textSecondary },
  content: { flex: 1 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', padding: 12, gap: 12 },
  cropCard: {
    width: '47%', backgroundColor: Colors.surface, borderRadius: 12, padding: 20, alignItems: 'center',
    elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4,
  },
  cropCardIcon: { fontSize: 48, marginBottom: 12 },
  cropCardName: { fontSize: 16, fontWeight: 'bold', color: Colors.text, marginBottom: 4, textAlign: 'center' },
  cropCardScientific: { fontSize: 12, color: Colors.textSecondary, fontStyle: 'italic', textAlign: 'center' },
  detailHeader: { flexDirection: 'row', alignItems: 'center', padding: 20, backgroundColor: Colors.surface },
  backButton: { marginRight: 16 },
  detailTitle: { fontSize: 24, fontWeight: 'bold', color: Colors.text },
  detailContent: { flex: 1, padding: 20 },
  cropIcon: { alignItems: 'center', marginBottom: 16 },
  cropIconText: { fontSize: 80 },
  scientificName: { fontSize: 18, fontStyle: 'italic', color: Colors.textSecondary, textAlign: 'center', marginBottom: 24 },
  section: { backgroundColor: Colors.surface, borderRadius: 12, padding: 16, marginBottom: 16 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: Colors.text, marginBottom: 12 },
  sectionText: { fontSize: 16, color: Colors.text, lineHeight: 24 },
  bottomSpace: { height: 20 },
});
