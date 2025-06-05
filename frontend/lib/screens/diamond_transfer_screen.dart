import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/user_provider.dart';
import '../generated/app_localizations.dart';
import '../themes/app_theme.dart';
import '../widgets/gradient_button.dart';
import '../services/diamond_service.dart';
import '../services/api_client.dart';

class DiamondTransferScreen extends ConsumerStatefulWidget {
  const DiamondTransferScreen({super.key});

  @override
  ConsumerState<DiamondTransferScreen> createState() => _DiamondTransferScreenState();
}

class _DiamondTransferScreenState extends ConsumerState<DiamondTransferScreen> 
    with TickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _recipientController = TextEditingController();
  final _amountController = TextEditingController();
  final _noteController = TextEditingController();

  bool _isLoading = false;
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
  }

  void _setupAnimations() {
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

    _fadeController.forward();
    _slideController.forward();
  }

  @override
  void dispose() {
    _recipientController.dispose();
    _amountController.dispose();
    _noteController.dispose();
    _fadeController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  Future<void> _transferCoins() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final userAsync = ref.read(userProvider);
      if (userAsync.value?.token == null) return;

      final diamondService = DiamondService(ApiClient());
      final success = await diamondService.transferDiamonds(
        token: userAsync.value!.token!,
        recipientUsername: _recipientController.text.trim(),
        amount: int.parse(_amountController.text.trim()),
        note: _noteController.text.trim().isEmpty ? null : _noteController.text.trim(),
      );

      if (success) {
        _showSuccessDialog();
        ref.refresh(userProvider); // Refresh user data to update diamond balance
      } else {
        _showErrorSnackBar('Transfer failed. Please try again.');
      }
    } catch (e) {
      _showErrorSnackBar('Transfer error: ${e.toString()}');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSuccessDialog() {
    final localizations = AppLocalizations.of(context);
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: AppTheme.instagramGradient,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.check, color: Colors.white),
            ),
            const SizedBox(width: 12),
            Text(localizations.transferSuccessful),
          ],
        ),
        content: Text(localizations.coinsTransferredSuccessfully),
        actions: [
          GradientButton(
            text: localizations.close,
            onPressed: () {
              Navigator.of(context).pop();
              context.pop(); // Go back to previous screen
            },
          ),
        ],
      ),
    );
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

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    final userAsync = ref.watch(userProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.coinTransfer),
        elevation: 0,
        backgroundColor: Colors.transparent,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: AppTheme.instagramGradient,
          ),
        ),
        foregroundColor: Colors.white,
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: SlideTransition(
          position: _slideAnimation,
          child: userAsync.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stack) => Center(
              child: Text('Error: $error'),
            ),
            data: (user) => user != null ? _buildTransferForm(context, user, localizations, theme) 
                : const Center(child: Text('No user data')),
          ),
        ),
      ),
    );
  }

  Widget _buildTransferForm(BuildContext context, user, AppLocalizations localizations, ThemeData theme) {
    final currentBalance = user.diamondBalance ?? 0;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Balance Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: AppTheme.instagramGradient,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.account_balance_wallet,
                    size: 48,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    localizations.currentBalance,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$currentBalance ${localizations.coins}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // Transfer Form
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: theme.cardColor,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    localizations.transferDetails,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Recipient Username
                  TextFormField(
                    controller: _recipientController,
                    decoration: InputDecoration(
                      labelText: localizations.recipientUsername,
                      hintText: localizations.enterRecipientUsername,
                      prefixIcon: Icon(Icons.person, color: theme.colorScheme.primary),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: theme.colorScheme.outline),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: theme.colorScheme.primary, width: 2),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return localizations.pleaseEnterRecipientUsername;
                      }
                      if (value.trim() == user.username) {
                        return localizations.cannotTransferToYourself;
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  // Amount
                  TextFormField(
                    controller: _amountController,
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                    ],
                    decoration: InputDecoration(
                      labelText: localizations.amount,
                      hintText: localizations.enterAmount,
                      prefixIcon: Icon(Icons.diamond, color: theme.colorScheme.primary),
                      suffixText: localizations.coins,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: theme.colorScheme.outline),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: theme.colorScheme.primary, width: 2),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return localizations.pleaseEnterAmount;
                      }
                      final amount = int.tryParse(value.trim());
                      if (amount == null || amount <= 0) {
                        return localizations.pleaseEnterValidAmount;
                      }
                      if (amount > currentBalance) {
                        return localizations.insufficientBalance;
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  // Note (Optional)
                  TextFormField(
                    controller: _noteController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      labelText: '${localizations.note} (${localizations.optional})',
                      hintText: localizations.enterTransferNote,
                      prefixIcon: Icon(Icons.note, color: theme.colorScheme.primary),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: theme.colorScheme.outline),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: theme.colorScheme.primary, width: 2),
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Transfer Button
                  SizedBox(
                    width: double.infinity,
                    child: GradientButton(
                      text: _isLoading ? localizations.processing : localizations.transferCoins,
                      icon: _isLoading ? null : Icons.send,
                      isLoading: _isLoading,
                      onPressed: _isLoading ? null : _transferCoins,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Information Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: theme.colorScheme.outline.withValues(alpha: 0.3),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: theme.colorScheme.primary,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        localizations.transferInformation,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '• ${localizations.transferInfo1}\\n'
                    '• ${localizations.transferInfo2}\\n'
                    '• ${localizations.transferInfo3}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
