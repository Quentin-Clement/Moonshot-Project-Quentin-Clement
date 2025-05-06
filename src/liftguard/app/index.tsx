import React, { useRef, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  NativeScrollEvent,
  NativeSyntheticEvent,
  Animated,
  Easing,
  Alert,
} from 'react-native';
// import Icon from 'react-native-vector-icons/Feather';
import * as ImagePicker from 'expo-image-picker';

const API_URL = 'http://192.168.14.175:8000';

export default function HomeScreen() {
  const scrollRef = useRef<ScrollView>(null);
  const uploaderY = useRef(0);

  // Arrow bounce animation
  const arrowAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(arrowAnim, {
          toValue: 8,
          duration: 500,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
        Animated.timing(arrowAnim, {
          toValue: 0,
          duration: 500,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, [arrowAnim]);

  const scrollToUploader = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ y: uploaderY.current, animated: true });
    }
  };

  // Expo Image Picker flow
  const pickVideo = async () => {
    console.log('🔍 pickVideo pressed');
    // 1. Request permission
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission required', 'Please allow access to your photo library.');
      return;
    }

    // 2. Launch video picker
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      quality: 1,
    });
    console.log('📽️ picker result', result);

    // 3. Check for cancellation
    if (result.canceled) {
      console.log('User cancelled picker');
      return;
    }

    // 4. Get the selected asset
    const asset = result.assets[0];
    const uri = asset.uri;

    // 5. Prepare FormData
    const formData = new FormData() as any;
    formData.append('video', {
      uri: asset.uri,
      name: asset.fileName || asset.uri.split('/').pop()!,
      type: 'video/mp4',
    });

    // 6. Upload
    try {
      const res = await fetch(`${API_URL}/api/process-video`, {
        method: 'POST',
        // headers: { 'Content-Type': 'multipart/form-data' },  <-- remove this
        body: formData,
      });
      const json = await res.json();
      console.log('Upload success', json);
      Alert.alert('Upload', 'Video uploaded successfully');
    } catch (err: any) {
      console.error('Upload error', err);
      Alert.alert('Upload failed', err.message);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView ref={scrollRef} contentContainerStyle={styles.container}>
        {/* Hero Section */}
        <View style={styles.section}>
          <View style={styles.header}>
            <View style={styles.logo}>
              {/* <Icon name="barbell" size={24} color="#3366FF" /> */}
              <Text style={styles.logoText}>SquatPro</Text>
            </View>
            <TouchableOpacity>
              {/* <Icon name="rotate-ccw" size={24} color="#555" /> */}
            </TouchableOpacity>
          </View>

          <Text style={styles.title}>
            <Text style={{ fontWeight: '600' }}>Perfect </Text>
            Your Squat Form
          </Text>
          <Text style={styles.subtitle}>
            Record or upload your squat and get instant AI feedback on your form.
          </Text>

          <TouchableOpacity style={styles.primaryButton} onPress={scrollToUploader}>
            <Text style={styles.primaryButtonText}>Start Analysis</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={scrollToUploader} style={styles.arrowContainer}>
            <Animated.View style={{ transform: [{ translateY: arrowAnim }] }}>
              {/* <Icon name="chevron-down" size={28} color="#888" /> */}
            </Animated.View>
          </TouchableOpacity>
        </View>

        {/* How It Works Section */}
        <View style={[styles.section, styles.card]}>          
          <Text style={styles.cardHeader}>How It Works</Text>

          {[
            {
              key: '1',
              title: 'Record or Upload',
              desc: 'Take a video of your squat or upload an existing one.',
            },
            {
              key: '2',
              title: 'AI Analysis',
              desc: 'Our AI breaks down your movement frame by frame.',
            },
            {
              key: '3',
              title: 'Get Feedback',
              desc: 'Receive detailed form feedback with visual guides.',
            },
          ].map((step) => (
            <View style={styles.stepRow} key={step.key}>
              <View style={styles.stepCircle}>
                <Text style={styles.stepNumber}>{step.key}</Text>
              </View>
              <View style={styles.stepText}>
                <Text style={styles.stepTitle}>{step.title}</Text>
                <Text style={styles.stepDesc}>{step.desc}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Uploader Section */}
        <View
          onLayout={e => { uploaderY.current = e.nativeEvent.layout.y; }}
          style={styles.section}
        >
          <Text style={styles.uploaderHeader}>Upload or Record Your Squat</Text>
          <TouchableOpacity style={styles.primaryButton}>
            {/* <Icon name="camera" size={20} color="#fff" style={{ marginRight: 8 }} /> */}
            <Text style={styles.primaryButtonText}>Record Squat</Text>
          </TouchableOpacity>
          <View style={styles.uploadBox}>
            <Text style={styles.uploadText}>Tap to upload or drop a video here</Text>
            <TouchableOpacity style={styles.uploadButton} onPress={pickVideo}>
              <Text style={styles.uploadButtonText}>Choose Video</Text>
            </TouchableOpacity>
          </View>
        </View>


        {/* Footer */}
        <Text style={styles.footerText}>© 2025 SquatPro Analyzer</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#F4F6FA' },
  container: {
    padding: 16,
    alignItems: 'stretch',
  },
  section: {
    marginBottom: 32, // more space between sections
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: { flexDirection: 'row', alignItems: 'center' },
  logoText: { marginLeft: 8, fontSize: 18, fontWeight: '600', color: '#3366FF' },

  title: {
    fontSize: 28,
    marginTop: 24,
    color: '#111',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginTop: 8,
    color: '#555',
    textAlign: 'center',
  },
  primaryButton: {
    width: '100%',
    flexDirection: 'row',
    backgroundColor: '#3366FF',
    paddingVertical: 14,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  primaryButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  arrowContainer: {
    alignSelf: 'center',
    marginTop: 16,
  },

  card: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    textAlign: 'center',
  },
  stepRow: {
    flexDirection: 'row',
    marginBottom: 24, // more space between steps
  },
  stepCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(51, 102, 255, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepNumber: {
    color: '#3366FF',
    fontWeight: '600',
  },
  stepText: { flex: 1, marginLeft: 12 },
  stepTitle: { fontSize: 16, fontWeight: '600', color: '#111' },
  stepDesc: { fontSize: 14, color: '#555', marginTop: 4 },

  uploaderHeader: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 16,
    textAlign: 'center',
  },
  uploadBox: {
    marginTop: 16,
    padding: 20,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: '#CCC',
    borderRadius: 8,
    alignItems: 'center',
  },
  uploadText: {
    fontSize: 14,
    color: '#888',
    marginBottom: 12,
    textAlign: 'center',
  },
  uploadButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#3366FF',
  },
  uploadButtonText: {
    color: '#3366FF',
    fontSize: 14,
    fontWeight: '600',
  },

  footerText: {
    textAlign: 'center',
    color: '#AAA',
    fontSize: 12,
    marginVertical: 24,
  },
});