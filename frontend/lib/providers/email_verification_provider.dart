import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../models/email_verification.dart';
import '../providers/user_provider.dart';

class EmailVerificationService {
  final ApiClient _apiClient;

  EmailVerificationService(this._apiClient);

  Future<EmailVerificationResponse> sendVerificationEmail(String email, String token) async {
    final response = await _apiClient.post('/send-verification-email', {'email': email}, token: token);
    return EmailVerificationResponse.fromJson(response);
  }

  Future<EmailVerificationResponse> verifyEmail(String verificationCode, String token) async {
    final response = await _apiClient.post('/verify-email', {'verification_code': verificationCode}, token: token);
    return EmailVerificationResponse.fromJson(response);
  }
}

final emailVerificationServiceProvider = Provider<EmailVerificationService>((ref) {
  final apiClient = ref.read(apiClientProvider);
  return EmailVerificationService(apiClient);
});

class EmailVerificationNotifier extends StateNotifier<AsyncValue<void>> {
  final EmailVerificationService _service;
  final Ref _ref;

  EmailVerificationNotifier(this._service, this._ref) : super(const AsyncValue.data(null));

  Future<EmailVerificationResponse> sendVerificationEmail(String email) async {
    final userAsync = _ref.read(userProvider);
    final user = userAsync.value;
    
    if (user?.token == null) throw Exception('Kullanıcı oturumu bulunamadı');

    state = const AsyncValue.loading();
    
    try {
      final response = await _service.sendVerificationEmail(email, user!.token!);
      state = const AsyncValue.data(null);
      return response;
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      rethrow;
    }
  }

  Future<EmailVerificationResponse> verifyEmail(String verificationCode) async {
    final userAsync = _ref.read(userProvider);
    final user = userAsync.value;
    
    if (user?.token == null) throw Exception('Kullanıcı oturumu bulunamadı');

    state = const AsyncValue.loading();
    
    try {
      final response = await _service.verifyEmail(verificationCode, user!.token!);
      
      // Update user profile to reflect email verification
      await _ref.read(userProvider.notifier).refreshProfile();
      
      state = const AsyncValue.data(null);
      return response;
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      rethrow;
    }
  }
}

final emailVerificationProvider = StateNotifierProvider<EmailVerificationNotifier, AsyncValue<void>>((ref) {
  final service = ref.read(emailVerificationServiceProvider);
  return EmailVerificationNotifier(service, ref);
});
