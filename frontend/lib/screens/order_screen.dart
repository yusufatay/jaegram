// Sipariş ekranı: Riverpod orderProvider ile sipariş oluşturma formu, loading/error state, SelectableText.rich ile hata, Türkçe ve modern UI.

import 'package:flutter/material.dart';
import '../providers/order_provider.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:instagram_puan_app/themes/app_theme.dart';
import 'package:instagram_puan_app/widgets/gradient_button.dart';
import 'package:go_router/go_router.dart';

// TODO: OrderProvider ve OrderService oluşturulacak
// TODO: OrderModel oluşturulacak

class OrderScreen extends HookConsumerWidget {
  const OrderScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final localizations = AppLocalizations.of(context)!;
    final orderAsync = ref.watch(orderProvider);
    final postUrlController = useTextEditingController();
    final targetCountController = useTextEditingController();
    final commentTextController = useTextEditingController();

    final orderType = useState<String>('like');

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.myOrders),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Section
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: AppTheme.instagramGradient,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.shopping_cart,
                    size: 48,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Yeni Sipariş Oluştur',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Instagram hesabınız için hızlı ve güvenilir sosyal medya hizmetleri',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.white70,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Order Form
            Text(
              'Sipariş Detayları',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            // Post URL Input
            _buildFormField(
              label: 'Instagram Gönderi Linki',
              controller: postUrlController,
              hint: 'https://instagram.com/p/...',
              icon: Icons.link,
              validator: (value) {
                if (value?.isEmpty ?? true) return 'Gönderi linki zorunludur';
                if (!value!.contains('instagram.com')) return 'Geçerli bir Instagram linki girin';
                return null;
              },
            ),
            const SizedBox(height: 20),

            // Order Type Selection
            Text(
              'Sipariş Türü',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildOrderTypeSelector(orderType),
            const SizedBox(height: 20),

            // Target Count Input
            _buildFormField(
              label: 'Hedef Miktar',
              controller: targetCountController,
              hint: 'Örn: 100',
              icon: Icons.numbers,
              keyboardType: TextInputType.number,
              validator: (value) {
                if (value?.isEmpty ?? true) return 'Hedef miktar zorunludur';
                final count = int.tryParse(value!);
                if (count == null || count <= 0) return 'Geçerli bir sayı girin';
                return null;
              },
            ),
            const SizedBox(height: 20),

            // Comment Text (for comment orders)
            if (orderType.value == 'comment') ...[
              _buildFormField(
                label: 'Yorum Metinleri',
                controller: commentTextController,
                hint: 'Her satıra bir yorum yazın...',
                icon: Icons.comment,
                maxLines: 4,
                validator: (value) {
                  if (orderType.value == 'comment' && (value?.isEmpty ?? true)) {
                    return 'Yorum metni zorunludur';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
            ],

            // Price Estimation
            _buildPriceEstimation(orderType.value, targetCountController.text),
            const SizedBox(height: 32),

            // Submit Button
            SizedBox(
              width: double.infinity,
              child: orderAsync.isLoading
                  ? Container(
                      height: 56,
                      decoration: BoxDecoration(
                        color: Colors.grey[300],
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Center(
                        child: CircularProgressIndicator(),
                      ),
                    )
                  : GradientButton(
                      text: 'Sipariş Oluştur',
                      onPressed: () => _submitOrder(
                        context,
                        ref,
                        postUrlController.text.trim(),
                        orderType.value,
                        int.tryParse(targetCountController.text.trim()) ?? 0,
                        commentTextController.text.trim(),
                      ),
                      icon: Icons.add_shopping_cart,
                    ),
            ),

            if (orderAsync.hasError) ...[
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red[700]),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Hata: ${orderAsync.error}',
                        style: TextStyle(color: Colors.red[700]),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 32),

            // Recent Orders Section
            _buildRecentOrdersSection(context, ref),
          ],
        ),
      ),
    );
  }

  Widget _buildFormField({
    required String label,
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    TextInputType? keyboardType,
    int maxLines = 1,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          maxLines: maxLines,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: AppTheme.instagramGradient.colors.first),
            ),
            filled: true,
            fillColor: Colors.grey[50],
          ),
        ),
      ],
    );
  }

  Widget _buildOrderTypeSelector(ValueNotifier<String> orderType) {
    final types = [
      {'value': 'like', 'label': 'Beğeni', 'icon': Icons.favorite, 'color': Colors.red},
      {'value': 'follow', 'label': 'Takip', 'icon': Icons.person_add, 'color': Colors.blue},
      {'value': 'comment', 'label': 'Yorum', 'icon': Icons.comment, 'color': Colors.green},
    ];

    return Row(
      children: types.map((type) {
        final isSelected = orderType.value == type['value'];
        return Expanded(
          child: GestureDetector(
            onTap: () => orderType.value = type['value'] as String,
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 4),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isSelected 
                  ? (type['color'] as Color).withValues(alpha: 0.1)
                  : Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected 
                    ? (type['color'] as Color)
                    : Colors.grey[300]!,
                  width: isSelected ? 2 : 1,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    type['icon'] as IconData,
                    color: isSelected 
                      ? (type['color'] as Color)
                      : Colors.grey[600],
                    size: 32,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    type['label'] as String,
                    style: TextStyle(
                      color: isSelected 
                        ? (type['color'] as Color)
                        : Colors.grey[600],
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildPriceEstimation(String orderType, String targetCountText) {
    final targetCount = int.tryParse(targetCountText) ?? 0;
    final pricePerUnit = orderType == 'like' ? 0.1 : orderType == 'follow' ? 0.5 : 1.0;
    final totalPrice = (targetCount * pricePerUnit).toInt();

    if (targetCount <= 0) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Tahmini Maliyet',
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                ),
              ),
              Text(
                '$totalPrice ⭐',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              '$targetCount adet',
              style: const TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentOrdersSection(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Son Siparişler',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () {
                // Navigate to orders history
              },
              child: const Text('Tümünü Gör'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        // TODO: Add recent orders list
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(Icons.history, size: 48, color: Colors.grey[400]),
              const SizedBox(height: 12),
              Text(
                'Henüz sipariş vermediniz',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _submitOrder(
    BuildContext context,
    WidgetRef ref,
    String postUrl,
    String orderType,
    int targetCount,
    String commentText, // Renamed from comment to avoid conflict
  ) async {
    // Validation
    if (postUrl.isEmpty || targetCount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Gönderi linki ve hedef miktar zorunludur'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (!postUrl.contains('instagram.com')) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Geçerli bir Instagram linki girin'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (orderType == 'comment' && commentText.isEmpty) { // Use commentText
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Yorum metni zorunludur'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    try {
      await ref.read(orderProvider.notifier).createOrder(
        postUrl: postUrl,
        orderType: orderType,
        targetCount: targetCount,
        commentText: commentText.isNotEmpty ? commentText : null, // Corrected parameter name
      );

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Sipariş başarıyla oluşturuldu!'),
          backgroundColor: Colors.green,
        ),
      );

      // Clear form
      // Controllers will be cleared automatically due to rebuild
    } catch (e) {
      // Handle Instagram connection specific errors more gracefully
      String errorMessage = 'Sipariş oluşturulurken hata: $e';
      bool showInstagramConnectAction = false;
      
      if (e.toString().contains('Instagram hesabınızın bağlı olması') || 
          e.toString().contains('Instagram ile giriş yapın')) {
        errorMessage = 'Instagram hesabınızın bağlanması gerekiyor';
        showInstagramConnectAction = true;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.error_outline, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(child: Text(errorMessage)),
              if (showInstagramConnectAction) ...[
                const SizedBox(width: 8),
                TextButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).hideCurrentSnackBar();
                    context.push('/profile'); // Navigate to profile to connect Instagram
                  },
                  child: const Text(
                    'Bağla',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ],
          ),
          backgroundColor: Colors.red,
          duration: showInstagramConnectAction ? const Duration(seconds: 6) : const Duration(seconds: 4),
        ),
      );
    }
  }
}
