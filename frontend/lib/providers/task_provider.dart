import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import './user_provider.dart';

/// Görevlerin state yönetimi için Riverpod provider.
final taskListProvider = AsyncNotifierProvider<TaskListNotifier, List<Map<String, dynamic>>>(TaskListNotifier.new);

class TaskListNotifier extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  Future<List<Map<String, dynamic>>> build() async {
    ref.watch(userProvider);
    return await fetchTasks();
  }

  Future<List<Map<String, dynamic>>> fetchTasks() async {
    final apiClient = ref.read(apiClientProvider);
    final userNotifier = ref.read(userProvider.notifier);
    final token = userNotifier.token;

    if (token == null) {
      throw Exception('Kullanıcı token bulunamadı. Görevler yüklenemiyor.');
    }

    try {
      final result = await apiClient.getList('/tasks', token: token);
      return result;
    } catch (e) {
      throw Exception('Görevler yüklenemedi: $e');
    }
  }

  /// Görevleri yenile
  Future<void> refreshTasks() async {
    state = const AsyncValue.loading();
    try {
      final tasks = await fetchTasks();
      state = AsyncValue.data(tasks);
    } catch (e) {
      state = AsyncValue.error('Görevler yüklenemedi: $e', StackTrace.current);
    }
  }

  /// Görev tamamla
  Future<void> completeTask(int taskId) async {
    final token = ref.read(userProvider.notifier).token;
    if (token == null) {
      state = AsyncValue.error('Görev tamamlanamadı: Kullanıcı token bulunamadı.', StackTrace.current);
      return;
    }
    state = const AsyncValue.loading();
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.post('/complete-task', {'task_id': taskId}, token: token);
      await refreshTasks();
    } catch (e) {
      state = AsyncValue.error('Görev tamamlanamadı: $e', StackTrace.current);
    }
  }

  /// Görev al
  Future<bool> takeTask() async { 
    final token = ref.read(userProvider.notifier).token;
    if (token == null) {
      state = AsyncValue.error('Görev alınamadı: Kullanıcı token bulunamadı.', StackTrace.current);
      return false; 
    }
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.post('/take-task', {}, token: token);
      await refreshTasks(); 
      return true; 
    } catch (e) {
      String errorMessage = 'Görev alınamadı. Bir sorun oluştu.';
      // The exception from ApiClient will be like "Exception: Sunucu hatası: <actual_detail_from_server>"
      if (e is Exception && e.toString().contains('Şu anda size uygun boş görev bulunmamaktadır.')) { 
        errorMessage = 'Şu anda size uygun boş görev bulunmamaktadır.';
      }
      state = AsyncValue.error(errorMessage, StackTrace.current);
      return false; 
    }
  }
}
