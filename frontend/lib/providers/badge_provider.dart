import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:convert';
import 'dart:developer' as developer;
import '../models/badge.dart';
import '../services/api_client.dart';
import 'user_provider.dart';

class BadgeState {
  final List<UserBadge> userBadges;
  final List<Badge> allBadges;
  final bool isLoading;
  final String? error;

  BadgeState({
    this.userBadges = const [],
    this.allBadges = const [],
    this.isLoading = false,
    this.error,
  });

  BadgeState copyWith({
    List<UserBadge>? userBadges,
    List<Badge>? allBadges,
    bool? isLoading,
    String? error,
  }) {
    return BadgeState(
      userBadges: userBadges ?? this.userBadges,
      allBadges: allBadges ?? this.allBadges,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class BadgeNotifier extends StateNotifier<BadgeState> {
  final Ref _ref;

  BadgeNotifier(this._ref) : super(BadgeState());

  Future<void> loadUserBadges(int userId) async {
    state = state.copyWith(isLoading: true, error: null);
    
    final apiClient = _ref.read(apiClientProvider);
    final userTokenNotifier = _ref.read(userProvider.notifier);
    final token = userTokenNotifier.token;
    
    if (token == null) {
      state = state.copyWith(
        error: 'Kimlik doğrulama gerekli',
        isLoading: false,
      );
      return;
    }
    
    try {
      final response = await apiClient.get('/user/badges', token: token);
      
      if (response['success'] == true) {
        final badgesData = response['badges'] as List;
        final userBadges = badgesData.map((badge) => UserBadge.fromJson(badge)).toList();
        
        state = state.copyWith(
          userBadges: userBadges,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          error: response['message'] ?? 'Rozetler yüklenirken hata oluştu',
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        error: 'Bağlantı hatası: $e',
        isLoading: false,
      );
    }
  }

  Future<void> loadAllBadges() async {
    final apiClient = _ref.read(apiClientProvider);
    final userTokenNotifier = _ref.read(userProvider.notifier);
    final token = userTokenNotifier.token;
    
    if (token == null) {
      developer.log('Token bulunamadı, tüm rozetler yüklenemedi', name: 'BadgeProvider');
      return;
    }
    
    try {
      final response = await apiClient.get('/social/badges/all', token: token);
      
      if (response['success'] == true) {
        final badgesData = response['badges'] as List;
        final allBadges = badgesData.map((badge) => Badge.fromJson(badge)).toList();
        
        state = state.copyWith(allBadges: allBadges);
      }
    } catch (e) {
      // Hata durumunda sessizce devam et, sadece kullanıcı rozetlerini göster
      developer.log('Tüm rozetler yüklenirken hata: $e', name: 'BadgeProvider');
    }
  }

  void addUserBadge(UserBadge badge) {
    final updatedBadges = [...state.userBadges, badge];
    state = state.copyWith(userBadges: updatedBadges);
  }

  void clearBadges() {
    state = BadgeState();
  }
}

final badgeProvider = StateNotifierProvider<BadgeNotifier, BadgeState>((ref) {
  return BadgeNotifier(ref);
});

// User badge'lerini almak için provider
final userBadgesProvider = FutureProvider.family<List<UserBadge>, int>((ref, userId) async {
  final badgeNotifier = ref.read(badgeProvider.notifier);
  await badgeNotifier.loadUserBadges(userId);
  return ref.read(badgeProvider).userBadges;
});

// Tüm badge'leri almak için provider
final allBadgesProvider = FutureProvider<List<Badge>>((ref) async {
  final badgeNotifier = ref.read(badgeProvider.notifier);
  await badgeNotifier.loadAllBadges();
  return ref.read(badgeProvider).allBadges;
});

// Badge details provider for individual badge
final badgeDetailsProvider = FutureProvider.family<Badge?, String>((ref, badgeId) async {
  final badgeNotifier = ref.read(badgeProvider.notifier);
  await badgeNotifier.loadAllBadges();
  final allBadges = ref.read(badgeProvider).allBadges;
  try {
    final id = int.parse(badgeId);
    return allBadges.firstWhere((badge) => badge.id == id);
  } catch (e) {
    return null;
  }
});
