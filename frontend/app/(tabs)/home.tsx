import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Colors } from '../../constants/colors';
import { Ionicons } from '@expo/vector-icons';
import api from '../../utils/api';

export default function Home() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();
  const [weather, setWeather] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [weatherRes, alertsRes] = await Promise.all([
        api.get('/weather', { params: { location: user?.location || 'default' } }),
        api.get('/alerts', { params: { location: user?.location } }),
      ]);
      setWeather(weatherRes.data);
      setAlerts(alertsRes.data.slice(0, 3));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally { setLoading(false); setRefreshing(false); }
  };

  const onRefresh = () => { setRefreshing(true); loadData(); };

  const quickActions = [
    { icon: 'camera', label: t('scan_plant'), color: Colors.primary, route: '/detect' },
    { icon: 'leaf', label: t('crop_library'), color: Colors.success, route: '/crops' },
    { icon: 'calculator', label: t('fertilizer_calc'), color: Colors.secondary, route: '/fertilizer' },
    { icon: 'people', label: t('community'), color: Colors.info, route: '/community' },
  ];

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={styles.header}>
          <Text style={styles.greeting}>{t('hello')}, {user?.name}! {'\ud83d\udc4b'}</Text>
          <Text style={styles.subtitle}>{t('how_help')}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{t('quick_actions')}</Text>
          <View style={styles.actionsGrid}>
            {quickActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                testID={`quick-action-${index}`}
                style={[styles.actionCard, { borderLeftColor: action.color }]}
                onPress={() => router.push(action.route as any)}
              >
                <Ionicons name={action.icon as any} size={32} color={action.color} />
                <Text style={styles.actionLabel}>{action.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {weather && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('weather_farming')}</Text>
            <View style={styles.weatherCard}>
              <View style={styles.weatherHeader}>
                <Ionicons name="partly-sunny" size={48} color={Colors.secondary} />
                <View style={styles.weatherInfo}>
                  <Text style={styles.weatherTemp}>{weather.temperature}{'\u00b0'}C</Text>
                  <Text style={styles.weatherDesc}>{weather.forecast}</Text>
                </View>
              </View>
              <View style={styles.weatherDetails}>
                <View style={styles.weatherDetail}>
                  <Ionicons name="water" size={20} color={Colors.info} />
                  <Text style={styles.weatherDetailText}>{t('humidity')}: {weather.humidity}%</Text>
                </View>
                <View style={styles.weatherDetail}>
                  <Ionicons name="rainy" size={20} color={Colors.info} />
                  <Text style={styles.weatherDetailText}>{t('rainfall')}: {weather.rainfall}mm</Text>
                </View>
              </View>
              {weather.best_for_spraying && (
                <View style={[styles.weatherTip, { backgroundColor: Colors.success + '20' }]}>
                  <Ionicons name="checkmark-circle" size={20} color={Colors.success} />
                  <Text style={styles.weatherTipText}>{t('good_for_spraying')}</Text>
                </View>
              )}
            </View>
          </View>
        )}

        {alerts.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('disease_alerts')}</Text>
            {alerts.map((alert, index) => (
              <View key={index} style={styles.alertCard}>
                <Ionicons name="warning" size={24} color={Colors.warning} />
                <View style={styles.alertContent}>
                  <Text style={styles.alertTitle}>{alert.disease_name}</Text>
                  <Text style={styles.alertText}>{alert.crop_name} {'\u2022'} {alert.location}</Text>
                </View>
              </View>
            ))}
          </View>
        )}
        <View style={styles.bottomSpace} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scroll: { flex: 1 },
  header: { padding: 20, backgroundColor: Colors.surface },
  greeting: { fontSize: 24, fontWeight: 'bold', color: Colors.text, marginBottom: 4 },
  subtitle: { fontSize: 16, color: Colors.textSecondary },
  section: { padding: 20 },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: Colors.text, marginBottom: 16 },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  actionCard: {
    flex: 1, minWidth: '45%', backgroundColor: Colors.surface, borderRadius: 12, padding: 20,
    alignItems: 'center', borderLeftWidth: 4, elevation: 2,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4,
  },
  actionLabel: { marginTop: 8, fontSize: 14, fontWeight: '600', color: Colors.text, textAlign: 'center' },
  weatherCard: {
    backgroundColor: Colors.surface, borderRadius: 12, padding: 16, elevation: 2,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4,
  },
  weatherHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  weatherInfo: { marginLeft: 16 },
  weatherTemp: { fontSize: 32, fontWeight: 'bold', color: Colors.text },
  weatherDesc: { fontSize: 16, color: Colors.textSecondary },
  weatherDetails: { flexDirection: 'row', gap: 16, marginBottom: 12 },
  weatherDetail: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  weatherDetailText: { fontSize: 14, color: Colors.textSecondary },
  weatherTip: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 12, borderRadius: 8 },
  weatherTipText: { fontSize: 14, color: Colors.success, fontWeight: '600' },
  alertCard: {
    flexDirection: 'row', backgroundColor: Colors.surface, borderRadius: 12, padding: 16,
    marginBottom: 12, borderLeftWidth: 4, borderLeftColor: Colors.warning,
  },
  alertContent: { marginLeft: 12, flex: 1 },
  alertTitle: { fontSize: 16, fontWeight: 'bold', color: Colors.text, marginBottom: 4 },
  alertText: { fontSize: 14, color: Colors.textSecondary },
  bottomSpace: { height: 20 },
});
