class ApiConstants {
  static const String baseUrl = 'https://jaegram-backend.up.railway.app';
  static const String wsBaseUrl = 'wss://jaegram-backend.up.railway.app';
  
  // Authentication endpoints
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String refreshToken = '/auth/refresh';
  
  // User endpoints
  static const String profile = '/user/profile';
  static const String updateProfile = '/user/profile';
  static const String statistics = '/user/statistics';
  
  // Task endpoints
  static const String tasks = '/tasks';
  static const String completeTasks = '/tasks/complete';
  static const String userTasks = '/tasks/user';
  
  // Order endpoints
  static const String orders = '/orders';
  static const String createOrder = '/orders/create';
  static const String orderHistory = '/orders/history';
  
  // Coin endpoints
  static const String coinBalance = '/coins/balance';
  static const String coinHistory = '/coins/history';
  static const String dailyReward = '/coins/daily-reward';
  
  // Notification endpoints
  static const String notifications = '/notifications';
  static const String markAsRead = '/notifications/mark-read';
  static const String notificationSettings = '/notifications/settings';
  
  // Instagram endpoints
  static const String instagramConnect = '/instagram/connect';
  static const String instagramProfile = '/instagram/profile';
  static const String instagramPosts = '/instagram/posts';
  
  // Social endpoints
  static const String leaderboard = '/social/leaderboard';
  static const String badges = '/social/badges';
  static const String referrals = '/social/referrals';
  
  // Education endpoints
  static const String educationModules = '/education/modules';
  static const String educationProgress = '/education/progress';
  
  // GDPR endpoints
  static const String gdprRequest = '/gdpr/request';
  static const String dataExport = '/gdpr/export';
  
  // Mental health endpoints
  static const String mentalHealthCheck = '/mental-health/check';
  static const String mentalHealthLog = '/mental-health/log';
  
  // WebSocket endpoints
  static const String wsNotifications = '/ws/notifications';
  
  // Headers
  static Map<String, String> headers(String? token) {
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }
  
  // WebSocket URL helper
  static String getWebSocketUrl(String endpoint, {String? token}) {
    String url = '$wsBaseUrl$endpoint';
    if (token != null) {
      url += '?token=$token';
    }
    return url;
  }
  
  // Error codes
  static const int unauthorized = 401;
  static const int forbidden = 403;
  static const int notFound = 404;
  static const int serverError = 500;
}
