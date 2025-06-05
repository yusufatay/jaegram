import 'package:flutter/material.dart';

class KvkkScreen extends StatelessWidget {
  const KvkkScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('KVKK & Gizlilik Politikası'),
        backgroundColor: Colors.teal.shade400,
        elevation: 0,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF11998e), Color(0xFF38ef7d)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const Icon(Icons.verified_user, size: 80, color: Colors.white70),
            const SizedBox(height: 24),
            Text(
              'Kişisel Verilerin Korunması (KVKK) & Gizlilik',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Card(
              color: Colors.white.withOpacity(0.97),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
              elevation: 6,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _sectionTitle('Veri Toplama ve Kullanımı'),
                    _sectionText('JAEGram, yalnızca hizmetin sunulması ve geliştirilmesi amacıyla gerekli olan kişisel verileri toplar ve işler.'),
                    const SizedBox(height: 12),
                    _sectionTitle('Veri Saklama Süresi'),
                    _sectionText('Kişisel veriler, yasal zorunluluklar ve hizmet gereksinimleri doğrultusunda makul süre boyunca saklanır.'),
                    const SizedBox(height: 12),
                    _sectionTitle('Haklarınız'),
                    _sectionText('KVKK kapsamında; verilerinize erişme, düzeltme, silme, işlenmesini kısıtlama ve itiraz etme hakkına sahipsiniz.'),
                    const SizedBox(height: 12),
                    _sectionTitle('Açık Rıza ve Onay'),
                    _sectionText('Hizmeti kullanarak gizlilik politikamızı ve KVKK metnini kabul etmiş olursunuz. Dilediğiniz zaman onayınızı geri çekebilirsiniz.'),
                    const SizedBox(height: 12),
                    _sectionTitle('Toplanan Veri Türleri'),
                    _sectionText('• Hesap bilgileri (kullanıcı adı, e-posta)\n• Instagram profil bilgileri (herkese açık)\n• Uygulama kullanım istatistikleri\n• Görev ve aktivite verileri'),
                    const SizedBox(height: 12),
                    _sectionTitle('Veri Güvenliği'),
                    _sectionText('Verileriniz endüstri standardı şifreleme yöntemleri ile korunur. Sunucularımız güvenli veri merkezlerinde barındırılır.'),
                    const SizedBox(height: 12),
                    _sectionTitle('Üçüncü Taraf Paylaşımlar'),
                    _sectionText('Kişisel verileriniz, yasal zorunluluklar dışında üçüncü taraflarla paylaşılmaz. Instagram API entegrasyonu sadece herkese açık veriler için kullanılır.'),
                    const SizedBox(height: 12),
                    _sectionTitle('İletişim'),
                    _sectionText('Veri koruma ile ilgili sorularınız için: privacy@jaegram.com adresine ulaşabilirsiniz.'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.teal.shade50,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.teal.shade200, width: 1.5),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: Colors.teal, size: 32),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      'KVKK ve gizlilik ile ilgili detaylı bilgi ve talepleriniz için destek ekibimize ulaşabilirsiniz.',
                      style: TextStyle(color: Colors.teal.shade900, fontSize: 16),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 40),
            Center(
              child: Text(
                'JAEGram Ekibi 🌱',
                style: TextStyle(
                  color: Colors.teal.shade700,
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String title) => Padding(
        padding: const EdgeInsets.only(bottom: 4.0),
        child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      );
  Widget _sectionText(String text) => Padding(
        padding: const EdgeInsets.only(bottom: 2.0),
        child: Text(text, style: const TextStyle(fontSize: 15, color: Colors.black87)),
      );
}
