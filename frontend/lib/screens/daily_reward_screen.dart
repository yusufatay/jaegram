import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/daily_reward_provider.dart';
import '../providers/user_provider.dart';

class DailyRewardScreen extends ConsumerStatefulWidget {
  const DailyRewardScreen({super.key});

  @override
  ConsumerState<DailyRewardScreen> createState() => _DailyRewardScreenState();
}

class _DailyRewardScreenState extends ConsumerState<DailyRewardScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );
    
    _rotationAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    // Fetch status on load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(dailyRewardProvider.notifier).fetchStatus();
    });
  }

  @override
  void dispose() {
    if (mounted) {
      _animationController.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dailyRewardAsync = ref.watch(dailyRewardProvider);
    final userAsync = ref.watch(userProvider);
    final user = userAsync.value;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Günlük Hediye'),
        centerTitle: true,
        elevation: 0,
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFFDD2A7B), Color(0xFF8134AF)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF8F9FA), Color(0xFFE9ECEF)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: dailyRewardAsync.when(
          data: (status) => _buildRewardContent(context, status, user),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error_outline, size: 64, color: Colors.grey[400]),
                const SizedBox(height: 16),
                Text(
                  'Hata: ${error.toString()}',
                  style: TextStyle(color: Colors.grey[600]),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.read(dailyRewardProvider.notifier).fetchStatus(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRewardContent(BuildContext context, status, user) {
    if (status == null) {
      return const Center(child: Text('Günlük hediye bilgisi yüklenemedi'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          // Current Balance Card
          Consumer(
            builder: (context, ref, child) {
              final userAsync = ref.watch(userProvider);
              final currentBalance = userAsync.value?.diamondBalance ?? 0;
              return _buildBalanceCard(currentBalance);
            },
          ),
          const SizedBox(height: 24),
          
          // Reward Box
          _buildRewardBox(status),
          const SizedBox(height: 24),
          
          // Streak Information
          _buildStreakInfo(status),
          const SizedBox(height: 24),
          
          // Claim Button
          _buildClaimButton(status),
          const SizedBox(height: 32),
          
          // Reward Schedule
          _buildRewardSchedule(),
        ],
      ),
    );
  }

  Widget _buildBalanceCard(int balance) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFDD2A7B), Color(0xFF8134AF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFDD2A7B).withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          const Icon(Icons.account_balance_wallet, color: Colors.white, size: 32),
          const SizedBox(height: 8),
          const Text(
            'Mevcut Bakiye',
            style: TextStyle(color: Colors.white70, fontSize: 16),
          ),
          const SizedBox(height: 4),
          Text(
            '$balance Elmas',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRewardBox(status) {
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Transform.rotate(
            angle: _rotationAnimation.value * 0.1,
            child: Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                gradient: status.canClaim
                    ? const LinearGradient(
                        colors: [Color(0xFFFFD700), Color(0xFFFFA500)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      )
                    : LinearGradient(
                        colors: [Colors.grey[300]!, Colors.grey[400]!],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: status.canClaim
                        ? const Color(0xFFFFD700).withValues(alpha: 0.5)
                        : Colors.grey.withValues(alpha: 0.3),
                    blurRadius: 30,
                    offset: const Offset(0, 15),
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    status.canClaim ? Icons.card_giftcard : Icons.schedule,
                    size: 64,
                    color: status.canClaim ? Colors.white : Colors.grey[600],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${status.nextReward}',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: status.canClaim ? Colors.white : Colors.grey[600],
                    ),
                  ),
                  Text(
                    'Elmas',
                    style: TextStyle(
                      fontSize: 16,
                      color: status.canClaim ? Colors.white : Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildStreakInfo(status) {
    return Container(
      padding: const EdgeInsets.all(20),
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
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          Column(
            children: [
              Icon(Icons.local_fire_department, color: Colors.orange[600], size: 32),
              const SizedBox(height: 8),
              Text(
                '${status.currentStreak}',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const Text('Gün Serisi', style: TextStyle(color: Colors.grey)),
            ],
          ),
          Container(width: 1, height: 60, color: Colors.grey[300]),
          Column(
            children: [
              Icon(Icons.trending_up, color: Colors.green[600], size: 32),
              const SizedBox(height: 8),
              Text(
                '${status.nextReward}',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const Text('Sonraki Ödül', style: TextStyle(color: Colors.grey)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildClaimButton(status) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: status.canClaim ? _claimReward : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: status.canClaim ? const Color(0xFFDD2A7B) : Colors.grey[400],
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          elevation: status.canClaim ? 8 : 0,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(status.canClaim ? Icons.card_giftcard : Icons.schedule),
            const SizedBox(width: 12),
            Text(
              status.canClaim ? 'Hediyeyi Al!' : 'Yarın Tekrar Gelin',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRewardSchedule() {
    final rewards = [
      {'day': 1, 'reward': 50},
      {'day': 2, 'reward': 60},
      {'day': 3, 'reward': 70},
      {'day': 4, 'reward': 80},
      {'day': 5, 'reward': 90},
      {'day': 6, 'reward': 100},
      {'day': 7, 'reward': 120},
    ];

    return Container(
      padding: const EdgeInsets.all(20),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Günlük Ödül Takvimi',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          ...rewards.map((reward) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${reward['day']}. Gün'),
                Text('${reward['reward']} Elmas', style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          )).toList(),
        ],
      ),
    );
  }

  void _claimReward() async {
    try {
      if (mounted) {
        _animationController.forward();
      }
      
      final response = await ref.read(dailyRewardProvider.notifier).claimReward();
      
      if (response != null && mounted) {
        // Show success message with earned diamonds
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    '${response.message} (+${response.diamondsAwarded} elmas)',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            duration: const Duration(seconds: 3),
          ),
        );
        
        // Add a small delay to show the animation effect
        await Future.delayed(const Duration(milliseconds: 500));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('Hata: ${e.toString()}'),
                ),
              ],
            ),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        );
      }
    } finally {
      if (mounted && _animationController.isAnimating) {
        _animationController.reset();
      }
    }
  }
}
