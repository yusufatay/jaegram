import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/badge_widget.dart';
import '../widgets/gradient_button.dart';
import '../providers/badge_provider.dart';
import '../providers/earned_badges_provider.dart';
import '../providers/notification_provider.dart';
import '../generated/app_localizations.dart';
import '../models/badge.dart' as app_badge;
import '../models/badge.dart';

class BadgesScreen extends ConsumerStatefulWidget {
  const BadgesScreen({super.key});

  @override
  ConsumerState<BadgesScreen> createState() => _BadgesScreenState();
}

class _BadgesScreenState extends ConsumerState<BadgesScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  final List<String> _categories = [];
  String? _selectedCategory;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    
    // Reset badge notification counter when this screen is opened
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(badgeNotificationCountProvider.notifier).state = 0;
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.badges),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(
              icon: const Icon(Icons.emoji_events),
              text: localizations.yourBadges,
            ),
            Tab(
              icon: const Icon(Icons.all_inclusive),
              text: localizations.allBadges,
            ),
          ],
          indicatorSize: TabBarIndicatorSize.tab,
          indicatorWeight: 3,
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Your Badges Tab
          RefreshIndicator(
            onRefresh: () async {
              ref.refresh(earnedBadgesProvider);
            },
            child: ref.watch(earnedBadgesProvider).when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.error_outline, color: theme.colorScheme.error, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      localizations.errorLoadingBadges,
                      style: TextStyle(color: theme.colorScheme.error),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => ref.refresh(earnedBadgesProvider),
                      child: Text(localizations.tryAgain),
                    ),
                  ],
                ),
              ),
              data: (badges) {
                if (badges.isEmpty) {
                  return _buildEmptyBadgesView(context, localizations, theme);
                }
                
                // Extract unique badge categories
                _updateCategoriesFromUserBadges(badges);
                
                return Column(
                  children: [
                    // Category filter chips
                    if (_categories.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: SizedBox(
                          height: 40,
                          child: ListView(
                            scrollDirection: Axis.horizontal,
                            children: [
                              Padding(
                                padding: const EdgeInsets.only(right: 8.0),
                                child: FilterChip(
                                  label: Text(localizations.all),
                                  selected: _selectedCategory == null,
                                  onSelected: (selected) {
                                    if (selected) {
                                      setState(() {
                                        _selectedCategory = null;
                                      });
                                    }
                                  },
                                ),
                              ),
                              ..._categories.map((category) {
                                return Padding(
                                  padding: const EdgeInsets.only(right: 8.0),
                                  child: FilterChip(
                                    label: Text(_getCategoryDisplayName(category, localizations)),
                                    selected: _selectedCategory == category,
                                    onSelected: (selected) {
                                      setState(() {
                                        _selectedCategory = selected ? category : null;
                                      });
                                    },
                                  ),
                                );
                              }),
                            ],
                          ),
                        ),
                      ),
                    
                    // Badges grid
                    Expanded(
                      child: GridView.builder(
                        padding: const EdgeInsets.all(16.0),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 3,
                          childAspectRatio: 0.8,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                        ),
                        itemCount: _filterUserBadges(badges).length,
                        itemBuilder: (context, index) {
                          final userBadge = _filterUserBadges(badges)[index];
                          return BadgeWidget(
                            badge: userBadge.badge!,
                            isEarned: true,
                            earnedAt: userBadge.earnedAt,
                            onTap: () => _showBadgeDetails(context, userBadge.badge!),
                          );
                        },
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
          
          // All Badges Tab
          RefreshIndicator(
            onRefresh: () async {
              ref.refresh(allBadgesProvider);
            },
            child: ref.watch(allBadgesProvider).when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.error_outline, color: theme.colorScheme.error, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      localizations.errorLoadingBadges,
                      style: TextStyle(color: theme.colorScheme.error),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => ref.refresh(allBadgesProvider),
                      child: Text(localizations.tryAgain),
                    ),
                  ],
                ),
              ),
              data: (badgesData) {
                final earnedBadges = ref.watch(earnedBadgesProvider).value ?? [];
                final earnedBadgeIds = earnedBadges.map((ub) => ub.badgeId).toSet();
                final allBadges = badgesData.map((badge) {
                  final userBadge = earnedBadges.firstWhere(
                    (ub) => ub.badgeId == badge.id,
                    orElse: () => UserBadge(
                      id: -1,
                      userId: -1,
                      badgeId: -1,
                      earnedAt: DateTime.now(),
                    ),
                  );
                  
                  return (
                    badge: badge,
                    isEarned: earnedBadgeIds.contains(badge.id),
                    earnedAt: userBadge.id != -1 ? userBadge.earnedAt : null,
                  );
                }).toList();
                
                if (allBadges.isEmpty) {
                  return _buildEmptyBadgesView(context, localizations, theme);
                }
                
                // Extract unique badge categories from all badges
                _updateCategoriesFromAll(badgesData);
                
                return Column(
                  children: [
                    // Progress indicator
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                '${localizations.badgesEarned}: ${earnedBadges.length}/${allBadges.length}',
                                style: theme.textTheme.bodyLarge,
                              ),
                              Text(
                                '${(earnedBadges.length / allBadges.length * 100).toStringAsFixed(1)}%',
                                style: theme.textTheme.bodyLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: theme.colorScheme.primary,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: allBadges.isEmpty ? 0 : earnedBadges.length / allBadges.length,
                              minHeight: 8,
                              backgroundColor: theme.colorScheme.surfaceContainerHighest,
                            ),
                          ),
                        ],
                      ),
                    ),
                
                    // Category filter chips
                    if (_categories.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: SizedBox(
                          height: 40,
                          child: ListView(
                            scrollDirection: Axis.horizontal,
                            children: [
                              Padding(
                                padding: const EdgeInsets.only(right: 8.0),
                                child: FilterChip(
                                  label: Text(localizations.all),
                                  selected: _selectedCategory == null,
                                  onSelected: (selected) {
                                    if (selected) {
                                      setState(() {
                                        _selectedCategory = null;
                                      });
                                    }
                                  },
                                ),
                              ),
                              ..._categories.map((category) {
                                final badgesInCategory = allBadges
                                    .where((b) => b.badge.category == category)
                                    .length;
                                final earnedInCategory = allBadges
                                    .where((b) => b.badge.category == category && b.isEarned)
                                    .length;
                                
                                return Padding(
                                  padding: const EdgeInsets.only(right: 8.0),
                                  child: FilterChip(
                                    label: Text(
                                      '${_getCategoryDisplayName(category, localizations)} ($earnedInCategory/$badgesInCategory)',
                                    ),
                                    selected: _selectedCategory == category,
                                    onSelected: (selected) {
                                      setState(() {
                                        _selectedCategory = selected ? category : null;
                                      });
                                    },
                                  ),
                                );
                              }),
                            ],
                          ),
                        ),
                      ),
                      
                    // Badges grid
                    Expanded(
                      child: GridView.builder(
                        padding: const EdgeInsets.all(16.0),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 3,
                          childAspectRatio: 0.8,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                        ),
                        itemCount: _filterAllBadges(allBadges).length,
                        itemBuilder: (context, index) {
                          final badgeData = _filterAllBadges(allBadges)[index];
                          return BadgeWidget(
                            badge: badgeData.badge,
                            isEarned: badgeData.isEarned,
                            earnedAt: badgeData.earnedAt,
                            onTap: () => _showBadgeDetails(
                              context,
                              badgeData.badge,
                              isEarned: badgeData.isEarned,
                              earnedAt: badgeData.earnedAt,
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyBadgesView(
    BuildContext context,
    AppLocalizations localizations,
    ThemeData theme,
  ) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.emoji_events_outlined,
            size: 70,
            color: theme.disabledColor,
          ),
          const SizedBox(height: 16),
          Text(
            localizations.noBadgesEarned,
            style: theme.textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32.0),
            child: Text(
              localizations.earnBadgesDescription,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              _tabController.animateTo(1); // Switch to All Badges tab
            },
            child: Text(localizations.viewAllBadges),
          ),
        ],
      ),
    );
  }

  void _updateCategoriesFromUserBadges(List<UserBadge> userBadges) {
    final categories = userBadges
        .where((userBadge) => userBadge.badge != null)
        .map((userBadge) => userBadge.badge!.category)
        .toSet()
        .toList();
    categories.sort();
    
    if (!listEquals(_categories, categories)) {
      setState(() {
        _categories.clear();
        _categories.addAll(categories);
      });
    }
  }
  
  void _updateCategoriesFromAll(List<app_badge.Badge> badges) {
    final categories = badges
        .map((badge) => badge.category)
        .toSet()
        .toList();
    categories.sort();
    
    if (!listEquals(_categories, categories)) {
      setState(() {
        _categories.clear();
        _categories.addAll(categories);
      });
    }
  }
  
  List<UserBadge> _filterUserBadges(List<UserBadge> userBadges) {
    if (_selectedCategory == null) {
      return userBadges;
    }
    return userBadges.where((userBadge) => 
      userBadge.badge != null && userBadge.badge!.category == _selectedCategory
    ).toList();
  }
  
  List<({app_badge.Badge badge, bool isEarned, DateTime? earnedAt})> _filterAllBadges(
    List<({app_badge.Badge badge, bool isEarned, DateTime? earnedAt})> badges
  ) {
    if (_selectedCategory == null) {
      return badges;
    }
    return badges.where((b) => b.badge.category == _selectedCategory).toList();
  }

  String _getCategoryDisplayName(String category, AppLocalizations localizations) {
    switch (category.toLowerCase()) {
      case 'gold':
        return localizations.goldBadges;
      case 'silver':
        return localizations.silverBadges;
      case 'bronze':
        return localizations.bronzeBadges;
      case 'instagram':
        return localizations.instagramBadges;
      case 'achievement':
        return localizations.achievementBadges;
      case 'special':
        return localizations.specialBadges;
      default:
        return category;
    }
  }

  void _showBadgeDetails(
    BuildContext context,
    app_badge.Badge badge, {
    bool isEarned = true,
    DateTime? earnedAt,
  }) {
    final localizations = AppLocalizations.of(context);
    final theme = Theme.of(context);
    
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
                      isEarned: isEarned,
                      earnedAt: earnedAt,
                      showAnimation: true,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      badge.name,
                      style: theme.textTheme.titleLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      badge.description,
                      style: theme.textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    
                    // Badge details
                    Card(
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                        side: BorderSide(
                          color: theme.colorScheme.surfaceContainerHighest,
                          width: 1,
                        ),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              localizations.badgeDetails,
                              style: theme.textTheme.titleMedium,
                            ),
                            const Divider(),
                            _buildDetailRow(
                              localizations.category,
                              _getCategoryDisplayName(badge.category, localizations),
                              theme,
                            ),
                            _buildDetailRow(
                              localizations.status,
                              isEarned 
                                  ? localizations.earned 
                                  : localizations.locked,
                              theme,
                              valueColor: isEarned 
                                  ? Colors.green 
                                  : theme.colorScheme.error,
                            ),
                            if (isEarned && earnedAt != null)
                              _buildDetailRow(
                                localizations.earnedOn,
                                _formatDate(earnedAt),
                                theme,
                              ),
                            _buildDetailRow(
                              localizations.addedOn,
                              _formatDate(badge.createdAt),
                              theme,
                            ),
                            
                            // Requirements section
                            if (!isEarned && badge.requirementsJson.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              const Divider(),
                              Text(
                                localizations.requirements,
                                style: theme.textTheme.titleSmall,
                              ),
                              const SizedBox(height: 8),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: _buildRequirementsList(badge, localizations, theme),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    GradientButton(
                      text: localizations.close,
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

  Widget _buildDetailRow(String label, String value, ThemeData theme, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: theme.textTheme.bodyMedium,
          ),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }

  List<Widget> _buildRequirementsList(
    app_badge.Badge badge,
    AppLocalizations localizations,
    ThemeData theme,
  ) {
    final requirements = <Widget>[];
    
    badge.requirementsJson.forEach((key, value) {
      if (value is int || value is double) {
        String requirementText;
        
        switch (key) {
          case 'posts_count':
            requirementText = '${localizations.instagramPosts}: $value';
            break;
          case 'followers_count':
            requirementText = '${localizations.followers}: $value';
            break;
          case 'days_streak':
            requirementText = '${localizations.daysStreak}: $value';
            break;
          case 'level':
            requirementText = '${localizations.accountLevel}: $value';
            break;
          case 'coins':
            requirementText = '${localizations.coins}: $value';
            break;
          default:
            requirementText = '$key: $value';
        }
        
        requirements.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 2.0),
            child: Row(
              children: [
                const Icon(
                  Icons.circle,
                  size: 8,
                ),
                const SizedBox(width: 8),
                Text(requirementText),
              ],
            ),
          ),
        );
      }
    });
    
    if (requirements.isEmpty) {
      return [Text(localizations.specialRequirements)];
    }
    
    return requirements;
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }
}
