import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:instagram_puan_app/providers/user_provider.dart';
import 'package:instagram_puan_app/themes/app_theme.dart';
import 'package:instagram_puan_app/widgets/gradient_button.dart';
import 'package:instagram_puan_app/services/statistics_service.dart';

class StatisticsScreen extends ConsumerWidget {
  const StatisticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final localizations = AppLocalizations.of(context)!;
    final statisticsAsync = ref.watch(statisticsProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.statistics),
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
          ),
        ),
      ),
      body: statisticsAsync.when(
        data: (statistics) => _buildStatisticsContent(context, localizations, statistics),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('İstatistikler yüklenemedi: $error'),
              const SizedBox(height: 16),
              GradientButton(
                text: 'Yeniden Dene',
                onPressed: () {
                  ref.refresh(statisticsProvider);
                  ref.refresh(userProvider);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatisticsContent(BuildContext context, AppLocalizations localizations, Map<String, dynamic> statistics) {
    final weeklyEarningsData = List<int>.from(statistics['weekly_earnings'] ?? [0, 0, 0, 0, 0, 0, 0]);
    final taskDistributionRaw = Map<String, dynamic>.from(statistics['task_distribution'] ?? {});
    final taskDistribution = Map<String, double>.fromEntries(
      taskDistributionRaw.entries.map((entry) => MapEntry(entry.key, (entry.value as num).toDouble()))
    );
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Özet Kartları
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  context,
                  'Toplam Kazanç',
                  '${statistics['total_earnings'] ?? 0} Diamond',
                  Icons.diamond,
                  AppTheme.primaryGradient,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  context,
                  'Tamamlanan',
                  '${statistics['completed_tasks'] ?? 0}',
                  Icons.check_circle,
                  AppTheme.instagramGradient,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  context,
                  'Aktif Görevler',
                  '${statistics['active_tasks'] ?? 0}',
                  Icons.pending_actions,
                  const LinearGradient(
                    colors: [Colors.orange, Colors.deepOrange],
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  context,
                  'Günlük Seri',
                  '${statistics['daily_streak'] ?? 0} Gün',
                  Icons.local_fire_department,
                  const LinearGradient(
                    colors: [Colors.red, Colors.pink],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Haftalık Kazanç Grafiği
          Text(
            'Haftalık Kazanç Trendi',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            height: 200,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withValues(alpha: 0.1),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: (weeklyEarningsData.reduce((a, b) => a > b ? a : b).toDouble() * 1.2),
                barTouchData: BarTouchData(enabled: false),
                titlesData: FlTitlesData(
                  show: true,
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        const days = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
                        return Text(
                          days[value.toInt() % 7],
                          style: const TextStyle(fontSize: 12),
                        );
                      },
                    ),
                  ),
                  leftTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                borderData: FlBorderData(show: false),
                barGroups: weeklyEarningsData.asMap().entries.map((entry) {
                  return BarChartGroupData(
                    x: entry.key,
                    barRods: [
                      BarChartRodData(
                        toY: entry.value.toDouble(),
                        color: AppTheme.primaryGradient.colors.first,
                        width: 16,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Görev Dağılımı
          Text(
            'Görev Dağılımı',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            height: 200,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withValues(alpha: 0.1),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: PieChart(
              PieChartData(
                sections: [
                  PieChartSectionData(
                    color: AppTheme.instagramGradient.colors.first,
                    value: taskDistribution['like'] ?? 0,
                    title: 'Beğeni\n${(taskDistribution['like'] ?? 0).toStringAsFixed(1)}%',
                    radius: 60,
                    titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  PieChartSectionData(
                    color: AppTheme.instagramGradient.colors.last,
                    value: taskDistribution['follow'] ?? 0,
                    title: 'Takip\n${(taskDistribution['follow'] ?? 0).toStringAsFixed(1)}%',
                    radius: 60,
                    titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  PieChartSectionData(
                    color: Colors.purple,
                    value: taskDistribution['comment'] ?? 0,
                    title: 'Yorum\n${(taskDistribution['comment'] ?? 0).toStringAsFixed(1)}%',
                    radius: 60,
                    titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  PieChartSectionData(
                    color: Colors.orange,
                    value: taskDistribution['other'] ?? 0,
                    title: 'Diğer\n${(taskDistribution['other'] ?? 0).toStringAsFixed(1)}%',
                    radius: 60,
                    titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
                centerSpaceRadius: 0,
                sectionsSpace: 2,
              ),
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildStatCard(BuildContext context, String title, String value, IconData icon, Gradient gradient) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: gradient.colors.first.withValues(alpha: 0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 8),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
