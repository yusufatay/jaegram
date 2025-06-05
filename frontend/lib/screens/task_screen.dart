// Görev ekranı için şablon dosyadır.
// Buraya görev detayları ve tamamla butonu ileride eklenecektir.
// Tüm metinler ve arayüz Türkçe olacak şekilde tasarlanacaktır.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:instagram_puan_app/providers/task_provider.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';

class TaskScreen extends ConsumerWidget {
  const TaskScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final taskAsync = ref.watch(taskListProvider);
    final taskNotifier = ref.read(taskListProvider.notifier);

    bool hasActiveTask(List<Map<String, dynamic>> tasks) {
      return tasks.any((t) => t['status'] == 'assigned');
    }

    return Scaffold(
      appBar: AppBar(title: Text(AppLocalizations.of(context)!.tasks)),
      body: RefreshIndicator(
        onRefresh: () => ref.read(taskListProvider.notifier).refreshTasks(),
        child: taskAsync.when(
          data: (tasks) => Column(
            children: [
              if (!hasActiveTask(tasks))
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.add_task),
                      label: Text(AppLocalizations.of(context)!.takeNewTask),
                      onPressed: () async {
                        // Butona basıldığında bir yükleniyor göstergesi eklenebilir (opsiyonel)
                        // Örneğin, bir state variable ile butonun text'ini değiştirebilir veya
                        // küçük bir progress indicator gösterebilirsiniz.

                        final bool success = await taskNotifier.takeTask();

                        if (success) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(AppLocalizations.of(context)!.taskTakenSuccess)),
                          );
                        } else {
                          // taskNotifier.takeTask() zaten state'i AsyncError olarak ayarladı.
                          // taskAsync.when(...) içindeki error builder bu hatayı gösterecektir.
                          // İsteğe bağlı olarak burada ek bir snackbar da gösterebilirsiniz,
                          // ama genellikle provider state'inin UI'ı güncellemesi tercih edilir.
                          // Örneğin:
                          // ScaffoldMessenger.of(context).showSnackBar(
                          //   SnackBar(content: Text(AppLocalizations.of(context)!.taskTakeFailedGeneral)),
                          // );
                        }
                        // Eski try-catch bloğu kaldırıldı çünkü takeTask artık exception fırlatmıyor.
                      },
                    ),
                  ),
                ),
              Expanded(
                child: tasks.isEmpty
                    ? Center(child: Text(AppLocalizations.of(context)!.noAssignedTask))
                    : ListView.builder(
                        itemCount: tasks.length,
                        itemBuilder: (context, index) {
                          final task = tasks[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            child: ListTile(
                              leading: Icon(
                                task['status'] == 'completed' ? Icons.check_circle : Icons.task,
                                color: task['status'] == 'completed' ? Colors.green : Colors.orange,
                              ),
                              title: Text(
                                'Görev ID: ${task['id']} (Sipariş: ${task['order_id']})',
                                style: Theme.of(context).textTheme.titleSmall,
                              ),
                              subtitle: Text('Durum: ${task['status']}'),
                              trailing: ElevatedButton(
                                onPressed: task['status'] == 'completed'
                                    ? null
                                    : () => ref.read(taskListProvider.notifier).completeTask(task['id'] as int),
                                child: Text(AppLocalizations.of(context)!.complete),
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(
            child: SelectableText.rich(
              TextSpan(
                text: 'Hata: ',
                style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                children: [
                  TextSpan(text: e.toString(), style: const TextStyle(color: Colors.red)),
                ],
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ),
    );
  }
}
