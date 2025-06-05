import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../models/instagram_integration.dart';
import '../providers/user_provider.dart';
import '../services/instagram_service.dart';
import '../generated/app_localizations.dart';
import '../themes/app_theme.dart';

class InstagramIntegrationScreen extends ConsumerStatefulWidget {
  const InstagramIntegrationScreen({super.key});

  @override
  ConsumerState<InstagramIntegrationScreen> createState() => _InstagramIntegrationScreenState();
}

class _InstagramIntegrationScreenState extends ConsumerState<InstagramIntegrationScreen> 
    with TickerProviderStateMixin {
  final InstagramService _instagramService = InstagramService();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  InstagramProfile? _profile;
  InstagramCredential? _credential;
  List<InstagramPost> _posts = [];
  bool _isLoading = true;
  bool _isConnecting = false;
  bool _isSyncing = false;
  bool _showPassword = false;

  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _slideController, curve: Curves.easeOutCubic));

    _loadInstagramData();
    _fadeController.forward();
    _slideController.forward();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _fadeController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  Future<void> _loadInstagramData() async {
    final userAsync = ref.read(userProvider);
    if (userAsync.value?.token == null) return;
    
    setState(() => _isLoading = true);

    try {
      final profile = await _instagramService.getProfile(userAsync.value!.token!);
      final credential = await _instagramService.getCredentialStatus(userAsync.value!.token!);
      
      if (profile != null) {
        final posts = await _instagramService.getPosts(userAsync.value!.token!);
        setState(() {
          _profile = profile;
          _posts = posts;
        });
      }

      setState(() {
        _credential = credential;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar(AppLocalizations.of(context).loadInstagramDataFailed);
    }
  }

  Future<void> _connectInstagram() async {
    final localizations = AppLocalizations.of(context);
    if (_usernameController.text.isEmpty || _passwordController.text.isEmpty) {
      _showErrorSnackBar(localizations.usernamePasswordRequired);
      return;
    }

    setState(() => _isConnecting = true);
    
    try {
      final result = await _instagramService.connectAccount(
        _usernameController.text,
        _passwordController.text,
      );
      
      if (result['success'] == true) {
        _showSuccessSnackBar(localizations.instagramConnected);
        await _loadInstagramData();
        _usernameController.clear();
        _passwordController.clear();
      } else {
        _showErrorSnackBar(localizations.instagramConnectionFailed);
      }
    } catch (e) {
      _showErrorSnackBar(localizations.instagramConnectionError);
    } finally {
      setState(() => _isConnecting = false);
    }
  }

  Future<void> _syncInstagram() async {
    final localizations = AppLocalizations.of(context);
    setState(() => _isSyncing = true);
    final userAsync = ref.read(userProvider);
    
    try {
      await _instagramService.syncProfile(userAsync.value!.token!);
      
      await _loadInstagramData();
      _showSuccessSnackBar(localizations.instagramSyncSuccess);
    } catch (e) {
      _showErrorSnackBar(localizations.instagramSyncError);
    } finally {
      setState(() => _isSyncing = false);
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(8.0),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
      ),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(8.0),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final locale = AppLocalizations.of(context);
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(locale.instagramIntegration),
        elevation: 0,
        backgroundColor: Colors.transparent,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: AppTheme.instagramGradient,
          ),
        ),
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton.icon(
              onPressed: () => Navigator.of(context).pushNamed('/instagram-dashboard'),
              icon: const Icon(Icons.dashboard),
              label: const Text('Instagram Dashboard'),
            ),
          ],
        ),
      ),
    );
  }
}
