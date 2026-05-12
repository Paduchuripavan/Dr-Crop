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

export default function Community() {
  const { t } = useLanguage();
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => { loadPosts(); }, []);

  const loadPosts = async () => {
    try {
      const response = await api.get('/community/posts');
      setPosts(response.data);
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally { setLoading(false); setRefreshing(false); }
  };

  const onRefresh = () => { setRefreshing(true); loadPosts(); };

  const likePost = async (postId: string) => {
    try {
      await api.post(`/community/posts/${postId}/like`);
      setPosts(posts.map(post =>
        post.id === postId ? { ...post, likes: post.likes + 1 } : post
      ));
    } catch (error) { console.error('Error liking post:', error); }
  };

  if (loading) {
    return <View style={styles.loadingContainer}><ActivityIndicator size="large" color={Colors.primary} /></View>;
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{t('community_title')}</Text>
        <Text style={styles.subtitle}>{t('connect_farmers')}</Text>
      </View>
      <ScrollView style={styles.content} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        {posts.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="people-outline" size={80} color={Colors.textSecondary} />
            <Text style={styles.emptyText}>{t('no_posts')}</Text>
            <Text style={styles.emptySubtext}>{t('be_first')}</Text>
          </View>
        ) : (
          posts.map((post) => (
            <View key={post.id} style={styles.postCard}>
              <View style={styles.postHeader}>
                <View style={styles.avatar}>
                  <Ionicons name="person" size={24} color={Colors.primary} />
                </View>
                <View style={styles.postMeta}>
                  <Text style={styles.postAuthor}>{post.user_name}</Text>
                  <Text style={styles.postTime}>{new Date(post.created_at).toLocaleDateString()}</Text>
                </View>
              </View>
              <Text style={styles.postTitle}>{post.title}</Text>
              <Text style={styles.postContent}>{post.content}</Text>
              {post.crop_type && (
                <View style={styles.cropTag}>
                  <Ionicons name="leaf" size={16} color={Colors.primary} />
                  <Text style={styles.cropTagText}>{post.crop_type}</Text>
                </View>
              )}
              <View style={styles.postActions}>
                <TouchableOpacity style={styles.actionButton} onPress={() => likePost(post.id)}>
                  <Ionicons name="heart-outline" size={20} color={Colors.error} />
                  <Text style={styles.actionText}>{post.likes}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionButton}>
                  <Ionicons name="chatbubble-outline" size={20} color={Colors.info} />
                  <Text style={styles.actionText}>{post.replies_count}</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))
        )}
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
  emptyContainer: { alignItems: 'center', padding: 40, marginTop: 60 },
  emptyText: { fontSize: 20, fontWeight: 'bold', color: Colors.text, marginTop: 16 },
  emptySubtext: { fontSize: 16, color: Colors.textSecondary, marginTop: 8 },
  postCard: {
    backgroundColor: Colors.surface, marginHorizontal: 16, marginTop: 16, borderRadius: 12, padding: 16,
    elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4,
  },
  postHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  avatar: {
    width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.primary + '20',
    alignItems: 'center', justifyContent: 'center',
  },
  postMeta: { marginLeft: 12 },
  postAuthor: { fontSize: 16, fontWeight: 'bold', color: Colors.text },
  postTime: { fontSize: 12, color: Colors.textSecondary },
  postTitle: { fontSize: 18, fontWeight: 'bold', color: Colors.text, marginBottom: 8 },
  postContent: { fontSize: 16, color: Colors.text, lineHeight: 24, marginBottom: 12 },
  cropTag: {
    flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start',
    backgroundColor: Colors.primary + '20', paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: 16, marginBottom: 12, gap: 4,
  },
  cropTagText: { fontSize: 14, color: Colors.primary, fontWeight: '600' },
  postActions: { flexDirection: 'row', borderTopWidth: 1, borderTopColor: Colors.border, paddingTop: 12, gap: 16 },
  actionButton: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  actionText: { fontSize: 14, color: Colors.textSecondary, fontWeight: '600' },
  bottomSpace: { height: 20 },
});
