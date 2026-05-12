import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Colors } from '../constants/colors';
import { Ionicons } from '@expo/vector-icons';
import api from '../utils/api';

export default function FertilizerCalculator() {
  const router = useRouter();
  const [crops, setCrops] = useState<any[]>([]);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [plotSize, setPlotSize] = useState('');
  const [soilType, setSoilType] = useState('Loamy');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCrops();
  }, []);

  const loadCrops = async () => {
    try {
      const response = await api.get('/crops');
      setCrops(response.data);
    } catch (error) {
      console.error('Error loading crops:', error);
    }
  };

  const calculate = async () => {
    if (!selectedCrop || !plotSize) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/fertilizer/calculate', {
        crop_name: selectedCrop,
        plot_size: parseFloat(plotSize),
        soil_type: soilType,
      });
      setResult(response.data);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={styles.title}>Fertilizer Calculator</Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.form}>
          <Text style={styles.label}>Select Crop</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.cropList}>
            {crops.map((crop) => (
              <TouchableOpacity
                key={crop.id}
                style={[
                  styles.cropOption,
                  selectedCrop === crop.name && styles.cropOptionSelected,
                ]}
                onPress={() => setSelectedCrop(crop.name)}
              >
                <Text style={styles.cropIcon}>{crop.icon}</Text>
                <Text
                  style={[
                    styles.cropName,
                    selectedCrop === crop.name && styles.cropNameSelected,
                  ]}
                >
                  {crop.name}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <Text style={styles.label}>Plot Size (acres)</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g., 2.5"
            value={plotSize}
            onChangeText={setPlotSize}
            keyboardType="decimal-pad"
            placeholderTextColor={Colors.textSecondary}
          />

          <Text style={styles.label}>Soil Type</Text>
          <View style={styles.soilTypes}>
            {['Loamy', 'Sandy', 'Clay', 'Silty'].map((type) => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.soilTypeOption,
                  soilType === type && styles.soilTypeSelected,
                ]}
                onPress={() => setSoilType(type)}
              >
                <Text
                  style={[
                    styles.soilTypeText,
                    soilType === type && styles.soilTypeTextSelected,
                  ]}
                >
                  {type}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity
            style={[styles.calculateButton, loading && styles.buttonDisabled]}
            onPress={calculate}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={Colors.textLight} />
            ) : (
              <>
                <Ionicons name="calculator" size={24} color={Colors.textLight} />
                <Text style={styles.calculateButtonText}>Calculate</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {result && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultTitle}>Fertilizer Requirements</Text>
            
            <View style={styles.nutrientCard}>
              <View style={styles.nutrientIcon}>
                <Text style={styles.nutrientIconText}>N</Text>
              </View>
              <View style={styles.nutrientInfo}>
                <Text style={styles.nutrientLabel}>Nitrogen</Text>
                <Text style={styles.nutrientValue}>{result.nitrogen_kg} kg</Text>
              </View>
            </View>

            <View style={styles.nutrientCard}>
              <View style={[styles.nutrientIcon, { backgroundColor: Colors.warning + '20' }]}>
                <Text style={[styles.nutrientIconText, { color: Colors.warning }]}>P</Text>
              </View>
              <View style={styles.nutrientInfo}>
                <Text style={styles.nutrientLabel}>Phosphorus</Text>
                <Text style={styles.nutrientValue}>{result.phosphorus_kg} kg</Text>
              </View>
            </View>

            <View style={styles.nutrientCard}>
              <View style={[styles.nutrientIcon, { backgroundColor: Colors.info + '20' }]}>
                <Text style={[styles.nutrientIconText, { color: Colors.info }]}>K</Text>
              </View>
              <View style={styles.nutrientInfo}>
                <Text style={styles.nutrientLabel}>Potassium</Text>
                <Text style={styles.nutrientValue}>{result.potassium_kg} kg</Text>
              </View>
            </View>

            <View style={styles.recommendationCard}>
              <Ionicons name="bulb" size={24} color={Colors.secondary} />
              <Text style={styles.recommendationTitle}>Application Guide</Text>
              <Text style={styles.recommendationText}>{result.recommendations}</Text>
            </View>
          </View>
        )}

        <View style={styles.bottomSpace} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: Colors.surface,
  },
  backButton: {
    marginRight: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
  },
  content: {
    flex: 1,
  },
  form: {
    padding: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 12,
    marginTop: 16,
  },
  cropList: {
    marginBottom: 8,
  },
  cropOption: {
    alignItems: 'center',
    marginRight: 16,
    padding: 12,
    backgroundColor: Colors.surface,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: Colors.border,
    minWidth: 80,
  },
  cropOptionSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primary + '10',
  },
  cropIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  cropName: {
    fontSize: 14,
    color: Colors.text,
  },
  cropNameSelected: {
    color: Colors.primary,
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  soilTypes: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  soilTypeOption: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    backgroundColor: Colors.surface,
    borderWidth: 2,
    borderColor: Colors.border,
  },
  soilTypeSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primary + '10',
  },
  soilTypeText: {
    fontSize: 14,
    color: Colors.text,
  },
  soilTypeTextSelected: {
    color: Colors.primary,
    fontWeight: 'bold',
  },
  calculateButton: {
    flexDirection: 'row',
    backgroundColor: Colors.primary,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
    gap: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  calculateButtonText: {
    color: Colors.textLight,
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultContainer: {
    padding: 20,
  },
  resultTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  nutrientCard: {
    flexDirection: 'row',
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
  },
  nutrientIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: Colors.primary + '20',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  nutrientIconText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  nutrientInfo: {
    flex: 1,
  },
  nutrientLabel: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  nutrientValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  recommendationCard: {
    backgroundColor: Colors.secondary + '10',
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
    marginBottom: 12,
  },
  recommendationText: {
    fontSize: 14,
    color: Colors.text,
    lineHeight: 22,
  },
  bottomSpace: {
    height: 20,
  },
});
