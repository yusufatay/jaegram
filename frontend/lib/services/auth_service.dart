import 'dart:convert';
import 'dart:developer' as developer;
import 'package:http/http.dart' as http;
import 'api_client.dart';

/// Giriş ve oturum yönetimi için servis.
class AuthService {
  final ApiClient _apiClient;
  AuthService(this._apiClient);

  /// Instagram ile gerçek giriş (2FA destekli)
  Future<String> login(String username, String password, {String? verificationCode}) async {
    final body = 'username=$username&password=$password';
    final response = await http.post(
      Uri.parse('${ApiClient.baseUrl}/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: verificationCode != null && verificationCode.isNotEmpty
          ? '$body&verification_code=$verificationCode'
          : body,
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['access_token'] as String;
    } else {
      final data = jsonDecode(response.body);
      throw Exception(data['detail'] ?? 'Giriş başarısız: ${response.body}');
    }
  }

  /// Profil bilgisi çekme
  Future<Map<String, dynamic>> getProfile(String token) async {
    final response = await _apiClient.get('/profile', token: token);
    developer.log('AuthService - getProfile - Raw JSON response: $response', name: 'AuthService');
    
    if (response.containsKey('is_admin_platform') && response['is_admin_platform'] == true) {
      developer.log('Admin user detected! Admin flag is set to: ${response['is_admin_platform']}', name: 'AuthService', level: 1000);
    }
    
    return response;
  }
}
