import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:instagram_puan_app/providers/theme_provider.dart';
import '../providers/user_provider.dart';
import '../providers/notification_settings_provider.dart';
import '../providers/instagram_credential_provider.dart';
import '../widgets/gradient_button.dart';
import '../themes/app_theme.dart';
import 'dart:math';

class SettingsScreenNew extends ConsumerStatefulWidget {
  const SettingsScreenNew({super.key});

  @override
  ConsumerState<SettingsScreenNew> createState() => _SettingsScreenNewState();
}

class _SettingsScreenNewState extends ConsumerState<SettingsScreenNew> 
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late AnimationController _headerController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _headerAnimation;

  @override
  void initState() {
    super.initState();
    
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _headerController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.5),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _slideController, curve: Curves.easeOutCubic));
    
    _headerAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _headerController, curve: Curves.elasticOut),
    );
    
    _fadeController.forward();
    _slideController.forward();
    _headerController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
    _headerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final userAsync = ref.watch(userProvider);
    final themeMode = ref.watch(themeProvider);
    final locale = ref.watch(localeProvider);
    final localizations = AppLocalizations.of(context)!;
    final isDark = themeMode == ThemeMode.dark || 
      (themeMode == ThemeMode.system && MediaQuery.of(context).platformBrightness == Brightness.dark);
    
    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF121212) : const Color(0xFFF8F9FA),
      extendBodyBehindAppBar: true,
      appBar: _buildAppBar(context, localizations, isDark),
      body: Stack(
        children: [
          // Background gradient
          Container(
            decoration: BoxDecoration(
              gradient: isDark
                  ? const LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Color(0xFF1A1A1A),
                        Color(0xFF121212),
                        Color(0xFF0A0A0A),
                      ],
                    )
                  : const LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Color(0xFFF8F9FA),
                        Color(0xFFFFFFFF),
                        Color(0xFFF0F2F5),
                      ],
                    ),
            ),
          ),
          
          // Floating orbs background effect
          ..._buildFloatingOrbs(isDark),
          
          // Main content
          FadeTransition(
            opacity: _fadeAnimation,
            child: SlideTransition(
              position: _slideAnimation,
              child: userAsync.when(
                loading: () => _buildLoadingState(),
                error: (error, stackTrace) => _buildErrorState(error, localizations),
                data: (user) => _buildMainContent(context, user, themeMode, locale, localizations, isDark),
              ),
            ),
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context, AppLocalizations localizations, bool isDark) {
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.transparent,
      flexibleSpace: Container(
        decoration: BoxDecoration(
          gradient: isDark 
              ? AppTheme.darkBackgroundGradient 
              : AppTheme.instagramGradient,
        ),
      ),
      title: ScaleTransition(
        scale: _headerAnimation,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                shape: BoxShape.circle,
                border: Border.all(
                  color: Colors.white.withValues(alpha: 0.3),
                  width: 1,
                ),
              ),
              child: const Icon(
                Icons.settings,
                color: Colors.white,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              localizations.settingsTitle,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 20,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      ),
      centerTitle: true,
      foregroundColor: Colors.white,
    );
  }

  List<Widget> _buildFloatingOrbs(bool isDark) {
    return List.generate(6, (index) {
      final random = Random(index);
      return Positioned(
        left: random.nextDouble() * 400,
        top: random.nextDouble() * 800,
        child: Container(
          width: 60 + random.nextDouble() * 40,
          height: 60 + random.nextDouble() * 40,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [
                (isDark 
                    ? [Colors.purple, Colors.blue, Colors.pink]
                    : [Colors.orange, Colors.pink, Colors.purple]
                )[index % 3].withValues(alpha: 0.1),
                Colors.transparent,
              ],
            ),
          ),
        ),
      );
    });
  }

  Widget _buildLoadingState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text(
            'Ayarlar yükleniyor...',
            style: TextStyle(fontSize: 16),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(dynamic error, AppLocalizations localizations) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            '${localizations.errorLoadingSettings}: $error',
            style: const TextStyle(fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildMainContent(
    BuildContext context,
    user,
    ThemeMode themeMode,
    Locale? locale,
    AppLocalizations localizations,
    bool isDark,
  ) {
    return CustomScrollView(
      physics: const BouncingScrollPhysics(),
      slivers: [
        // Space for app bar
        const SliverToBoxAdapter(child: SizedBox(height: 100)),
        
        // Profile Header
        SliverToBoxAdapter(
          child: _buildProfileHeader(context, user, localizations, isDark),
        ),
        
        // Settings sections
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Account Section
                _buildAnimatedSection(
                  delay: 0,
                  child: _buildAccountSection(context, user, localizations, isDark),
                ),
                
                const SizedBox(height: 16),
                
                // Instagram Integration Section
                _buildAnimatedSection(
                  delay: 100,
                  child: _buildInstagramSection(context, localizations, isDark),
                ),
                
                const SizedBox(height: 16),
                
                // Notification Settings Section
                _buildAnimatedSection(
                  delay: 200,
                  child: _buildNotificationSection(context, localizations, isDark),
                ),
                
                const SizedBox(height: 16),
                
                // Display Settings Section
                _buildAnimatedSection(
                  delay: 300,
                  child: _buildDisplaySection(context, themeMode, locale, localizations, isDark),
                ),
                
                const SizedBox(height: 16),
                
                // Security Section
                _buildAnimatedSection(
                  delay: 400,
                  child: _buildSecuritySection(context, localizations, isDark),
                ),
                
                const SizedBox(height: 16),
                
                // About Section
                _buildAnimatedSection(
                  delay: 500,
                  child: _buildAboutSection(context, localizations, isDark),
                ),
                
                const SizedBox(height: 24),
                
                // Logout Button
                _buildAnimatedSection(
                  delay: 600,
                  child: _buildLogoutSection(context, localizations),
                ),
                
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProfileHeader(BuildContext context, user, AppLocalizations localizations, bool isDark) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: isDark 
            ? const LinearGradient(
                colors: [Color(0xFF2A2A2A), Color(0xFF1E1E1E)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : const LinearGradient(
                colors: [Colors.white, Color(0xFFF8F9FA)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
        boxShadow: [
          BoxShadow(
            color: isDark 
                ? Colors.black.withValues(alpha: 0.3)
                : Colors.black.withValues(alpha: 0.1),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Hero(
            tag: 'profile_avatar',
            child: Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppTheme.instagramGradient,
                boxShadow: [
                  BoxShadow(
                    color: Colors.purple.withValues(alpha: 0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Container(
                margin: const EdgeInsets.all(3),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isDark ? const Color(0xFF2A2A2A) : Colors.white,
                ),
                child: CircleAvatar(
                  radius: 32,
                  backgroundColor: Colors.transparent,
                  backgroundImage: user?.profilePicUrl != null
                      ? NetworkImage(user!.profilePicUrl!)
                      : null,
                  child: user?.profilePicUrl == null
                      ? Icon(
                          Icons.person,
                          size: 32,
                          color: isDark ? Colors.white70 : Colors.grey.shade600,
                        )
                      : null,
                ),
              ),
            ),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  user?.username ?? 'Kullanıcı',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: isDark ? Colors.white : Colors.black87,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  user?.email ?? 'email@example.com',
                  style: TextStyle(
                    fontSize: 14,
                    color: isDark ? Colors.white60 : Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    gradient: AppTheme.instagramGradient,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${user?.diamondBalance ?? 0} 💎',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
          InkWell(
            onTap: () => context.push('/edit-profile'),
            borderRadius: BorderRadius.circular(16),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isDark 
                    ? Colors.white.withValues(alpha: 0.1)
                    : Colors.black.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(
                Icons.edit,
                color: isDark ? Colors.white70 : Colors.grey.shade600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnimatedSection({required int delay, required Widget child}) {
    return TweenAnimationBuilder<double>(
      duration: Duration(milliseconds: 600 + delay),
      tween: Tween(begin: 0.0, end: 1.0),
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        return Transform.translate(
          offset: Offset(0, 20 * (1 - value)),
          child: Opacity(
            opacity: value,
            child: child,
          ),
        );
      },
      child: child,
    );
  }

  Widget _buildGlassSection({
    required bool isDark,
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: isDark
            ? LinearGradient(
                colors: [
                  Colors.white.withValues(alpha: 0.05),
                  Colors.white.withValues(alpha: 0.02),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : LinearGradient(
                colors: [
                  Colors.white.withValues(alpha: 0.9),
                  Colors.white.withValues(alpha: 0.7),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
        border: Border.all(
          color: isDark 
              ? Colors.white.withValues(alpha: 0.1)
              : Colors.white.withValues(alpha: 0.3),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: isDark 
                ? Colors.black.withValues(alpha: 0.3)
                : Colors.black.withValues(alpha: 0.08),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    gradient: AppTheme.instagramGradient,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: isDark ? Colors.white : Colors.black87,
                  ),
                ),
              ],
            ),
          ),
          ...children,
        ],
      ),
    );
  }

  Widget _buildModernListTile({
    required bool isDark,
    required IconData icon,
    Color? iconColor,
    required String title,
    required String subtitle,
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: (iconColor ?? Colors.purple).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  icon,
                  color: iconColor ?? Colors.purple,
                  size: 20,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: isDark ? Colors.white : Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 13,
                        color: isDark ? Colors.white60 : Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              if (trailing != null) trailing,
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildModernSwitchTile({
    required bool isDark,
    required IconData icon,
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.purple.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              color: Colors.purple,
              size: 20,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: isDark ? Colors.white : Colors.black87,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 13,
                    color: isDark ? Colors.white60 : Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: Colors.purple,
          ),
        ],
      ),
    );
  }

  Widget _buildAccountSection(BuildContext context, user, AppLocalizations localizations, bool isDark) {
    return _buildGlassSection(
      isDark: isDark,
      title: 'Hesap Yönetimi',
      icon: Icons.person_outline,
      children: [
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.account_circle_outlined,
          title: 'Profil Görüntüle',
          subtitle: 'Profil bilgilerinizi görüntüleyin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/profile'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.edit_outlined,
          title: 'Profili Düzenle',
          subtitle: 'Bilgilerinizi güncelleyin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/edit-profile'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.lock_outline,
          title: 'Şifre Değiştir',
          subtitle: 'Güvenlik için şifrenizi güncelleyin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/change-password'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.security_outlined,
          title: 'İki Faktörlü Kimlik Doğrulama',
          subtitle: 'Hesabınızı daha güvenli hale getirin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/two-factor-auth'),
        ),
      ],
    );
  }

  Widget _buildInstagramSection(BuildContext context, AppLocalizations localizations, bool isDark) {
    final isConnected = ref.watch(instagramCredentialProvider).maybeWhen(
      data: (credential) => credential?['is_connected'] as bool? ?? false,
      orElse: () => false,
    );

    return _buildGlassSection(
      isDark: isDark,
      title: 'Instagram Entegrasyonu',
      icon: Icons.camera_alt_outlined,
      children: [
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.link,
          iconColor: isConnected ? Colors.green : Colors.orange,
          title: 'Instagram Hesabı',
          subtitle: isConnected ? 'Bağlı ✓' : 'Bağlantı Yok',
          trailing: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: isConnected ? Colors.green.withValues(alpha: 0.2) : Colors.orange.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              isConnected ? 'Aktif' : 'Pasif',
              style: TextStyle(
                color: isConnected ? Colors.green : Colors.orange,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          onTap: () => context.push('/instagram-integration'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.dashboard_outlined,
          title: 'Instagram Dashboard',
          subtitle: 'Performans ve istatistikler',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/instagram-integration-dashboard'),
        ),
      ],
    );
  }

  Widget _buildNotificationSection(BuildContext context, AppLocalizations localizations, bool isDark) {
    return _buildGlassSection(
      isDark: isDark,
      title: 'Bildirim Ayarları',
      icon: Icons.notifications_outlined,
      children: [
        _buildModernSwitchTile(
          isDark: isDark,
          icon: Icons.notifications_active_outlined,
          title: 'Push Bildirimleri',
          subtitle: 'Uygulama bildirimlerini etkinleştir',
          value: ref.watch(notificationEnabledProvider),
          onChanged: (value) {
            ref.read(notificationEnabledProvider.notifier).state = value;
          },
        ),
        _buildModernSwitchTile(
          isDark: isDark,
          icon: Icons.emoji_events_outlined,
          title: 'Rozet Bildirimleri',
          subtitle: 'Yeni rozetler için bildirim al',
          value: ref.watch(badgeNotificationEnabledProvider),
          onChanged: (value) {
            ref.read(badgeNotificationEnabledProvider.notifier).state = value;
          },
        ),
        _buildModernSwitchTile(
          isDark: isDark,
          icon: Icons.volume_up_outlined,
          title: 'Ses Bildirimleri',
          subtitle: 'Bildirim sesleri',
          value: ref.watch(soundNotificationEnabledProvider),
          onChanged: (value) {
            ref.read(soundNotificationEnabledProvider.notifier).state = value;
          },
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.tune_outlined,
          title: 'Gelişmiş Bildirim Ayarları',
          subtitle: 'Detaylı bildirim tercihleri',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/notification-settings'),
        ),
      ],
    );
  }

  Widget _buildDisplaySection(BuildContext context, ThemeMode themeMode, Locale? locale, AppLocalizations localizations, bool isDark) {
    return _buildGlassSection(
      isDark: isDark,
      title: 'Görünüm Ayarları',
      icon: Icons.palette_outlined,
      children: [
        _buildModernListTile(
          isDark: isDark,
          icon: _getThemeIcon(themeMode),
          iconColor: _getThemeColor(themeMode),
          title: 'Tema Modu',
          subtitle: _getThemeName(themeMode, localizations),
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _showThemePicker(context),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.language_outlined,
          title: 'Dil / Language',
          subtitle: locale?.languageCode == 'tr' ? 'Türkçe' : 'English',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _showLanguageDialog(context, ref),
        ),
      ],
    );
  }

  Widget _buildSecuritySection(BuildContext context, AppLocalizations localizations, bool isDark) {
    return _buildGlassSection(
      isDark: isDark,
      title: 'Güvenlik & Gizlilik',
      icon: Icons.security_outlined,
      children: [
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.shield_outlined,
          title: 'Gizlilik Ayarları',
          subtitle: 'Veri koruma tercihleri',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _showPrivacyDialog(context),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.history_outlined,
          title: 'Etkinlik Geçmişi',
          subtitle: 'Hesap aktivitelerinizi görüntüleyin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _showActivityDialog(context),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.backup_outlined,
          title: 'Veri Yedekleme',
          subtitle: 'Verilerinizi yedekleyin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _showDataBackupDialog(context),
        ),
      ],
    );
  }

  Widget _buildAboutSection(BuildContext context, AppLocalizations localizations, bool isDark) {
    return _buildGlassSection(
      isDark: isDark,
      title: 'Hakkında & Destek',
      icon: Icons.info_outlined,
      children: [
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.help_outline,
          title: 'Yardım & Destek',
          subtitle: 'SSS ve yardım merkezi',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/help'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.description_outlined,
          title: 'Gizlilik Politikası',
          subtitle: 'KVKK ve veri koruma',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => context.push('/kvkk'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.gavel_outlined,
          title: 'Kullanım Koşulları',
          subtitle: 'Hizmet şartları',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _launchURL('https://example.com/terms'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.star_outline,
          title: 'Uygulamayı Değerlendir',
          subtitle: 'App Store\'da değerlendirin',
          trailing: const Icon(Icons.arrow_forward_ios, size: 16),
          onTap: () => _launchURL('https://example.com/rate'),
        ),
        _buildModernListTile(
          isDark: isDark,
          icon: Icons.info_outline,
          title: 'Versiyon',
          subtitle: 'JAEGram v1.0.0 (Build 1)',
          onTap: null,
        ),
      ],
    );
  }

  Widget _buildLogoutSection(BuildContext context, AppLocalizations localizations) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: const LinearGradient(
          colors: [Color(0xFFFF6B6B), Color(0xFFEE5A52)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.red.withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(20),
          onTap: () => _confirmLogout(context),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.logout,
                  color: Colors.white,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Text(
                  localizations.logout,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Helper methods
  IconData _getThemeIcon(ThemeMode themeMode) {
    switch (themeMode) {
      case ThemeMode.light:
        return Icons.light_mode;
      case ThemeMode.dark:
        return Icons.dark_mode;
      case ThemeMode.system:
        return Icons.brightness_auto;
    }
  }

  Color _getThemeColor(ThemeMode themeMode) {
    switch (themeMode) {
      case ThemeMode.light:
        return Colors.amber;
      case ThemeMode.dark:
        return Colors.indigo;
      case ThemeMode.system:
        return Colors.grey;
    }
  }

  String _getThemeName(ThemeMode themeMode, AppLocalizations localizations) {
    switch (themeMode) {
      case ThemeMode.light:
        return localizations.lightTheme;
      case ThemeMode.dark:
        return localizations.darkTheme;
      case ThemeMode.system:
        return localizations.systemTheme;
    }
  }

  Future<void> _showLanguageDialog(BuildContext context, WidgetRef ref) async {
    final localizations = AppLocalizations.of(context)!;
    final currentLocale = ref.read(localeProvider);
    final selected = await showDialog<Locale>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(localizations.selectLanguage),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Text('🇹🇷', style: TextStyle(fontSize: 24)),
              title: const Text('Türkçe'),
              trailing: currentLocale?.languageCode == 'tr' 
                  ? const Icon(Icons.check, color: Colors.green) 
                  : null,
              onTap: () => Navigator.pop(ctx, const Locale('tr')),
            ),
            ListTile(
              leading: const Text('🇺🇸', style: TextStyle(fontSize: 24)),
              title: const Text('English'),
              trailing: currentLocale?.languageCode == 'en' 
                  ? const Icon(Icons.check, color: Colors.green) 
                  : null,
              onTap: () => Navigator.pop(ctx, const Locale('en')),
            ),
          ],
        ),
      ),
    );
    
    if (selected != null) {
      ref.read(localeProvider.notifier).state = selected;
    }
  }

  Future<void> _showThemePicker(BuildContext context) async {
    final localizations = AppLocalizations.of(context)!;
    final themeMode = ref.read(themeProvider);
    
    final selected = await showDialog<ThemeMode>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(localizations.selectTheme),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.light_mode, color: Colors.amber),
              title: Text(localizations.lightTheme),
              trailing: themeMode == ThemeMode.light
                  ? const Icon(Icons.check, color: Colors.green)
                  : null,
              onTap: () => Navigator.pop(ctx, ThemeMode.light),
            ),
            ListTile(
              leading: const Icon(Icons.dark_mode, color: Colors.indigo),
              title: Text(localizations.darkTheme),
              trailing: themeMode == ThemeMode.dark
                  ? const Icon(Icons.check, color: Colors.green)
                  : null,
              onTap: () => Navigator.pop(ctx, ThemeMode.dark),
            ),
            ListTile(
              leading: const Icon(Icons.brightness_auto),
              title: Text(localizations.systemTheme),
              trailing: themeMode == ThemeMode.system
                  ? const Icon(Icons.check, color: Colors.green)
                  : null,
              onTap: () => Navigator.pop(ctx, ThemeMode.system),
            ),
          ],
        ),
      ),
    );
    
    if (selected != null) {
      ref.read(themeProvider.notifier).setTheme(selected);
    }
  }

  Future<void> _confirmLogout(BuildContext context) async {
    final localizations = AppLocalizations.of(context)!;
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(Icons.logout, color: Colors.red.shade400),
            const SizedBox(width: 8),
            Text(localizations.confirmLogout),
          ],
        ),
        content: Text(localizations.logoutConfirmationText),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(localizations.cancel),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: Text(localizations.logout),
          ),
        ],
      ),
    );
    
    if (confirm == true) {
      ref.read(userProvider.notifier).logout();
      context.go('/login');
    }
  }

  void _showPrivacyDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.shield, color: Colors.green),
            SizedBox(width: 8),
            Text('Gizlilik Ayarları'),
          ],
        ),
        content: const Text('Gizlilik ayarları yakında eklenecek...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  void _showActivityDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.history, color: Colors.blue),
            SizedBox(width: 8),
            Text('Etkinlik Geçmişi'),
          ],
        ),
        content: const Text('Etkinlik geçmişi yakında eklenecek...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  void _showDataBackupDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.backup, color: Colors.orange),
            SizedBox(width: 8),
            Text('Veri Yedekleme'),
          ],
        ),
        content: const Text('Veri yedekleme özelliği yakında eklenecek...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  void _launchURL(String url) {
    // Implementation would use url_launcher package or similar
    // Launch URL: $url
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Açılacak: $url')),
    );
  }
}
