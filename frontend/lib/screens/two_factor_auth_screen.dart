import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../providers/user_provider.dart';

class TwoFactorAuthScreen extends ConsumerStatefulWidget {
  const TwoFactorAuthScreen({super.key});

  @override
  ConsumerState<TwoFactorAuthScreen> createState() => _TwoFactorAuthScreenState();
}

class _TwoFactorAuthScreenState extends ConsumerState<TwoFactorAuthScreen> {
  final _codeController = TextEditingController();
  bool _isLoading = false;
  bool _isEnabled = false;
  String? _secretKey;
  String? _qrCodeUrl;

  @override
  void initState() {
    super.initState();
    _loadCurrentStatus();
  }

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  void _loadCurrentStatus() {
    final user = ref.read(userProvider).value;
    setState(() {
      _isEnabled = user?.twoFactorEnabled ?? false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('İki Faktörlü Kimlik Doğrulama'),
        centerTitle: true,
        elevation: 0,
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFFDD2A7B), Color(0xFF8134AF)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF8F9FA), Color(0xFFE9ECEF)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 20),
              
              // Status Card
              _buildStatusCard(),
              
              const SizedBox(height: 24),
              
              if (!_isEnabled) ...[
                _buildSetupCard(),
              ] else ...[
                _buildDisableCard(),
              ],
              
              const SizedBox(height: 24),
              
              // Info Card
              _buildInfoCard(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: _isEnabled 
              ? [const Color(0xFF4CAF50), const Color(0xFF2E7D32)]
              : [const Color(0xFFFF9800), const Color(0xFFE65100)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: (_isEnabled ? const Color(0xFF4CAF50) : const Color(0xFFFF9800))
                .withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(
            _isEnabled ? Icons.security : Icons.security_outlined,
            size: 64,
            color: Colors.white,
          ),
          const SizedBox(height: 16),
          Text(
            _isEnabled ? 'İki Faktörlü Kimlik Doğrulama Aktif' : 'İki Faktörlü Kimlik Doğrulama Pasif',
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            _isEnabled 
                ? 'Hesabınız ekstra güvenlik katmanı ile korunuyor'
                : 'Hesabınızı daha güvenli hale getirin',
            style: TextStyle(
              fontSize: 14,
              color: Colors.white.withValues(alpha: 0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSetupCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.qr_code, color: Color(0xFFDD2A7B)),
              SizedBox(width: 12),
              Text(
                '2FA Kurulumu',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2D3748),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          const Text(
            '1. Authenticator uygulamanızla QR kodu tarayın',
            style: TextStyle(fontSize: 14, color: Color(0xFF718096)),
          ),
          
          const SizedBox(height: 12),
          
          // QR Code Placeholder (would need actual secret key from backend)
          Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: _qrCodeUrl != null 
                ? QrImageView(
                    data: _qrCodeUrl!,
                    version: QrVersions.auto,
                    size: 180,
                  )
                : const Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.qr_code, size: 64, color: Colors.grey),
                      SizedBox(height: 8),
                      Text('QR Kod burada görünecek'),
                    ],
                  ),
          ),
          
          const SizedBox(height: 16),
          
          const Text(
            '2. Doğrulama kodunu girin',
            style: TextStyle(fontSize: 14, color: Color(0xFF718096)),
          ),
          
          const SizedBox(height: 12),
          
          TextField(
            controller: _codeController,
            keyboardType: TextInputType.number,
            maxLength: 6,
            textAlign: TextAlign.center,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: InputDecoration(
              labelText: '6 Haneli Kod',
              hintText: '123456',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              counterText: '',
            ),
          ),
          
          const SizedBox(height: 24),
          
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _generateQRCode,
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text('QR Kod Oluştur'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _enable2FA,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF4CAF50),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text('Aktifleştir'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDisableCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.security_outlined, color: Color(0xFFFF5722)),
              SizedBox(width: 12),
              Text(
                '2FA Devre Dışı Bırak',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2D3748),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          const Text(
            'İki faktörlü kimlik doğrulamayı devre dışı bırakmak hesabınızı daha az güvenli hale getirir.',
            style: TextStyle(fontSize: 14, color: Color(0xFF718096)),
          ),
          
          const SizedBox(height: 16),
          
          TextField(
            controller: _codeController,
            keyboardType: TextInputType.number,
            maxLength: 6,
            textAlign: TextAlign.center,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            decoration: InputDecoration(
              labelText: 'Doğrulama Kodu',
              hintText: '123456',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              counterText: '',
            ),
          ),
          
          const SizedBox(height: 24),
          
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _disable2FA,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFF5722),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Devre Dışı Bırak'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFE3F2FD),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF2196F3).withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.info_outline, color: Color(0xFF2196F3)),
              SizedBox(width: 12),
              Text(
                'İki Faktörlü Kimlik Doğrulama Nedir?',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2D3748),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            '• Hesabınıza ekstra bir güvenlik katmanı ekler\n'
            '• Şifrenizin yanında ikinci bir doğrulama gerektirir\n'
            '• Google Authenticator, Authy gibi uygulamalar kullanır\n'
            '• Hesap güvenliğinizi önemli ölçüde artırır',
            style: TextStyle(
              fontSize: 14,
              color: Color(0xFF4A5568),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  void _generateQRCode() {
    // Simulate QR code generation
    setState(() {
      _secretKey = 'JBSWY3DPEHPK3PXP'; // This would come from backend
      _qrCodeUrl = 'otpauth://totp/InstagramCoinApp:user@example.com?secret=$_secretKey&issuer=InstagramCoinApp';
    });
    
    _showSuccess('QR kod oluşturuldu! Authenticator uygulamanızla tarayın.');
  }

  void _enable2FA() async {
    if (_codeController.text.trim().length != 6) {
      _showError('Lütfen 6 haneli doğrulama kodunu girin');
      return;
    }

    if (_secretKey == null) {
      _showError('Önce QR kod oluşturun');
      return;
    }

    if (mounted) {
      setState(() => _isLoading = true);
    }

    try {
      // Simulate API call to enable 2FA
      await Future.delayed(const Duration(seconds: 2));
      
      // Here you would call your backend API
      // await ref.read(userProvider.notifier).enable2FA(_codeController.text);
      
      if (mounted) {
        setState(() {
          _isEnabled = true;
          _isLoading = false;
        });
      }
      
      _showSuccess('İki faktörlü kimlik doğrulama başarıyla aktifleştirildi!');
      _codeController.clear();
      
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
      _showError('Hata: ${e.toString()}');
    }
  }

  void _disable2FA() async {
    if (_codeController.text.trim().length != 6) {
      _showError('Lütfen 6 haneli doğrulama kodunu girin');
      return;
    }

    if (mounted) {
      setState(() => _isLoading = true);
    }

    try {
      // Simulate API call to disable 2FA
      await Future.delayed(const Duration(seconds: 2));
      
      // Here you would call your backend API
      // await ref.read(userProvider.notifier).disable2FA(_codeController.text);
      
      if (mounted) {
        setState(() {
          _isEnabled = false;
          _isLoading = false;
          _secretKey = null;
          _qrCodeUrl = null;
        });
      }
      
      _showSuccess('İki faktörlü kimlik doğrulama devre dışı bırakıldı.');
      _codeController.clear();
      
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
      _showError('Hata: ${e.toString()}');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}
