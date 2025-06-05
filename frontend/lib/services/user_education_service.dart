import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_education.dart';
import '../utils/api_constants.dart';

class UserEducationService {
  final String baseUrl = ApiConstants.baseUrl;

  // Get Available Modules
  Future<List<EducationModule>> getAvailableModules(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/modules'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => EducationModule.fromJson(json)).toList();
    }
    throw Exception('Failed to load education modules');
  }

  // Get User Progress
  Future<List<UserEducation>> getUserProgress(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/progress'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => UserEducation.fromJson(json)).toList();
    }
    throw Exception('Failed to load user progress');
  }

  // Start Module
  Future<UserEducation> startModule(String token, String moduleId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/education/start'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'module_id': moduleId}),
    );

    if (response.statusCode == 200) {
      return UserEducation.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to start module');
  }

  // Update Progress
  Future<UserEducation> updateProgress(
    String token,
    String moduleId,
    double progressPercentage,
    int timeSpentMinutes,
  ) async {
    final response = await http.put(
      Uri.parse('$baseUrl/education/progress'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'module_id': moduleId,
        'progress_percentage': progressPercentage,
        'time_spent_minutes': timeSpentMinutes,
      }),
    );

    if (response.statusCode == 200) {
      return UserEducation.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to update progress');
  }

  // Complete Module
  Future<UserEducation> completeModule(
    String token,
    String moduleId,
    List<int> quizAnswers,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/education/complete'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'module_id': moduleId,
        'quiz_answers': quizAnswers,
      }),
    );

    if (response.statusCode == 200) {
      return UserEducation.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to complete module');
  }

  // Get Module Content
  Future<EducationModule> getModuleContent(String token, String moduleId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/modules/$moduleId'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return EducationModule.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load module content');
  }

  // Get Recommendations
  Future<List<EducationModule>> getRecommendedModules(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/recommendations'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => EducationModule.fromJson(json)).toList();
    }
    throw Exception('Failed to load recommended modules');
  }

  // Get User Statistics
  Future<Map<String, dynamic>> getEducationStats(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/stats'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load education statistics');
  }

  // Search Modules
  Future<List<EducationModule>> searchModules(String token, String query) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/search?q=${Uri.encodeComponent(query)}'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => EducationModule.fromJson(json)).toList();
    }
    throw Exception('Failed to search modules');
  }

  // Get Certificates
  Future<List<Map<String, dynamic>>> getCertificates(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/certificates'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    }
    throw Exception('Failed to load certificates');
  }

  // Get Module by Category
  Future<List<EducationModule>> getModulesByCategory(String token, String category) async {
    final response = await http.get(
      Uri.parse('$baseUrl/education/modules/category/$category'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => EducationModule.fromJson(json)).toList();
    }
    throw Exception('Failed to load modules by category');
  }
}
