import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/instagram_service.dart';
import '../models/instagram_integration.dart';
import '../widgets/instagram_error_handler.dart';
import '../widgets/instagram_task_validation_widget.dart';
import '../widgets/instagram_real_time_monitor.dart';
import '../providers/user_provider.dart';

class InstagramIntegrationDashboard extends ConsumerStatefulWidget {
  const InstagramIntegrationDashboard({
    super.key,
  });

  @override
  ConsumerState<InstagramIntegrationDashboard> createState() => _InstagramIntegrationDashboardState();
}

class _InstagramIntegrationDashboardState extends ConsumerState<InstagramIntegrationDashboard>
    with TickerProviderStateMixin {
  final InstagramService _instagramService = InstagramService();
  final PageController _pageController = PageController();
  
  late TabController _tabController;
  
  InstagramProfile? _profile;
  InstagramConnectionStatus? _connectionStatus;
  List<InstagramPost> _posts = [];
  List<Map<String, dynamic>> _availableTasks = [];
  List<Map<String, dynamic>> _errors = [];
  Map<String, dynamic>? _analytics;
  
  bool _isLoading = true;
  bool _isConnected = false;
  int _completedTasks = 0;
  int _totalDiamondsEarned = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _loadDashboardData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _loadDashboardData() async {
    final userAsync = ref.read(userProvider);
    final userToken = userAsync.value?.token;
    
    if (userToken == null) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Load all data in parallel
      final results = await Future.wait([
        _instagramService.getProfile(userToken),
        _instagramService.getConnectionStatus(userToken),
        _instagramService.getPosts(userToken, limit: 10),
        _instagramService.getAnalytics(userToken),
        _instagramService.getSyncErrors(userToken),
      ]);

      setState(() {
        _profile = results[0] as InstagramProfile?;
        _connectionStatus = results[1] as InstagramConnectionStatus;
        _posts = results[2] as List<InstagramPost>;
        _analytics = results[3] as Map<String, dynamic>?;
        _errors = (results[4] as List<Map<String, dynamic>>);
        _isConnected = _connectionStatus?.isConnected ?? false;
        
        // Mock available tasks (in real app, this would come from backend)
        _availableTasks = _generateMockTasks();
      });

      // Dashboard loaded successfully
    } catch (e) {
      _addError('dashboard_load', e.toString());
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  List<Map<String, dynamic>> _generateMockTasks() {
    return [
      {
        'id': 1,
        'type': 'like',
        'description': 'Like 5 Instagram posts',
        'diamonds_reward': 10,
        'target_url': 'https://instagram.com/p/example1',
      },
      {
        'id': 2,
        'type': 'follow',
        'description': 'Follow 3 Instagram accounts',
        'diamonds_reward': 15,
        'target_url': 'https://instagram.com/example_account',
      },
      {
        'id': 3,
        'type': 'comment',
        'description': 'Comment on 2 posts',
        'diamonds_reward': 20,
        'target_url': 'https://instagram.com/p/example2',
      },
    ];
  }

  void _addError(String type, String message) {
    setState(() {
      _errors.insert(0, {
        'type': type,
        'message': message,
        'timestamp': DateTime.now(),
      });
    });
  }

  void _onStatusUpdate(Map<String, dynamic> update) {
    // Status update received
    
    // Handle specific status updates
    if (update['type'] == 'error') {
      _addError(update['error_type'], update['error_message']);
    }
  }

  void _onErrorsResolved(int resolvedCount) {
    // Errors resolved: $resolvedCount
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Instagram Integration'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.blue,
          unselectedLabelColor: Colors.grey,
          indicatorColor: Colors.blue,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Overview'),
            Tab(icon: Icon(Icons.task_alt), text: 'Tasks'),
            Tab(icon: Icon(Icons.analytics), text: 'Analytics'),
            Tab(icon: Icon(Icons.error_outline), text: 'Issues'),
            Tab(icon: Icon(Icons.settings), text: 'Settings'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildOverviewTab(),
                _buildTasksTab(),
                _buildAnalyticsTab(),
                _buildIssuesTab(),
                _buildSettingsTab(),
              ],
            ),
    );
  }

  Widget _buildOverviewTab() {
    final userAsync = ref.read(userProvider);
    final userToken = userAsync.value?.token;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Connection Status Card
          _buildConnectionStatusCard(),
          
          const SizedBox(height: 16),
          
          // Profile Summary Card
          if (_profile != null) _buildProfileSummaryCard(),
          
          const SizedBox(height: 16),
          
          // Real-time Monitor
          if (userToken != null)
            InstagramRealTimeMonitor(
              userToken: userToken,
              onStatusUpdate: _onStatusUpdate,
            ),
          
          const SizedBox(height: 16),
          
          // Activity Feed (Mock implementation since InstagramActivityFeed might not exist)
          _buildActivityFeedCard(),
          
          const SizedBox(height: 16),
          
          // Quick Stats
          _buildQuickStatsCard(),
        ],
      ),
    );
  }

  Widget _buildTasksTab() {
    final userAsync = ref.read(userProvider);
    final userToken = userAsync.value?.token;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Tasks Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.purple[100]!, Colors.blue[100]!],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(Icons.task_alt, color: Colors.purple[700], size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Instagram Tasks',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.purple[700],
                        ),
                      ),
                      Text(
                        'Complete tasks to earn diamonds',
                        style: TextStyle(
                          color: Colors.purple[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.amber[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.diamond, color: Colors.blue[700], size: 16),
                      const SizedBox(width: 4),
                      Text(
                        '$_totalDiamondsEarned',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.amber[700],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Task List
          if (_isConnected && userToken != null)
            _buildTaskListWidget(userToken)
          else
            _buildConnectionRequiredCard(),
        ],
      ),
    );
  }

  Widget _buildAnalyticsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Analytics Header
          const Text(
            'Analytics & Insights',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          
          if (_analytics != null) ...[
            // Analytics Cards
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.5,
              children: _analytics!.entries.map((entry) {
                return _buildAnalyticsCard(entry.key, entry.value);
              }).toList(),
            ),
            
            const SizedBox(height: 16),
            
            // Recent Posts
            if (_posts.isNotEmpty) _buildRecentPostsCard(),
          ] else
            _buildNoAnalyticsCard(),
        ],
      ),
    );
  }

  Widget _buildIssuesTab() {
    final userAsync = ref.read(userProvider);
    final userToken = userAsync.value?.token;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Issues Header
          Row(
            children: [
              Icon(Icons.error_outline, color: Colors.red[600], size: 28),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Issues & Troubleshooting',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (_errors.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.red[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${_errors.length}',
                    style: TextStyle(
                      color: Colors.red[700],
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          if (_errors.isNotEmpty)
            InstagramErrorManager(
              errors: _errors,
              userToken: userToken,
              onErrorsResolved: _onErrorsResolved,
            )
          else
            _buildNoIssuesCard(),
        ],
      ),
    );
  }

  Widget _buildSettingsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Settings Header
          const Text(
            'Instagram Settings',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          
          // Connection Management
          _buildConnectionManagementCard(),
          
          const SizedBox(height: 16),
          
          // Sync Settings
          _buildSyncSettingsCard(),
          
          const SizedBox(height: 16),
          
          // Security Settings
          _buildSecuritySettingsCard(),
        ],
      ),
    );
  }

  Widget _buildConnectionStatusCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: _isConnected 
                ? [Colors.green[50]!, Colors.green[100]!]
                : [Colors.red[50]!, Colors.red[100]!],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _isConnected ? Colors.green : Colors.red,
                shape: BoxShape.circle,
              ),
              child: Icon(
                _isConnected ? Icons.check : Icons.close,
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
                    _isConnected ? 'Instagram Connected' : 'Instagram Disconnected',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _isConnected ? Colors.green[700] : Colors.red[700],
                    ),
                  ),
                  if (_connectionStatus != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      _connectionStatus!.connectionStatus,
                      style: TextStyle(
                        color: _isConnected ? Colors.green[600] : Colors.red[600],
                        fontSize: 14,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            if (!_isConnected)
              ElevatedButton(
                onPressed: () {
                  // Navigate to connection screen
                },
                child: const Text('Connect'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileSummaryCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              radius: 30,
              backgroundImage: (_profile != null && _profile!.profilePicUrl.isNotEmpty)
                  ? NetworkImage(_profile!.profilePicUrl)
                  : const AssetImage('assets/instagram_default_avatar.png') as ImageProvider,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _profile!.username,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    _profile!.fullName,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildStatChip('Posts', _profile!.postsCount),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatChip(String label, int value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          fontSize: 12,
          color: Colors.blue[700],
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildQuickStatsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quick Stats',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildQuickStat('Tasks Completed', '$_completedTasks', Icons.task_alt, Colors.green),
                ),
                Expanded(
                  child: _buildQuickStat('Diamonds Earned', '$_totalDiamondsEarned', Icons.diamond, Colors.blue),
                ),
                Expanded(
                  child: _buildQuickStat('Active Issues', '${_errors.length}', Icons.error_outline, Colors.red),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStat(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: color.withValues(alpha: 0.8),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildConnectionRequiredCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Icon(Icons.link_off, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'Instagram Connection Required',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Please connect your Instagram account to access tasks',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to connection screen
              },
              icon: const Icon(Icons.link),
              label: const Text('Connect Instagram'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsCard(String key, dynamic value) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              value.toString(),
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              key.replaceAll('_', ' ').toUpperCase(),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentPostsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Posts',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              height: 100,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _posts.length,
                itemBuilder: (context, index) {
                  final post = _posts[index];
                  return Container(
                    width: 100,
                    margin: const EdgeInsets.only(right: 8),
                    child: Column(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(
                              post.mediaUrl,
                              fit: BoxFit.cover,
                              width: double.infinity,
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${post.likeCount} likes',
                          style: const TextStyle(fontSize: 10),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoAnalyticsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Icon(Icons.analytics, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No Analytics Data',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Analytics will be available after connecting your Instagram account',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoIssuesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Icon(Icons.check_circle, size: 48, color: Colors.green[400]),
            const SizedBox(height: 16),
            Text(
              'No Issues Detected',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.green[700],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Your Instagram integration is working perfectly',
              style: TextStyle(
                color: Colors.green[600],
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTaskListWidget(String userToken) {
    return InstagramTaskListWidget(
      tasks: _availableTasks,
      userToken: userToken,
      onTasksComplete: (completedTasks, totalDiamonds) {
        setState(() {
          _completedTasks = completedTasks;
          _totalDiamondsEarned = totalDiamonds;
        });
      },
    );
  }

  Widget _buildActivityFeedCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Activity Feed',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey[200]!),
              ),
              child: _isConnected
                  ? InstagramActivityFeed(
                      userToken: ref.read(userProvider).value?.token,
                      maxItems: 10,
                    )
                  : Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: const [
                          Icon(Icons.timeline, size: 32, color: Colors.grey),
                          SizedBox(height: 8),
                          Text(
                            'Connect Instagram to see activity',
                            style: TextStyle(color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectionManagementCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Connection Management',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ListTile(
              leading: const Icon(Icons.link),
              title: const Text('Test Connection'),
              subtitle: const Text('Verify Instagram connection'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // Test connection
              },
            ),
            ListTile(
              leading: const Icon(Icons.refresh),
              title: const Text('Refresh Account'),
              subtitle: const Text('Update profile and posts'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // Refresh account
              },
            ),
            if (_isConnected)
              ListTile(
                leading: Icon(Icons.link_off, color: Colors.red[600]),
                title: Text('Disconnect', style: TextStyle(color: Colors.red[600])),
                subtitle: const Text('Remove Instagram connection'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // Disconnect
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSyncSettingsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sync Settings',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            SwitchListTile(
              title: const Text('Auto Sync Profile'),
              subtitle: const Text('Automatically update profile data'),
              value: true,
              onChanged: (value) {
                // Update setting
              },
            ),
            SwitchListTile(
              title: const Text('Real-time Monitoring'),
              subtitle: const Text('Monitor connection status'),
              value: true,
              onChanged: (value) {
                // Update setting
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSecuritySettingsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Security Settings',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ListTile(
              leading: const Icon(Icons.security),
              title: const Text('Challenge Settings'),
              subtitle: const Text('Configure security challenges'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // Open challenge settings
              },
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('Activity Log'),
              subtitle: const Text('View connection history'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // Open activity log
              },
            ),
          ],
        ),
      ),
    );
  }
}
