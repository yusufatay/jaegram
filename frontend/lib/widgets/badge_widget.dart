import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/badge.dart' as app_badge;
import '../generated/app_localizations.dart';
import '../utils/safe_animation_mixin.dart';

class BadgeWidget extends StatefulWidget {
  final app_badge.Badge badge;
  final bool isEarned;
  final DateTime? earnedAt;
  final bool showAnimation;
  final VoidCallback? onTap;

  const BadgeWidget({
    super.key,
    required this.badge,
    required this.isEarned,
    this.earnedAt,
    this.showAnimation = false,
    this.onTap,
  });

  @override
  State<BadgeWidget> createState() => _BadgeWidgetState();
  
  static void _showBadgeDetail(BuildContext context, dynamic userBadge) {
    if (userBadge.badge == null) return;
    
    showDialog(
      context: context,
      builder: (context) => BadgeDetailDialog(
        badge: userBadge.badge!,
        isEarned: true,
        earnedAt: userBadge.earnedAt,
      ),
    );
  }
}

class _BadgeWidgetState extends State<BadgeWidget>
    with SafeTickerProviderMixin {
  late AnimationController _scaleController;
  late AnimationController _rotationController;
  late AnimationController _shineController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;
  late Animation<double> _shineAnimation;

  @override
  void initState() {
    super.initState();
    _scaleController = createSafeAnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _rotationController = createSafeAnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    _shineController = createSafeAnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _scaleController, curve: Curves.elasticOut),
    );
    _rotationAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _rotationController, curve: Curves.easeInOut),
    );
    _shineAnimation = Tween<double>(begin: -1.0, end: 1.0).animate(
      CurvedAnimation(parent: _shineController, curve: Curves.easeInOut),
    );

    if (widget.showAnimation) {
      _playAnimations();
    } else {
      _scaleController.value = 1.0;
    }
  }

  void _playAnimations() {
    if (mounted) {
      _scaleController.forward();
      _rotationController.forward();
      
      // Add shine effect for earned badges
      if (widget.isEarned) {
        Future.delayed(const Duration(milliseconds: 300), () {
          if (mounted) {
            _shineController.forward();
          }
        });
      }
    }
  }

  @override
  void didUpdateWidget(BadgeWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // If animation flag changes or badge is newly earned
    if (widget.showAnimation && !oldWidget.showAnimation && mounted) {
      _playAnimations();
    }
  }

  @override
  void dispose() {
    // SafeTickerProviderMixin handles automatic disposal
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Badge null ise fallback göster
    if (widget.badge == null) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, color: Colors.red, size: 40),
          const SizedBox(height: 8),
          Text('Rozet verisi eksik', style: TextStyle(color: Colors.red, fontSize: 12)),
        ],
      );
    }

    return GestureDetector(
      onTap: widget.onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              // Badge background glow (for earned badges)
              if (widget.isEarned)
                AnimatedBuilder(
                  animation: _rotationAnimation,
                  builder: (context, child) {
                    return Transform.rotate(
                      angle: _rotationAnimation.value * 0.2 * 3.14,
                      child: Container(
                        width: 70,
                        height: 70,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              _getBadgeColor(context, opacity: 0.7),
                              _getBadgeColor(context, opacity: 0.0),
                            ],
                            stops: const [0.7, 1.0],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              
              // Badge icon with scale animation
              ScaleTransition(
                scale: _scaleAnimation,
                child: AnimatedBuilder(
                  animation: _rotationAnimation,
                  builder: (context, child) {
                    return Transform.rotate(
                      angle: widget.showAnimation 
                          ? _rotationAnimation.value * 2 * 3.14 
                          : 0.0,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // Badge container
                          Container(
                            width: 60,
                            height: 60,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: widget.isEarned 
                                  ? null
                                  : Colors.grey[300],
                              gradient: widget.isEarned
                                  ? LinearGradient(
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                      colors: [
                                        _getBadgeColor(context),
                                        _getBadgeColor(context).withValues(alpha: 0.7),
                                      ],
                                    )
                                  : null,
                              boxShadow: widget.isEarned
                                  ? [
                                      BoxShadow(
                                        color: _getBadgeColor(context, opacity: 0.3),
                                        blurRadius: 8,
                                        spreadRadius: 1,
                                      ),
                                    ]
                                  : null,
                              border: Border.all(
                                color: widget.isEarned 
                                    ? Colors.white.withValues(alpha: 0.5) 
                                    : Colors.grey[400] ?? Colors.grey,
                                width: 2,
                              ),
                            ),
                            child: ClipOval(
                              child: Stack(
                                children: [
                                  // Badge icon
                                  Center(
                                    child: widget.badge.iconUrl.startsWith('http')
                                      ? Image.network(
                                          widget.badge.iconUrl,
                                          width: 40,
                                          height: 40,
                                          errorBuilder: (context, error, stackTrace) {
                                            return const Icon(
                                              Icons.emoji_events,
                                              color: Colors.white,
                                              size: 30,
                                            );
                                          },
                                        )
                                      : Icon(
                                          _getBadgeIcon(),
                                          color: widget.isEarned 
                                              ? Colors.white 
                                              : Colors.grey[600],
                                          size: 30,
                                        ),
                                  ),
                                  
                                  // Shine effect for earned badges
                                  if (widget.isEarned && widget.showAnimation)
                                    AnimatedBuilder(
                                      animation: _shineAnimation,
                                      builder: (context, child) {
                                        return Transform.rotate(
                                          angle: -0.3,
                                          child: Align(
                                            alignment: Alignment(
                                              _shineAnimation.value * 2,
                                              0,
                                            ),
                                            child: Container(
                                              width: 15,
                                              height: 60,
                                              decoration: BoxDecoration(
                                                gradient: LinearGradient(
                                                  begin: Alignment.topLeft,
                                                  end: Alignment.bottomRight,
                                                  colors: [
                                                    Colors.white.withValues(alpha: 0.0),
                                                    Colors.white.withValues(alpha: 0.4),
                                                    Colors.white.withValues(alpha: 0.0),
                                                  ],
                                                ),
                                              ),
                                            ),
                                          ),
                                        );
                                      },
                                    ),
                                ],
                              ),
                            ),
                          ),
                          
                          // Lock icon overlay for unearned badges
                          if (!widget.isEarned)
                            Positioned.fill(
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.black.withValues(alpha: 0.5),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.lock,
                                  color: Colors.white70,
                                  size: 24,
                                ),
                              ),
                            ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          
          // Badge name
          Text(
            widget.badge.name,
            style: TextStyle(
              fontSize: 12,
              fontWeight: widget.isEarned ? FontWeight.bold : FontWeight.normal,
              color: widget.isEarned 
                  ? Theme.of(context).colorScheme.primary 
                  : Theme.of(context).disabledColor,
            ),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          
          // Badge earned date
          if (widget.isEarned && widget.earnedAt != null) ...[
            const SizedBox(height: 2),
            Text(
              _formatDate(widget.earnedAt ?? DateTime.now()),
              style: TextStyle(
                fontSize: 10,
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getBadgeColor(BuildContext context, {double opacity = 1.0}) {
    switch (widget.badge.category.toLowerCase()) {
      case 'gold':
        return Colors.amber.withValues(alpha: opacity);
      case 'silver':
        return Colors.blueGrey.withValues(alpha: opacity);
      case 'bronze':
        return Colors.brown.withValues(alpha: opacity);
      case 'instagram':
        return Colors.purple.withValues(alpha: opacity);
      case 'achievement':
        return Colors.blue.withValues(alpha: opacity);
      case 'special':
        return Colors.redAccent.withValues(alpha: opacity);
      default:
        return Theme.of(context).colorScheme.primary.withValues(alpha: opacity);
    }
  }

  IconData _getBadgeIcon() {
    switch (widget.badge.category.toLowerCase()) {
      case 'gold':
        return Icons.emoji_events;
      case 'silver':
        return Icons.stars;
      case 'bronze':
        return Icons.military_tech;
      case 'instagram':
        return Icons.camera_alt;
      case 'achievement':
        return Icons.workspace_premium;
      case 'special':
        return Icons.auto_awesome;
      default:
        return Icons.emoji_events;
    }
  }
  
  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }
}

class BadgeListWidget extends ConsumerWidget {
  final List<app_badge.UserBadge> userBadges;
  final List<app_badge.Badge> allBadges;
  final bool showAll;

  const BadgeListWidget({
    super.key,
    required this.userBadges,
    required this.allBadges,
    this.showAll = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final earnedBadgeIds = userBadges.map((ub) => ub.badgeId).toSet();
    final displayBadges = showAll 
        ? allBadges 
        : allBadges.where((badge) => earnedBadgeIds.contains(badge.id)).toList();

    if (displayBadges.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.emoji_events_outlined,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              showAll 
                  ? (AppLocalizations.of(context)?.noBadgesAvailable ?? 'No badges available')
                  : (AppLocalizations.of(context)?.noBadgesEarned ?? 'No badges earned'),
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1,
      ),
      itemCount: displayBadges.length,
      itemBuilder: (context, index) {
        final badge = displayBadges[index];
        final isEarned = earnedBadgeIds.contains(badge.id);
        final userBadge = userBadges.firstWhere(
          (ub) => ub.badgeId == badge.id,
          orElse: () => app_badge.UserBadge(
            id: -1,
            userId: -1,
            badgeId: badge.id,
            earnedAt: DateTime.now(),
          ),
        );

        return BadgeWidget(
          badge: badge,
          isEarned: isEarned,
          earnedAt: isEarned ? userBadge.earnedAt : null,
          onTap: () => _showBadgeDetail(context, badge, isEarned, userBadge.earnedAt),
        );
      },
    );
  }

  void _showBadgeDetail(BuildContext context, app_badge.Badge badge, bool isEarned, DateTime? earnedAt) {
    showDialog(
      context: context,
      builder: (context) => BadgeDetailDialog(
        badge: badge,
        isEarned: isEarned,
        earnedAt: earnedAt,
      ),
    );
  }
}

class BadgeDetailDialog extends StatelessWidget {
  final app_badge.Badge badge;
  final bool isEarned;
  final DateTime? earnedAt;

  const BadgeDetailDialog({
    super.key,
    required this.badge,
    required this.isEarned,
    this.earnedAt,
  });

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            BadgeWidget(
              badge: badge,
              isEarned: isEarned,
              earnedAt: earnedAt,
              showAnimation: isEarned,
            ),
            const SizedBox(height: 20),
            Text(
              badge.name,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              badge.description,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            if (isEarned && earnedAt != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.check_circle, color: Colors.green, size: 20),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        '${AppLocalizations.of(context)?.earnedOn ?? 'Earned on'} ${_formatDate(earnedAt ?? DateTime.now())}',
                        style: const TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.w600,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 20),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(AppLocalizations.of(context)?.close ?? 'Close'),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

class BadgeSectionWidget extends StatelessWidget {
  final List<app_badge.UserBadge> userBadges;
  final VoidCallback? onViewAll;

  const BadgeSectionWidget({
    super.key,
    required this.userBadges,
    this.onViewAll,
  });

  @override
  Widget build(BuildContext context) {
    final recentBadges = userBadges.take(4).toList();

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  AppLocalizations.of(context)?.badges ?? 'Badges',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (userBadges.length > 4)
                  TextButton(
                    onPressed: onViewAll,
                    child: Text(AppLocalizations.of(context)?.viewAll ?? 'View All'),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            if (recentBadges.isEmpty)
              Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.emoji_events_outlined,
                      size: 48,
                      color: Colors.grey.shade400,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      AppLocalizations.of(context)?.noBadgesEarned ?? 'No badges earned',
                      style: TextStyle(color: Colors.grey.shade600),
                    ),
                  ],
                ),
              )
            else
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: recentBadges.where((userBadge) => userBadge.badge != null).map((userBadge) {
                  return BadgeWidget(
                    badge: userBadge.badge!,
                    isEarned: true,
                    earnedAt: userBadge.earnedAt,
                    onTap: () => _showBadgeDetail(context, userBadge),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  void _showBadgeDetail(BuildContext context, app_badge.UserBadge userBadge) {
    showDialog(
      context: context,
      builder: (context) => BadgeDetailDialog(
        badge: userBadge.badge!,
        isEarned: true,
        earnedAt: userBadge.earnedAt,
      ),
    );
  }
}
