import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/instagram_provider.dart';
import '../utils/safe_animation_mixin.dart';

class InstagramChallengeDialog extends ConsumerStatefulWidget {
  final String challengeId;
  final String challengeType;
  final String message;
  final Map<String, dynamic> challengeData;
  final String? userToken;
  
  // For login flow
  final String? username;
  final String? password;
  final Map<String, dynamic>? challengeInfo;

  const InstagramChallengeDialog({
    super.key,
    required this.challengeId,
    required this.challengeType,
    required this.message,
    required this.challengeData,
    this.userToken,
    this.username,
    this.password,
    this.challengeInfo,
  });
  
  // Constructor for login flow
  const InstagramChallengeDialog.forLogin({
    super.key,
    required this.username,
    required this.password,
    required this.challengeInfo,
  }) : challengeId = '',
       challengeType = 'login_challenge',
       message = '',
       challengeData = const {},
       userToken = null;

  @override
  ConsumerState<InstagramChallengeDialog> createState() =>
      _InstagramChallengeDialogState();
}

class _InstagramChallengeDialogState
    extends ConsumerState<InstagramChallengeDialog>
    with SafeTickerProviderMixin {
  final TextEditingController _codeController = TextEditingController();
  bool _isSubmitting = false;
  bool _isResending = false;
  String? _errorMessage;
  int _attemptsRemaining = 3;
  int _timeRemaining = 300; // 5 minutes
  late AnimationController _timerController;
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _timerController = createSafeAnimationController(
      duration: const Duration(seconds: 300),
      vsync: this,
    );
    _pulseController = createSafeAnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _startTimer();
    _pulseController.repeat();
  }

  void _startTimer() {
    _timerController.addListener(() {
      setState(() {
        _timeRemaining = (300 * (1 - _timerController.value)).round();
      });
      if (_timeRemaining <= 0) {
        _timerController.stop();
        if (mounted && Navigator.of(context).canPop()) {
          Navigator.of(context).pop({'success': false, 'error': 'Zaman aşımı'});
        }
      }
    });
    _timerController.forward();
  }

  String get _formatTime {
    final minutes = _timeRemaining ~/ 60;
    final seconds = _timeRemaining % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  String get _challengeTypeDisplayName {
    switch (_actualChallengeType.toLowerCase()) {
      case 'sms':
        return 'SMS';
      case 'email':
        return 'E-posta';
      case 'phone':
        return 'Telefon';
      case 'totp':
      case '2fa':
        return '2FA';
      case 'login_challenge':
        return 'Instagram Giriş';
      default:
        return 'Doğrulama';
    }
  }

  IconData get _challengeIcon {
    switch (_actualChallengeType.toLowerCase()) {
      case 'sms':
      case 'phone':
        return Icons.sms;
      case 'email':
        return Icons.email;
      case 'totp':
      case '2fa':
        return Icons.security;
      case 'login_challenge':
        return Icons.login;
      default:
        return Icons.verified_user;
    }
  }

  String get _challengeMessage {
    // For login challenges, use the message from challengeInfo
    if (widget.challengeInfo != null && widget.challengeInfo!.isNotEmpty) {
      final message = widget.challengeInfo!['message'] as String?;
      final contactPoint = widget.challengeInfo!['contact_point'] as String?;
      final challengeType = widget.challengeInfo!['challenge_type'] as String?;
      
      if (message != null && message.isNotEmpty) {
        return message;
      } else if (contactPoint != null && contactPoint.isNotEmpty) {
        switch (challengeType) {
          case 'email':
            return 'E-posta adresiniz ($contactPoint) adresine gönderilen 6 haneli doğrulama kodunu girin.';
          case 'sms':
            return 'Telefon numaranız ($contactPoint) adresine gönderilen 6 haneli doğrulama kodunu girin.';
          default:
            return 'Gönderilen 6 haneli doğrulama kodunu girin.';
        }
      }
    }
    
    // Fallback to widget message or default
    return widget.message.isNotEmpty 
        ? widget.message 
        : 'Instagram doğrulama kodunu girin';
  }

  String get _actualChallengeType {
    if (widget.challengeInfo != null && widget.challengeInfo!.isNotEmpty) {
      return widget.challengeInfo!['challenge_type'] as String? ?? widget.challengeType;
    }
    return widget.challengeType;
  }

  Future<void> _submitCode() async {
    if (_codeController.text.length != 6) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Lütfen 6 haneli kodu girin';
        });
      }
      return;
    }

    if (mounted) {
      setState(() {
        _isSubmitting = true;
        _errorMessage = null;
      });
    }

    try {
      final instagramService = ref.read(instagramServiceProvider);
      bool success = false;
      
      // Check if this is a login challenge or regular challenge
      if (widget.username != null && widget.password != null) {
        // Login challenge
        final result = await instagramService.submitInstagramChallenge(
          widget.username!,
          widget.password!,
          _codeController.text,
        );
        
        // Null safety check for result
        if (result == null) {
          if (mounted) {
            setState(() {
              _errorMessage = 'Sunucudan yanıt alınamadı';
            });
          }
          return;
        }
        
        success = result['success'] ?? false;
        
        if (success) {
          // Validate response structure for null safety
          final accessToken = result['access_token'];
          final userData = result['user_data'];
          
          if (accessToken != null && userData != null) {
            // Login successful with valid data, return user data
            if (mounted && Navigator.of(context).canPop()) {
              Navigator.of(context).pop(result);
            }
            return;
          } else {
            // Success but missing required data
            if (mounted) {
              setState(() {
                _errorMessage = 'Giriş başarılı ancak kullanıcı bilgileri eksik';
              });
            }
            return;
          }
        } else {
          // Handle login challenge error with enhanced error messages
          final error = result['error'] ?? 'Doğrulama başarısız';
          final attemptsRemaining = result['attempts_remaining'];
          
          if (mounted) {
            setState(() {
              _errorMessage = error;
              if (attemptsRemaining != null && attemptsRemaining is int) {
                _attemptsRemaining = attemptsRemaining;
              } else {
                _attemptsRemaining--;
              }
            });
          }
          
          if (_attemptsRemaining <= 0) {
            if (mounted && Navigator.of(context).canPop()) {
              Navigator.of(context).pop({'success': false, 'error': 'Çok fazla hatalı deneme'});
            }
          }
          return;
        }
      } else {
        // Regular challenge
        success = await instagramService.resolveChallenge(
          widget.userToken ?? '',
          widget.challengeId,
          _codeController.text,
        );
        
        if (success) {
          if (mounted && Navigator.of(context).canPop()) {
            Navigator.of(context).pop({'success': true, 'verified': true});
          }
          return;
        }
      }

      if (!success) {
        if (mounted) {
          setState(() {
            _attemptsRemaining--;
            _errorMessage = 'Geçersiz kod. Kalan deneme: $_attemptsRemaining';
          });
        }
        if (_attemptsRemaining <= 0) {
          if (mounted && Navigator.of(context).canPop()) {
            Navigator.of(context).pop({'success': false, 'error': 'Çok fazla hatalı deneme'});
          }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Doğrulama hatası: ${e.toString()}';
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  Future<void> _resendCode() async {
    if (mounted) {
      setState(() {
        _isResending = true;
        _errorMessage = null;
      });
    }

    try {
      final instagramService = ref.read(instagramServiceProvider);
      await instagramService.resendChallenge(widget.userToken ?? '', widget.challengeId);
      if (mounted) {
        setState(() {
          _timeRemaining = 300;
        });
      }
      _timerController.reset();
      _timerController.forward();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Yeni kod gönderildi'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Kod tekrar gönderilemedi: ${e.toString()}';
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isResending = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _codeController.dispose();
    // Animation controllers are automatically disposed by SafeTickerProviderMixin
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Container(
        padding: const EdgeInsets.all(24),
        constraints: const BoxConstraints(maxWidth: 400),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header with icon and timer
            Row(
              children: [
                AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: 1.0 + (_pulseController.value * 0.1),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.blue.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(
                          _challengeIcon,
                          color: Colors.blue,
                          size: 24,
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$_challengeTypeDisplayName Doğrulaması',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Kalan süre: $_formatTime',
                        style: TextStyle(
                          color: _timeRemaining < 60 ? Colors.red : Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Progress indicator
            LinearProgressIndicator(
              value: _timeRemaining / 300,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(
                _timeRemaining < 60 ? Colors.red : Colors.blue,
              ),
            ),
            
            const SizedBox(height: 20),
            
            // Message
            Text(
              _challengeMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14),
            ),
            
            const SizedBox(height: 20),
            
            // Code input
            TextField(
              controller: _codeController,
              textAlign: TextAlign.center,
              keyboardType: TextInputType.number,
              maxLength: 6,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 8,
              ),
              decoration: InputDecoration(
                hintText: '000000',
                counterText: '',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Colors.blue, width: 2),
                ),
              ),
              onChanged: (value) {
                setState(() {
                  _errorMessage = null;
                });
                
                // Auto-submit when 6 digits entered
                if (value.length == 6) {
                  _submitCode();
                }
              },
            ),
            
            const SizedBox(height: 16),
            
            // Error message
            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            
            const SizedBox(height: 20),
            
            // Attempts remaining
            if (_attemptsRemaining < 3)
              Text(
                'Kalan deneme hakkı: $_attemptsRemaining',
                style: TextStyle(
                  color: _attemptsRemaining == 1 ? Colors.red : Colors.orange,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            
            const SizedBox(height: 20),
            
            // Action buttons
            Row(
              children: [
                // Hide resend button for login challenges since they don't support resending
                if (widget.username == null && widget.password == null)
                  Expanded(
                    child: TextButton(
                      onPressed: _isResending
                          ? null
                          : _resendCode,
                      child: _isResending
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Kodu Tekrar Gönder'),
                    ),
                  ),
                if (widget.username == null && widget.password == null)
                  const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isSubmitting || _codeController.text.length != 6
                        ? null
                        : _submitCode,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: _isSubmitting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Text('Doğrula'),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Cancel button
            TextButton(
              onPressed: () {
                if (Navigator.of(context).canPop()) {
                  Navigator.of(context).pop({'success': false, 'cancelled': true});
                }
              },
              child: const Text(
                'İptal',
                style: TextStyle(color: Colors.grey),
              ),
            ),
          ],
        ),
      ),
    );
  }
}