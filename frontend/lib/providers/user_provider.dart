import 'dart:developer' as developer;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../services/auth_service.dart';
import '../services/api_client.dart';

/// Kullanıcı oturum state yönetimi için Riverpod provider.
/// Giriş/çıkış işlemleri ve kullanıcı state'i burada yönetilir.
final userProvider = AsyncNotifierProvider<UserNotifier, User?>(UserNotifier.new);

typedef On2FACallback = void Function();
typedef OnLoginSuccess = void Function();

class UserNotifier extends AsyncNotifier<User?> {
  AuthService? _authService;
  String? _token;
  bool _awaiting2FA = false;
  String? _pendingUsername;
  String? _pendingPassword;
  On2FACallback? _on2FA;
  OnLoginSuccess? _onLoginSuccess;

  /// Get the current user token
  String? get token => _token;

  @override
  Future<User?> build() async {
    // Use shared ApiClient provider instead of creating new instance
    final apiClient = ref.read(apiClientProvider);
    _authService = AuthService(apiClient);
    // Otomatik login veya session kontrolü burada yapılabilir.
    return null; // Başlangıçta kullanıcı yok
  }

  /// Instagram ile giriş (2FA destekli)
  Future<void> login(String username, String password, {String? verificationCode, On2FACallback? on2FA, OnLoginSuccess? onLoginSuccess}) async {
    state = const AsyncValue.loading();
    _on2FA = on2FA;
    _onLoginSuccess = onLoginSuccess;
    try {
      final tokenFromLogin = await _authService!.login(username, password, verificationCode: verificationCode);
      _token = tokenFromLogin; // Keep for internal use if UserNotifier needs direct token access
      _awaiting2FA = false;
      _pendingUsername = null;
      _pendingPassword = null;

      try {
        final profileData = await _authService!.getProfile(tokenFromLogin);
        
        // Log the raw profile data to debug
        developer.log('Raw profile data: $profileData', name: 'UserProvider');
        
        // Make sure profileData contains is_admin_platform: true for admin users
        if (profileData.containsKey('user_data') && profileData['user_data']?['is_admin'] == true) {
          profileData['is_admin_platform'] = true;
        }
        
        final userWithoutToken = User.fromJson(profileData);
        // Ensure the token from login is added to the User object
        final userWithToken = userWithoutToken.copyWith(token: tokenFromLogin);
        
        // Log whether this is an admin user
        if (userWithToken.isAdminPlatform) {
          developer.log('Admin user successfully logged in: ${userWithToken.username}', 
            name: 'UserProvider', level: 1000);
          developer.log('isAdminPlatform = ${userWithToken.isAdminPlatform}',
            name: 'UserProvider', level: 1000);
        } else {
          developer.log('Regular user successfully logged in: ${userWithToken.username}', 
            name: 'UserProvider');
        }
        
        state = AsyncValue.data(userWithToken);
        _onLoginSuccess?.call();
      } catch (e, stackTrace) {
        // Error fetching profile AFTER successful login
        _token = null; // Invalidate token as profile fetch failed
        developer.log('Error fetching profile after login: $e', 
          name: 'UserProvider', level: 1000, error: e, stackTrace: stackTrace);
          
        state = AsyncValue.error(
          'Profil bilgileri alınamadı: $e', // More specific error
          stackTrace,
        );
      }
    } catch (e) {
      final msg = e.toString();
      if (msg.contains('2FA kodu gerekli')) {
        _awaiting2FA = true;
        _pendingUsername = username;
        _pendingPassword = password;
        state = AsyncValue.error('2FA kodu gerekli. Lütfen kodu girin.', StackTrace.current);
        _on2FA?.call();
      } else {
        state = AsyncValue.error('Giriş başarısız: $e', StackTrace.current);
      }
    }
  }

  /// 2FA kodu ile devam et
  Future<void> submit2FA(String code, {OnLoginSuccess? onLoginSuccess}) async {
    if (_pendingUsername != null && _pendingPassword != null) {
      await login(_pendingUsername!, _pendingPassword!, verificationCode: code, onLoginSuccess: onLoginSuccess);
    }
  }

  /// Çıkış yap
  Future<void> logout() async {
    _token = null;
    _awaiting2FA = false;
    _pendingUsername = null;
    _pendingPassword = null;
    state = const AsyncValue.data(null);
  }

  /// Kullanıcı profilini yeniden yükle
  Future<void> refreshProfile() async {
    if (_token == null) return;
    try {
      final profileData = await _authService!.getProfile(_token!);
      developer.log('Profile refresh response: $profileData', name: 'UserProvider');

      // diamondBalance ve coin_balance mappingini garanti altına al
      int? diamondBalance;
      if (profileData['diamondBalance'] != null) {
        diamondBalance = (profileData['diamondBalance'] as num?)?.toInt();
      } else if (profileData['coin_balance'] != null) {
        diamondBalance = (profileData['coin_balance'] as num?)?.toInt();
      }
      if (diamondBalance != null) {
        profileData['coin_balance'] = diamondBalance;
        profileData['diamondBalance'] = diamondBalance;
      }

      final userWithoutToken = User.fromJson(profileData);
      final userWithToken = userWithoutToken.copyWith(token: _token);
      state = AsyncValue.data(userWithToken);
      developer.log('Profile refreshed: diamondBalance=${userWithToken.diamondBalance}', name: 'UserProvider');
    } catch (e, stackTrace) {
      developer.log('Error refreshing profile: $e', name: 'UserProvider', error: e, stackTrace: stackTrace);
      if (state.value == null) {
        state = AsyncValue.error('Profil güncellenemedi: $e', stackTrace);
      }
    }
  }

  /// Set user directly (for Instagram login)
  void setUser(User user) {
    state = AsyncValue.data(user);
    _token = user.token;
  }
  
  /// Set user from challenge result (for Instagram challenge completion)
  Future<void> setUserFromChallengeResult(User user, String token) async {
    // Null safety validation
    if (token.isEmpty) {
      developer.log('Error: Empty token provided to setUserFromChallengeResult', 
        name: 'UserProvider', level: 1000);
      throw ArgumentError('Token cannot be empty');
    }
    
    // Validate user object has required fields
    if (user.username.isEmpty) {
      developer.log('Error: User object missing required username', 
        name: 'UserProvider', level: 1000);
      throw ArgumentError('User object must have a valid username');
    }
    
    _token = token;
    state = AsyncValue.data(user.copyWith(token: token));
    
    developer.log('User set from challenge result: ${user.username}', 
      name: 'UserProvider');
    developer.log('Is admin: ${user.isAdminPlatform}', 
      name: 'UserProvider');
  }

  bool get awaiting2FA => _awaiting2FA;
}
