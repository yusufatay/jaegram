import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:instagram_puan_app/providers/user_provider.dart';
import 'package:instagram_puan_app/screens/admin_panel_screen.dart';
import 'package:instagram_puan_app/screens/daily_reward_screen.dart';
import 'package:instagram_puan_app/screens/email_verification_screen.dart';
import 'package:instagram_puan_app/screens/login_screen.dart';
import 'package:instagram_puan_app/screens/main_screen.dart';
import 'package:instagram_puan_app/screens/notifications_screen.dart';
import 'package:instagram_puan_app/screens/order_screen.dart';
import 'package:instagram_puan_app/screens/profile_screen.dart';
import 'package:instagram_puan_app/screens/settings_screen_new.dart';
import 'package:instagram_puan_app/screens/splash_screen.dart';
import 'package:instagram_puan_app/screens/statistics_screen.dart'; // Oluşturulacak
import 'package:instagram_puan_app/screens/task_screen.dart';
import 'package:instagram_puan_app/screens/two_factor_auth_screen.dart';
import 'package:instagram_puan_app/screens/instagram_integration_screen.dart';
import 'package:instagram_puan_app/screens/instagram_integration_dashboard.dart';
import 'package:instagram_puan_app/screens/leaderboard_screen.dart';
import 'package:instagram_puan_app/screens/diamond_transfer_screen.dart';
import 'package:instagram_puan_app/screens/badges_screen.dart';
import 'package:instagram_puan_app/screens/edit_profile_screen.dart';
import 'package:instagram_puan_app/screens/change_password_screen.dart';
import 'package:instagram_puan_app/screens/help_screen.dart';
import 'package:instagram_puan_app/screens/kvkk_screen.dart';
import 'package:instagram_puan_app/screens/instagram_profile_screen.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'root');

final routerProvider = Provider<GoRouter>((ref) {
  final userAsync = ref.watch(userProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/', // SplashScreen ile başla
    debugLogDiagnostics: true, // Enable debug logging for router
    redirect: (BuildContext context, GoRouterState state) {
      // Handle navigation logic
      final bool loggedIn = userAsync.hasValue && userAsync.value != null;
      final bool isAdmin = loggedIn && userAsync.value?.isAdminPlatform == true;
      final bool loggingIn = state.matchedLocation == '/login';
      final bool splashing = state.matchedLocation == '/';

      if (splashing) return null; // Splash ekranı her zaman gösterilir

      // Giriş yapılmadıysa ve login sayfasında değilse splash'e (o da login'e yönlendirecek)
      if (!loggedIn && !loggingIn) return '/'; 
      
      // Admin kullanıcı giriş yapmışsa ve admin panelinde değilse, admin paneline yönlendir
      if (isAdmin && loggingIn) return '/admin';
      
      // Normal kullanıcı giriş yapmışsa ve login sayfasındaysa ana ekrana (ilk sekme olan tasks)
      if (loggedIn && loggingIn && !isAdmin) return '/main/tasks';
      
      return null; // Diğer durumlarda yönlendirme yok
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      // StatefulShellRoute for main app navigation with BottomNavigationBar
      StatefulShellRoute.indexedStack(
        builder: (BuildContext context, GoRouterState state, StatefulNavigationShell navigationShell) {
          // Pass the navigationShell to the MainScreen.
          return MainScreen(navigationShell: navigationShell);
        },
        branches: <StatefulShellBranch>[
          // Branch for the 'Tasks' tab
          StatefulShellBranch(
            routes: <RouteBase>[
              GoRoute(
                path: '/main/tasks',
                pageBuilder: (context, state) => const NoTransitionPage(child: TaskScreen()),
              ),
            ],
          ),
          // Branch for the 'Orders' tab
          StatefulShellBranch(
            routes: <RouteBase>[
              GoRoute(
                path: '/main/orders',
                pageBuilder: (context, state) => const NoTransitionPage(child: OrderScreen()),
              ),
            ],
          ),
          // Branch for the 'Leaderboard' tab
          StatefulShellBranch(
            routes: <RouteBase>[
              GoRoute(
                path: '/main/leaderboard',
                pageBuilder: (context, state) => const NoTransitionPage(child: LeaderboardScreen()),
              ),
            ],
          ),
          // Branch for the 'Statistics' tab
          StatefulShellBranch(
            routes: <RouteBase>[
              GoRoute(
                path: '/main/statistics',
                pageBuilder: (context, state) => const NoTransitionPage(child: StatisticsScreen()),
              ),
            ],
          ),
          // Branch for the 'Profile' tab
          StatefulShellBranch(
            routes: <RouteBase>[
              GoRoute(
                path: '/main/profile',
                pageBuilder: (context, state) => const NoTransitionPage(child: ProfileScreen()),
              ),
            ],
          ),
        ],
      ),
      // ShellRoute dışındaki diğer ekranlar (Modal veya tam sayfa)
      GoRoute(
        path: '/notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),
      GoRoute(
        path: '/statistics',
        builder: (context, state) => const StatisticsScreen(), // Oluşturulacak
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreenNew(),
      ),
      GoRoute(
        path: '/daily-reward',
        builder: (context, state) => const DailyRewardScreen(),
      ),
      GoRoute(
        path: '/email-verification',
        builder: (context, state) => const EmailVerificationScreen(),
      ),
      GoRoute(
        path: '/two-factor-auth',
        builder: (context, state) => const TwoFactorAuthScreen(),
      ),
      GoRoute(
        path: '/instagram-integration',
        builder: (context, state) => const InstagramIntegrationScreen(),
      ),
      GoRoute(
        path: '/instagram-integration-dashboard',
        builder: (context, state) => const InstagramIntegrationDashboard(),
      ),
      GoRoute(
        path: '/leaderboard',
        builder: (context, state) => const LeaderboardScreen(),
      ),
      GoRoute(
        path: '/diamond-transfer',
        builder: (context, state) => const DiamondTransferScreen(),
      ),
      GoRoute(
        path: '/badges',
        builder: (context, state) => const BadgesScreen(),
      ),
      GoRoute(
        path: '/admin',
        builder: (context, state) {
          // Check admin access
          if (userAsync.hasValue && userAsync.value?.isAdminPlatform == true) {
            return const AdminPanelScreen();
          }
          
          // For non-admin users, redirect to login
          WidgetsBinding.instance.addPostFrameCallback((_) {
            GoRouter.of(context).go('/login');
          });
          
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            )
          ); 
        },
      ),
      GoRoute(
        path: '/order',
        builder: (context, state) => const OrderScreen(),
      ),
      // Add routes for missing settings pages
      GoRoute(
        path: '/edit-profile',
        builder: (context, state) => const EditProfileScreen(),
      ),
      GoRoute(
        path: '/change-password',
        builder: (context, state) => const ChangePasswordScreen(),
      ),
      GoRoute(
        path: '/help',
        builder: (context, state) => const HelpScreen(),
      ),
      GoRoute(
        path: '/kvkk',
        builder: (context, state) => const KvkkScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const InstagramProfileScreen(),
      ),
    ],
  );
});