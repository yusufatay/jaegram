import 'package:flutter/material.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Yardım & Sıkça Sorulan Sorular'),
        backgroundColor: Colors.indigo.shade400,
        elevation: 0,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF43cea2), Color(0xFF185a9d)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const Icon(Icons.help_outline, size: 80, color: Colors.white70),
            const SizedBox(height: 24),
            Text(
              'Sıkça Sorulan Sorular',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            _faqTile(
              'JAEGram Platformu nedir?',
              'JAEGram, Instagram hesabını yönetmeni, görevlerle puan kazanmanı ve ödüller almanı sağlayan sosyal bir platformdur.',
            ),
            _faqTile(
              'Profilimi nasıl güncellerim?',
              'Profilini güncellemek için Ayarlar > Profilini Düzenle rehberini takip edebilirsin.',
            ),
            _faqTile(
              'Şifremi unuttum, ne yapmalıyım?',
              'Giriş ekranında "Şifremi Unuttum" seçeneğini kullanarak yeni şifre talep edebilirsin.',
            ),
            _faqTile(
              'Bildirimleri nasıl açıp kapatabilirim?',
              'Ayarlar > Bildirimler bölümünden istediğin bildirimleri açıp kapatabilirsin.',
            ),
            _faqTile(
              'Destek ekibine nasıl ulaşabilirim?',
              'Uygulama içindeki yardım bölümünden veya destek mail adresimizden bize ulaşabilirsin.',
            ),
            _faqTile(
              'Instagram hesabımı nasıl bağlarım?',
              'Profil > Ayarlar > Instagram Entegrasyonu kısmından Instagram hesabınızı güvenli bir şekilde bağlayabilirsiniz.',
            ),
            _faqTile(
              'Elmas nasıl kazanırım?',
              'Görevleri tamamlayarak, günlük ödülleri toplayarak ve Instagram hesabınızı aktif tutarak elmas kazanabilirsiniz.',
            ),
            _faqTile(
              'Rozetleri nasıl kazanırım?',
              'Belirli görevleri tamamlayarak, seviye atlayarak ve özel etkinliklere katılarak çeşitli rozetler kazanabilirsiniz.',
            ),
            _faqTile(
              'Hesabım neden kilitlendi?',
              'Hesap güvenliği için kurallara aykırı davranışlar tespit edilirse hesaplar geçici olarak kilitlenebilir. Destek ekibimizle iletişime geçin.',
            ),
            _faqTile(
              'Verilerim güvende mi?',
              'Evet, tüm verileriniz şifrelenerek korunur ve KVKK uyumlu olarak işlenir. Gizlilik politikamızı inceleyebilirsiniz.',
            ),
            _faqTile(
              'Uygulama ücretsiz mi?',
              'JAEGram temel özellikleri tamamen ücretsizdir. Premium özellikler için isteğe bağlı içi ödemeler bulunmaktadır.',
            ),
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.indigo.shade50,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.indigo.shade200, width: 1.5),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: Colors.indigo, size: 32),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      'Sorunun cevabını bulamadın mı? Bizimle iletişime geç, sana yardımcı olalım! 💬',
                      style: TextStyle(color: Colors.indigo.shade900, fontSize: 16),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 40),
            Center(
              child: Text(
                'JAEGram Ekibi 💙',
                style: TextStyle(
                  color: Colors.indigo.shade700,
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

  Widget _faqTile(String question, String answer) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10.0),
      child: Card(
        color: Colors.white.withOpacity(0.97),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        elevation: 4,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(question, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 6),
              Text(answer, style: const TextStyle(fontSize: 15, color: Colors.black87)),
            ],
          ),
        ),
      ),
    );
  }
}
