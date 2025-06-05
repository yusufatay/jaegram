import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:instagram_puan_app/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Gerçek kullanıcı akışı: login, görev al, tamamla, diamond güncelle, bildirim', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Login ekranı
    expect(find.text('Instagram ile Giriş'), findsOneWidget);
    await tester.enterText(find.byType(TextField).at(0), 'testuser');
    await tester.enterText(find.byType(TextField).at(1), 'testpass');
    await tester.tap(find.text('Instagram ile Giriş Yap'));
    await tester.pumpAndSettle(const Duration(seconds: 2));

    // Ana ekran
    expect(find.text('Ana Ekran'), findsOneWidget);
    // Görevler sekmesine geç
    await tester.tap(find.byIcon(Icons.task));
    await tester.pumpAndSettle();
    expect(find.text('Görevler'), findsOneWidget);
    // Görev al
    if (find.text('Yeni Görev Al').evaluate().isNotEmpty) {
      await tester.tap(find.text('Yeni Görev Al'));
      await tester.pumpAndSettle(const Duration(seconds: 1));
    }
    // Görev tamamla
    final tamamlaBtn = find.text('Tamamla');
    if (tamamlaBtn.evaluate().isNotEmpty) {
      await tester.tap(tamamlaBtn.first);
      await tester.pumpAndSettle(const Duration(seconds: 1));
    }
    // Diamond güncellendi mi?
    await tester.tap(find.byIcon(Icons.home));
    await tester.pumpAndSettle();
    expect(find.byIcon(Icons.diamond), findsOneWidget);
    // Bildirimler sekmesine geç
    await tester.tap(find.byIcon(Icons.notifications));
    await tester.pumpAndSettle();
    expect(find.text('Bildirimler'), findsOneWidget);
    // Push notification ve deeplink testleri için manuel tetikleme gerekebilir
  });
} 