import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { Colors } from '../../constants/colors';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();

  const handleRegister = async () => {
    if (!email || !password || !name) {
      Alert.alert(t('error'), t('fill_required_fields'));
      return;
    }
    setLoading(true);
    try {
      await register(email, password, name, location);
      router.replace('/(tabs)/home');
    } catch (error: any) {
      Alert.alert(t('registration_failed'), error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <Text style={styles.logo}>{'\ud83c\udf3e'}</Text>
            <Text style={styles.title}>{t('join')}</Text>
            <Text style={styles.subtitle}>{t('start_diagnosing')}</Text>
          </View>
          <View style={styles.form}>
            <TextInput
              testID="register-name-input"
              style={styles.input}
              placeholder={`${t('full_name')} *`}
              value={name}
              onChangeText={setName}
              placeholderTextColor={Colors.textSecondary}
            />
            <TextInput
              testID="register-email-input"
              style={styles.input}
              placeholder={`${t('email')} *`}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              placeholderTextColor={Colors.textSecondary}
            />
            <TextInput
              testID="register-location-input"
              style={styles.input}
              placeholder={t('location_optional')}
              value={location}
              onChangeText={setLocation}
              placeholderTextColor={Colors.textSecondary}
            />
            <TextInput
              testID="register-password-input"
              style={styles.input}
              placeholder={`${t('password')} *`}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              placeholderTextColor={Colors.textSecondary}
            />
            <TouchableOpacity
              testID="register-submit-btn"
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleRegister}
              disabled={loading}
            >
              <Text style={styles.buttonText}>
                {loading ? t('creating_account') : t('register')}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.linkButton} onPress={() => router.back()}>
              <Text style={styles.linkText}>{t('have_account')}</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  keyboardView: { flex: 1 },
  scrollContent: { flexGrow: 1, padding: 24, justifyContent: 'center' },
  header: { alignItems: 'center', marginBottom: 40 },
  logo: { fontSize: 60, marginBottom: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: Colors.text, marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 16, color: Colors.textSecondary, textAlign: 'center' },
  form: { width: '100%' },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  button: {
    backgroundColor: Colors.primary,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: Colors.textLight, fontSize: 18, fontWeight: 'bold' },
  linkButton: { marginTop: 16, alignItems: 'center' },
  linkText: { color: Colors.primary, fontSize: 16 },
});
