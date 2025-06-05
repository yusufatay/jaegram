// Flutter widget testleri için şablon dosyadır.
// Buraya ana ekran, giriş ekranı ve diğer widgetlar için testler ileride eklenecektir.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('Test widget creation', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: Center(
              child: Text('Test App'),
            ),
          ),
        ),
      ),
    );
    
    expect(find.text('Test App'), findsOneWidget);
  });
}
