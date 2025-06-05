import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/user_provider.dart';
import '../providers/diamond_provider.dart';
import '../providers/notification_provider.dart';
import '../providers/leaderboard_provider.dart';
import 'package:go_router/go_router.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:instagram_puan_app/themes/app_theme.dart';
import 'package:badges/badges.dart' as badges;
import 'dart:async';

class MainScreen extends ConsumerStatefulWidget {
  final StatefulNavigationShell navigationShell;

  const MainScreen({
    super.key,
    required this.navigationShell,
  });

  @override
  ConsumerState<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends ConsumerState<MainScreen> {
  Timer? _diamondUpdateTimer;

  @override
  void initState() {
    super.initState();
    // Diamond balance'ı her 30 saniyede bir güncelle
    _diamondUpdateTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      ref.read(userProvider.notifier).refreshProfile();
    });
  }

  @override
  void dispose() {
    _diamondUpdateTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final userAsync = ref.watch(userProvider);
    final localizations = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: _buildAppBar(context, ref, userAsync, localizations),
      body: widget.navigationShell,
      bottomNavigationBar: _buildBottomNavigationBar(localizations),
      floatingActionButton: _buildFloatingActionButton(context),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }

  PreferredSizeWidget _buildAppBar(
    BuildContext context,
    WidgetRef ref,
    AsyncValue userAsync,
    AppLocalizations localizations,
  ) {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.transparent,
      flexibleSpace: Container(
        decoration: BoxDecoration(
          gradient: AppTheme.instagramGradient,
        ),
      ),
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.diamond,
              color: Colors.white,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          Expanded( // Added Expanded to prevent overflow
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  localizations.mainScreenTitle,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis, // Added overflow handling
                ),
                userAsync.when(
                  data: (user) => Text(
                    'Hoş geldin, ${user?.username ?? 'Kullanıcı'}',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                    ),
                    overflow: TextOverflow.ellipsis, // Added overflow handling
                  ),
                  loading: () => const SizedBox(height: 12),
                  error: (e, _) => const SizedBox(height: 12),
                ),
              ],
            ),
          ),
        ],
      ),
      actions: [
        // Notifications
        Consumer(
          builder: (context, ref, _) {
            final notificationsData = ref.watch(notificationsProvider);
            final unreadCount = notificationsData['unread_count'] ?? 0;
            return IconButton(
              icon: badges.Badge(
                showBadge: unreadCount > 0,
                badgeContent: Text(
                  unreadCount > 99 ? '99+' : unreadCount.toString(),
                  style: const TextStyle(color: Colors.white, fontSize: 10),
                ),
                child: const Icon(Icons.notifications_outlined, color: Colors.white),
              ),
              onPressed: () => context.push('/notifications'),
            );
          },
        ),
        
        // Daily reward
        IconButton(
          icon: badges.Badge(
            showBadge: true,
            badgeContent: const Icon(Icons.circle, color: Colors.green, size: 8),
            child: const Icon(Icons.card_giftcard_outlined, color: Colors.white),
          ),
          tooltip: 'Günlük Ödül',
          onPressed: () => context.push('/daily-reward'),
        ),
        
        // Diamond balance
        Container(
          margin: const EdgeInsets.only(right: 16),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Consumer(
            builder: (context, ref, child) {
              final userRankAsync = ref.watch(currentUserRankProvider);
              return userRankAsync.when(
                data: (rank) => Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.diamond, color: Colors.blue, size: 20),
                    const SizedBox(width: 4),
                    Text(
                      (rank?['total_coins'] ?? '0').toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
                loading: () => const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                ),
                error: (e, _) => const Icon(Icons.error, color: Colors.red, size: 20),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildBottomNavigationBar(AppLocalizations localizations) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: BottomAppBar(
        height: 80, // Increased from 70 to 80 to prevent overflow
        notchMargin: 8,
        shape: const CircularNotchedRectangle(),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildNavItem(
              icon: Icons.task_alt_outlined,
              activeIcon: Icons.task_alt,
              label: localizations.tasksTab,
              index: 0,
            ),
            _buildNavItem(
              icon: Icons.shopping_cart_outlined,
              activeIcon: Icons.shopping_cart,
              label: localizations.ordersTab,
              index: 1,
            ),
            _buildNavItem( // Added Leaderboard Tab
              icon: Icons.leaderboard_outlined,
              activeIcon: Icons.leaderboard,
              label: 'Sıralama', // You might want to localize this
              index: 2,
            ),
            const SizedBox(width: 48), // Space for FAB
            _buildNavItem(
              icon: Icons.bar_chart_outlined,
              activeIcon: Icons.bar_chart,
              label: 'İstatistik',
              index: 3, // Adjusted index
            ),
            _buildNavItem(
              icon: Icons.person_outline,
              activeIcon: Icons.person,
              label: localizations.profileTab,
              index: 4, // Adjusted index
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required IconData icon,
    required IconData activeIcon,
    required String label,
    required int index,
  }) {
    final isActive = widget.navigationShell.currentIndex == index;
    
    return GestureDetector(
      onTap: () {
        widget.navigationShell.goBranch(
          index,
          initialLocation: index == widget.navigationShell.currentIndex,
        );
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 6), // Reduced from 8 to 6
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isActive ? activeIcon : icon,
              color: isActive 
                ? AppTheme.instagramGradient.colors.first 
                : Colors.grey[600],
              size: 22, // Reduced from 24 to 22
            ),
            const SizedBox(height: 3), // Reduced from 4 to 3
            Text(
              label,
              style: TextStyle(
                color: isActive 
                  ? AppTheme.instagramGradient.colors.first 
                  : Colors.grey[600],
                fontSize: 10, // Reduced from 11 to 10
                fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget? _buildFloatingActionButton(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: AppTheme.instagramGradient,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: AppTheme.instagramGradient.colors.first.withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: FloatingActionButton(
        onPressed: () => context.push('/order'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        child: const Icon(
          Icons.add,
          color: Colors.white,
          size: 28,
        ),
      ),
    );
  }
}
