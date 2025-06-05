import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/leaderboard.dart';
import '../services/social_service.dart';
import '../services/api_client.dart';
import '../providers/user_provider.dart';
import '../generated/app_localizations.dart';

class LeaderboardScreen extends ConsumerStatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  ConsumerState<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends ConsumerState<LeaderboardScreen> 
    with TickerProviderStateMixin {
  late SocialService _socialService;
  
  late TabController _tabController;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  
  List<Leaderboard> _weeklyLeaderboard = [];
  List<Leaderboard> _monthlyLeaderboard = [];
  List<Leaderboard> _allTimeLeaderboard = [];
  
  Map<String, dynamic>? _currentUserRank;
  bool _isLoading = true;
  bool _hasError = false;
  
  @override
  void initState() {
    super.initState();
    // Initialize SocialService with shared ApiClient
    _socialService = SocialService(apiClient: ref.read(apiClientProvider));
    
    _tabController = TabController(length: 3, vsync: this);
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animationController, curve: Curves.easeOutCubic));
    
    _loadLeaderboardData();
    _animationController.forward();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    _animationController.dispose();
    super.dispose();
  }
  
  Future<void> _loadLeaderboardData() async {
    final userAsync = ref.read(userProvider);
    final userToken = userAsync.value?.token;
    
    if (userToken == null) return;
    
    setState(() {
      _isLoading = true;
      _hasError = false;
    });
    
    try {
      final results = await Future.wait([
        _socialService.getLeaderboard(userToken, period: 'weekly'),
        _socialService.getLeaderboard(userToken, period: 'monthly'),
        _socialService.getLeaderboard(userToken, period: 'all'),
        _socialService.getUserRank(userToken),
      ]);
      
      setState(() {
        _weeklyLeaderboard = results[0] as List<Leaderboard>;
        _monthlyLeaderboard = results[1] as List<Leaderboard>;
        _allTimeLeaderboard = results[2] as List<Leaderboard>;
        _currentUserRank = results[3] as Map<String, dynamic>;
        _isLoading = false;
      });
    } catch (e, stack) {
      print('Leaderboard load error: ' + e.toString());
      print(stack);
      setState(() {
        _hasError = true;
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final locale = AppLocalizations.of(context);
    final userAsync = ref.watch(userProvider);
    
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF8F9FA), Color(0xFFE9ECEF)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Custom App Bar
              Container(
                padding: const EdgeInsets.all(20),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFFDD2A7B), Color(0xFF8134AF)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.arrow_back, color: Colors.white),
                          onPressed: () {
                            if (context.canPop()) {
                              context.pop();
                            } else {
                              context.go('/main/profile');
                            }
                          },
                        ),
                        Expanded(
                          child: Text(
                            locale.leaderboard,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.refresh, color: Colors.white),
                          onPressed: _loadLeaderboardData,
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    
                    // Current User Rank Card
                    if (_currentUserRank != null)
                      FadeTransition(
                        opacity: _fadeAnimation,
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: Colors.white.withValues(alpha: 0.3)),
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 32,
                                height: 32,
                                decoration: const BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                ),
                                child: Center(
                                  child: Text(
                                    '#${_currentUserRank!['rank'] ?? '?'}',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFFDD2A7B),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      '${userAsync.value?.username ?? 'User'}',
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.white,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 1,
                                    ),
                                    Text(
                                      '${_currentUserRank!['score'] ?? 0} puan',
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.white70,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 1,
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                constraints: const BoxConstraints(maxWidth: 60),
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  '${_currentUserRank!['score'] ?? 0}',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              
              // Tab Bar
              Container(
                color: Colors.white,
                child: TabBar(
                  controller: _tabController,
                  labelColor: const Color(0xFFDD2A7B),
                  unselectedLabelColor: Colors.grey,
                  indicatorColor: const Color(0xFFDD2A7B),
                  indicatorWeight: 3,
                  tabs: [
                    Tab(text: locale.weeklyRanking),
                    Tab(text: locale.monthlyRanking),
                    Tab(text: locale.all),
                  ],
                ),
              ),
              
              // Content
              Expanded(
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: SlideTransition(
                    position: _slideAnimation,
                    child: _isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : _hasError
                            ? _buildErrorWidget(locale)
                            : TabBarView(
                                controller: _tabController,
                                children: [
                                  _buildLeaderboardList(_weeklyLeaderboard),
                                  _buildLeaderboardList(_monthlyLeaderboard),
                                  _buildLeaderboardList(_allTimeLeaderboard),
                                ],
                              ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildErrorWidget(AppLocalizations locale) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            locale.errorOccurred,
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadLeaderboardData,
            child: Text(locale.retry),
          ),
        ],
      ),
    );
  }
  
  Widget _buildLeaderboardList(List<Leaderboard> leaderboard) {
    if (leaderboard.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.emoji_events_outlined,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              AppLocalizations.of(context).noDataToExport,
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: leaderboard.length,
      itemBuilder: (context, index) {
        final entry = leaderboard[index];
        return AnimatedContainer(
          duration: Duration(milliseconds: 200 + (index * 50)),
          margin: const EdgeInsets.only(bottom: 12),
          child: _buildLeaderboardCard(entry, index),
        );
      },
    );
  }
  
  Widget _buildLeaderboardCard(Leaderboard entry, int index) {
    final isTopThree = entry.rank <= 3;
    final userAsync = ref.watch(userProvider);
    final isCurrentUser = userAsync.value?.id?.toString() == entry.userId.toString();
    const String defaultAvatarAsset = 'assets/instagram_default_avatar.png';
    Color? rankColor;
    IconData? rankIcon;
    switch (entry.rank) {
      case 1:
        rankColor = const Color(0xFFFFD700); // Gold
        rankIcon = Icons.emoji_events;
        break;
      case 2:
        rankColor = const Color(0xFFC0C0C0); // Silver
        rankIcon = Icons.emoji_events;
        break;
      case 3:
        rankColor = const Color(0xFFCD7F32); // Bronze
        rankIcon = Icons.emoji_events;
        break;
      default:
        rankColor = Colors.grey[600];
        rankIcon = Icons.person;
    }
    return Container(
      decoration: BoxDecoration(
        gradient: isCurrentUser
            ? const LinearGradient(
                colors: [Color(0xFF8134AF), Color(0xFFDD2A7B)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : null,
        color: isCurrentUser ? null : Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: isTopThree ? rankColor!.withAlpha(77) : Colors.black.withAlpha(25),
            blurRadius: isTopThree ? 8 : 4,
            offset: const Offset(0, 2),
          ),
        ],
        border: isTopThree
            ? Border.all(color: rankColor!, width: 2)
            : null,
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // Profile Picture
            CircleAvatar(
              radius: 20,
              backgroundColor: Colors.grey[200],
              child: entry.profilePicUrl.isNotEmpty 
                ? ClipOval(
                    child: Image.network(
                      entry.profilePicUrl,
                      width: 40,
                      height: 40,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return CircleAvatar(
                          radius: 20,
                          backgroundColor: Colors.grey[300], 
                          child: Text(entry.username[0].toUpperCase(), style: TextStyle(color: isCurrentUser ? Colors.white : Colors.black)),
                        );
                      },
                      loadingBuilder: (context, child, loadingProgress) {
                        if (loadingProgress == null) return child;
                        return CircularProgressIndicator(
                          value: loadingProgress.expectedTotalBytes != null 
                            ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                            : null,
                          strokeWidth: 2,
                        );
                      },
                    ),
                  )
                : Text(entry.username[0].toUpperCase(), style: TextStyle(color: isCurrentUser ? Colors.white : Colors.black)),
            ),
            const SizedBox(width: 12),
            // Rank
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: isCurrentUser ? Colors.white.withAlpha(51) : rankColor?.withAlpha(25),
                shape: BoxShape.circle,
                border: isTopThree
                    ? Border.all(color: rankColor!, width: 2)
                    : null,
              ),
              child: Center(
                child: isTopThree
                    ? Icon(rankIcon, color: rankColor, size: 20)
                    : Text(
                        '${entry.rank}',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: isCurrentUser ? Colors.white : rankColor,
                        ),
                      ),
              ),
            ),
            const SizedBox(width: 12),
            // User Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    entry.username,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: isCurrentUser ? Colors.white : Colors.black87,
                    ),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                  if (isCurrentUser) ...[
                    const SizedBox(height: 2),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                      decoration: BoxDecoration(
                        color: Colors.white.withAlpha(51),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        AppLocalizations.of(context).you,
                        style: const TextStyle(
                          fontSize: 9,
                          color: Colors.white,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 2),
                ],
              ),
            ),
            const SizedBox(width: 8),
            // Score
            SizedBox(
              width: 80,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${entry.totalCoins}',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: isCurrentUser ? Colors.white : const Color(0xFFDD2A7B),
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    AppLocalizations.of(context).totalCoins,
                    style: TextStyle(
                      fontSize: 11,
                      color: isCurrentUser ? Colors.white70 : Colors.grey[600],
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
