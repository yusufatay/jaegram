import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:app_links/app_links.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'providers/notification_provider.dart';
import 'providers/badge_provider.dart';
import 'package:instagram_puan_app/providers/theme_provider.dart';
import 'package:instagram_puan_app/themes/app_theme.dart';
import 'package:instagram_puan_app/router.dart';
import 'dart:async';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'utils/safe_keyboard_handler.dart' as safe_keyboard;
import 'firebase_options.dart';

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
final GlobalKey<NavigatorState> rootNavigatorKey = GlobalKey<NavigatorState>();

Future<void> _initializePlatformSpecifics() async {
  if (kIsWeb ||
      defaultTargetPlatform == TargetPlatform.android ||
      defaultTargetPlatform == TargetPlatform.iOS) {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  }
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Enhanced error handling for Flutter framework warnings
  FlutterError.onError = (FlutterErrorDetails details) {
    final exceptionStr = details.exception.toString();
    
    // Suppress keyboard event errors (primarily on Linux desktop)
    if (exceptionStr.contains('KeyDownEvent') && 
        exceptionStr.contains('already pressed')) {
      developer.log('Suppressed keyboard event error', name: 'KeyboardHandler');
      return;
    }
    
    // Suppress JSON framework response errors (all platforms)
    if (exceptionStr.contains('Message is not valid JSON') ||
        exceptionStr.contains('Unable to retrieve framework response') ||
        exceptionStr.contains('framework response')) {
      developer.log('Suppressed framework JSON error', name: 'FrameworkHandler');
      return;
    }
    
    // Suppress other common framework warnings
    if (exceptionStr.contains('RenderFlex overflowed') ||
        exceptionStr.contains('A RenderFlex overflowed')) {
      developer.log('Suppressed layout overflow warning', name: 'LayoutHandler');
      return;
    }
    
    // For other errors, use default handling
    FlutterError.presentError(details);
  };
  
  // Handle async errors (including platform message errors)
  PlatformDispatcher.instance.onError = (error, stack) {
    final errorStr = error.toString();
    
    // Suppress JSON framework response errors in async context
    if (errorStr.contains('Message is not valid JSON') ||
        errorStr.contains('Unable to retrieve framework response') ||
        errorStr.contains('framework response') ||
        errorStr.contains('PlatformException')) {
      developer.log('Suppressed async framework error: $errorStr', name: 'AsyncFrameworkHandler');
      return true; // Mark as handled
    }
    
    // For other async errors, let them bubble up
    return false;
  };
  
  await _initializePlatformSpecifics();

  final container = ProviderContainer();
  await _initLocalNotifications(container);
  // await _initFCM(container); // Bildirim özelliğini devre dışı bırakıyoruz
  runApp(
    UncontrolledProviderScope(
      container: container,
      child: const JAEGramApp(), 
    ),
  );
}

Future<void> _initLocalNotifications(ProviderContainer container) async {
  const initializationSettings = InitializationSettings(
    android: AndroidInitializationSettings('@mipmap/ic_launcher'),
    iOS: DarwinInitializationSettings(),
    macOS: DarwinInitializationSettings(),
    linux: LinuxInitializationSettings(
      defaultActionName: 'Open notification',
      defaultIcon: null, // Set to null if you do not have a Linux icon asset
    ),
  );
  await flutterLocalNotificationsPlugin.initialize(initializationSettings,
    onDidReceiveNotificationResponse: (details) {
      final route = details.payload;
      if (route != null && route.isNotEmpty) {
        try {
          final router = container.read(routerProvider);
          router.go(route);
        } catch (e) {
          developer.log("Local notification navigation error: $e", name: 'LocalNotifications');
        }
      }
    },
  );
}

Future<void> _initFCM(ProviderContainer container) async {
  if (kIsWeb ||
      defaultTargetPlatform == TargetPlatform.android ||
      defaultTargetPlatform == TargetPlatform.iOS) {
    await Firebase.initializeApp(); // Defensive: ensure initialized
    final messaging = FirebaseMessaging.instance;
    NotificationSettings settings = await messaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );
    developer.log('User granted permission: ${settings.authorizationStatus}', name: 'FCM');
    FirebaseMessaging.onMessage.listen((RemoteMessage message) async {
      developer.log('Got a message whilst in the foreground!', name: 'FCM');
      developer.log('Message data: ${message.data}', name: 'FCM');
      final notification = message.notification;
      if (notification != null) {
        developer.log('Message also contained a notification: ${notification.title}, ${notification.body}', name: 'FCM');
        await flutterLocalNotificationsPlugin.show(
          notification.hashCode,
          notification.title,
          notification.body,
          const NotificationDetails(
            android: AndroidNotificationDetails(
              'default_channel_id',
              'General Notifications',
              channelDescription: 'Default channel for app notifications',
              importance: Importance.max,
              priority: Priority.high,
              ticker: 'ticker',
            ),
            iOS: DarwinNotificationDetails(),
          ),
          payload: message.data['route'] as String?,
        );
        container.read(notificationProvider.notifier).fetchNotifications();
      }
    });
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      developer.log('Message clicked!', name: 'FCM');
      final route = message.data['route'] as String?;
      if (route != null && route.isNotEmpty) {
        try {
          final router = container.read(routerProvider);
          router.go(route);
        } catch (e) {
          developer.log("FCM onMessageOpenedApp navigation error: $e", name: 'FCM');
        }
      }
    });
  }
  // On other platforms, do nothing
}

class JAEGramApp extends HookConsumerWidget {
  const JAEGramApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    useEffect(() {
      // Initialize AppLinks
      final appLinks = AppLinks();

      // Subscribe to link stream
      final sub = appLinks.uriLinkStream.listen(
        (Uri? uri) {
          if (uri != null) {
            developer.log('Received deep link: $uri', name: 'InstagramPuanApp.onLink');
            // Navigate using the router provider
            // Using ref.read as this is an action triggered by an event stream
            ref.read(routerProvider).go(uri.toString());
          }
        },
        onError: (Object error, StackTrace stackTrace) {
          developer.log(
            'Deep link error', 
            name: 'InstagramPuanApp.onLinkError', 
            error: error, 
            stackTrace: stackTrace,
          );
        },
      );

      // Cleanup subscription on dispose
      return () {
        sub.cancel();
      };
    }, const []);

    final goRouter = ref.watch(routerProvider);
    final themeMode = ref.watch(themeProvider);
    final locale = ref.watch(localeProvider);
    
    return safe_keyboard.SafeKeyboardHandler(
      child: MaterialApp.router(
        title: 'JAEGram',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: themeMode,
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: AppLocalizations.supportedLocales,
        locale: locale,
        routerConfig: goRouter,
      ),
    );
  }
}
