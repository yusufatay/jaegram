// Profil ekranı için şablon dosyadır.
// Buraya kullanıcı bilgileri ve ayarlar arayüzü ileride eklenecektir.
// Tüm metinler ve arayüz Türkçe olacak şekilde tasarlanacaktır.
// Profil ekranı: Kullanıcı bilgileri (userProvider), çıkış yap butonu, loading/error state, SelectableText.rich ile hata, Türkçe ve modern UI.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/user_provider.dart';
import 'package:go_router/go_router.dart';
import 'dart:math';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:instagram_puan_app/providers/theme_provider.dart';
import '../widgets/profile_stat_widget.dart';
import '../widgets/gradient_button.dart';
import '../widgets/badge_widget.dart';
import '../providers/instagram_profile_provider.dart';
import '../providers/earned_badges_provider.dart';
import '../providers/instagram_posts_provider.dart';
import '../models/user.dart';
import '../models/badge.dart' as app_badge;
import 'package:flutter/services.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userProvider);
    final themeMode = ref.watch(themeProvider);
    final isDark = themeMode == ThemeMode.dark || (themeMode == ThemeMode.system && MediaQuery.of(context).platformBrightness == Brightness.dark);
    final localizations = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations?.profile ?? 'Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: localizations.settingsTitle,
            onPressed: () {
              context.push('/settings');
            },
          ),
          IconButton(
            icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
            tooltip: isDark 
                ? localizations.switchToLight
                : localizations.switchToDark,
            onPressed: () {
              final newMode = isDark ? ThemeMode.light : ThemeMode.dark;
              ref.read(themeProvider.notifier).setTheme(newMode);
            },
          ),
        ],
      ),
      body: userAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => Center(
          child: SelectableText.rich(
            TextSpan(
              text: '${localizations.errorLoadingProfile}: ',
              style: const TextStyle(fontSize: 16),
              children: [
                TextSpan(
                  text: error.toString(),
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ),
        data: (user) => user != null ? _buildProfileContent(context, ref, user) : const Center(child: Text('No user data')),
      ),
    );
  }

  Widget _buildProfileContent(BuildContext context, WidgetRef ref, User user) {
    final localizations = AppLocalizations.of(context);
    final instagramProfileAsync = ref.watch(instagramProfileProvider);
    final earnedBadgesAsync = ref.watch(earnedBadgesProvider);
    final theme = Theme.of(context);
    
    return RefreshIndicator(
      onRefresh: () async {
        ref.refresh(userProvider);
        ref.refresh(instagramProfileProvider);
        ref.refresh(earnedBadgesProvider);
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Hero Section with User Info
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    theme.colorScheme.primary,
                    theme.colorScheme.secondary,
                  ],
                ),
              ),
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  // Avatar with Badge Indicator
                  Stack(
                    alignment: Alignment.bottomRight,
                    children: [
                      _ProfilePhoto(url: user.profilePicUrl),
                      
                      // Instagram Verification Badge (if available)
                      instagramProfileAsync.maybeWhen(
                        data: (profile) {
                          if (profile?.isVerified ?? false) {
                            return Container(
                              padding: const EdgeInsets.all(3),
                              decoration: BoxDecoration(
                                color: Colors.blue,
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: theme.colorScheme.primary,
                                  width: 2,
                                ),
                              ),
                              child: const Icon(
                                Icons.verified,
                                color: Colors.white,
                                size: 20,
                              ),
                            );
                          }
                          return const SizedBox();
                        },
                        orElse: () => const SizedBox(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  
                  // Username and Bio
                  Text(
                    user.username,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  
                  if (user.email?.isNotEmpty ?? false) ...[
                    const SizedBox(height: 4),
                    Text(
                      user.email ?? '',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.8),
                      ),
                    ),
                  ],
                  
                  // Bio from Instagram (if available)
                  instagramProfileAsync.maybeWhen(
                    data: (profile) {
                      final bio = profile?.biography;
                      if (profile != null && bio != null && bio.isNotEmpty) {
                        return Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(
                            bio,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: 0.9),
                              fontSize: 14,
                            ),
                          ),
                        );
                      }
                      return const SizedBox();
                    },
                    orElse: () => const SizedBox(),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Stats Row - Enhanced Instagram Stats
                  instagramProfileAsync.maybeWhen(
                    data: (profile) {
                      if (profile != null && (profile.isConnected ?? false)) {
                        // Instagram connected - show Instagram stats
                        return Column(
                          children: [
                            // Instagram Profile Info
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.camera_alt,
                                  color: Colors.white.withValues(alpha: 0.8),
                                  size: 16,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  '@${profile.username}',
                                  style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.9),
                                    fontSize: 16,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                if (profile.isVerified ?? false) ...[
                                  const SizedBox(width: 4),
                                  const Icon(
                                    Icons.verified,
                                    color: Colors.blue,
                                    size: 16,
                                  ),
                                ],
                              ],
                            ),
                            const SizedBox(height: 16),
                            
                            // Instagram Stats
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                              children: [
                                ProfileStatWidget(
                                  icon: Icons.grid_on,
                                  value: _formatNumber(profile.mediaCount ?? 0),
                                  label: localizations.posts,
                                ),
                                ProfileStatWidget(
                                  icon: Icons.diamond,
                                  value: (user.diamondBalance ?? 0).toString(),
                                  label: localizations.totalCoins,
                                ),
                              ],
                            ),
                          ],
                        );
                      } else {
                        // Instagram not connected - show platform stats only (reduced fallback data)
                        return Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            ProfileStatWidget(
                              icon: Icons.diamond,
                              value: (user.diamondBalance ?? 0).toString(),
                              label: localizations.totalCoins,
                            ),
                          ],
                        );
                      }
                    },
                    orElse: () => Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        ProfileStatWidget(
                          icon: Icons.diamond,
                          value: (user.diamondBalance ?? 0).toString(),
                          label: localizations.totalCoins,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // Quick Action Buttons Section
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            context.go('/leaderboard');
                          },
                          icon: const Icon(Icons.leaderboard),
                          label: Text(localizations.leaderboard),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.primaryContainer,
                            foregroundColor: theme.colorScheme.onPrimaryContainer,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            context.go('/badges');
                          },
                          icon: const Icon(Icons.emoji_events),
                          label: Text(localizations.badges),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.secondaryContainer,
                            foregroundColor: theme.colorScheme.onSecondaryContainer,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            context.go('/diamond-transfer');
                          },
                          icon: const Icon(Icons.send),
                          label: Text(localizations.coinTransfer),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.tertiaryContainer,
                            foregroundColor: theme.colorScheme.onTertiaryContainer,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            context.go('/instagram-integration');
                          },
                          icon: const Icon(Icons.camera_alt),
                          label: Text(localizations.instagramIntegration),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.primaryContainer,
                            foregroundColor: theme.colorScheme.onPrimaryContainer,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            // Earned Badges Section
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        localizations.badges,
                        style: theme.textTheme.titleLarge,
                      ),
                      TextButton(
                        onPressed: () {
                          context.go('/badges');
                        },
                        child: Text(localizations.viewAll),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  
                  earnedBadgesAsync.when(
                    loading: () => const Center(
                      child: Padding(
                        padding: EdgeInsets.all(16.0),
                        child: CircularProgressIndicator(),
                      ),
                    ),
                    error: (_, __) => Center(
                      child: Text(localizations.errorLoadingBadges),
                    ),
                    data: (badges) {
                      if (badges.isEmpty) {
                        return Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24.0),
                            child: Column(
                              children: [
                                Icon(
                                  Icons.emoji_events_outlined,
                                  size: 48,
                                  color: theme.disabledColor,
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  localizations.noBadgesEarned,
                                  textAlign: TextAlign.center,
                                  style: theme.textTheme.bodyMedium,
                                ),
                              ],
                            ),
                          ),
                        );
                      }
                      
                      return SizedBox(
                        height: 120,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          itemCount: badges.length > 5 ? 5 : badges.length,
                          itemBuilder: (context, index) {
                            final userBadge = badges[index];
                            final badge = userBadge.badge;
                            if (badge == null) return const SizedBox.shrink();
                            return Padding(
                              padding: const EdgeInsets.only(right: 16.0),
                              child: BadgeWidget(
                                badge: badge,
                                isEarned: true,
                                earnedAt: userBadge.earnedAt,
                                onTap: () {
                                  _showBadgeDetails(context, badge, earnedAt: userBadge.earnedAt);
                                },
                              ),
                            );
                          },
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
            
            // Instagram Posts Section (KALDIRILDI)
            // Sadece Instagram profil paylaşma butonu gösterilecek
            instagramProfileAsync.maybeWhen(
              data: (profile) {
                if (profile != null && (profile.isConnected ?? false)) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () async {
                              final url = 'https://instagram.com/${profile.username}';
                              await Clipboard.setData(ClipboardData(text: url));
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Instagram profil bağlantısı kopyalandı!')),
                              );
                            },
                            icon: const Icon(Icons.link),
                            label: const Text('Instagram Profil Bağlantısını Kopyala'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: theme.colorScheme.secondaryContainer,
                              foregroundColor: theme.colorScheme.onSecondaryContainer,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }
                return const SizedBox();
              },
              orElse: () => const SizedBox(),
            ),
            
            // Account Details Section
            Padding(
              padding: const EdgeInsets.all(16),
              child: Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        localizations.accountDetails,
                        style: theme.textTheme.titleMedium,
                      ),
                      const Divider(),
                      _buildDetailItem(
                        context,
                        icon: Icons.calendar_today,
                        title: localizations.joinDate,
                        value: _formatDate(DateTime.now()), // Default since joinDate is not in new User model
                      ),
                      _buildDetailItem(
                        context,
                        icon: Icons.timeline,
                        title: localizations.progress,
                        value: "0%", // Default since progress is not in new User model
                        showProgressBar: true,
                        progress: 0.0,
                      ),
                      _buildDetailItem(
                        context,
                        icon: Icons.leaderboard,
                        title: localizations.rank,
                        value: "#0", // Default since rank is not in new User model
                      ),
                      const SizedBox(height: 8),
                      GradientButton(
                        text: localizations.leaderboard,
                        onPressed: () {
                          context.go('/leaderboard');
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildConnectInstagramCard(
    BuildContext context, 
    ThemeData theme, 
    AppLocalizations localizations
  ) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Card(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              const Icon(
                Icons.camera_alt, // Replaced Instagram icon with camera
                size: 48,
                color: Colors.purple,
              ),
              const SizedBox(height: 8),
              Text(
                localizations.connectInstagramBenefits,
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyLarge,
              ),
              const SizedBox(height: 16),
              GradientButton(
                text: localizations.connectInstagram,
                onPressed: () {
                  context.go('/instagram-integration');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String value,
    bool showProgressBar = false,
    double progress = 0.0,
  }) {
    final theme = Theme.of(context);
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: theme.colorScheme.primary),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: theme.textTheme.bodySmall,
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: theme.textTheme.titleSmall,
                ),
                if (showProgressBar) ...[
                  const SizedBox(height: 4),
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: theme.colorScheme.surfaceContainerHighest,
                    valueColor: AlwaysStoppedAnimation<Color>(theme.colorScheme.primary),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showBadgeDetails(BuildContext context, app_badge.Badge badge, {DateTime? earnedAt}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.6,
          maxChildSize: 0.9,
          minChildSize: 0.5,
          expand: false,
          builder: (context, scrollController) {
            return SingleChildScrollView(
              controller: scrollController,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    BadgeWidget(
                      badge: badge,
                      isEarned: true,
                      showAnimation: true,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      badge.name,
                      style: Theme.of(context).textTheme.titleLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      badge.description,
                      style: Theme.of(context).textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    if (earnedAt != null) ...[
                      Text(
                        '${AppLocalizations.of(context)?.earnedOn ?? 'Earned on'}: ${_formatDate(earnedAt)}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 24),
                    ],
                    GradientButton(
                      text: AppLocalizations.of(context)?.close ?? 'Close',
                      onPressed: () {
                        Navigator.of(context).pop();
                      },
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toString();
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }
}

class _ProfilePhoto extends StatelessWidget {
  final String? url;
  const _ProfilePhoto({this.url});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(60),
      child: url != null
          ? Image.network(
              url!, // Added non-null assertion after null check
              width: 110,
              height: 110,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) => Container(
                width: 110,
                height: 110,
                color: Colors.grey[200],
                child: const Icon(Icons.account_circle, size: 80, color: Colors.deepPurple),
              ),
            )
          : Container(
              width: 110,
              height: 110,
              color: Colors.grey[200],
              child: const Icon(Icons.account_circle, size: 80, color: Colors.deepPurple),
            ),
    );
  }
}

class _AnimatedDiamondBox extends StatefulWidget {
  final int diamond;
  const _AnimatedDiamondBox({required this.diamond});

  @override
  State<_AnimatedDiamondBox> createState() => _AnimatedDiamondBoxState();
}

class _AnimatedDiamondBoxState extends State<_AnimatedDiamondBox> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(seconds: 1));
    _animation = Tween<double>(begin: 0, end: widget.diamond.toDouble()).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutBack),
    );
    _controller.forward();
  }

  @override
  void didUpdateWidget(covariant _AnimatedDiamondBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.diamond != widget.diamond) {
      _animation = Tween<double>(begin: 0, end: widget.diamond.toDouble()).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeOutBack),
      );
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) => Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.amber[100],
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.amber, width: 2),
              boxShadow: [
                BoxShadow(
                  color: Colors.amber.withValues(alpha: 0.2),
                  blurRadius: 12,
                  spreadRadius: 2,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                Transform.rotate(
                  angle: pi / 12,
                  child: Icon(Icons.diamond, color: Colors.blue[800], size: 32),
                ),
                const SizedBox(width: 8),
                Text(
                  _animation.value.toInt().toString(),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 24,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(width: 4),
                const Text('Elmas', style: TextStyle(fontSize: 16, color: Colors.black54)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DailyRewardCard extends StatelessWidget {
  final DateTime? lastReward;
  final int streak;
  final VoidCallback onTap;

  const _DailyRewardCard({
    required this.lastReward,
    required this.streak,
    required this.onTap,
  });

  bool get canClaimToday {
    if (lastReward == null) return true;
    final today = DateTime.now();
    final lastRewardDate = DateTime(lastReward!.year, lastReward!.month, lastReward!.day);
    final todayDate = DateTime(today.year, today.month, today.day);
    return lastRewardDate.isBefore(todayDate);
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              colors: canClaimToday 
                ? [Colors.orange.shade300, Colors.deepOrange.shade400]
                : [Colors.grey.shade300, Colors.grey.shade400],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  canClaimToday ? Icons.card_giftcard : Icons.schedule,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      canClaimToday ? 'Günlük Ödül Hazır!' : 'Günlük Ödül',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      streak > 0 ? '$streak gün üst üste' : 'İlk ödülünü al',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                color: Colors.white,
                size: 16,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EmailVerificationCard extends StatelessWidget {
  final String email;
  final bool isVerified;
  final VoidCallback onVerifyTap;

  const _EmailVerificationCard({
    required this.email,
    required this.isVerified,
    required this.onVerifyTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: isVerified
              ? [Colors.green.shade300, Colors.teal.shade400]
              : [Colors.blue.shade300, Colors.indigo.shade400],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                isVerified ? Icons.verified : Icons.email_outlined,
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isVerified ? 'E-posta Doğrulandı' : 'E-posta Doğrulama',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    email,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),
            if (!isVerified)
              InkWell(
                onTap: onVerifyTap,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text(
                    'Doğrula',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _TwoFactorAuthCard extends StatelessWidget {
  final bool isEnabled;
  final VoidCallback onTap;

  const _TwoFactorAuthCard({
    required this.isEnabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: isEnabled 
                ? [const Color(0xFF4CAF50), const Color(0xFF2E7D32)]
                : [const Color(0xFFFF9800), const Color(0xFFE65100)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    isEnabled ? Icons.security : Icons.security_outlined,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'İki Faktörlü Kimlik Doğrulama',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        isEnabled 
                            ? 'Hesabınız ekstra güvenlik ile korunuyor'
                            : 'Hesabınızı daha güvenli hale getirin',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.white.withValues(alpha: 0.9),
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    isEnabled ? 'Aktif' : 'Ayarla',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
