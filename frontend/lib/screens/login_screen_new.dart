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
  bool _isPasswordVisible = false;
  
  late AnimationController _animationController;
  late AnimationController _buttonAnimationController;
  late AnimationController _pulseAnimationController;
  late AnimationController _particleAnimationController;
  
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _buttonAnimationController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _pulseAnimationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    _particleAnimationController = AnimationController(
      duration: const Duration(seconds: 10),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.5),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _pulseAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _animationController.forward();
    _pulseAnimationController.repeat(reverse: true);
    _particleAnimationController.repeat();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _buttonAnimationController.dispose();
    _pulseAnimationController.dispose();
    _particleAnimationController.dispose();
    instagramUsernameController.dispose();
    instagramPasswordController.dispose();
    super.dispose();
  }

  void _onLoginSuccess() {
    final userState = ref.read(userProvider);
    if (userState.value?.isAdminPlatform == true) {
      GoRouter.of(context).go('/admin');
    } else {
      GoRouter.of(context).go('/main/tasks');
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isTablet = size.width > 600;
    
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
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
        child: Stack(
          children: [
            // Animated background particles
            ...List.generate(15, (index) => _buildFloatingParticle(index, size)),
            
            // Main content
            SafeArea(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: size.height - MediaQuery.of(context).padding.top,
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: isTablet ? size.width * 0.15 : 24,
                      vertical: 20,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 40),
                        
                        // Header Section
                        _buildHeaderSection(),
                        
                        const SizedBox(height: 60),
                        
                        // Login Form
                        _buildLoginForm(size),
                        
                        const SizedBox(height: 40),
                        
                        // Footer
                        _buildFooter(),
                        
                        const SizedBox(height: 20),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFloatingParticle(int index, Size size) {
    return AnimatedBuilder(
      animation: _particleAnimationController,
      builder: (context, child) {
        final progress = _particleAnimationController.value;
        final angle = progress * 2 * math.pi + (index * 0.5);
        final radius = 30 + (index * 5);
        
        return Positioned(
          left: size.width * 0.5 + math.cos(angle) * radius + (index * 40),
          top: size.height * 0.3 + math.sin(angle) * radius + (index * 30),
          child: Opacity(
            opacity: 0.1 + (0.1 * math.sin(progress * math.pi)),
            child: Container(
              width: 3 + (index % 4),
              height: 3 + (index % 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.7),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.white.withOpacity(0.3),
                    blurRadius: 8,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeaderSection() {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: Column(
          children: [
            // Logo
            ScaleTransition(
              scale: _scaleAnimation,
              child: Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.white.withOpacity(0.2),
                      Colors.white.withOpacity(0.1),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(
                    color: Colors.white.withOpacity(0.3),
                    width: 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 30,
                      offset: const Offset(0, 15),
                    ),
                  ],
                ),
                child: Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [
                        Color(0xFFDD2A7B),
                        Color(0xFF8134AF),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFDD2A7B).withOpacity(0.4),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.camera_alt_rounded,
                    color: Colors.white,
                    size: 35,
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 30),
            
            // App Title
            ShaderMask(
              shaderCallback: (bounds) => const LinearGradient(
                colors: [Colors.white, Color(0xFFF0F0F0)],
              ).createShader(bounds),
              child: const Text(
                'Instagram',
                style: TextStyle(
                  fontSize: 44,
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
                    const Color(0xFFDD2A7B).withOpacity(0.9),
                    const Color(0xFF8134AF).withOpacity(0.9),
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
              child: const Text(
                'PUAN',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                  color: Colors.white,
                  letterSpacing: 4.0,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Subtitle
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.white.withOpacity(0.15),
                    Colors.white.withOpacity(0.05),
                  ],
                ),
                borderRadius: BorderRadius.circular(25),
                border: Border.all(
                  color: Colors.white.withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.auto_awesome_rounded,
                    color: Colors.white.withOpacity(0.9),
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Instagram hesabınızla güvenli giriş yapın',
                    style: TextStyle(
                      fontSize: 15,
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.3,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    Icons.auto_awesome_rounded,
                    color: Colors.white.withOpacity(0.9),
                    size: 18,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoginForm(Size size) {
    return SlideTransition(
      position: _slideAnimation,
      child: Container(
        padding: const EdgeInsets.all(32),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.95),
          borderRadius: BorderRadius.circular(28),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 50,
              offset: const Offset(0, 25),
            ),
            BoxShadow(
              color: const Color(0xFF8134AF).withOpacity(0.1),
              blurRadius: 25,
              offset: const Offset(0, 15),
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
            // Form Header
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.deepPurple[400]!,
                        Colors.purple[300]!,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.login_rounded,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Giriş Yap',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                    color: Colors.deepPurple[700],
                    letterSpacing: 0.5,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 32),
            
            // Username Field
            _buildTextField(
              controller: instagramUsernameController,
              label: 'Instagram Kullanıcı Adı',
              hint: 'Kullanıcı adınızı girin',
              icon: Icons.person_outline_rounded,
              gradientColors: [Colors.blue[400]!, Colors.blue[600]!],
              borderColor: Colors.blue[200]!,
              obscureText: false,
            ),
            
            const SizedBox(height: 20),
            
            // Password Field
            _buildTextField(
              controller: instagramPasswordController,
              label: 'Instagram Şifre',
              hint: 'Şifrenizi girin',
              icon: Icons.lock_outline_rounded,
              gradientColors: [Colors.purple[400]!, Colors.purple[600]!],
              borderColor: Colors.purple[200]!,
              obscureText: !_isPasswordVisible,
              suffixIcon: IconButton(
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
              onSubmitted: (_) => _handleInstagramLogin(),
            ),
            
            const SizedBox(height: 24),
            
            // Login Buttons
            _buildLoginButtons(),
            
            const SizedBox(height: 24),
            
            // Security Info
            _buildSecurityInfo(),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    required List<Color> gradientColors,
    required Color borderColor,
    required bool obscureText,
    Widget? suffixIcon,
    Function(String)? onSubmitted,
  }) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.white,
            gradientColors[0].withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: borderColor.withOpacity(0.3),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: gradientColors[0].withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: TextField(
        controller: controller,
        obscureText: obscureText,
        onSubmitted: onSubmitted,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: Color(0xFF2C2C2C),
          letterSpacing: 0.3,
        ),
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          prefixIcon: Container(
            margin: const EdgeInsets.all(10),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              gradient: LinearGradient(colors: gradientColors),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              color: Colors.white,
              size: 20,
            ),
          ),
          suffixIcon: suffixIcon,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 20,
            horizontal: 16,
          ),
          labelStyle: TextStyle(
            fontSize: 14,
            color: gradientColors[1],
            fontWeight: FontWeight.w600,
          ),
          hintStyle: TextStyle(
            fontWeight: FontWeight.w400,
            color: Colors.grey[500],
          ),
        ),
        textInputAction: suffixIcon != null ? TextInputAction.done : TextInputAction.next,
      ),
    );
  }

  Widget _buildLoginButtons() {
    return Column(
      children: [
        // Instagram Login Button
        AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: 1.0, // Always enabled, no KVKK dependency
              child: Container(
                height: 56,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Color(0xFF667eea),
                      Color(0xFF764ba2),
                      Color(0xFF8134AF),
                    ],
                  ),
                  borderRadius: BorderRadius.all(Radius.circular(16)),
                  boxShadow: [
                    BoxShadow(
                      color: Color(0x66813AAF),
                      blurRadius: 20,
                      offset: Offset(0, 8),
                    ),
                  ],
                ),
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: !_isInstagramLoading ? _handleInstagramLogin : null,
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
                        : const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.camera_alt_outlined,
                                color: Colors.white,
                                size: 20,
                              ),
                              SizedBox(width: 12),
                              Text(
                                'Instagram ile Giriş Yap',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.5,
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
        ),
      ],
    );
  }

  Widget _buildSecurityInfo() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.green[50]!.withOpacity(0.8),
            Colors.green[100]!.withOpacity(0.4),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.green[200]!.withOpacity(0.6),
          width: 1.5,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.green[500]!, Colors.green[600]!],
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: Colors.green.withOpacity(0.3),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Icon(
              Icons.security_rounded,
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
                  'Gizliliğiniz Bizim İçin Önemli',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 15,
                    color: Colors.green[800],
                    letterSpacing: 0.3,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Verileriniz asla 3. şahıslarla paylaşılmaz ve güvenliğiniz için şifrelenir.',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.green[700],
                    height: 1.4,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        children: [
          // Divider with brand
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
                  gradient: LinearGradient(
                    colors: [
                      Colors.white.withOpacity(0.1),
                      Colors.white.withOpacity(0.05),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(15),
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
                      size: 14,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Instagram Puan',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 11,
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
          
          const SizedBox(height: 20),
          
          // Copyright
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.white.withOpacity(0.1),
                  Colors.white.withOpacity(0.05),
                ],
              ),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Column(
              children: [
                Text(
                  '© 2025 Instagram Puan App',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.favorite,
                      color: Colors.pink[300],
                      size: 14,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Instagram ile puan kazanın, ödüller alın',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.7),
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Icon(
                      Icons.favorite,
                      color: Colors.pink[300],
                      size: 14,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // KVKK Dialog implementation
  // Include all the existing login methods here...
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
}
