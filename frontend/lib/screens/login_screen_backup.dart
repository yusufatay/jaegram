import 'dart:developer' as developer;
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:instagram_puan_app/models/user.dart';
import 'package:instagram_puan_app/providers/user_provider.dart';
import 'package:instagram_puan_app/services/instagram_service.dart';
import 'package:instagram_puan_app/widgets/instagram_challenge_dialog.dart';
import 'package:instagram_puan_app/utils/admin_route_helper.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> with TickerProviderStateMixin {
  final instagramUsernameController = TextEditingController();
  final instagramPasswordController = TextEditingController();
  
  final InstagramService _instagramService = InstagramService();

  bool _isInstagramLoading = false;
  bool _isManualLoginPolling = false;
  bool _acceptedKvkk = false;
  bool _isPasswordVisible = false;
  late AnimationController _animationController;
  late AnimationController _buttonAnimationController;
  late AnimationController _pulseAnimationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _buttonScaleAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _buttonAnimationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _pulseAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutBack,
    ));
    
    _buttonScaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _buttonAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _pulseAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _animationController.forward();
    _pulseAnimationController.repeat(reverse: true);
  }

  void _onLoginSuccess() {
    final userState = ref.read(userProvider);
    if (userState.value?.isAdminPlatform == true) {
      GoRouter.of(context).go('/admin');
    } else {
      GoRouter.of(context).go('/main/tasks');
    }
  }

  Future<void> _handleInstagramLogin() async {
    final username = instagramUsernameController.text.trim();
    final password = instagramPasswordController.text.trim();

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Instagram kullanıcı adı ve şifre gerekli'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (username.toLowerCase() == 'admin' && password == 'admin') {
      return _handleAdminLogin(username, password);
    }

    setState(() => _isInstagramLoading = true);

    try {
      final response = await _instagramService.loginInstagram(username, password);

      if (response['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Instagram girişi başarılı! ✅'),
            backgroundColor: Colors.green,
          ),
        );

        final accessToken = response['access_token'] as String?;
        if (accessToken == null) throw Exception('Access token bulunamadı');

        try {
          final userData = response['user_data'] as Map<String, dynamic>? ?? {};

          final instagramStats = InstagramProfileStats(
            instagramUserId: response['user_id']?.toString() ?? userData['instagram_user_id']?.toString() ?? '',
            username: response['username']?.toString() ?? userData['instagram_username']?.toString() ?? username,
            fullName: userData['full_name']?.toString() ?? response['full_name']?.toString(),
            profilePicUrl: userData['profile_pic_url']?.toString() ?? response['profile_pic_url']?.toString(),
            isPrivate: (userData['is_private'] as bool?) ?? false,
            isVerified: (userData['is_verified'] as bool?) ?? false,
            biography: userData['biography']?.toString(),
          );

          final user = User(
            id: userData['id']?.toString() ?? response['user_id']?.toString() ?? '0',
            username: userData['username']?.toString() ?? response['username']?.toString() ?? username,
            fullName: userData['full_name']?.toString() ?? response['full_name']?.toString(),
            profilePicUrl: userData['profile_pic_url']?.toString() ?? response['profile_pic_url']?.toString(),
            diamondBalance: (userData['coins'] as num?)?.toInt() ?? 0,
            isAdminPlatform: (userData['is_admin'] as bool?) == true || (response['is_admin_platform'] as bool?) == true,
            instagramStats: instagramStats,
            instagramConnected: true,
            token: accessToken,
          );

          ref.read(userProvider.notifier).setUser(user);
          _onLoginSuccess();
        } catch (e, stackTrace) {
          developer.log('Error updating user state: $e',
              name: 'LoginScreen', error: e, stackTrace: stackTrace);

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Kullanıcı durumu güncellenemedi: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } else if (response['requires_challenge'] == true) {
        final challengeResult = await showDialog<Map<String, dynamic>>(
          context: context,
          barrierDismissible: false,
          builder: (context) => InstagramChallengeDialog.forLogin(
            username: username,
            password: password,
            challengeInfo: response['challenge_info'] ?? {},
          ),
        );

        if (challengeResult != null && challengeResult['success'] == true) {
          final token = challengeResult['access_token'] as String?;
          final userData = challengeResult['user_data'] as Map<String, dynamic>?;

          if (token != null && token.isNotEmpty && userData != null) {
            try {
              final user = User.fromJson({
                'id': userData['id']?.toString() ?? userData['user_id']?.toString() ?? '0',
                'username': userData['username']?.toString() ?? username,
                'full_name': userData['full_name']?.toString(),
                'email': userData['email']?.toString(),
                'profile_pic_url': userData['profile_pic_url']?.toString(),
                'email_verified': userData['email_verified'] as bool? ?? false,
                'two_factor_enabled': userData['two_factor_enabled'] as bool? ?? false,
                'coin_balance': userData['coin_balance'] as int? ?? userData['coins'] as int? ?? 0,
                'completed_tasks': userData['completed_tasks'] as int? ?? 0,
                'active_tasks': userData['active_tasks'] as int? ?? 0,
                'is_admin_platform': userData['is_admin_platform'] as bool? ?? false,
                'instagram_stats': userData['instagram_stats'] ?? {
                  'instagram_user_id': userData['instagram_user_id']?.toString() ?? '0',
                  'username': userData['username']?.toString() ?? username,
                  'full_name': userData['full_name']?.toString(),
                  'profile_pic_url': userData['profile_pic_url']?.toString(),
                  'follower_count': userData['follower_count'] as int?,
                  'following_count': userData['following_count'] as int?,
                  'media_count': userData['media_count'] as int?,
                  'is_private': userData['is_private'] as bool?,
                  'is_verified': userData['is_verified'] as bool?,
                  'biography': userData['biography']?.toString(),
                },
                'last_daily_reward': userData['last_daily_reward']?.toString(),
                'daily_reward_streak': userData['daily_reward_streak'] as int? ?? 0,
                'instagram_connected': userData['instagram_connected'] as bool? ?? true,
                'access_token': token,
                'token': token,
              });

              if (user.username.isNotEmpty) {
                await ref.read(userProvider.notifier).setUserFromChallengeResult(user, token);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Instagram doğrulama başarılı! ✅'),
                    backgroundColor: Colors.green,
                  ),
                );
                _onLoginSuccess();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Kullanıcı bilgileri geçersiz'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            } catch (e) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Kullanıcı verisi işlenirken hata: $e'),
                  backgroundColor: Colors.red,
                ),
              );
            }
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Challenge tamamlandı ama gerekli bilgiler eksik'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        } else if (challengeResult == null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Instagram doğrulama iptal edildi'),
              backgroundColor: Colors.orange,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(challengeResult['error'] ?? 'Instagram doğrulama başarısız'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['error'] ?? 'Instagram giriş başarısız'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Instagram giriş hatası: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _isInstagramLoading = false);
    }
  }

  Future<void> _handleAdminLogin(String username, String password) async {
    setState(() => _isInstagramLoading = true);

    try {
      final response = await _instagramService.loginInstagram(username, password);
      
      if (response['success'] == true) {
        final token = response['access_token'];
        final bool isAdmin = response['is_admin_platform'] == true || 
                            (response['user_data']?['is_admin'] == true);
        
        ref.read(userProvider.notifier).login(username, password);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Admin girişi başarılı! ✅'),
            backgroundColor: Colors.green,
          ),
        );
        AdminRouteHelper.navigateToAdminPanel(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Admin girişi başarısız'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Admin giriş hatası: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _isInstagramLoading = false);
    }
  }
  
  Future<void> _handleManualInstagramLogin() async {
    final username = instagramUsernameController.text.trim();
    setState(() => _isInstagramLoading = true);

    try {
      String tempToken = '';
      try {
        final adminResponse = await _instagramService.loginInstagram('admin', 'admin');
        if (adminResponse['success'] == true) {
          tempToken = adminResponse['access_token'];
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Manuel giriş için sistem erişimi gerekli'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      final response = await _instagramService.openManualInstagramLogin(
        username.isNotEmpty ? username : null,
        tempToken,
      );
      
      if (response['success'] == true) {
        _showManualLoginDialog(tempToken);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['error'] ?? 'Browser açılamadı'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _isInstagramLoading = false);
    }
  }

  void _showManualLoginDialog(String tempToken) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.web, color: Colors.blue),
                SizedBox(width: 8),
                Text('Manuel Instagram Girişi'),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Instagram\'a giriş yapmak için açılan tarayıcı penceresini kullanın:',
                  style: TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 16),
                const Text(
                  '1. Tarayıcıda Instagram\'a giriş yapın\n'
                  '2. İki faktörlü doğrulama varsa tamamlayın\n'
                  '3. Herhangi bir challenge\'ı çözün\n'
                  '4. Ana sayfaya ulaştığınızda "Kontrol Et" tuşuna basın',
                  style: TextStyle(fontSize: 14, height: 1.4),
                ),
                const SizedBox(height: 20),
                if (_isManualLoginPolling)
                  const Row(
                    children: [
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      SizedBox(width: 12),
                      Text('Giriş durumu kontrol ediliyor...'),
                    ],
                  ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: _isManualLoginPolling ? null : () {
                  _instagramService.closeInstagramBrowser(tempToken);
                  Navigator.of(context).pop();
                },
                child: const Text('İptal'),
              ),
              ElevatedButton(
                onPressed: _isManualLoginPolling ? null : () {
                  _checkManualLoginStatus(tempToken, setDialogState);
                },
                child: const Text('Kontrol Et'),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _checkManualLoginStatus(String tempToken, StateSetter setDialogState) async {
    setDialogState(() => _isManualLoginPolling = true);

    try {
      final response = await _instagramService.checkManualLoginStatus(tempToken);
      
      if (response['success'] == true && response['status'] == 'logged_in') {
        final userData = response['user_data'] ?? {};
        final instagramStats = InstagramProfileStats(
          instagramUserId: userData['username'] ?? '',
          username: userData['username'] ?? '',
          fullName: userData['full_name'],
          profilePicUrl: userData['profile_pic_url'],
          mediaCount: userData['posts_count']?.toInt(),
          isPrivate: userData['is_private'] ?? false,
          isVerified: userData['is_verified'] ?? false,
          biography: userData['bio'],
        );
        
        final user = User(
          id: '0',
          username: userData['username'] ?? 'instagram_user',
          fullName: userData['full_name'],
          profilePicUrl: userData['profile_pic_url'],
          diamondBalance: 0,
          isAdminPlatform: false,
          instagramStats: instagramStats,
          instagramConnected: true,
          token: tempToken,
        );
        
        ref.read(userProvider.notifier).setUser(user);
        await _instagramService.closeInstagramBrowser(tempToken);
        if (mounted) Navigator.of(context).pop();
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Instagram girişi başarılı! ✅'),
            backgroundColor: Colors.green,
          ),
        );
        _onLoginSuccess();
      } else {
        String message = response['message'] ?? 'Giriş henüz tamamlanmadı';
        if (response['status'] == 'challenge_required') {
          message = 'Lütfen challenge\'ı tamamlayın ve tekrar deneyin';
        } else if (response['status'] == 'login_incomplete') {
          message = 'Lütfen Instagram\'a giriş yapın ve tekrar deneyin';
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Kontrol hatası: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setDialogState(() => _isManualLoginPolling = false);
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    _buttonAnimationController.dispose();
    _pulseAnimationController.dispose();
    instagramUsernameController.dispose();
    instagramPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isTablet = size.width > 600;
    return Scaffold(
      body: Stack(
        children: [
          // Background with enhanced gradient
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF667eea),
                  Color(0xFF764ba2),
                  Color(0xFF8134AF),
                  Color(0xFFDD2A7B),
                ],
                stops: [0.0, 0.3, 0.7, 1.0],
              ),
            ),
          ),
          // Animated floating particles
          ...List.generate(20, (index) => 
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0.0, end: 1.0),
              duration: Duration(milliseconds: 2000 + (index * 100)),
              builder: (context, value, child) {
                return Positioned(
                  left: (size.width * (index * 0.05)) + (50 * value),
                  top: (size.height * (index * 0.05)) + (30 * value),
                  child: Opacity(
                    opacity: 0.1 + (0.1 * value),
                    child: Container(
                      width: 4 + (index % 3),
                      height: 4 + (index % 3),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.6),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.white.withOpacity(0.3),
                            blurRadius: 10,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          // Main content
          SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Container(
              width: double.infinity,
              constraints: BoxConstraints(
                minHeight: size.height - MediaQuery.of(context).padding.top,
              ),
              child: Column(
                children: [
                  const SizedBox(height: 40),
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: SlideTransition(
                      position: _slideAnimation,
                      child: Hero(
                        tag: 'logo',
                        child: Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                Colors.white.withOpacity(0.2),
                                Colors.white.withOpacity(0.1),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(25),
                            border: Border.all(
                              color: Colors.white.withOpacity(0.3),
                              width: 1,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 20,
                                offset: const Offset(0, 10),
                              ),
                            ],
                          ),
                          child: Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.white.withOpacity(0.2),
                                  Colors.white.withOpacity(0.1),
                                ],
                              ),
                              borderRadius: BorderRadius.circular(25),
                              border: Border.all(
                                color: Colors.white.withOpacity(0.3),
                                width: 1,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 20,
                                  offset: const Offset(0, 10),
                                ),
                              ],
                            ),
                            child: Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: [
                                    const Color(0xFFDD2A7B),
                                    const Color(0xFF8134AF),
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(20),
                                boxShadow: [
                                  BoxShadow(
                                    color: const Color(0xFFDD2A7B).withOpacity(0.3),
                                    blurRadius: 15,
                                    offset: const Offset(0, 5),
                                  ),
                                ],
                              ),
                              child: const Icon(
                                Icons.camera_alt_rounded,
                                color: Colors.white,
                                size: 40,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 40),
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: Column(
                      children: [
                        ShaderMask(
                          shaderCallback: (bounds) => const LinearGradient(
                            colors: [Colors.white, Color(0xFFF0F0F0)],
                          ).createShader(bounds),
                          child: const Text(
                            'Instagram',
                            style: TextStyle(
                              fontSize: 48,
                              fontWeight: FontWeight.w900,
                              color: Colors.white,
                              letterSpacing: 3.0,
                              height: 1.1,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                const Color(0xFFDD2A7B).withOpacity(0.8),
                                const Color(0xFF8134AF).withOpacity(0.8),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFFDD2A7B).withOpacity(0.3),
                                blurRadius: 10,
                                offset: const Offset(0, 5),
                              ),
                            ],
                          ),
                          child: const Text(
                            'PUAN',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              color: Colors.white,
                              letterSpacing: 4.0,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.white.withOpacity(0.15),
                            Colors.white.withOpacity(0.05),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(30),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.3),
                          width: 1,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.stars_rounded,
                            color: Colors.white.withOpacity(0.9),
                            size: 20,
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'Instagram hesabınızla güvenli giriş yapın',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 0.5,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(width: 12),
                          Icon(
                            Icons.stars_rounded,
                            color: Colors.white.withOpacity(0.9),
                            size: 20,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 60),
                  SlideTransition(
                    position: _slideAnimation,
                    child: Container(
                      margin: EdgeInsets.symmetric(
                        horizontal: isTablet ? size.width * 0.15 : 24,
                      ),
                      padding: const EdgeInsets.all(40),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.95),
                        borderRadius: BorderRadius.circular(32),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 40,
                            offset: const Offset(0, 20),
                          ),
                          BoxShadow(
                            color: const Color(0xFF8134AF).withOpacity(0.1),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                        border: Border.all(
                          color: Colors.white.withOpacity(0.2),
                          width: 1,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Container(
                            padding: const EdgeInsets.only(bottom: 32),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.lock_outline_rounded, color: Colors.deepPurple, size: 32),
                                const SizedBox(width: 12),
                                Text(
                                  'Giriş Yap',
                                  style: TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.deepPurple[700],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.white,
                                  Colors.blue[25]?.withOpacity(0.8) ?? Colors.blue[50]!.withOpacity(0.8),
                                ],
                                end: Alignment.bottomRight,
                              ),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: Colors.blue[200]!.withOpacity(0.8),
                                width: 2,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.blue.withOpacity(0.1),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                                BoxShadow(
                                  color: Colors.white.withOpacity(0.9),
                                  blurRadius: 1,
                                  offset: const Offset(0, 1),
                                ),
                              ],
                            ),
                            child: TextField(
                              controller: instagramUsernameController,
                              decoration: InputDecoration(
                                labelText: 'Instagram Kullanıcı Adı',
                                hintText: 'Kullanıcı adınızı girin',
                                prefixIcon: Container(
                                  margin: const EdgeInsets.all(12),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        Colors.blue[400]!,
                                        Colors.blue[600]!,
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: const Icon(
                                    Icons.person_outline_rounded,
                                    color: Colors.white,
                                    size: 20,
                                  ),
                                ),
                                border: InputBorder.none,
                                contentPadding: const EdgeInsets.symmetric(
                                  vertical: 22,
                                  horizontal: 16,
                                ),
                                labelStyle: TextStyle(
                                  fontSize: 15,
                                  color: Colors.blue[700],
                                  fontWeight: FontWeight.w600,
                                ),
                                hintStyle: TextStyle(
                                  fontWeight: FontWeight.w400,
                                  color: Colors.grey[500],
                                ),
                              ),
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF2C2C2C),
                                letterSpacing: 0.3,
                              ),
                              textInputAction: TextInputAction.next,
                            ),
                          ),
                          const SizedBox(height: 24),
                          Container(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.white,
                                  Colors.purple[25]?.withOpacity(0.8) ?? Colors.purple[50]!.withOpacity(0.8),
                                ],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: Colors.purple[200]!.withOpacity(0.8),
                                width: 2,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.purple.withOpacity(0.1),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                                BoxShadow(
                                  color: Colors.white.withOpacity(0.9),
                                  blurRadius: 1,
                                  offset: const Offset(0, 1),
                                ),
                              ],
                            ),
                            child: TextField(
                              controller: instagramPasswordController,
                              decoration: InputDecoration(
                                labelText: 'Instagram Şifre',
                                hintText: 'Şifrenizi girin',
                                prefixIcon: Container(
                                  margin: const EdgeInsets.all(12),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        Colors.purple[400]!,
                                        Colors.purple[600]!,
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: const Icon(
                                    Icons.lock_outline_rounded,
                                    color: Colors.white,
                                    size: 20,
                                  ),
                                ),
                                suffixIcon: Container(
                                  margin: const EdgeInsets.all(12),
                                  child: IconButton(
                                    icon: Icon(
                                      _isPasswordVisible 
                                        ? Icons.visibility_off_outlined 
                                        : Icons.visibility_outlined,
                                      color: Colors.purple[600],
                                    ),
                                    onPressed: () {
                                      setState(() {
                                        _isPasswordVisible = !_isPasswordVisible;
                                      });
                                    },
                                  ),
                                ),
                                border: InputBorder.none,
                                contentPadding: const EdgeInsets.symmetric(
                                  vertical: 22,
                                  horizontal: 16,
                                ),
                                labelStyle: TextStyle(
                                  fontSize: 15,
                                  color: Colors.purple[700],
                                  fontWeight: FontWeight.w600,
                                ),
                                hintStyle: TextStyle(
                                  fontWeight: FontWeight.w400,
                                  color: Colors.grey[500],
                                ),
                              ),
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF2C2C2C),
                                letterSpacing: 0.3,
                              ),
                              obscureText: !_isPasswordVisible,
                              textInputAction: TextInputAction.done,
                              onSubmitted: (_) => _handleInstagramLogin(),
                            ),
                          ),
                          const SizedBox(height: 32),
                          Container(
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.blue[25]?.withOpacity(0.6) ?? Colors.blue[50]!.withOpacity(0.6),
                                  Colors.blue[50]!.withOpacity(0.3),
                                ],
                              ),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: Colors.blue[200]!.withOpacity(0.7),
                                width: 2,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.blue.withOpacity(0.08),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: Row(
                              children: [
                                Container(
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        Colors.blue[400]!,
                                        Colors.blue[600]!,
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(8),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.blue.withOpacity(0.3),
                                        blurRadius: 5,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  child: Transform.scale(
                                    scale: 1.2,
                                    child: Checkbox(
                                      value: _acceptedKvkk,
                                      onChanged: (val) {
                                        setState(() {
                                          _acceptedKvkk = val ?? false;
                                        });
                                      },
                                      checkColor: Colors.white,
                                      fillColor: MaterialStateProperty.all(Colors.transparent),
                                      side: BorderSide.none,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: GestureDetector(
                                    onTap: () => _showKvkkDialog(context),
                                    child: Text(
                                      'KVKK & Gizlilik Politikasını okudum, kabul ediyorum',
                                      style: TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.blue[800],
                                        decoration: TextDecoration.underline,
                                        decorationColor: Colors.blue[600],
                                        decorationThickness: 1.5,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 32),
                          AnimatedBuilder(
                            animation: _pulseAnimation,
                            builder: (context, child) {
                              return Transform.scale(
                                scale: _acceptedKvkk ? _pulseAnimation.value : 1.0,
                                child: ScaleTransition(
                                  scale: _buttonScaleAnimation,
                                  child: Container(
                                    height: 64,
                                    decoration: BoxDecoration(
                                      gradient: LinearGradient(
                                        colors: _acceptedKvkk
                                            ? [
                                                const Color(0xFF667eea),
                                                const Color(0xFF764ba2),
                                                const Color(0xFF8134AF),
                                              ]
                                            : [
                                                Colors.grey[300]!,
                                                Colors.grey[400]!,
                                              ],
                                      ),
                                      borderRadius: BorderRadius.circular(22),
                                      boxShadow: _acceptedKvkk
                                          ? [
                                              BoxShadow(
                                                color: const Color(0xFF8134AF).withOpacity(0.3),
                                                blurRadius: 15,
                                                offset: const Offset(0, 8),
                                              ),
                                              BoxShadow(
                                                color: Colors.white.withOpacity(0.1),
                                                blurRadius: 1,
                                                offset: const Offset(0, 1),
                                              ),
                                            ]
                                          : [
                                              BoxShadow(
                                                color: Colors.grey.withOpacity(0.2),
                                                blurRadius: 5,
                                                offset: const Offset(0, 2),
                                              ),
                                            ],
                                    ),
                                    child: Material(
                                      color: Colors.transparent,
                                      child: InkWell(
                                        borderRadius: BorderRadius.circular(22),
                                        onTap: _acceptedKvkk && !_isInstagramLoading 
                                            ? () {
                                                _buttonAnimationController.forward().then((_) {
                                                  _buttonAnimationController.reverse();
                                                });
                                                _handleInstagramLogin();
                                              } 
                                            : null,
                                        child: Center(
                                          child: _isInstagramLoading
                                              ? const SizedBox(
                                                  width: 24,
                                                  height: 24,
                                                  child: CircularProgressIndicator(
                                                    color: Colors.white,
                                                    strokeWidth: 2,
                                                  ),
                                                )
                                              : Row(
                                                  mainAxisAlignment: MainAxisAlignment.center,
                                                  children: [
                                                    Icon(
                                                      Icons.camera_alt_outlined,
                                                      color: _acceptedKvkk ? Colors.white : Colors.grey[600],
                                                      size: 22,
                                                    ),
                                                    const SizedBox(width: 12),
                                                    Text(
                                                      'Instagram ile Giriş Yap',
                                                      style: TextStyle(
                                                        color: _acceptedKvkk ? Colors.white : Colors.grey[600],
                                                        fontSize: 18,
                                                        fontWeight: FontWeight.bold,
                                                        letterSpacing: 0.5,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                          const SizedBox(height: 20),
                          ScaleTransition(
                            scale: _buttonScaleAnimation,
                            child: Container(
                              height: 64,
                              decoration: BoxDecoration(
                                gradient: _acceptedKvkk
                                    ? const LinearGradient(
                                        colors: [
                                          Color(0xFF667eea),
                                          Color(0xFFDD2A7B),
                                        ],
                                      )
                                    : LinearGradient(
                                        colors: [
                                          Colors.grey[300]!,
                                          Colors.grey[400]!,
                                        ],
                                      ),
                                borderRadius: BorderRadius.circular(22),
                                boxShadow: _acceptedKvkk
                                    ? [
                                        BoxShadow(
                                          color: const Color(0xFFDD2A7B).withOpacity(0.3),
                                          blurRadius: 15,
                                          offset: const Offset(0, 8),
                                        ),
                                      ]
                                    : [
                                        BoxShadow(
                                          color: Colors.grey.withOpacity(0.2),
                                          blurRadius: 5,
                                          offset: const Offset(0, 2),
                                        ),
                                      ],
                              ),
                              child: Material(
                                color: Colors.transparent,
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(22),
                                  onTap: _acceptedKvkk && !_isInstagramLoading 
                                      ? () {
                                          _buttonAnimationController.forward().then((_) {
                                            _buttonAnimationController.reverse();
                                          });
                                          _handleManualInstagramLogin();
                                        } 
                                      : null,
                                  child: Center(
                                    child: _isManualLoginPolling
                                        ? const SizedBox(
                                            width: 24,
                                            height: 24,
                                            child: CircularProgressIndicator(
                                              color: Colors.white,
                                              strokeWidth: 2,
                                            ),
                                          )
                                        : Row(
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            children: [
                                              Icon(
                                                Icons.touch_app_outlined,
                                                color: _acceptedKvkk ? Colors.white : Colors.grey[600],
                                                size: 22,
                                              ),
                                              const SizedBox(width: 12),
                                              Text(
                                                'Manuel Instagram Girişi',
                                                style: TextStyle(
                                                  color: _acceptedKvkk ? Colors.white : Colors.grey[600],
                                                  fontSize: 18,
                                                  fontWeight: FontWeight.bold,
                                                  letterSpacing: 0.5,
                                                ),
                                              ),
                                            ],
                                          ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 32),
                          Container(
                            padding: const EdgeInsets.all(28),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.blue[25]?.withOpacity(0.9) ?? Colors.blue[50]!.withOpacity(0.9),
                                  Colors.indigo[25]?.withOpacity(0.7) ?? Colors.indigo[50]!.withOpacity(0.7),
                                ],
                              ),
                              borderRadius: BorderRadius.circular(24),
                              border: Border.all(
                                color: Colors.blue[200]!.withOpacity(0.8),
                                width: 2,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.blue.withOpacity(0.12),
                                  blurRadius: 20,
                                  offset: const Offset(0, 8),
                                ),
                                BoxShadow(
                                  color: Colors.white.withOpacity(0.8),
                                  blurRadius: 1,
                                  offset: const Offset(0, 1),
                                ),
                              ],
                            ),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        Colors.blue[500]!,
                                        Colors.purple[400]!,
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(20),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.blue.withOpacity(0.3),
                                        blurRadius: 10,
                                        offset: const Offset(0, 4),
                                      ),
                                    ],
                                  ),
                                  child: const Icon(
                                    Icons.security_rounded,
                                    color: Colors.white,
                                    size: 28,
                                  ),
                                ),
                                const SizedBox(width: 20),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Gizliliğiniz Bizim İçin Önemli',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 17,
                                          color: Colors.blue[800],
                                          letterSpacing: 0.3,
                                        ),
                                      ),
                                      const SizedBox(height: 6),
                                      Text(
                                        'Verileriniz asla 3. şahıslarla paylaşılmaz ve güvenliğiniz için şifrelenir.',
                                        style: TextStyle(
                                          fontSize: 14,
                                          color: Colors.grey[700],
                                          height: 1.5,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 50),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Container(
                                height: 1,
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    colors: [
                                      Colors.transparent,
                                      Colors.white.withOpacity(0.3),
                                      Colors.transparent,
                                    ],
                                  ),
                                ),
                              ),
                            ),
                            Container(
                              margin: const EdgeInsets.symmetric(horizontal: 16),
                              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                  color: Colors.white.withOpacity(0.2),
                                ),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.stars_rounded,
                                    color: Colors.white.withOpacity(0.8),
                                    size: 16,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Instagram Puan',
                                    style: TextStyle(
                                      color: Colors.white.withOpacity(0.9),
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      letterSpacing: 0.5,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Expanded(
                              child: Container(
                                height: 1,
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    colors: [
                                      Colors.transparent,
                                      Colors.white.withOpacity(0.3),
                                      Colors.transparent,
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0.0, end: 1.0),
                          duration: const Duration(milliseconds: 1500),
                          builder: (context, value, child) {
                            return Opacity(
                              opacity: value,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    colors: [
                                      Colors.white.withOpacity(0.1),
                                      Colors.white.withOpacity(0.05),
                                    ],
                                  ),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: Colors.white.withOpacity(0.2),
                                    width: 1,
                                  ),
                                ),
                                child: Text(
                                  '© 2025 Instagram Puan App',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.9),
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                    letterSpacing: 0.8,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            );
                          },
                        ),
                        const SizedBox(height: 12),
                        TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0.0, end: 1.0),
                          duration: const Duration(milliseconds: 1800),
                          builder: (context, value, child) {
                            return Opacity(
                              opacity: value * 0.8,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.05),
                                  borderRadius: BorderRadius.circular(15),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.favorite,
                                      color: Colors.pink[300],
                                      size: 16,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      'Instagram ile puan kazanın, ödüller alın',
                                      style: TextStyle(
                                        color: Colors.white.withOpacity(0.7),
                                        fontSize: 14,
                                        fontWeight: FontWeight.w500,
                                        letterSpacing: 0.3,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    const SizedBox(width: 8),
                                    Icon(
                                      Icons.favorite,
                                      color: Colors.pink[300],
                                      size: 16,
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showKvkkDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        elevation: 16,
        child: Container(
          width: 450,
          height: 600,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white,
                Color(0xFFF8F9FA),
              ],
            ),
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [
                      Color(0xFF8134AF),
                      Color(0xFFDD2A7B),
                    ],
                  ),
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(24),
                    topRight: Radius.circular(24),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.security_rounded,
                        color: Colors.white,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Text(
                        'KVKK & Gizlilik Politikası',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.of(ctx).pop(),
                      icon: const Icon(
                        Icons.close_rounded,
                        color: Colors.white,
                        size: 24,
                      ),
                    ),
                  ],
                ),
              ),
              
              const Expanded(
                child: SingleChildScrollView(
                  padding: EdgeInsets.all(24),
                  child: KvkkDialogContent(),
                ),
              ),
              
              Container(
                padding: const EdgeInsets.all(24),
                child: Container(
                  width: double.infinity,
                  height: 50,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [
                        Color(0xFF8134AF),
                        Color(0xFFDD2A7B),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF8134AF).withOpacity(0.3),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(16),
                      onTap: () => Navigator.of(ctx).pop(),
                      child: const Center(
                        child: Text(
                          'Anladım',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
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
}

class KvkkDialogContent extends StatelessWidget {
  const KvkkDialogContent({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.blue[200]!, width: 1),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue[100],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.info_outline_rounded,
                  color: Colors.blue[700],
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Text(
                  'Kişisel Verilerin Korunması (KVKK) & Gizlilik',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 16,
                    color: Color(0xFF2C2C2C),
                    height: 1.3,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        
        _buildContentSection(
          icon: Icons.security_rounded,
          title: 'Veri Toplama',
          content: 'JAEGram, yalnızca hizmetin sunulması ve geliştirilmesi amacıyla gerekli olan kişisel verileri toplar ve işler.',
          color: Colors.green,
        ),
        const SizedBox(height: 16),
        
        _buildContentSection(
          icon: Icons.timer_rounded,
          title: 'Veri Saklama',
          content: 'Kişisel veriler, yasal zorunluluklar ve hizmet gereksinimleri doğrultusunda makul süre boyunca saklanır.',
          color: Colors.orange,
        ),
        const SizedBox(height: 16),
        
        _buildContentSection(
          icon: Icons.admin_panel_settings_rounded,
          title: 'Haklarınız',
          content: 'KVKK kapsamında; verilerinize erişme, düzeltme, silme, işlenmesini kısıtlama ve itiraz etme hakkına sahipsiniz.',
          color: Colors.purple,
        ),
        const SizedBox(height: 16),
        
        _buildContentSection(
          icon: Icons.handshake_rounded,
          title: 'Onay',
          content: 'Hizmeti kullanarak gizlilik politikamızı ve KVKK metnini kabul etmiş olursunuz. Dilediğiniz zaman onayınızı geri çekebilirsiniz.',
          color: Colors.blue,
        ),
        const SizedBox(height: 24),
        
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[200]!),
          ),
          child: Row(
            children: [
              Icon(
                Icons.support_agent_rounded,
                color: Colors.grey[600],
                size: 20,
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Daha fazla bilgi için destek ekibimize ulaşabilirsiniz.',
                  style: TextStyle(
                    fontStyle: FontStyle.italic,
                    color: Color(0xFF666666),
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildContentSection({
    required IconData icon,
    required String title,
    required String content,
    required MaterialColor color,
  }) {
    // MaterialColor olmayan bir şey gelirse default olarak Colors.blue kullan
    final safeColor = color;
    Color? getShade(int shade, {Color? fallback}) {
      return (safeColor[shade]) ?? fallback ?? Colors.blue;
    }
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: getShade(50, fallback: Colors.blue[50]),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: getShade(200, fallback: Colors.blue[200])!, width: 1),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: getShade(100, fallback: Colors.blue[100]),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: getShade(700, fallback: Colors.blue[700]),
              size: 18,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    color: getShade(800, fallback: Colors.blue[800]),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  content,
                  style: TextStyle(
                    fontSize: 13,
                    color: getShade(700, fallback: Colors.blue[700]),
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}