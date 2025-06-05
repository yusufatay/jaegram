import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/instagram_service.dart';
// import '../utils/instagram_dialog_utils.dart';

class InstagramErrorHandler extends StatefulWidget {
  final String errorType;
  final String errorMessage;
  final Map<String, dynamic>? errorDetails;
  final String? userToken;
  final Function(bool resolved) onErrorHandled;

  const InstagramErrorHandler({
    Key? key,
    required this.errorType,
    required this.errorMessage,
    this.errorDetails,
    this.userToken,
    required this.onErrorHandled,
  }) : super(key: key);

  @override
  State<InstagramErrorHandler> createState() => _InstagramErrorHandlerState();
}

class _InstagramErrorHandlerState extends State<InstagramErrorHandler>
    with SingleTickerProviderStateMixin {
  final InstagramService _instagramService = InstagramService();
  
  bool _isResolving = false;
  bool _showDetails = false;
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  IconData get _errorIcon {
    switch (widget.errorType.toLowerCase()) {
      case 'challenge_required':
        return Icons.security;
      case 'rate_limit':
        return Icons.speed;
      case 'authentication':
        return Icons.lock;
      case 'network':
        return Icons.wifi_off;
      case 'account_locked':
        return Icons.lock_person;
      case 'suspicious_activity':
        return Icons.warning;
      case 'invalid_credentials':
        return Icons.key_off;
      case 'two_factor':
        return Icons.phonelink_lock;
      default:
        return Icons.error;
    }
  }

  Color get _errorColor {
    switch (widget.errorType.toLowerCase()) {
      case 'challenge_required':
        return Colors.orange;
      case 'rate_limit':
        return Colors.blue;
      case 'authentication':
        return Colors.red;
      case 'network':
        return Colors.grey;
      case 'account_locked':
        return Colors.red[800]!;
      case 'suspicious_activity':
        return Colors.amber[800]!;
      case 'invalid_credentials':
        return Colors.red;
      case 'two_factor':
        return Colors.purple;
      default:
        return Colors.red;
    }
  }

  String get _errorTitle {
    switch (widget.errorType.toLowerCase()) {
      case 'challenge_required':
        return 'Security Challenge Required';
      case 'rate_limit':
        return 'Rate Limit Exceeded';
      case 'authentication':
        return 'Authentication Error';
      case 'network':
        return 'Network Error';
      case 'account_locked':
        return 'Account Locked';
      case 'suspicious_activity':
        return 'Suspicious Activity Detected';
      case 'invalid_credentials':
        return 'Invalid Credentials';
      case 'two_factor':
        return 'Two-Factor Authentication Required';
      default:
        return 'Instagram Error';
    }
  }

  String get _errorDescription {
    switch (widget.errorType.toLowerCase()) {
      case 'challenge_required':
        return 'Instagram requires additional verification to continue. Please complete the security challenge.';
      case 'rate_limit':
        return 'Too many requests have been made. Please wait before trying again.';
      case 'authentication':
        return 'Unable to authenticate with Instagram. Please check your credentials.';
      case 'network':
        return 'Unable to connect to Instagram. Please check your internet connection.';
      case 'account_locked':
        return 'Your Instagram account has been temporarily locked. Please try again later.';
      case 'suspicious_activity':
        return 'Instagram has detected suspicious activity. Additional verification may be required.';
      case 'invalid_credentials':
        return 'The username or password is incorrect. Please verify your credentials.';
      case 'two_factor':
        return 'Two-factor authentication is required to access your account.';
      default:
        return widget.errorMessage;
    }
  }

  List<String> get _resolutionSteps {
    switch (widget.errorType.toLowerCase()) {
      case 'challenge_required':
        return [
          'Complete the security challenge',
          'Follow the verification instructions',
          'Enter the verification code when prompted',
        ];
      case 'rate_limit':
        return [
          'Wait for the rate limit to reset',
          'Reduce the frequency of requests',
          'Try again in a few minutes',
        ];
      case 'authentication':
        return [
          'Verify your username and password',
          'Check if your account is active',
          'Reset your password if necessary',
        ];
      case 'network':
        return [
          'Check your internet connection',
          'Try switching to a different network',
          'Restart the app if the problem persists',
        ];
      case 'account_locked':
        return [
          'Wait for the account to be unlocked',
          'Contact Instagram support if needed',
          'Follow Instagram\'s security guidelines',
        ];
      case 'suspicious_activity':
        return [
          'Verify your identity with Instagram',
          'Complete any required challenges',
          'Review your account security settings',
        ];
      case 'invalid_credentials':
        return [
          'Double-check your username',
          'Verify your password is correct',
          'Reset your password if forgotten',
        ];
      case 'two_factor':
        return [
          'Open your authenticator app',
          'Enter the 6-digit verification code',
          'Ensure your phone has signal',
        ];
      default:
        return [
          'Review the error message',
          'Try refreshing the connection',
          'Contact support if the issue persists',
        ];
    }
  }

  bool get _canAutoResolve {
    return ['challenge_required', 'rate_limit', 'network'].contains(
      widget.errorType.toLowerCase(),
    );
  }

  Future<void> _handleChallenge() async {
    if (widget.errorDetails?['challenge_id'] != null) {
      // Temporary implementation - will be replaced with proper dialog
      final result = await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Instagram Challenge'),
          content: Text(widget.errorDetails!['challenge_message'] ?? 'Complete the challenge'),
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
        widget.onErrorHandled(true);
      }
    }
  }

  Future<void> _retryConnection() async {
    setState(() {
      _isResolving = true;
    });

    try {
      final success = await _instagramService.testConnection(widget.userToken ?? '');
      widget.onErrorHandled(success);
    } catch (e) {
      // Handle retry failure
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Retry failed: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isResolving = false;
      });
    }
  }

  Future<void> _resolveError() async {
    switch (widget.errorType.toLowerCase()) {
      case 'challenge_required':
        await _handleChallenge();
        break;
      case 'network':
      case 'rate_limit':
        await _retryConnection();
        break;
      default:
        // Show resolution instructions
        _showResolutionDialog();
        break;
    }
  }

  void _showResolutionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('How to Resolve: $_errorTitle'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_errorDescription),
            const SizedBox(height: 16),
            const Text(
              'Resolution Steps:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ..._resolutionSteps.asMap().entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('${entry.key + 1}. '),
                    Expanded(child: Text(entry.value)),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }

  void _copyErrorDetails() {
    final details = {
      'error_type': widget.errorType,
      'error_message': widget.errorMessage,
      'timestamp': DateTime.now().toIso8601String(),
      if (widget.errorDetails != null) ...widget.errorDetails!,
    };
    
    Clipboard.setData(ClipboardData(text: details.toString()));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Error details copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.3),
        end: Offset.zero,
      ).animate(_animation),
      child: FadeTransition(
        opacity: _animation,
        child: Card(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _errorColor.withValues(alpha: 0.3),
                width: 2,
              ),
            ),
            child: Column(
              children: [
                // Header
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: _errorColor.withValues(alpha: 0.1),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(14),
                      topRight: Radius.circular(14),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        _errorIcon,
                        size: 32,
                        color: _errorColor,
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _errorTitle,
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: _errorColor,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _errorDescription,
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: _copyErrorDetails,
                        icon: const Icon(Icons.copy),
                        tooltip: 'Copy error details',
                      ),
                    ],
                  ),
                ),
                
                // Content
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      // Error Message
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
                                widget.errorMessage,
                                style: TextStyle(
                                  color: Colors.red[700],
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      // Details Toggle
                      if (widget.errorDetails != null) ...[
                        const SizedBox(height: 12),
                        InkWell(
                          onTap: () {
                            setState(() {
                              _showDetails = !_showDetails;
                            });
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.info_outline, size: 16),
                                const SizedBox(width: 4),
                                const Text(
                                  'Show Details',
                                  style: TextStyle(fontSize: 12),
                                ),
                                const SizedBox(width: 4),
                                Icon(
                                  _showDetails
                                      ? Icons.keyboard_arrow_up
                                      : Icons.keyboard_arrow_down,
                                  size: 16,
                                ),
                              ],
                            ),
                          ),
                        ),
                        
                        if (_showDetails) ...[
                          const SizedBox(height: 12),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.grey[50],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.grey[300]!),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: widget.errorDetails!.entries.map((entry) {
                                return Padding(
                                  padding: const EdgeInsets.only(bottom: 4),
                                  child: Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        '${entry.key}:',
                                        style: const TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          entry.value.toString(),
                                          style: const TextStyle(fontSize: 12),
                                        ),
                                      ),
                                    ],
                                  ),
                                );
                              }).toList(),
                            ),
                          ),
                        ],
                      ],
                      
                      const SizedBox(height: 16),
                      
                      // Action Buttons
                      Row(
                        children: [
                          if (_canAutoResolve) ...[
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _isResolving ? null : _resolveError,
                                child: _isResolving
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          valueColor: AlwaysStoppedAnimation<Color>(
                                            Colors.white,
                                          ),
                                        ),
                                      )
                                    : Text(
                                        widget.errorType.toLowerCase() == 'challenge_required'
                                            ? 'Complete Challenge'
                                            : 'Retry',
                                      ),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: _errorColor,
                                  foregroundColor: Colors.white,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                          ],
                          Expanded(
                            child: OutlinedButton(
                              onPressed: _showResolutionDialog,
                              child: const Text('Show Help'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: _errorColor,
                                side: BorderSide(color: _errorColor),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
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

// Error Handler Manager for multiple errors
class InstagramErrorManager extends StatefulWidget {
  final List<Map<String, dynamic>> errors;
  final String? userToken;
  final Function(int resolvedErrors) onErrorsResolved;

  const InstagramErrorManager({
    Key? key,
    required this.errors,
    required this.onErrorsResolved,
    this.userToken,
  }) : super(key: key);

  @override
  State<InstagramErrorManager> createState() => _InstagramErrorManagerState();
}

class _InstagramErrorManagerState extends State<InstagramErrorManager> {
  int _resolvedErrors = 0;

  void _onErrorResolved(bool resolved) {
    if (resolved) {
      setState(() {
        _resolvedErrors++;
      });
      widget.onErrorsResolved(_resolvedErrors);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.errors.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.red[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.red[200]!),
          ),
          child: Row(
            children: [
              Icon(
                Icons.error_outline,
                color: Colors.red[600],
                size: 24,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Instagram Issues Detected',
                      style: TextStyle(
                        color: Colors.red[700],
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${widget.errors.length - _resolvedErrors} issues need attention',
                      style: TextStyle(
                        color: Colors.red[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Error List
        ...widget.errors.asMap().entries.map((entry) {
          final error = entry.value;
          
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: InstagramErrorHandler(
              errorType: error['type'] ?? 'unknown',
              errorMessage: error['message'] ?? 'An error occurred',
              errorDetails: error['details'],
              userToken: widget.userToken,
              onErrorHandled: _onErrorResolved,
            ),
          );
        }).toList(),
      ],
    );
  }
}
