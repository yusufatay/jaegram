import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/instagram_service.dart';
import '../models/instagram_integration.dart';

class InstagramTaskValidationWidget extends StatefulWidget {
  final int taskId;
  final String taskType;
  final String taskDescription;
  final int coinsReward;
  final String? userToken;
  final Function(bool success, int coinsEarned) onValidationComplete;

  const InstagramTaskValidationWidget({
    Key? key,
    required this.taskId,
    required this.taskType,
    required this.taskDescription,
    required this.coinsReward,
    required this.onValidationComplete,
    this.userToken,
  }) : super(key: key);

  @override
  State<InstagramTaskValidationWidget> createState() => _InstagramTaskValidationWidgetState();
}

class _InstagramTaskValidationWidgetState extends State<InstagramTaskValidationWidget>
    with SingleTickerProviderStateMixin {
  final TextEditingController _urlController = TextEditingController();
  final InstagramService _instagramService = InstagramService();
  
  bool _isValidating = false;
  bool _isCompleted = false;
  String? _errorMessage;
  InstagramTaskValidation? _validationResult;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<Color?> _colorAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    _colorAnimation = ColorTween(
      begin: Colors.blue,
      end: Colors.green,
    ).animate(_animationController);
  }

  @override
  void dispose() {
    _urlController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  IconData get _taskIcon {
    switch (widget.taskType.toLowerCase()) {
      case 'like':
        return Icons.favorite;
      case 'follow':
        return Icons.person_add;
      case 'comment':
        return Icons.comment;
      case 'share':
        return Icons.share;
      case 'save':
        return Icons.bookmark;
      default:
        return Icons.task_alt;
    }
  }

  Color get _taskColor {
    switch (widget.taskType.toLowerCase()) {
      case 'like':
        return Colors.red;
      case 'follow':
        return Colors.blue;
      case 'comment':
        return Colors.green;
      case 'share':
        return Colors.orange;
      case 'save':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  String get _taskAction {
    switch (widget.taskType.toLowerCase()) {
      case 'like':
        return 'Like the post';
      case 'follow':
        return 'Follow the account';
      case 'comment':
        return 'Comment on the post';
      case 'share':
        return 'Share the post';
      case 'save':
        return 'Save the post';
      default:
        return 'Complete the task';
    }
  }

  bool _isValidUrl(String url) {
    final uri = Uri.tryParse(url);
    return uri != null && 
           uri.hasScheme && 
           (uri.host.contains('instagram.com') || uri.host.contains('instagr.am'));
  }

  Future<void> _validateTask() async {
    setState(() {
      _isValidating = true;
      _errorMessage = null;
    });

    try {
      final result = await _instagramService.validateTask(
        widget.userToken ?? '',
        widget.taskId,
        '', // postUrl not needed for backend
        taskType: widget.taskType,
      );

      setState(() {
        _validationResult = result;
        _isCompleted = result.isValid;
      });

      if (result.isValid) {
        _animationController.forward();
        widget.onValidationComplete(true, result.coinsEarned);
      } else {
        setState(() {
          _errorMessage = result.errorReason ?? 'Task validation failed';
        });
        widget.onValidationComplete(false, 0);
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Validation failed: \\${e.toString()}';
      });
      widget.onValidationComplete(false, 0);
    } finally {
      setState(() {
        _isValidating = false;
      });
    }
  }

  void _copyTaskUrl() {
    // This would typically copy a sample URL or instruction
    Clipboard.setData(const ClipboardData(text: 'https://instagram.com/p/'));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('URL format copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: _isCompleted
              ? LinearGradient(
                  colors: [Colors.green[50]!, Colors.green[100]!],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                )
              : null,
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  AnimatedBuilder(
                    animation: _animationController,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _isCompleted ? _scaleAnimation.value : 1.0,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: _isCompleted 
                                ? _colorAnimation.value?.withValues(alpha: 0.2)
                                : _taskColor.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            _isCompleted ? Icons.check_circle : _taskIcon,
                            color: _isCompleted 
                                ? _colorAnimation.value
                                : _taskColor,
                            size: 28,
                          ),
                        ),
                      );
                    },
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.taskDescription,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Text(
                              _taskAction,
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                            const Spacer(),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.amber[100],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.diamond,
                                    size: 16,
                                    color: Colors.amber[700],
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    '${widget.coinsReward}',
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.amber[700],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              if (!_isCompleted) ...[
                const SizedBox(height: 20),
                
                if (_errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red[200]!),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.error_outline,
                          color: Colors.red[600],
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: TextStyle(
                              color: Colors.red[700],
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                
                const SizedBox(height: 16),
                
                // Validate Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isValidating ? null : _validateTask,
                    child: _isValidating
                        ? Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    Colors.white,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              const Text('Validating...'),
                            ],
                          )
                        : Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(_taskIcon),
                              const SizedBox(width: 8),
                              const Text('Validate Task'),
                            ],
                          ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _taskColor,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ] else ...[
                const SizedBox(height: 20),
                
                // Success Message
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.green[50],
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.green[200]!),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.check_circle,
                        color: Colors.green[600],
                        size: 24,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Task Completed Successfully!',
                              style: TextStyle(
                                color: Colors.green[700],
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            if (_validationResult != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                'Earned ${_validationResult!.coinsEarned} coins',
                                style: TextStyle(
                                  color: Colors.green[600],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// Task List Widget for multiple tasks
class InstagramTaskListWidget extends StatefulWidget {
  final List<Map<String, dynamic>> tasks;
  final String? userToken;
  final Function(int completedTasks, int totalCoins) onTasksComplete;

  const InstagramTaskListWidget({
    Key? key,
    required this.tasks,
    required this.onTasksComplete,
    this.userToken,
  }) : super(key: key);

  @override
  State<InstagramTaskListWidget> createState() => _InstagramTaskListWidgetState();
}

class _InstagramTaskListWidgetState extends State<InstagramTaskListWidget> {
  int _completedTasks = 0;
  int _totalCoinsEarned = 0;

  void _onTaskComplete(bool success, int coinsEarned) {
    if (success) {
      setState(() {
        _completedTasks++;
        _totalCoinsEarned += coinsEarned;
      });
      widget.onTasksComplete(_completedTasks, _totalCoinsEarned);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Progress Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue[200]!),
          ),
          child: Row(
            children: [
              Icon(
                Icons.task_alt,
                color: Colors.blue[600],
                size: 24,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Instagram Tasks Progress',
                      style: TextStyle(
                        color: Colors.blue[700],
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$_completedTasks/${widget.tasks.length} completed • $_totalCoinsEarned coins earned',
                      style: TextStyle(
                        color: Colors.blue[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              CircularProgressIndicator(
                value: _completedTasks / widget.tasks.length,
                backgroundColor: Colors.blue[100],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[600]!),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Task List
        ...widget.tasks.asMap().entries.map((entry) {
          final index = entry.key;
          final task = entry.value;
          
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: InstagramTaskValidationWidget(
              taskId: task['id'] ?? index,
              taskType: task['type'] ?? 'unknown',
              taskDescription: task['description'] ?? 'Complete task',
              coinsReward: task['coins_reward'] ?? 0,
              userToken: widget.userToken,
              onValidationComplete: _onTaskComplete,
            ),
          );
        }).toList(),
      ],
    );
  }
}
