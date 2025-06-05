import 'api_client.dart';
import '../models/task.dart';
import 'dart:developer' as developer;
import 'dart:convert';

/// Görevlerle ilgili API işlemleri
class TaskService {
  final ApiClient _apiClient;
  TaskService(this._apiClient);

  /// Kullanıcıya atanmış görevleri getir
  Future<List<Task>> getTasks(String token) async {
    final dynamic responseData = await _apiClient.get('/tasks', token: token);

    developer.log(
      'TaskService.getTasks: responseData runtimeType: ${responseData.runtimeType}',
      name: 'TaskService',
    );
    // Be careful with logging potentially large responses in production
    // For debugging, converting to JSON string can be helpful if it's complex
    String responseDataString = 'Could not convert to string';
    try {
      if (responseData is Map || responseData is List) {
        responseDataString = jsonEncode(responseData);
      } else {
        responseDataString = responseData.toString();
      }
    } catch (e) {
      responseDataString = 'Error encoding responseData: $e';
    }
    developer.log(
      'TaskService.getTasks: responseData content: $responseDataString',
      name: 'TaskService',
    );

    // The API now returns a List<dynamic> directly.
    if (responseData is List) {
      return responseData
          .map((taskJson) => Task.fromJson(taskJson as Map<String, dynamic>))
          .toList();
    } else {
      // Handle unexpected response format, though API should always return a list for /tasks
      throw Exception('Görevler yüklenemedi: Beklenmeyen yanıt formatı.');
    }
  }

  /// Görev tamamla
  Future<bool> completeTask(int taskId, String token) async {
    final response = await _apiClient.post(
      '/tasks/complete',
      {'task_id': taskId},
      token: token,
    );
    return response['success'] == true;
  }
}
