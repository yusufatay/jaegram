import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:instagram_puan_app/providers/user_provider.dart'; // Diamond bilgisi için
import 'package:instagram_puan_app/generated/app_localizations.dart'; // Yerelleştirme

class CommonAppBar extends ConsumerWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  const CommonAppBar({super.key, required this.title, this.actions});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userProvider);
    final localizations = AppLocalizations.of(context)!;

    return AppBar(
      title: Text(title),
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 8.0),
          child: userAsync.when(
            data: (user) => Row(
              children: [
                Icon(Icons.diamond, color: Colors.blue[700]),
                const SizedBox(width: 4),
                Text(user?.diamondBalance?.toString() ?? '0', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              ],
            ),
            loading: () => const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
            error: (e,st) => Tooltip(message: localizations.errorFetchingCoin, child: const Icon(Icons.error_outline, color: Colors.red)),
          ),
        ),
        if (actions != null) ...actions!,
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
} 