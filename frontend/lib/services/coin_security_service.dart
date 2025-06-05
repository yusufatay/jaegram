import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/coin_withdrawal.dart';
import '../utils/api_constants.dart';

class CoinSecurityService {
  final String baseUrl = ApiConstants.baseUrl;

  // Withdrawal Methods
  Future<List<String>> getAvailableWithdrawalMethods(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/coins/withdrawal-methods'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return List<String>.from(jsonDecode(response.body));
    }
    throw Exception('Failed to load withdrawal methods');
  }

  // Security Validation
  Future<Map<String, dynamic>> validateWithdrawal(String token, int amount, String method) async {
    final response = await http.post(
      Uri.parse('$baseUrl/coins/validate-withdrawal'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'amount': amount,
        'withdrawal_method': method,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to validate withdrawal');
  }

  // Withdrawal Request
  Future<CoinWithdrawalRequest> requestWithdrawal(
    String token,
    int amount,
    String method,
    Map<String, dynamic>? bankAccountInfo,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/coins/request-withdrawal'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'amount': amount,
        'withdrawal_method': method,
        'bank_account_info': bankAccountInfo,
      }),
    );

    if (response.statusCode == 200) {
      return CoinWithdrawalRequest.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to request withdrawal');
  }

  // Get Withdrawal History
  Future<List<CoinWithdrawalRequest>> getWithdrawalHistory(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/coins/withdrawal-history'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => CoinWithdrawalRequest.fromJson(json)).toList();
    }
    throw Exception('Failed to load withdrawal history');
  }

  // Cancel Withdrawal
  Future<bool> cancelWithdrawal(String token, int withdrawalId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/coins/cancel-withdrawal/$withdrawalId'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  // Security Settings
  Future<Map<String, dynamic>> getSecuritySettings(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/coins/security-settings'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load security settings');
  }

  Future<bool> updateSecuritySettings(String token, Map<String, dynamic> settings) async {
    final response = await http.put(
      Uri.parse('$baseUrl/coins/security-settings'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(settings),
    );

    return response.statusCode == 200;
  }

  // Two-Factor Authentication
  Future<bool> enableTwoFactor(String token) async {
    final response = await http.post(
      Uri.parse('$baseUrl/coins/enable-2fa'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  Future<bool> verifyTwoFactor(String token, String code) async {
    final response = await http.post(
      Uri.parse('$baseUrl/coins/verify-2fa'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'code': code}),
    );

    return response.statusCode == 200;
  }

  // Anti-Fraud
  Future<Map<String, dynamic>> getFraudDetectionStatus(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/coins/fraud-status'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load fraud detection status');
  }

  // Minimum Withdrawal Info
  Future<Map<String, dynamic>> getWithdrawalInfo(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/coins/withdrawal-info'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load withdrawal info');
  }
}
