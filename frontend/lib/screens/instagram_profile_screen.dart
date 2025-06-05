import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../providers/user_provider.dart';
import '../models/user.dart';
import '../widgets/gradient_background.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';

class InstagramProfileScreen extends ConsumerStatefulWidget {
  const InstagramProfileScreen({super.key});

  @override
  ConsumerState<InstagramProfileScreen> createState() => _InstagramProfileScreenState();
}

class _InstagramProfileScreenState extends ConsumerState<InstagramProfileScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  late ScrollController _scrollController;
  bool _isScrolled = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _scrollController = ScrollController()..addListener(_onScroll);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.offset > 100 && !_isScrolled) {
      setState(() => _isScrolled = true);
    } else if (_scrollController.offset <= 100 && _isScrolled) {
      setState(() => _isScrolled = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final userAsync = ref.watch(userProvider);
    
    return Scaffold(
      body: userAsync.when(
        loading: () => _buildLoadingState(),
        error: (error, stack) => _buildErrorState(error),
        data: (user) => user != null ? _buildProfileContent(user) : _buildErrorState("Kullanıcı verisi bulunamadı"),
      ),
    );
  }

  Widget _buildLoadingState() {
    return const GradientBackground(
      child: Center(
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
        ),
      ),
    );
  }

  Widget _buildErrorState(Object error) {
    return GradientBackground(
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.white70),
            const SizedBox(height: 16),
            Text(
              'Profil yüklenirken hata oluştu',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.white70,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => ref.refresh(userProvider),
              icon: const Icon(Icons.refresh),
              label: const Text('Tekrar Dene'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.deepPurple,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileContent(User user) {
    return CustomScrollView(
      controller: _scrollController,
      slivers: [
        _buildAppBar(user),
        _buildProfileHeader(user),
        _buildStatsSection(user),
        _buildActionButtons(user),
        _buildBioSection(user),
        _buildHighlights(),
        _buildTabBar(),
        _buildTabContent(user),
      ],
    );
  }

  Widget _buildAppBar(User user) {
    return SliverAppBar(
      expandedHeight: 0,
      floating: true,
      pinned: true,
      backgroundColor: _isScrolled 
          ? Theme.of(context).scaffoldBackgroundColor.withValues(alpha: 0.9)
          : Colors.transparent,
      elevation: _isScrolled ? 1 : 0,
      leading: IconButton(
        icon: Icon(
          Icons.arrow_back_ios,
          color: _isScrolled ? Theme.of(context).primaryColor : Colors.white,
        ),
        onPressed: () => context.pop(),
      ),
      title: _isScrolled
          ? Row(
              children: [
                CircleAvatar(
                  radius: 16,
                  backgroundImage: user.profilePicUrl != null
                      ? CachedNetworkImageProvider(user.profilePicUrl!)
                      : null,
                  child: user.profilePicUrl == null
                      ? const Icon(Icons.person, size: 16)
                      : null,
                ),
                const SizedBox(width: 12),
                Text(
                  user.instagramStats?.username ?? user.username,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            )
          : null,
      actions: [
        IconButton(
          icon: Icon(
            Icons.more_vert,
            color: _isScrolled ? Theme.of(context).primaryColor : Colors.white,
          ),
          onPressed: () => _showMoreOptions(context),
        ),
      ],
    );
  }

  Widget _buildProfileHeader(User user) {
    return SliverToBoxAdapter(
      child: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF667eea),
              Color(0xFF764ba2),
              Color(0xFFf093fb),
              Color(0xFFf5576c),
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              const SizedBox(height: 40), // Space for status bar
              _buildProfilePicture(user),
              const SizedBox(height: 16),
              Text(
                user.instagramStats?.username ?? user.username,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              if (user.fullName != null && user.fullName!.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  user.fullName!,
                  style: const TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                  ),
                ),
              ],
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfilePicture(User user) {
    return Hero(
      tag: 'profile_picture',
      child: GestureDetector(
        onTap: () => _showProfilePictureFullScreen(user),
        child: Container(
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white, width: 4),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: CircleAvatar(
            radius: 60,
            backgroundColor: Colors.grey[300],
            backgroundImage: user.profilePicUrl != null
                ? CachedNetworkImageProvider(user.profilePicUrl!)
                : null,
            child: user.profilePicUrl == null
                ? const Icon(Icons.person, size: 60, color: Colors.white)
                : null,
          ),
        ),
      ),
    );
  }

  Widget _buildStatsSection(User user) {
    return SliverToBoxAdapter(
      child: Container(
        color: Theme.of(context).scaffoldBackgroundColor,
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildStatItem(
              '${user.instagramStats?.mediaCount ?? 0}',
              'Gönderi',
              Icons.grid_on,
            ),
            _buildStatItem(
              '${user.diamondBalance}',
              'Elmas',
              Icons.diamond,
              color: Colors.blue,
            ),
            _buildStatItem(
              _getLevel(user.diamondBalance ?? 0),
              'Seviye',
              Icons.trending_up,
              color: Colors.green,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String value, String label, IconData icon, {Color? color}) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: (color ?? Theme.of(context).primaryColor).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Icon(
            icon,
            size: 24,
            color: color ?? Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons(User user) {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _editProfile(),
                icon: const Icon(Icons.edit),
                label: const Text('Profili Düzenle'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).primaryColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            ElevatedButton(
              onPressed: () => _shareProfile(),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[200],
                foregroundColor: Colors.black87,
                padding: const EdgeInsets.all(12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Icon(Icons.share),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBioSection(User user) {
    if (user.instagramStats?.biography == null || 
        user.instagramStats!.biography!.isEmpty) {
      return const SliverToBoxAdapter(child: SizedBox.shrink());
    }

    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              user.instagramStats!.biography!,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildHighlights() {
    return SliverToBoxAdapter(
      child: SizedBox(
        height: 100,
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          itemCount: 5, // Mock highlights
          itemBuilder: (context, index) {
            return Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                children: [
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.grey[300]!, width: 2),
                    ),
                    child: const Icon(Icons.add, color: Colors.grey),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    index == 0 ? 'Yeni' : 'Öne Çıkan',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildTabBar() {
    return SliverPersistentHeader(
      pinned: true,
      delegate: _SliverTabBarDelegate(
        TabBar(
          controller: _tabController,
          indicatorColor: Theme.of(context).primaryColor,
          labelColor: Theme.of(context).primaryColor,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(icon: Icon(Icons.grid_on)),
            Tab(icon: Icon(Icons.video_library)),
            Tab(icon: Icon(Icons.assignment_ind)),
          ],
        ),
      ),
    );
  }

  Widget _buildTabContent(User user) {
    return SliverFillRemaining(
      child: TabBarView(
        controller: _tabController,
        children: [
          _buildPostsGrid(),
          _buildVideosGrid(),
          _buildTaggedGrid(),
        ],
      ),
    );
  }

  Widget _buildPostsGrid() {
    // Mock posts data
    return MasonryGridView.count(
      crossAxisCount: 3,
      mainAxisSpacing: 2,
      crossAxisSpacing: 2,
      padding: const EdgeInsets.all(2),
      itemCount: 15,
      itemBuilder: (context, index) {
        return GestureDetector(
          onTap: () => _showPostDetail(index),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(8),
            ),
            child: AspectRatio(
              aspectRatio: index % 3 == 0 ? 1 : 0.8,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  gradient: LinearGradient(
                    colors: [
                      Colors.primaries[index % Colors.primaries.length].withValues(alpha: 0.6),
                      Colors.primaries[index % Colors.primaries.length],
                    ],
                  ),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.image,
                        color: Colors.white,
                        size: 24,
                      ),
                      Text(
                        '${index + 1}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildVideosGrid() {
    return GridView.builder(
      padding: const EdgeInsets.all(2),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 2,
        mainAxisSpacing: 2,
      ),
      itemCount: 6,
      itemBuilder: (context, index) {
        return Container(
          decoration: BoxDecoration(
            color: Colors.grey[300],
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Center(
            child: Icon(Icons.play_circle_outline, size: 40),
          ),
        );
      },
    );
  }

  Widget _buildTaggedGrid() {
    return GridView.builder(
      padding: const EdgeInsets.all(2),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 2,
        mainAxisSpacing: 2,
      ),
      itemCount: 3,
      itemBuilder: (context, index) {
        return Container(
          decoration: BoxDecoration(
            color: Colors.grey[300],
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Center(
            child: Icon(Icons.person_pin, size: 40),
          ),
        );
      },
    );
  }

  String _getLevel(int diamonds) {
    if (diamonds < 100) return 'Başlangıç';
    if (diamonds < 500) return 'Bronz';
    if (diamonds < 1000) return 'Gümüş';
    if (diamonds < 2000) return 'Altın';
    if (diamonds < 5000) return 'Platin';
    return 'Elmas';
  }

  void _showMoreOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Ayarlar'),
              onTap: () {
                Navigator.pop(context);
                context.push('/settings');
              },
            ),
            ListTile(
              leading: const Icon(Icons.help),
              title: const Text('Yardım'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Çıkış Yap', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                _logout();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showProfilePictureFullScreen(User user) {
    Navigator.of(context).push(
      PageRouteBuilder(
        opaque: false,
        barrierColor: Colors.black,
        pageBuilder: (context, _, __) => Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            backgroundColor: Colors.transparent,
            iconTheme: const IconThemeData(color: Colors.white),
          ),
          body: Center(
            child: Hero(
              tag: 'profile_picture',
              child: InteractiveViewer(
                child: CachedNetworkImage(
                  imageUrl: user.profilePicUrl ?? '',
                  fit: BoxFit.contain,
                  errorWidget: (context, url, error) => 
                      const Icon(Icons.person, size: 200, color: Colors.white),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _showPostDetail(int index) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                height: 200,
                decoration: BoxDecoration(
                  color: Colors.primaries[index % Colors.primaries.length],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    'Post ${index + 1}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text('Bu gönderi için detay bilgileri burada gösterilecek.'),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Kapat'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _editProfile() {
    // TODO: Navigate to edit profile screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Profil düzenleme özelliği yakında eklenecek')),
    );
  }

  void _shareProfile() {
    final userAsync = ref.read(userProvider);
    
    userAsync.whenData((user) async {
      String? instagramUsername;
      
      // Get Instagram username from user's Instagram stats or fall back to username
      if (user?.instagramStats?.username != null) {
        instagramUsername = user!.instagramStats!.username;
      } else if (user?.username?.isNotEmpty == true) {
        instagramUsername = user!.username;
      }
      
      if (instagramUsername != null && instagramUsername.isNotEmpty) {
        final instagramUrl = 'https://instagram.com/$instagramUsername';
        
        try {
          await Clipboard.setData(ClipboardData(text: instagramUrl));
          
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Instagram profil bağlantısı kopyalandı! 📋\n$instagramUrl'),
                backgroundColor: Colors.green,
                duration: const Duration(seconds: 3),
              ),
            );
          }
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Bağlantı kopyalanırken hata oluştu'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Instagram kullanıcı adı bulunamadı'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    });
  }

  void _logout() {
    ref.read(userProvider.notifier).logout();
    context.go('/login');
  }
}

class _SliverTabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar _tabBar;

  _SliverTabBarDelegate(this._tabBar);

  @override
  double get minExtent => _tabBar.preferredSize.height;

  @override
  double get maxExtent => _tabBar.preferredSize.height;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      child: _tabBar,
    );
  }

  @override
  bool shouldRebuild(_SliverTabBarDelegate oldDelegate) {
    return false;
  }
}
