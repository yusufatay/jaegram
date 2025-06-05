import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../generated/app_localizations.dart';

import '../providers/user_provider.dart';
import '../providers/instagram_profile_provider.dart';
import '../providers/instagram_posts_provider.dart';
import '../models/user.dart';
import '../models/instagram_post.dart';
import '../widgets/gradient_button.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final localizations = AppLocalizations.of(context);
    final userAsync = ref.watch(userProvider);
    final instagramProfileAsync = ref.watch(instagramProfileProvider);
    final instagramPostsAsync = ref.watch(instagramPostsProvider);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      appBar: AppBar(
        title: Text(localizations.profile),
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: Container(
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
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.go('/settings'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(userProvider);
          ref.invalidate(instagramProfileProvider);
          ref.invalidate(instagramPostsProvider);
        },
        child: userAsync.when(
          data: (user) => user != null ? _buildProfileContent(
            context, 
            theme, 
            localizations, 
            user, 
            instagramProfileAsync, 
            instagramPostsAsync
          ) : const Center(child: Text('User data not available')),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Center(
            child: Text('Error: $error'),
          ),
        ),
      ),
    );
  }

  Widget _buildProfileContent(
    BuildContext context,
    ThemeData theme,
    AppLocalizations localizations,
    User user,
    AsyncValue<InstagramProfileStats?> instagramProfileAsync,
    AsyncValue<List<InstagramPost>> instagramPostsAsync,
  ) {
    return SingleChildScrollView(
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
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  // Profile Photo
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 4),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.3),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: ClipOval(
                      child: user.profilePicUrl != null && user.profilePicUrl!.isNotEmpty
                          ? Image.network(
                              user.profilePicUrl!,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) => 
                                  _buildDefaultProfileImage(),
                            )
                          : _buildDefaultProfileImage(),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // User Info
                  Text(
                    user.fullName ?? user.username,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  
                  Text(
                    '@${user.username}',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.8),
                      fontSize: 16,
                    ),
                  ),
                  
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
                                  profile.username,
                                  style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.8),
                                    fontSize: 12,
                                  ),
                                ),
                                if (profile.isVerified ?? false) ...[
                                  const SizedBox(width: 4),
                                  Icon(
                                    Icons.verified,
                                    color: Colors.blue[400],
                                    size: 16,
                                  ),
                                ],
                              ],
                            ),
                            const SizedBox(height: 12),
                            // Instagram Stats
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                              children: [
                                _StatItem(
                                  label: localizations.posts,
                                  value: _formatNumber(profile.mediaCount ?? 0),
                                ),
                              ],
                            ),
                          ],
                        );
                      } else {
                        // Instagram not connected - show platform stats
                        return Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            _StatItem(
                              label: localizations.coins,
                              value: (user.diamondBalance ?? 0).toString(),
                            ),
                            _StatItem(
                              label: localizations.accountLevel,
                              value: ((user.diamondBalance ?? 0) ~/ 100 + 1).toString(),
                            ),
                            const _StatItem(
                              label: 'Rank',
                              value: 'N/A',
                            ),
                          ],
                        );
                      }
                    },
                    orElse: () => Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _StatItem(
                          label: localizations.coins,
                          value: (user.diamondBalance ?? 0).toString(),
                        ),
                        _StatItem(
                          label: localizations.accountLevel,
                          value: ((user.diamondBalance ?? 0) ~/ 100 + 1).toString(),
                        ),
                        const _StatItem(
                          label: 'Rank',
                          value: 'N/A',
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Instagram Integration Section
          instagramProfileAsync.when(
            data: (profile) {
              if (profile != null && (profile.isConnected ?? false)) {
                return _buildInstagramSection(
                  context, 
                  theme, 
                  localizations, 
                  profile, 
                  instagramPostsAsync
                );
              } else {
                return _buildConnectInstagramCard(context, theme, localizations);
              }
            },
            loading: () => const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (error, _) => _buildConnectInstagramCard(context, theme, localizations),
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
                    const SizedBox(height: 16),
                    _buildDetailItem(
                      context,
                      title: localizations.joinDate,
                      value: _formatDate(DateTime.now()), // Default since joinDate is not in new User model
                    ),
                    _buildDetailItem(
                      context,
                      title: localizations.progress,
                      value: '${user.diamondBalance} diamonds earned',
                    ),
                    _buildDetailItem(
                      context,
                      title: localizations.rank,
                      value: 'Coming Soon',
                    ),
                    const SizedBox(height: 16),
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
    );
  }

  Widget _buildDefaultProfileImage() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
        ),
      ),
      child: const Icon(
        Icons.person,
        size: 60,
        color: Colors.white,
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
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              Icon(
                Icons.camera_alt_outlined,
                size: 48,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(height: 16),
              Text(
                'Connect Instagram',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Connect your Instagram account to view your profile stats and recent posts.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                ),
              ),
              const SizedBox(height: 24),
              GradientButton(
                text: 'Connect Instagram',
                onPressed: () {
                  context.go('/instagram-login');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInstagramSection(
    BuildContext context,
    ThemeData theme,
    AppLocalizations localizations,
    InstagramProfileStats profile,
    AsyncValue<List<InstagramPost>> instagramPostsAsync,
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.camera_alt,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Instagram Posts',
                    style: theme.textTheme.titleMedium,
                  ),
                  const Spacer(),
                  if (profile.isConnected ?? false)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.check_circle,
                            size: 16,
                            color: Colors.green[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'Connected',
                            style: TextStyle(
                              color: Colors.green[600],
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 16),
              instagramPostsAsync.when(
                data: (posts) {
                  if (posts.isEmpty) {
                    return Container(
                      height: 200,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surface,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: theme.colorScheme.outline.withValues(alpha: 0.2),
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.photo_library_outlined,
                            size: 48,
                            color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No posts found',
                            style: theme.textTheme.bodyLarge?.copyWith(
                              color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Your recent Instagram posts will appear here',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
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
                      crossAxisCount: 3,
                      crossAxisSpacing: 8,
                      mainAxisSpacing: 8,
                      childAspectRatio: 1,
                    ),
                    itemCount: posts.length,
                    itemBuilder: (context, index) {
                      final post = posts[index];
                      return GestureDetector(
                        onTap: () => _showPostDetails(context, post),
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: theme.colorScheme.outline.withValues(alpha: 0.2),
                            ),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Stack(
                              fit: StackFit.expand,
                              children: [
                                if (post.imageUrl != null && post.imageUrl!.isNotEmpty)
                                  Image.network(
                                    post.imageUrl!,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) =>
                                        Container(
                                      color: theme.colorScheme.surface,
                                      child: Icon(
                                        Icons.image_not_supported,
                                        color: theme.colorScheme.onSurface
                                            .withValues(alpha: 0.5),
                                      ),
                                    ),
                                  )
                                else
                                  Container(
                                    color: theme.colorScheme.surface,
                                    child: Icon(
                                      Icons.image,
                                      color: theme.colorScheme.onSurface
                                          .withValues(alpha: 0.5),
                                    ),
                                  ),
                                if (post.videoUrl != null)
                                  const Positioned(
                                    top: 8,
                                    right: 8,
                                    child: Icon(
                                      Icons.play_circle,
                                      color: Colors.white,
                                      size: 20,
                                    ),
                                  ),
                                Positioned(
                                  bottom: 0,
                                  left: 0,
                                  right: 0,
                                  child: Container(
                                    padding: const EdgeInsets.all(4),
                                    decoration: BoxDecoration(
                                      gradient: LinearGradient(
                                        begin: Alignment.bottomCenter,
                                        end: Alignment.topCenter,
                                        colors: [
                                          Colors.black.withValues(alpha: 0.7),
                                          Colors.transparent,
                                        ],
                                      ),
                                    ),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Row(
                                          children: [
                                            const Icon(
                                              Icons.favorite,
                                              size: 12,
                                              color: Colors.white,
                                            ),
                                            const SizedBox(width: 2),
                                            Text(
                                              _formatNumber(post.likeCount ?? 0),
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 10,
                                              ),
                                            ),
                                          ],
                                        ),
                                        Row(
                                          children: [
                                            const Icon(
                                              Icons.comment,
                                              size: 12,
                                              color: Colors.white,
                                            ),
                                            const SizedBox(width: 2),
                                            Text(
                                              _formatNumber(post.commentCount ?? 0),
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 10,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  );
                },
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (error, _) => Container(
                  height: 100,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.errorContainer.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: theme.colorScheme.error.withValues(alpha: 0.2),
                    ),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.error_outline,
                          color: theme.colorScheme.error,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Failed to load posts',
                          style: TextStyle(
                            color: theme.colorScheme.error,
                          ),
                        ),
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

  Widget _buildDetailItem(
    BuildContext context, {
    required String title,
    required String value,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
            ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
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

  void _showPostDetails(BuildContext context, InstagramPost post) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400, maxHeight: 600),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Post Image
              if (post.imageUrl != null && post.imageUrl!.isNotEmpty)
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                  child: AspectRatio(
                    aspectRatio: 1,
                    child: Image.network(
                      post.imageUrl!,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) => Container(
                        color: Colors.grey[300],
                        child: const Icon(
                          Icons.image_not_supported,
                          size: 50,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                  ),
                ),
              
              // Post Details
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Engagement stats
                    Row(
                      children: [
                        Icon(Icons.favorite, color: Colors.red[400], size: 16),
                        const SizedBox(width: 4),
                        Text(_formatNumber(post.likeCount ?? 0)),
                        const SizedBox(width: 16),
                        Icon(Icons.comment, color: Colors.blue[400], size: 16),
                        const SizedBox(width: 4),
                        Text(_formatNumber(post.commentCount ?? 0)),
                      ],
                    ),
                    
                    // Caption
                    if (post.caption != null && post.caption!.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Text(
                        post.caption!,
                        style: Theme.of(context).textTheme.bodyMedium,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    
                    // Date
                    if (post.createdAt != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        _formatDate(post.createdAt!),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              
              // Close button
              Padding(
                padding: const EdgeInsets.all(16),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Close'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;

  const _StatItem({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.8),
            fontSize: 14,
          ),
        ),
      ],
    );
  }
}
