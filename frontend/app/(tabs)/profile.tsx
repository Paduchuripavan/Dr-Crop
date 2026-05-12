import { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Alert, ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Colors } from '../../constants/colors';
import { Ionicons } from '@expo/vector-icons';
import { languageNames } from '../../constants/translations';
import api from '../../utils/api';

export default function Profile() {
  const { user, logout } = useAuth();
  const { t, language, setLanguage } = useLanguage();
  const router = useRouter();
  const [diagnoses, setDiagnoses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadDiagnoses(); }, []);

  const loadDiagnoses = async () => {
    try {
      if (user) {
        const response = await api.get(`/diagnoses/${user.id}`);
        setDiagnoses(response.data);
      }
    } catch (error) { console.error('Error loading diagnoses:', error); }
    finally { setLoading(false); }
  };

  const handleLogout = () => {
    Alert.alert(t('logout'), t('logout_confirm'), [
      { text: t('cancel'), style: 'cancel' },
      {
        text: t('logout'), style: 'destructive',
        onPress: async () => { await logout(); router.replace('/auth/login'); },
      },
    ]);
  };

  const cycleLang = async () => {
    const langs = Object.keys(languageNames);
    const idx = langs.indexOf(language);
    const next = langs[(idx + 1) % langs.length];
    await setLanguage(next);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content}>
        <View style={styles.header}>
          <View style={styles.avatar}>
            <Ionicons name="person" size={48} color={Colors.primary} />
          </View>
          <Text style={styles.name}>{user?.name}</Text>
          <Text style={styles.email}>{user?.email}</Text>
          {user?.location && (
            <View style={styles.locationContainer}>
              <Ionicons name="location" size={16} color={Colors.textSecondary} />
              <Text style={styles.location}>{user.location}</Text>
            </View>
          )}
        </View>

        {/* Language Selector */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('language')}</Text>
          <View style={styles.langRow}>
            {Object.entries(languageNames).map(([code, name]) => (
              <TouchableOpacity
                key={code}
                testID={`lang-${code}-btn`}
                style={[styles.langOption, language === code && styles.langOptionActive]}
                onPress={() => setLanguage(code)}
              >
                <Text style={[styles.langOptionText, language === code && styles.langOptionTextActive]}>
                  {name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('statistics')}</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Ionicons name="camera" size={32} color={Colors.primary} />
              <Text style={styles.statValue}>{diagnoses.length}</Text>
              <Text style={styles.statLabel}>{t('scans')}</Text>
            </View>
            <View style={styles.statCard}>
              <Ionicons name="leaf" size={32} color={Colors.success} />
              <Text style={styles.statValue}>8</Text>
              <Text style={styles.statLabel}>{t('crops')}</Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('recent_diagnoses')}</Text>
          {loading ? (
            <ActivityIndicator size="small" color={Colors.primary} />
          ) : diagnoses.length === 0 ? (
            <Text style={styles.emptyText}>{t('no_diagnoses')}</Text>
          ) : (
            diagnoses.slice(0, 5).map((diagnosis) => (
              <View key={diagnosis.id} style={styles.diagnosisCard}>
                <View style={styles.diagnosisHeader}>
                  <Ionicons
                    name={diagnosis.disease_name === 'Healthy' ? 'checkmark-circle' : 'warning'}
                    size={24}
                    color={diagnosis.disease_name === 'Healthy' ? Colors.success : Colors.warning}
                  />
                  <View style={styles.diagnosisInfo}>
                    <Text style={styles.diagnosisName}>{diagnosis.disease_name || 'Unknown'}</Text>
                    <Text style={styles.diagnosisDate}>{new Date(diagnosis.timestamp).toLocaleDateString()}</Text>
                  </View>
                </View>
                {diagnosis.crop_name && (
                  <Text style={styles.diagnosisCrop}>{t('crops')}: {diagnosis.crop_name}</Text>
                )}
              </View>
            ))
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('app_info')}</Text>
          <View style={styles.menuCard}>
            <View style={styles.menuItem}>
              <Ionicons name="leaf" size={24} color={Colors.primary} />
              <Text style={styles.menuText}>{t('version')}</Text>
            </View>
            <View style={styles.menuItem}>
              <Ionicons name="business" size={24} color={Colors.primary} />
              <Text style={styles.menuText}>{t('tagline')}</Text>
            </View>
          </View>
        </View>

        <TouchableOpacity testID="logout-btn" style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out" size={24} color={Colors.error} />
          <Text style={styles.logoutText}>{t('logout')}</Text>
        </TouchableOpacity>

        <View style={styles.bottomSpace} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { flex: 1 },
  header: { backgroundColor: Colors.surface, padding: 24, alignItems: 'center' },
  avatar: {
    width: 100, height: 100, borderRadius: 50, backgroundColor: Colors.primary + '20',
    alignItems: 'center', justifyContent: 'center', marginBottom: 16,
  },
  name: { fontSize: 24, fontWeight: 'bold', color: Colors.text, marginBottom: 4 },
  email: { fontSize: 16, color: Colors.textSecondary, marginBottom: 8 },
  locationContainer: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  location: { fontSize: 14, color: Colors.textSecondary },
  section: { padding: 20 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.text, marginBottom: 16 },
  langRow: { flexDirection: 'row', gap: 10, flexWrap: 'wrap' },
  langOption: {
    paddingHorizontal: 20, paddingVertical: 12, borderRadius: 24,
    backgroundColor: Colors.surface, borderWidth: 2, borderColor: Colors.border,
  },
  langOptionActive: { borderColor: Colors.primary, backgroundColor: Colors.primary + '15' },
  langOptionText: { fontSize: 16, color: Colors.text, fontWeight: '600' },
  langOptionTextActive: { color: Colors.primary },
  statsGrid: { flexDirection: 'row', gap: 12 },
  statCard: {
    flex: 1, backgroundColor: Colors.surface, borderRadius: 12, padding: 20, alignItems: 'center',
    elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4,
  },
  statValue: { fontSize: 28, fontWeight: 'bold', color: Colors.text, marginTop: 8 },
  statLabel: { fontSize: 14, color: Colors.textSecondary, marginTop: 4 },
  diagnosisCard: { backgroundColor: Colors.surface, borderRadius: 12, padding: 16, marginBottom: 12 },
  diagnosisHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  diagnosisInfo: { marginLeft: 12, flex: 1 },
  diagnosisName: { fontSize: 16, fontWeight: 'bold', color: Colors.text },
  diagnosisDate: { fontSize: 12, color: Colors.textSecondary, marginTop: 2 },
  diagnosisCrop: { fontSize: 14, color: Colors.textSecondary, marginLeft: 36 },
  emptyText: { fontSize: 16, color: Colors.textSecondary, textAlign: 'center', padding: 20 },
  menuCard: { backgroundColor: Colors.surface, borderRadius: 12, padding: 16 },
  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, gap: 12 },
  menuText: { fontSize: 16, color: Colors.text },
  logoutButton: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    backgroundColor: Colors.surface, marginHorizontal: 20, padding: 16, borderRadius: 12,
    borderWidth: 2, borderColor: Colors.error, gap: 8,
  },
  logoutText: { fontSize: 18, fontWeight: 'bold', color: Colors.error },
  bottomSpace: { height: 20 },
});
