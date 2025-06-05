import 'api_client.dart';
import '../models/diamond.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

/// Diamond (puan) ile ilgili API işlemleri
class DiamondService {
  final ApiClient _apiClient;
  static const String baseUrl = 'https://jaegram-production.up.railway.app';
  
  DiamondService(this._apiClient);

  /// Kullanıcının diamond bakiyesini getir
  Future<Diamond> getDiamond(String token) async {
    final response = await _apiClient.get('/coins', token: token);
    return Diamond.fromJson(response['coin'] as Map<String, dynamic>);
  }

  /// Diamond transfer işlemi
  Future<bool> transferDiamonds({
    required String token,
    required String recipientUsername,
    required int amount,
    String? note,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/coins/transfer'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'recipient_username': recipientUsername,
          'amount': amount,
          'note': note,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] ?? false;
      }
      
      return false;
    } catch (e) {
      debugPrint('Diamond transfer error: $e');
      return false;
    }
  }

  /// Transfer geçmişini getir
  Future<List<Map<String, dynamic>>> getTransferHistory({
    required String token,
    int? limit,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/coins/transfer-history');
      final uriWithParams = limit != null 
          ? uri.replace(queryParameters: {'limit': limit.toString()})
          : uri;

      final response = await http.get(
        uriWithParams,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['transfers'] ?? []);
      }
      
      return [];
    } catch (e) {
      debugPrint('Transfer history error: $e');
      return [];
    }
  }

  /// Diamond bakiyesini kontrol et
  Future<Map<String, dynamic>?> getDiamondBalance({required String token}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/coins/balance'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      
      return null;
    } catch (e) {
      debugPrint('Get balance error: $e');
      return null;
    }
  }

  /// Diamond kullanım işlemi
  Future<bool> redeemDiamonds({
    required String token,
    required String rewardType,
    required int amount,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/coins/redeem'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'reward_type': rewardType,
          'amount': amount,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] ?? false;
      }
      
      return false;
    } catch (e) {
      debugPrint('Diamond redemption error: $e');
      return false;
    }
  }
}
