import 'package:flutter/material.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart'; // Yerelleştirme

class ErrorDisplay extends StatelessWidget {
  final Object error;
  final StackTrace? stackTrace;
  final VoidCallback? onRetry;

  const ErrorDisplay({
    super.key,
    required this.error,
    this.stackTrace,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, color: Colors.red[700], size: 60),
            const SizedBox(height: 20),
            Text(
              localizations.genericErrorEncountered,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.red[700]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            SelectableText(
              error.toString(),
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            if (stackTrace != null) ...[
              const SizedBox(height: 8),
              ExpansionTile(
                title: Text(localizations.details, style: TextStyle(color: Colors.grey[600])),
                children: [
                  SingleChildScrollView(
                    child: SelectableText(
                      stackTrace.toString(),
                      style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                    ),
                  )
                ],
              ),
            ],
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: Text(localizations.retry),
                onPressed: onRetry,
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red[100]),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 