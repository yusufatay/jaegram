import 'dart:convert';
import 'dart:developer' as developer;
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/instagram_integration.dart';
import '../utils/api_constants.dart';

class InstagramService {
  final String baseUrl = ApiConstants.baseUrl;

  // Instagram Direct Login (for initial login flow)
  Future<Map<String, dynamic>> loginInstagram(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login-instagram'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      final responseData = jsonDecode(response.body);
      developer.log('Instagram Login Response: $responseData', name: 'InstagramService');
      developer.log('User type check 1: ${responseData['is_admin_platform'] == true ? 'Admin' : 'Regular User'}', name: 'InstagramService', level: 1000);
      developer.log('User type check 2: ${responseData['user_data']?['is_admin'] == true ? 'Admin' : 'Regular User'}', name: 'InstagramService', level: 1000);
      developer.log('Login status code: ${response.statusCode}', name: 'InstagramService');
      
      if (response.statusCode == 200) {
        // Check if it's a challenge response
        if (responseData['challenge_required'] == true || responseData['requires_challenge'] == true) {
          // Extract contact point from challenge details
          final challengeDetails = responseData['challenge_details'] ?? {};
          final stepData = challengeDetails['step_data'] ?? {};
          final contactPoint = stepData['contact_point'] ?? responseData['contact_point'] ?? '';
          final formType = stepData['form_type'] ?? 'email';
          
          return {
            'success': false,
            'requires_challenge': true,
            'challenge_info': {
              'challenge_url': responseData['challenge_url'],
              'challenge_details': responseData['challenge_details'] ?? responseData['challenge_info'],
              'username': responseData['username'] ?? username,
              'message': responseData['message'],
              'challenge_type': formType,
              'contact_point': contactPoint,
              'step_name': challengeDetails['step_name'] ?? 'verify_email',
              'nonce_code': challengeDetails['nonce_code'] ?? '',
              'challenge_context': challengeDetails['challenge_context'] ?? '',
            },
            'error': responseData['message'] ?? 'Challenge required',
          };
        } else {
          // Check if this is an admin login response
          final isAdmin = responseData['user_data'] != null && responseData['user_data']['is_admin'] == true;
          
          // For admin users, make sure is_admin_platform flag is set properly
          if (isAdmin) {
            responseData['is_admin_platform'] = true;
            developer.log('Admin user detected in response', name: 'InstagramService', level: 1000);
          }
          
          // Normal successful login
          return {
            'success': true,
            'access_token': responseData['access_token'],
            'user_data': responseData,
            'is_admin_platform': isAdmin,
          };
        }
      } else if (response.statusCode == 400) {
        // Enhanced error handling for different error types
        final detail = responseData['detail'] ?? '';
        final errorType = responseData['error_type'] ?? '';
        
        // Check if it's a challenge requirement
        if (detail.toLowerCase().contains('challenge') || 
            detail.toLowerCase().contains('doğrulama') ||
            errorType == 'challenge_required') {
          return {
            'success': false,
            'requires_challenge': true,
            'challenge_info': {
              'challenge_url': responseData['challenge_url'],
              'challenge_details': responseData['challenge_details'] ?? responseData['challenge_info'],
              'username': responseData['username'] ?? username,
              'message': responseData['message'] ?? detail,
              'challenge_type': responseData['challenge_type'] ?? 'email',
              'contact_point': responseData['contact_point'] ?? '',
            },
            'error': detail,
          };
        } else {
          // Handle specific error types
          String userFriendlyError = detail;
          switch (errorType) {
            case 'invalid_credentials':
              userFriendlyError = 'Kullanıcı adı veya şifre hatalı';
              break;
            case 'account_suspended':
              userFriendlyError = 'Instagram hesabınız askıya alınmış';
              break;
            case 'rate_limited':
              userFriendlyError = 'Çok fazla deneme. Lütfen daha sonra tekrar deneyin';
              break;
            case 'connection_error':
              userFriendlyError = 'Instagram\'a bağlanılamıyor. İnternet bağlantınızı kontrol edin';
              break;
            case 'two_factor_required':
              userFriendlyError = 'İki faktörlü doğrulama gerekli';
              break;
          }
          
          return {
            'success': false,
            'requires_challenge': false,
            'error': userFriendlyError,
            'error_type': errorType,
          };
        }
      } else {
        return {
          'success': false,
          'requires_challenge': false,
          'error': responseData['detail'] ?? 'Instagram giriş başarısız',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'requires_challenge': false,
        'error': 'Bağlantı hatası: $e',
      };
    }
  }

  // Submit Instagram Challenge
  Future<Map<String, dynamic>> submitInstagramChallenge(
    String username, 
    String password, 
    String challengeCode
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login-instagram-challenge'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'password': password,
          'challenge_code': challengeCode,
        }),
      );

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {
          'success': true,
          'access_token': responseData['access_token'],
          'user_data': responseData,
          'message': responseData['message'] ?? 'Instagram girişi başarılı',
        };
      } else {
        // Enhanced error handling for challenge submission
        final detail = responseData['detail'] ?? 'Challenge doğrulama başarısız';
        String userFriendlyError = detail;
        
        if (detail.toLowerCase().contains('geçersiz')) {
          userFriendlyError = 'Geçersiz doğrulama kodu. Lütfen tekrar deneyin.';
        } else if (detail.toLowerCase().contains('süresi')) {
          userFriendlyError = 'Doğrulama kodunun süresi dolmuş. Yeni kod isteyin.';
        } else if (detail.toLowerCase().contains('deneme')) {
          userFriendlyError = detail; // Already user-friendly from backend
        }
        
        return {
          'success': false,
          'error': userFriendlyError,
          'attempts_remaining': _extractAttemptsFromError(detail),
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Bağlantı hatası: $e',
      };
    }
  }

  // Helper method to extract remaining attempts from error message
  int? _extractAttemptsFromError(String errorMessage) {
    final regex = RegExp(r'\(Deneme (\d+)/(\d+)\)');
    final match = regex.firstMatch(errorMessage);
    if (match != null) {
      final current = int.parse(match.group(1)!);
      final total = int.parse(match.group(2)!);
      return total - current;
    }
    return null;
  }

  // Instagram Account Verification
  Future<bool> connectInstagram(String token, String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/connect'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    return response.statusCode == 200;
  }

  Future<bool> disconnectInstagram(String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/disconnect'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  // Profile Information
  Future<InstagramProfile?> getProfile(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/profile'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return InstagramProfile.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 404) {
      return null; // No Instagram account connected
    }
    throw Exception('Failed to load Instagram profile');
  }

  Future<InstagramProfile> syncProfile(String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/sync-profile'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return InstagramProfile.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to sync Instagram profile');
  }

  // Posts Management
  Future<List<InstagramPost>> getPosts(String token, {int limit = 20}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/posts?limit=$limit'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => InstagramPost.fromJson(json)).toList();
    }
    throw Exception('Failed to load Instagram posts');
  }

  Future<List<InstagramPost>> syncPosts(String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/sync-posts'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => InstagramPost.fromJson(json)).toList();
    }
    throw Exception('Failed to sync Instagram posts');
  }

  // Credential Status
  Future<InstagramCredential?> getCredentialStatus(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/credential-status'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return InstagramCredential.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 404) {
      return null; // No credentials found
    }
    throw Exception('Failed to load credential status');
  }

  // Verification
  Future<bool> verifyAccount(String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/verify'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  // Instagram Analytics
  Future<Map<String, dynamic>> getAnalytics(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/analytics'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load Instagram analytics');
  }

  // Task Validation
  Future<bool> validateTaskCompletion(String token, int taskId, String postUrl) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/validate-task'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'task_id': taskId,
        'post_url': postUrl,
      }),
    );

    return response.statusCode == 200;
  }

  // Auto-sync Settings
  Future<Map<String, dynamic>> getSyncSettings(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/sync-settings'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load sync settings');
  }

  Future<bool> updateSyncSettings(String token, Map<String, dynamic> settings) async {
    final response = await http.put(
      Uri.parse('$baseUrl/instagram/sync-settings'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(settings),
    );

    return response.statusCode == 200;
  }

  // Error Handling
  Future<List<Map<String, dynamic>>> getSyncErrors(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/sync-errors'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    }
    throw Exception('Failed to load sync errors');
  }

  Future<bool> clearSyncErrors(String token) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/instagram/sync-errors'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  // Challenge Management Methods
  
  // Get challenge status for a username
  Future<Map<String, dynamic>> getChallengeStatus(String username) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/instagram/challenge-status/$username'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get challenge status');
      }
    } catch (e) {
      throw Exception('Error getting challenge status: $e');
    }
  }

  // Clear challenge data for a username
  Future<bool> clearChallenge(String username) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/instagram/challenge/$username'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      throw Exception('Error clearing challenge: $e');
    }
  }

  // Resend challenge code (for existing challenges)
  Future<bool> resendChallenge(String userToken, String challengeId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/instagram/resend-challenge'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $userToken',
        },
        body: jsonEncode({
          'challenge_id': challengeId,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      throw Exception('Error resending challenge: $e');
    }
  }

  // Resolve regular challenges (not login challenges)
  Future<bool> resolveChallenge(String userToken, String challengeId, String code) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/instagram/resolve-challenge'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $userToken',
        },
        body: jsonEncode({
          'challenge_id': challengeId,
          'code': code,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      throw Exception('Error resolving challenge: $e');
    }
  }

  // Enhanced Connection Management
  Future<InstagramConnectionStatus> getConnectionStatus(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/connection-status'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return InstagramConnectionStatus.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load connection status');
  }

  Future<InstagramConnectionStatus> connectInstagramWithChallenge(
    String token, 
    String username, 
    String password
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/connect-enhanced'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      return InstagramConnectionStatus.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 202) {
      // Challenge required
      return InstagramConnectionStatus.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to connect Instagram account');
  }

  /// Validates a task by calling the backend /complete-task endpoint.
  /// Returns a rich InstagramTaskValidation object for UI feedback.
  Future<InstagramTaskValidation> validateTask(
    String token,
    int taskId,
    String postUrl, // Not used by backend, kept for interface compatibility
    {String? taskType}
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/complete-task'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'task_id': taskId,
        }),
      );

      final now = DateTime.now();
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return InstagramTaskValidation(
          taskId: taskId,
          isValid: true,
          validationStatus: 'success',
          coinsEarned: data['coin'] ?? 0,
          validatedAt: now,
          errorReason: null,
        );
      } else {
        // Try to parse backend error for user-friendly feedback
        Map<String, dynamic> data = {};
        try {
          data = jsonDecode(response.body);
        } catch (_) {}
        String? errorMsg = data['detail'] ?? data['message'] ?? response.reasonPhrase;
        return InstagramTaskValidation(
          taskId: taskId,
          isValid: false,
          validationStatus: 'failed',
          coinsEarned: 0,
          validatedAt: now,
          errorReason: errorMsg ?? 'Task validation failed',
        );
      }
    } catch (e) {
      // Network or unexpected error
      return InstagramTaskValidation(
        taskId: taskId,
        isValid: false,
        validationStatus: 'error',
        coinsEarned: 0,
        validatedAt: DateTime.now(),
        errorReason: 'Ağ hatası veya beklenmedik hata: $e',
      );
    }
  }

  // Real-time Connection Testing
  Future<bool> testConnection(String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/instagram/test-connection'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  // Account Health Check
  Future<Map<String, dynamic>> getAccountHealth(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/instagram/account-health'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load account health');
  }

  /// Connect Instagram account
  Future<Map<String, dynamic>> connectAccount(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/connect-instagram'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to connect account');
    } catch (e) {
      throw Exception('Connection error: $e');
    }
  }

  /// Disconnect Instagram account
  Future<Map<String, dynamic>> disconnectAccount() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/disconnect-instagram'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception('Failed to disconnect account');
    } catch (e) {
      throw Exception('Disconnection error: $e');
    }
  }

  // Manual Instagram Login (Selenium-based visible browser)
  Future<Map<String, dynamic>> openManualInstagramLogin(String? username, String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/instagram/open-manual-login'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'username': username,
        }),
      );

      final responseData = jsonDecode(response.body);
      developer.log('Manual Instagram Login Open Response: $responseData', name: 'InstagramService');
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': responseData['message'] ?? 'Browser opened for manual login',
          'status': responseData['status'] ?? 'browser_opened',
          'instructions': responseData['instructions'],
        };
      } else {
        return {
          'success': false,
          'error': responseData['detail'] ?? 'Failed to open browser',
        };
      }
    } catch (e) {
      developer.log('Error opening manual Instagram login: $e', name: 'InstagramService');
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  // Check Manual Login Status
  Future<Map<String, dynamic>> checkManualLoginStatus(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/instagram/check-login-status'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      final responseData = jsonDecode(response.body);
      developer.log('Manual Login Status Response: $responseData', name: 'InstagramService');
      
      if (response.statusCode == 200) {
        return {
          'success': responseData['success'] ?? true,
          'status': responseData['status'],
          'message': responseData['message'],
          'user_data': responseData['user_data'],
          'session_cookies': responseData['session_cookies'],
          'challenge_info': responseData['challenge_info'],
          'current_url': responseData['current_url'],
        };
      } else {
        return {
          'success': false,
          'error': responseData['detail'] ?? 'Failed to check login status',
        };
      }
    } catch (e) {
      developer.log('Error checking manual login status: $e', name: 'InstagramService');
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  // Close Instagram Browser
  Future<Map<String, dynamic>> closeInstagramBrowser(String token) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/instagram/close-browser'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      final responseData = jsonDecode(response.body);
      developer.log('Close Browser Response: $responseData', name: 'InstagramService');
      
      return {
        'success': responseData['success'] ?? true,
        'message': responseData['message'] ?? 'Browser closed',
      };
    } catch (e) {
      developer.log('Error closing Instagram browser: $e', name: 'InstagramService');
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
}

// Provider for dependency injection
final instagramServiceProvider = Provider<InstagramService>((ref) {
  return InstagramService();
});
