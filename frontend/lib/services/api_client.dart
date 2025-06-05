import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Tüm API çağrıları için temel client.
/// Hata yönetimi ve ortak base url burada tanımlanır.
class ApiClient {
  static const String baseUrl = 'https://jaegram-production.up.railway.app'; // Railway backend URL
  final http.Client _client;

  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  Future<Map<String, dynamic>> get(String endpoint, {String? token}) async {
    final response = await _client.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        if (token != null) 'Authorization': 'Bearer $token',
      },
    );
    return _handleResponse(response);
  }

  Future<List<Map<String, dynamic>>> getList(String endpoint, {String? token}) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }

    final response = await _client.get(url, headers: headers);
    return _handleListResponse(response);
  }

  Future<Map<String, dynamic>> post(String endpoint, Map<String, dynamic> data, {String? token}) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }

    final response = await _client.post(url, headers: headers, body: jsonEncode(data));
    return _handleResponse(response);
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>; // Expects a Map
    } else {
      // Handle API error
      String detail = 'API Hatası: ${response.statusCode}';
      try {
        final data = jsonDecode(response.body);
        if (data is Map && data['detail'] != null) {
          detail = data['detail'].toString();
        }
      } catch (_) {}
      throw Exception('Sunucu hatası: $detail');
    }
  }

  List<Map<String, dynamic>> _handleListResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final decoded = jsonDecode(response.body);
      if (decoded is List) {
        return decoded.cast<Map<String, dynamic>>();
      } else {
        // Handle unexpected response format
        if (decoded is Map<String, dynamic>) { // If backend mistakenly sent a map instead of list
          return [decoded]; 
        }
        throw Exception('API Hatası: Beklenen liste formatı değil, gelen: ${decoded.runtimeType}');
      }
    } else {
      // Handle API error for list requests
      String detail = 'API Hatası (Liste): ${response.statusCode}';
      try {
        final data = jsonDecode(response.body);
        if (data is Map && data.containsKey('detail')) {
          detail = data['detail'].toString();
        }
      } catch (e) {
        // If body is not JSON or 'detail' key is missing
      }
      throw Exception('Sunucu hatası (Liste): $detail');
    }
  }
}

// Global ApiClient provider
final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
