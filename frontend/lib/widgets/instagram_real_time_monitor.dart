import 'package:flutter/material.dart';
import 'dart:async';
import '../services/instagram_service.dart';
import '../models/instagram_integration.dart';
// import '../utils/instagram_dialog_utils.dart';

class InstagramRealTimeMonitor extends StatefulWidget {
  final String? userToken;
  final Function(Map<String, dynamic> statusUpdate) onStatusUpdate;

  const InstagramRealTimeMonitor({
    Key? key,
    this.userToken,
    required this.onStatusUpdate,
  }) : super(key: key);

  @override
  State<InstagramRealTimeMonitor> createState() => _InstagramRealTimeMonitorState();
}

class _InstagramRealTimeMonitorState extends State<InstagramRealTimeMonitor>
    with SingleTickerProviderStateMixin {
  final InstagramService _instagramService = InstagramService();
  
  Timer? _monitoringTimer;
  Timer? _heartbeatTimer;
  InstagramConnectionStatus? _connectionStatus;
  Map<String, dynamic>? _accountHealth;
  List<Map<String, dynamic>> _recentErrors = [];
  bool _isMonitoring = false;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    _pulseController.repeat(reverse: true);
    _startMonitoring();
  }

  @override
  void dispose() {
    // Timer'ları iptal et ama setState çağırma
    _monitoringTimer?.cancel();
    _heartbeatTimer?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  void _startMonitoring() {
    if (_isMonitoring) return;
    
    if (mounted) {
      setState(() {
        _isMonitoring = true;
      });
    }

    // Check connection status every 30 seconds
    _monitoringTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      _checkConnectionStatus();
    });

    // Heartbeat check every 5 minutes
    _heartbeatTimer = Timer.periodic(const Duration(minutes: 5), (timer) {
      _performHeartbeatCheck();
    });

    // Initial check
    _checkConnectionStatus();
    _performHeartbeatCheck();
  }

  void _stopMonitoring() {
    _monitoringTimer?.cancel();
    _heartbeatTimer?.cancel();
    // Widget dispose edilirken setState çağırma
    if (mounted) {
      setState(() {
        _isMonitoring = false;
      });
    }
  }

  Future<void> _checkConnectionStatus() async {
    if (widget.userToken == null || !mounted) return;

    try {
      final status = await _instagramService.getConnectionStatus(widget.userToken!);
      if (mounted) {
        setState(() {
          _connectionStatus = status;
        });

        widget.onStatusUpdate({
          'type': 'connection_status',
          'status': status.connectionStatus,
          'is_connected': status.isConnected,
          'requires_challenge': status.requiresChallenge,
          'timestamp': DateTime.now().toIso8601String(),
        });

        // Handle challenge automatically if required
        if (status.requiresChallenge && status.challengeInfo != null) {
          _handleAutomaticChallenge(status.challengeInfo!);
        }
      }
    } catch (e) {
      if (mounted) {
        _addError('connection_check', e.toString());
      }
    }
  }

  Future<void> _performHeartbeatCheck() async {
    if (widget.userToken == null || !mounted) return;

    try {
      final isAlive = await _instagramService.testConnection(widget.userToken!);
      final health = await _instagramService.getAccountHealth(widget.userToken!);
      
      if (mounted) {
        setState(() {
          _accountHealth = health;
        });

        widget.onStatusUpdate({
          'type': 'heartbeat',
          'is_alive': isAlive,
          'health': health,
          'timestamp': DateTime.now().toIso8601String(),
        });

        if (!isAlive) {
          _addError('heartbeat_failed', 'Instagram connection is not responding');
        }
      }
    } catch (e) {
      if (mounted) {
        _addError('heartbeat_error', e.toString());
      }
    }
  }

  void _addError(String type, String message) {
    if (!mounted) return;
    
    setState(() {
      _recentErrors.insert(0, {
        'type': type,
        'message': message,
        'timestamp': DateTime.now(),
      });
      // Keep only last 10 errors
      if (_recentErrors.length > 10) {
        _recentErrors = _recentErrors.take(10).toList();
      }
    });

    widget.onStatusUpdate({
      'type': 'error',
      'error_type': type,
      'error_message': message,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  Future<void> _handleAutomaticChallenge(InstagramChallenge challenge) async {
    // Show challenge dialog automatically
    // Temporary implementation - will be replaced with proper dialog
    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Instagram Challenge'),
        content: Text(challenge.message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Complete'),
          ),
        ],
      ),
    );

    if (result == true) {
      // Refresh connection status after successful challenge
      await _checkConnectionStatus();
    }
  }

  Color get _statusColor {
    if (_connectionStatus == null) return Colors.grey;
    
    if (_connectionStatus!.isConnected) {
      return Colors.green;
    } else if (_connectionStatus!.requiresChallenge) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  IconData get _statusIcon {
    if (_connectionStatus == null) return Icons.help_outline;
    
    if (_connectionStatus!.isConnected) {
      return Icons.check_circle;
    } else if (_connectionStatus!.requiresChallenge) {
      return Icons.security;
    } else {
      return Icons.error;
    }
  }

  String get _statusText {
    if (_connectionStatus == null) return 'Checking...';
    
    if (_connectionStatus!.isConnected) {
      return 'Connected';
    } else if (_connectionStatus!.requiresChallenge) {
      return 'Challenge Required';
    } else {
      return 'Disconnected';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                AnimatedBuilder(
                  animation: _pulseAnimation,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: _isMonitoring ? _pulseAnimation.value : 1.0,
                      child: Icon(
                        Icons.monitor_heart,
                        color: _isMonitoring ? Colors.blue : Colors.grey,
                        size: 24,
                      ),
                    );
                  },
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Instagram Connection Monitor',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Switch(
                  value: _isMonitoring,
                  onChanged: (value) {
                    if (value) {
                      _startMonitoring();
                    } else {
                      _stopMonitoring();
                    }
                  },
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Connection Status
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _statusColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _statusColor.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _statusIcon,
                    color: _statusColor,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _statusText,
                    style: TextStyle(
                      color: _statusColor,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (_connectionStatus?.lastVerified != null) ...[
                    const Spacer(),
                    Text(
                      'Last: ${_formatTime(_connectionStatus!.lastVerified!)}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            
            // Account Health
            if (_accountHealth != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.health_and_safety,
                          color: Colors.blue[600],
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Account Health',
                          style: TextStyle(
                            color: Colors.blue[700],
                            fontWeight: FontWeight.w500,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: _accountHealth!.entries.map((entry) {
                        final isGood = _isHealthMetricGood(entry.key, entry.value);
                        return Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: isGood ? Colors.green[100] : Colors.orange[100],
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            '${entry.key}: ${entry.value}',
                            style: TextStyle(
                              fontSize: 10,
                              color: isGood ? Colors.green[700] : Colors.orange[700],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ],
            
            // Recent Errors
            if (_recentErrors.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.error_outline,
                          color: Colors.red[600],
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Recent Issues (${_recentErrors.length})',
                          style: TextStyle(
                            color: Colors.red[700],
                            fontWeight: FontWeight.w500,
                            fontSize: 12,
                          ),
                        ),
                        const Spacer(),
                        TextButton(
                          onPressed: () {
                            if (mounted) {
                              setState(() {
                                _recentErrors.clear();
                              });
                            }
                          },
                          style: TextButton.styleFrom(
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(0, 0),
                          ),
                          child: Text(
                            'Clear',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.red[600],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ...(_recentErrors.take(3).map((error) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          children: [
                            Container(
                              width: 4,
                              height: 4,
                              decoration: BoxDecoration(
                                color: Colors.red[400],
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                '${error['type']}: ${error['message']}',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.red[600],
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              _formatTime(error['timestamp']),
                              style: TextStyle(
                                fontSize: 9,
                                color: Colors.red[400],
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList()),
                  ],
                ),
              ),
            ],
            
            // Actions
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _checkConnectionStatus,
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text('Check Now'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _performHeartbeatCheck,
                    icon: const Icon(Icons.favorite, size: 16),
                    label: const Text('Health Check'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  bool _isHealthMetricGood(String key, dynamic value) {
    switch (key.toLowerCase()) {
      case 'rate_limit_remaining':
        return (value as num) > 10;
      case 'account_status':
        return value == 'active';
      case 'api_calls_today':
        return (value as num) < 1000;
      case 'errors_last_hour':
        return (value as num) < 5;
      default:
        return true;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    
    if (diff.inMinutes < 1) {
      return 'now';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}m';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}h';
    } else {
      return '${diff.inDays}d';
    }
  }
}

// Live Activity Feed Widget
class InstagramActivityFeed extends StatefulWidget {
  final String? userToken;
  final int maxItems;

  const InstagramActivityFeed({
    Key? key,
    this.userToken,
    this.maxItems = 50,
  }) : super(key: key);

  @override
  State<InstagramActivityFeed> createState() => _InstagramActivityFeedState();
}

class _InstagramActivityFeedState extends State<InstagramActivityFeed> {
  final List<Map<String, dynamic>> _activities = [];
  final ScrollController _scrollController = ScrollController();
  bool _autoScroll = true;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void addActivity(Map<String, dynamic> activity) {
    if (!mounted) return;
    
    setState(() {
      _activities.insert(0, {
        ...activity,
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'timestamp': DateTime.now(),
      });
      
      // Keep only recent activities
      if (_activities.length > widget.maxItems) {
        _activities.removeRange(widget.maxItems, _activities.length);
      }
    });

    // Auto-scroll to top if enabled
    if (_autoScroll && _scrollController.hasClients) {
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  IconData _getActivityIcon(String type) {
    switch (type.toLowerCase()) {
      case 'connection_status':
        return Icons.link;
      case 'heartbeat':
        return Icons.favorite;
      case 'error':
        return Icons.error;
      case 'task_validation':
        return Icons.task_alt;
      case 'challenge_completed':
        return Icons.security;
      case 'sync':
        return Icons.sync;
      default:
        return Icons.info;
    }
  }

  Color _getActivityColor(String type) {
    switch (type.toLowerCase()) {
      case 'connection_status':
        return Colors.blue;
      case 'heartbeat':
        return Colors.green;
      case 'error':
        return Colors.red;
      case 'task_validation':
        return Colors.purple;
      case 'challenge_completed':
        return Colors.orange;
      case 'sync':
        return Colors.teal;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.feed, size: 20),
                const SizedBox(width: 8),
                const Text(
                  'Activity Feed',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const Spacer(),
                Row(
                  children: [
                    Text(
                      'Auto-scroll',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(width: 4),
                    Switch(
                      value: _autoScroll,
                      onChanged: (value) {
                        if (mounted) {
                          setState(() {
                            _autoScroll = value;
                          });
                        }
                      },
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ],
                ),
                IconButton(
                  onPressed: () {
                    if (mounted) {
                      setState(() {
                        _activities.clear();
                      });
                    }
                  },
                  icon: const Icon(Icons.clear_all, size: 18),
                  tooltip: 'Clear all',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
            ),
          ),
          
          // Activity List
          Container(
            height: 200,
            child: _activities.isEmpty
                ? Center(
                    child: Text(
                      'No recent activity',
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 12,
                      ),
                    ),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(8),
                    itemCount: _activities.length,
                    itemBuilder: (context, index) {
                      final activity = _activities[index];
                      final color = _getActivityColor(activity['type']);
                      
                      return Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.05),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                            color: color.withValues(alpha: 0.2),
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _getActivityIcon(activity['type']),
                              size: 14,
                              color: color,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _formatActivityMessage(activity),
                                style: const TextStyle(fontSize: 11),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              _formatTime(activity['timestamp']),
                              style: TextStyle(
                                fontSize: 9,
                                color: Colors.grey[500],
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
    );
  }

  String _formatActivityMessage(Map<String, dynamic> activity) {
    switch (activity['type']) {
      case 'connection_status':
        return 'Connection ${activity['status']}: ${activity['is_connected'] ? 'Connected' : 'Disconnected'}';
      case 'heartbeat':
        return 'Heartbeat check: ${activity['is_alive'] ? 'Alive' : 'Failed'}';
      case 'error':
        return 'Error (${activity['error_type']}): ${activity['error_message']}';
      case 'task_validation':
        return 'Task #${activity['task_id']} validated: ${activity['success'] ? 'Success' : 'Failed'}';
      case 'challenge_completed':
        return 'Security challenge completed: ${activity['challenge_type']}';
      case 'sync':
        return 'Profile sync: ${activity['status']}';
      default:
        return activity['message'] ?? 'Unknown activity';
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    
    if (diff.inSeconds < 60) {
      return '${diff.inSeconds}s';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h';
    } else {
      return '${diff.inDays}d';
    }
  }
}
