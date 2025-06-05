import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
// import '../utils/instagram_dialog_utils.dart';

class InstagramAccountSettingsScreen extends ConsumerStatefulWidget {
  const InstagramAccountSettingsScreen({super.key});

  @override
  ConsumerState<InstagramAccountSettingsScreen> createState() =>
      _InstagramAccountSettingsScreenState();
}

class _InstagramAccountSettingsScreenState
    extends ConsumerState<InstagramAccountSettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _isConnected = false;
  String? _connectedUsername;
  Map<String, dynamic>? _accountInfo;

  @override
  void initState() {
    super.initState();
    _loadInstagramAccount();
  }

  Future<void> _loadInstagramAccount() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.get('/instagram/account-info');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _isConnected = data['connected'] ?? false;
          _connectedUsername = data['username'];
          _accountInfo = data['account_info'];
        });
      }
    } catch (e) {
      _showErrorDialog('Hesap bilgileri yüklenirken hata oluştu: ${e.toString()}');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _connectInstagramAccount() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.post('/instagram/connect', body: {
        'username': _usernameController.text.trim(),
        'password': _passwordController.text,
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        if (data['success']) {
          setState(() {
            _isConnected = true;
            _connectedUsername = _usernameController.text.trim();
            _accountInfo = data['account_info'];
          });
          _showSuccessDialog('Instagram hesabınız başarıyla bağlandı!');
          _usernameController.clear();
          _passwordController.clear();
        } else if (data['challenge_required']) {
          // Challenge gerekli - dialog göster
          _showChallengeDialog(data);
        } else {
          _showErrorDialog(data['message'] ?? 'Bağlantı kurulurken hata oluştu');
        }
      }
    } catch (e) {
      _showErrorDialog('Bağlantı kurulurken hata oluştu: ${e.toString()}');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _disconnectInstagramAccount() async {
    final confirm = await _showConfirmDialog(
      'Instagram Hesabı Bağlantısını Kes',
      'Instagram hesabınızın bağlantısını kesmek istediğinizden emin misiniz? Bu işlem sonrasında Instagram görevlerini yapamazsınız.',
    );

    if (!confirm) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.post('/instagram/disconnect');

      if (response.statusCode == 200) {
        setState(() {
          _isConnected = false;
          _connectedUsername = null;
          _accountInfo = null;
        });
        _showSuccessDialog('Instagram hesabınızın bağlantısı kesildi.');
      }
    } catch (e) {
      _showErrorDialog('Bağlantı kesilirken hata oluştu: ${e.toString()}');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final response = await apiService.post('/instagram/test-connection');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success']) {
          _showSuccessDialog('Bağlantı başarılı! Instagram hesabınız aktif.');
          await _loadInstagramAccount(); // Bilgileri yenile
        } else {
          _showErrorDialog(data['message'] ?? 'Bağlantı testi başarısız');
        }
      }
    } catch (e) {
      _showErrorDialog('Bağlantı test edilirken hata oluştu: ${e.toString()}');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showChallengeDialog(Map<String, dynamic> challengeData) async {
    // Temporary implementation - will be replaced with proper dialog
    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Instagram Challenge'),
        content: Text(challengeData['message'] ?? 'Complete the verification'),
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
      _loadInstagramAccount();
    } else {
      _showErrorDialog('Doğrulama başarısız');
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hata'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  void _showSuccessDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Başarılı'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  Future<bool> _showConfirmDialog(String title, String message) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Evet'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Instagram Hesap Ayarları'),
        backgroundColor: Colors.pink[100],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Mevcut bağlantı durumu
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                _isConnected ? Icons.check_circle : Icons.error,
                                color: _isConnected ? Colors.green : Colors.red,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _isConnected ? 'Bağlı' : 'Bağlı Değil',
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  color: _isConnected ? Colors.green : Colors.red,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          if (_isConnected && _connectedUsername != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Kullanıcı Adı: @$_connectedUsername',
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ],
                          if (_accountInfo != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Takipçi: ${_accountInfo!['followers_count'] ?? 'Bilinmiyor'}',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            Text(
                              'Takip Edilen: ${_accountInfo!['following_count'] ?? 'Bilinmiyor'}',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 20),

                  if (!_isConnected) ...[
                    // Instagram hesabı bağlama formu
                    const Text(
                      'Instagram Hesabınızı Bağlayın',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Form(
                          key: _formKey,
                          child: Column(
                            children: [
                              TextFormField(
                                controller: _usernameController,
                                decoration: const InputDecoration(
                                  labelText: 'Instagram Kullanıcı Adı',
                                  prefixIcon: Icon(Icons.person),
                                  border: OutlineInputBorder(),
                                ),
                                validator: (value) {
                                  if (value == null || value.trim().isEmpty) {
                                    return 'Kullanıcı adı gerekli';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 16),
                              TextFormField(
                                controller: _passwordController,
                                decoration: const InputDecoration(
                                  labelText: 'Şifre',
                                  prefixIcon: Icon(Icons.lock),
                                  border: OutlineInputBorder(),
                                ),
                                obscureText: true,
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Şifre gerekli';
                                  }
                                  return null;
                                },
                              ),
                              const SizedBox(height: 20),
                              ElevatedButton(
                                onPressed: _isLoading ? null : _connectInstagramAccount,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.pink,
                                  foregroundColor: Colors.white,
                                  minimumSize: const Size(double.infinity, 50),
                                ),
                                child: _isLoading
                                    ? const CircularProgressIndicator(color: Colors.white)
                                    : const Text('Instagram Hesabını Bağla'),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Güvenlik bilgisi
                    Card(
                      color: Colors.blue[50],
                      child: const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.info, color: Colors.blue),
                                SizedBox(width: 8),
                                Text(
                                  'Güvenlik Bilgisi',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.blue,
                                  ),
                                ),
                              ],
                            ),
                            SizedBox(height: 8),
                            Text(
                              '• Bilgileriniz güvenli bir şekilde şifrelenir\n'
                              '• Instagram API kullanılarak doğrulanır\n'
                              '• Hesabınız sadece görev doğrulaması için kullanılır\n'
                              '• İstediğiniz zaman bağlantıyı kesebilirsiniz',
                              style: TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ] else ...[
                    // Bağlı hesap için işlemler
                    const Text(
                      'Hesap İşlemleri',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _testConnection,
                      icon: const Icon(Icons.wifi_protected_setup),
                      label: const Text('Bağlantıyı Test Et'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 50),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _loadInstagramAccount,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Hesap Bilgilerini Yenile'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 50),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _disconnectInstagramAccount,
                      icon: const Icon(Icons.link_off),
                      label: const Text('Hesap Bağlantısını Kes'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 50),
                      ),
                    ),
                  ],
                  
                  const SizedBox(height: 20),
                  
                  // Kullanım istatistikleri (varsa)
                  if (_isConnected) ...[
                    const Text(
                      'Kullanım İstatistikleri',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            _buildStatRow('Tamamlanan Görevler', '15'),
                            _buildStatRow('Kazanılan Puan', '750'),
                            _buildStatRow('Son Görev', '2 saat önce'),
                          ],
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}