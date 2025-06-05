// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'JAEGram';

  @override
  String get switchToLight => 'Switch to Light Mode';

  @override
  String get switchToDark => 'Switch to Dark Mode';

  @override
  String get followers => 'Followers';

  @override
  String get following => 'Following';

  @override
  String get systemStats => 'System Statistics';

  @override
  String get newLogArrived => 'New log arrived!';

  @override
  String get webSocketConnectionError =>
      'WebSocket connection error. Please try again later.';

  @override
  String expiresAt(Object dateTime) {
    return 'Expires at: $dateTime';
  }

  @override
  String get expiresAtLabel => 'Expires At';

  @override
  String get completedAtLabel => 'Completed At';

  @override
  String get completedAt => 'Completed At';

  @override
  String get id => 'ID';

  @override
  String get orderId => 'Order ID';

  @override
  String get assignedUser => 'Assigned User';

  @override
  String get status => 'Status';

  @override
  String get assignedAt => 'Assigned At';

  @override
  String get loginTitle => 'Login';

  @override
  String get mainScreenTitle => 'Dashboard';

  @override
  String get tasks => 'Tasks';

  @override
  String get orders => 'Orders';

  @override
  String get profile => 'Profile';

  @override
  String get notifications => 'Notifications';

  @override
  String get statistics => 'Statistics';

  @override
  String get admin => 'Admin';

  @override
  String get logout => 'Logout';

  @override
  String get coin => 'Diamond';

  @override
  String completedTasks(Object count) {
    return 'Completed Tasks';
  }

  @override
  String get completedTasksLabel => 'Completed Tasks';

  @override
  String get activeTasksLabel => 'Active Tasks';

  @override
  String get activeTasks => 'Active Tasks';

  @override
  String get settings => 'Settings';

  @override
  String get about => 'About';

  @override
  String get theme => 'Theme';

  @override
  String get darkTheme => 'Dark';

  @override
  String get lightTheme => 'Light';

  @override
  String get loginSubtitle => 'Access your account';

  @override
  String get username => 'Username';

  @override
  String get password => 'Password';

  @override
  String get loginButton => 'Login';

  @override
  String get twoFACode => '2FA Code';

  @override
  String get continueWith2FA => 'Continue with 2FA';

  @override
  String get usernamePasswordRequired => 'Username and password are required.';

  @override
  String get twoFARequired => '2FA code is required.';

  @override
  String get selectTab => 'Select a Tab';

  @override
  String get takeNewTask => 'Take New Task';

  @override
  String get taskTakenSuccess => 'Task taken successfully!';

  @override
  String taskTakeFailed(Object error) {
    return 'Failed to take task: $error';
  }

  @override
  String get noAssignedTask => 'No assigned task currently.';

  @override
  String get complete => 'Complete';

  @override
  String get noNotifications => 'No notifications yet.';

  @override
  String get markAsRead => 'Mark as Read';

  @override
  String get orderCreatedSuccessfully => 'Order created successfully!';

  @override
  String get orderCreationError => 'Failed to create order. Please try again.';

  @override
  String get myOrders => 'My Orders';

  @override
  String get createOrder => 'Create Order';

  @override
  String errorWithMessage(Object message) {
    return 'Error: $message';
  }

  @override
  String get settingsTitle => 'Settings';

  @override
  String get changeLanguage => 'Change Language';

  @override
  String get changeTheme => 'Change Theme';

  @override
  String get notificationSettings => 'Notification Settings';

  @override
  String get editProfile => 'Edit Profile';

  @override
  String get changePassword => 'Change Password';

  @override
  String get language => 'Language';

  @override
  String get save => 'Save';

  @override
  String get cancel => 'Cancel';

  @override
  String get dark => 'Dark';

  @override
  String get light => 'Light';

  @override
  String get system => 'System';

  @override
  String get selectLanguage => 'Select Language';

  @override
  String get selectTheme => 'Select Theme';

  @override
  String get profileUpdated => 'Profile updated successfully!';

  @override
  String get passwordChanged => 'Password changed successfully!';

  @override
  String get errorOccurred => 'An error occurred!';

  @override
  String get confirmLogout => 'Are you sure you want to logout?';

  @override
  String get yes => 'Yes';

  @override
  String get no => 'No';

  @override
  String get rollback => 'Rollback';

  @override
  String get rollbackSuccess => 'Rollback successful!';

  @override
  String get userBanned => 'User banned.';

  @override
  String get coinOperationSuccess => 'Diamond operation successful.';

  @override
  String get adminPanel => 'Admin Panel';

  @override
  String get instagramLogin => 'Login with Instagram';

  @override
  String get platformLogin => 'Platform Login';

  @override
  String get register => 'Register';

  @override
  String get fullName => 'Full Name';

  @override
  String get registerSuccess => 'Registration successful! Please login.';

  @override
  String registerFailed(Object error) {
    return 'Registration failed: $error';
  }

  @override
  String get requiredField => 'This field is required.';

  @override
  String minCommentLength(Object length) {
    return 'Comment must be at least $length characters.';
  }

  @override
  String maxCommentLength(Object length) {
    return 'Comment can be at most $length characters.';
  }

  @override
  String get orderTypeLike => 'Like';

  @override
  String get orderTypeFollow => 'Follow';

  @override
  String get orderTypeComment => 'Comment';

  @override
  String get postUrl => 'Post URL';

  @override
  String get targetCount => 'Target Count';

  @override
  String get commentText => 'Comment Text (for comment orders)';

  @override
  String get orderCreationSuccess => 'Order created successfully!';

  @override
  String orderCreationFailed(Object error) {
    return 'Order creation failed: $error';
  }

  @override
  String get taskStatusPending => 'Pending';

  @override
  String get taskStatusAssigned => 'Assigned';

  @override
  String get taskStatusCompleted => 'Completed';

  @override
  String get taskStatusExpired => 'Expired';

  @override
  String get taskStatusFailed => 'Failed';

  @override
  String get taskCompletedSuccess => 'Task completed successfully!';

  @override
  String taskCompletionFailed(Object error) {
    return 'Task completion failed: $error';
  }

  @override
  String get withdrawCoins => 'Withdraw Diamonds';

  @override
  String get amount => 'Amount';

  @override
  String minCompletedTasksRequired(Object count) {
    return 'You need to complete at least $count tasks to withdraw.';
  }

  @override
  String get insufficientCoins => 'Insufficient diamonds.';

  @override
  String get positiveAmountRequired => 'Amount must be positive.';

  @override
  String get withdrawalSuccess => 'Withdrawal successful!';

  @override
  String withdrawalFailed(Object error) {
    return 'Withdrawal failed: $error';
  }

  @override
  String get coins => 'Diamonds';

  @override
  String get activeTask => 'Active Task';

  @override
  String get appName => 'Instagram Score App';

  @override
  String get usernameHint => 'Enter your Instagram username';

  @override
  String get passwordHint => 'Enter your Instagram password';

  @override
  String get turkish => 'Turkish';

  @override
  String get english => 'English';

  @override
  String get error => 'Error';

  @override
  String get retry => 'Retry';

  @override
  String get genericErrorEncountered => 'An error occurred.';

  @override
  String get details => 'Details';

  @override
  String get systemDefault => 'System Default';

  @override
  String get appSettings => 'App Settings';

  @override
  String get users => 'Users';

  @override
  String get coinTransactions => 'Diamond Transactions';

  @override
  String get logs => 'Logs';

  @override
  String get refresh => 'Refresh';

  @override
  String get searchInUsers => 'Search in users (ID, username, name, email)';

  @override
  String get searchInOrders => 'Search in orders (ID, user ID, post URL, type)';

  @override
  String get searchInTasks => 'Search in tasks (ID, order ID, user ID, status)';

  @override
  String get searchInCoinTransactions =>
      'Search in diamond transactions (ID, user ID, type, description)';

  @override
  String get searchInLogs =>
      'Search in logs (ID, admin, target, action, description)';

  @override
  String get exportCsv => 'Export to CSV';

  @override
  String get exportCsvShort => 'Export';

  @override
  String get all => 'All Time';

  @override
  String get admins => 'Admins';

  @override
  String get bannedUsers => 'Banned Users';

  @override
  String get platformAdmin => 'Platform Admin?';

  @override
  String get banned => 'Banned?';

  @override
  String get actions => 'Actions';

  @override
  String userActionsFor(Object username) {
    return 'Actions for $username';
  }

  @override
  String get banUser => 'Ban User';

  @override
  String get unbanUser => 'Unban User';

  @override
  String get confirmBan => 'Confirm Ban';

  @override
  String get confirmUnban => 'Confirm Unban';

  @override
  String areYouSureBan(Object banUnban, Object username) {
    return 'Are you sure you want to $banUnban user $username?';
  }

  @override
  String get banVerb => 'ban';

  @override
  String get unbanVerb => 'unban';

  @override
  String get userUnbanned => 'User unbanned.';

  @override
  String get addRemoveCoin => 'Add/Remove Diamond';

  @override
  String addRemoveCoinFor(Object username) {
    return 'Add/Remove diamond for $username';
  }

  @override
  String get coinAmount => 'Diamond Amount';

  @override
  String get coinAmountInfo => 'Coin Amount (negative to remove)';

  @override
  String get confirm => 'Confirm';

  @override
  String get promoteToAdmin => 'Promote to Admin';

  @override
  String get demoteFromAdmin => 'Demote from Admin';

  @override
  String get confirmPromote => 'Confirm Promotion';

  @override
  String get confirmDemote => 'Confirm Demotion';

  @override
  String areYouSureAdmin(Object promoteDemote, Object username) {
    return 'Are you sure you want to $promoteDemote user $username as a platform admin?';
  }

  @override
  String get promoteVerb => 'promote';

  @override
  String get demoteVerb => 'demote';

  @override
  String get userPromoted => 'User promoted to admin.';

  @override
  String get userDemoted => 'User demoted from admin.';

  @override
  String get logDetails => 'Log Details';

  @override
  String get date => 'Date';

  @override
  String get action => 'Action';

  @override
  String get adminUsername => 'Admin Username';

  @override
  String get targetUser => 'Target User';

  @override
  String get targetUsername => 'Target Username';

  @override
  String get description => 'Description';

  @override
  String get closeButton => 'Close';

  @override
  String get confirmRollback => 'Confirm Rollback';

  @override
  String areYouSureRollback(Object actionDescription) {
    return 'Are you sure you want to rollback \"$actionDescription\"? This cannot be undone.';
  }

  @override
  String get cannotRollback => 'This action cannot be rolled back.';

  @override
  String get thisAction => 'this action';

  @override
  String get noDataToExport => 'No data to export.';

  @override
  String get csvDownloadStarting => 'CSV download starting...';

  @override
  String get csvExportNotSupportedOnMobileYet =>
      'CSV export is not supported on this platform yet.';

  @override
  String get user => 'User';

  @override
  String get orderType => 'Order Type';

  @override
  String get completedCount => 'Completed Count';

  @override
  String get createdAt => 'Created At';

  @override
  String get userId => 'User ID';

  @override
  String get transactionType => 'Transaction Type';

  @override
  String get balanceAfter => 'Balance After';

  @override
  String get logActionUserBan => 'User Ban';

  @override
  String get logActionUserUnban => 'User Unban';

  @override
  String get logActionCoinAdjust => 'Coin Adjustment';

  @override
  String get logActionAdminPromote => 'Admin Promotion';

  @override
  String get logActionAdminDemote => 'Admin Demotion';

  @override
  String get errorFetchingCoin => 'Error fetching diamond balance';

  @override
  String get tasksTab => 'Tasks';

  @override
  String get ordersTab => 'Orders';

  @override
  String get profileTab => 'Profile';

  @override
  String get orderFilterStatusAll => 'All';

  @override
  String get orderFilterStatusPending => 'Pending';

  @override
  String get orderFilterStatusActive => 'Active';

  @override
  String get orderFilterStatusCompleted => 'Completed';

  @override
  String get orderFilterStatusFailed => 'Failed';

  @override
  String get orderFilterStatusCancelled => 'Cancelled';

  @override
  String get taskFilterStatusAll => 'All';

  @override
  String get taskFilterStatusPending => 'Pending';

  @override
  String get taskFilterStatusAssigned => 'Assigned';

  @override
  String get taskFilterStatusCompleted => 'Completed';

  @override
  String get taskFilterStatusFailed => 'Failed';

  @override
  String get taskFilterStatusExpired => 'Expired';

  @override
  String get coinTransactionFilterAll => 'All';

  @override
  String get coinTransactionFilterEarn => 'Earn';

  @override
  String get coinTransactionFilterSpend => 'Spend';

  @override
  String get coinTransactionFilterWithdraw => 'Withdrawal';

  @override
  String get coinTransactionFilterAdminAdd => 'Admin Add';

  @override
  String get coinTransactionFilterAdminRemove => 'Admin Remove';

  @override
  String get adminLogFilterAll => 'All';

  @override
  String get badges => 'Badges';

  @override
  String get viewAll => 'View All';

  @override
  String get noBadgesEarned => 'No badges earned yet';

  @override
  String get noBadgesAvailable => 'No badges available';

  @override
  String get earnedOn => 'Earned On';

  @override
  String get close => 'Close';

  @override
  String get badgeStats => 'Badge Statistics';

  @override
  String get totalBadges => 'Total Badges';

  @override
  String get categories => 'Categories';

  @override
  String get earnedBadges => 'Earned Badges';

  @override
  String get allBadges => 'All Badges';

  @override
  String get progressStatus => 'Progress Status';

  @override
  String get badgeEarned => 'Badge Earned!';

  @override
  String get congratulations => 'Congratulations!';

  @override
  String get youEarnedBadge => 'You earned the badge:';

  @override
  String get instagramIntegration => 'Instagram Integration';

  @override
  String get instagramDashboard => 'Instagram Dashboard';

  @override
  String get connectInstagram => 'Connect Instagram';

  @override
  String get disconnectInstagram => 'Disconnect Instagram';

  @override
  String get instagramConnected => 'Instagram Connected';

  @override
  String get instagramNotConnected => 'Instagram Not Connected';

  @override
  String get syncProfile => 'Sync Profile';

  @override
  String get syncPosts => 'Sync Posts';

  @override
  String get connectionStatus => 'Connection Status';

  @override
  String get connectedSince => 'Connected since';

  @override
  String get lastSync => 'Last sync';

  @override
  String get followersCount => 'Followers';

  @override
  String get followingCount => 'Following';

  @override
  String get mediaCount => 'Posts';

  @override
  String get profileInfo => 'Profile Information';

  @override
  String get postGrid => 'Recent Posts';

  @override
  String get accountInfo => 'Account Information';

  @override
  String get verified => 'Verified';

  @override
  String get private => 'Private';

  @override
  String get connectYourAccount => 'Connect Your Instagram Account';

  @override
  String get enterCredentials =>
      'Enter your Instagram credentials to connect your account';

  @override
  String get connecting => 'Connecting...';

  @override
  String get connectionFailed => 'Connection Failed';

  @override
  String get tryAgain => 'Try Again';

  @override
  String get connectionSuccessful => 'Connection Successful';

  @override
  String get accountConnectedSuccessfully =>
      'Your Instagram account has been connected successfully!';

  @override
  String get dailyReward => 'Daily Reward';

  @override
  String get claimReward => 'Claim Reward';

  @override
  String get rewardClaimed => 'Reward Claimed';

  @override
  String get comeBackTomorrow => 'Come back tomorrow for your next reward!';

  @override
  String get streak => 'Streak';

  @override
  String get days => 'days';

  @override
  String get emailVerification => 'Email Verification';

  @override
  String get verifyEmail => 'Verify Email';

  @override
  String get emailVerified => 'Email Verified';

  @override
  String get emailNotVerified => 'Email Not Verified';

  @override
  String get twoFactorAuth => 'Two-Factor Authentication';

  @override
  String get enable2FA => 'Enable 2FA';

  @override
  String get disable2FA => 'Disable 2FA';

  @override
  String get twoFactorEnabled => '2FA Enabled';

  @override
  String get twoFactorDisabled => '2FA Disabled';

  @override
  String get logoutConfirmation => 'Are you sure you want to logout?';

  @override
  String get logoutError => 'An error occurred while logging out';

  @override
  String get aboutAppDescription =>
      'JAEGram is a comprehensive social media management application that helps you track your Instagram performance, earn points through various activities, and compete with other users.';

  @override
  String get accountLevel => 'Level';

  @override
  String get joinDate => 'Join Date';

  @override
  String get totalCoins => 'Diamonds';

  @override
  String get totalPoints => 'Points';

  @override
  String get leaderboard => 'Leaderboard';

  @override
  String get weeklyRanking => 'Weekly Ranking';

  @override
  String get rank => 'Rank';

  @override
  String get progress => 'Progress';

  @override
  String get accountSettings => 'Account Settings';

  @override
  String get privacySettings => 'Privacy Settings';

  @override
  String get displaySettings => 'Display Settings';

  @override
  String get generalSettings => 'General Settings';

  @override
  String get aboutApp => 'About App';

  @override
  String get enableNotifications => 'Enable Notifications';

  @override
  String get userProfile => 'User Profile';

  @override
  String get instagramPosts => 'Instagram Posts';

  @override
  String get recentPosts => 'Recent Posts';

  @override
  String get viewDetails => 'View Details';

  @override
  String get loadInstagramDataFailed => 'Failed to load Instagram data';

  @override
  String get instagramConnectionError => 'Error connecting Instagram account';

  @override
  String get instagramSyncSuccess => 'Instagram profile synced successfully';

  @override
  String get instagramSyncFailed => 'Failed to sync Instagram profile';

  @override
  String get instagramSyncError => 'Error syncing Instagram profile';

  @override
  String get instagramDisconnected => 'Instagram account disconnected';

  @override
  String get instagramDisconnectionFailed =>
      'Failed to disconnect Instagram account';

  @override
  String get confirmDisconnect => 'Confirm Disconnect';

  @override
  String get disconnectConfirmText =>
      'Are you sure you want to disconnect your Instagram account? You\'ll need to reconnect it later to resume syncing.';

  @override
  String get disconnect => 'Disconnect';

  @override
  String get connect => 'Connect';

  @override
  String get syncing => 'Syncing...';

  @override
  String get lastSynced => 'Last Synced';

  @override
  String get disconnectDescription =>
      'Disconnecting will stop syncing your Instagram account with the app.';

  @override
  String get instagramConnectedStatus =>
      'Your Instagram account is connected and synced with the app';

  @override
  String get instagramDisconnectedStatus =>
      'Your Instagram account is not connected to the app';

  @override
  String get posts => 'Posts';

  @override
  String get instagramDisclaimerText =>
      'We never store your Instagram credentials and use them only to sync your public profile data.';

  @override
  String get yourBadges => 'Your Badges';

  @override
  String get earnBadgesDescription =>
      'Complete tasks and connect your Instagram account to earn badges';

  @override
  String get viewAllBadges => 'View All Badges';

  @override
  String get badgesEarned => 'Badges Earned';

  @override
  String get goldBadges => 'Gold';

  @override
  String get silverBadges => 'Silver';

  @override
  String get bronzeBadges => 'Bronze';

  @override
  String get instagramBadges => 'Instagram';

  @override
  String get achievementBadges => 'Achievement';

  @override
  String get specialBadges => 'Special';

  @override
  String get badgeDetails => 'Badge Details';

  @override
  String get category => 'Category';

  @override
  String get earned => 'Earned';

  @override
  String get locked => 'Locked';

  @override
  String get addedOn => 'Added On';

  @override
  String get requirements => 'Requirements to Earn';

  @override
  String get specialRequirements => 'This badge has special requirements';

  @override
  String get daysStreak => 'Daily Streaks';

  @override
  String get notificationsWillAppearHere =>
      'Your notifications will appear here';

  @override
  String get newBadgeEarned => 'New Badge Earned';

  @override
  String get levelUp => 'Level Up';

  @override
  String get coinsReceived => 'Coins Received';

  @override
  String get instagramUpdate => 'Instagram Update';

  @override
  String get systemNotification => 'System Notification';

  @override
  String get notification => 'Notification';

  @override
  String get month => 'month';

  @override
  String get months => 'months';

  @override
  String get day => 'day';

  @override
  String get hour => 'hour';

  @override
  String get hours => 'hours';

  @override
  String get minute => 'minute';

  @override
  String get minutes => 'minutes';

  @override
  String get ago => 'ago';

  @override
  String get justNow => 'Just Now';

  @override
  String get viewBadge => 'View Badge';

  @override
  String get viewProfile => 'View Profile';

  @override
  String get viewInstagram => 'View Instagram';

  @override
  String get collectCoins => 'Collect Coins';

  @override
  String get view => 'View';

  @override
  String get markAllAsRead => 'Mark All as Read';

  @override
  String get allNotificationsMarkedAsRead => 'All notifications marked as read';

  @override
  String get filterNotifications => 'Filter Notifications';

  @override
  String get showBadgeNotifications => 'Show Badge Notifications';

  @override
  String get showLevelNotifications => 'Show Level Notifications';

  @override
  String get showCoinNotifications => 'Show Coin Notifications';

  @override
  String get showInstagramNotifications => 'Show Instagram Notifications';

  @override
  String get showSystemNotifications => 'Show System Notifications';

  @override
  String get resetFilters => 'Reset Filters';

  @override
  String get apply => 'Apply';

  @override
  String get coinsCollected => 'Coins collected!';

  @override
  String get errorLoadingNotifications => 'Error loading notifications';

  @override
  String get badgeNotifications => 'Badge Notifications';

  @override
  String get soundNotifications => 'Sound Notifications';

  @override
  String get themeMode => 'Theme Mode';

  @override
  String get systemTheme => 'System';

  @override
  String get privacyPolicy => 'Privacy Policy';

  @override
  String get termsOfService => 'Terms of Service';

  @override
  String get help => 'Help';

  @override
  String get version => 'Version';

  @override
  String get logoutConfirmationText =>
      'Are you sure you want to log out of your account?';

  @override
  String get errorLoadingSettings => 'Error loading settings';

  @override
  String get integrations => 'Integrations';

  @override
  String get connected => 'Connected';

  @override
  String get notConnected => 'Not Connected';

  @override
  String get unknown => 'Unknown';

  @override
  String get accountDetails => 'Account Details';

  @override
  String get errorLoadingProfile => 'Error loading profile';

  @override
  String get errorLoadingBadges => 'Error loading badges';

  @override
  String get errorLoadingPosts => 'Error loading posts';

  @override
  String get noPostsFound => 'No posts found';

  @override
  String get connectInstagramBenefits =>
      'Connect your Instagram account to track your posts, followers, and earn special badges';

  @override
  String get loadingInstagramData => 'Loading Instagram data...';

  @override
  String get coinTransfer => 'Diamond Transfer';

  @override
  String get currentBalance => 'Current Balance';

  @override
  String get transferDetails => 'Transfer Details';

  @override
  String get recipientUsername => 'Recipient Username';

  @override
  String get enterRecipientUsername => 'Enter recipient username';

  @override
  String get pleaseEnterRecipientUsername => 'Please enter recipient username';

  @override
  String get cannotTransferToYourself => 'Cannot transfer to yourself';

  @override
  String get enterAmount => 'Enter amount';

  @override
  String get pleaseEnterAmount => 'Please enter amount';

  @override
  String get pleaseEnterValidAmount => 'Please enter a valid amount';

  @override
  String get insufficientBalance => 'Insufficient balance';

  @override
  String get note => 'Note';

  @override
  String get optional => 'Optional';

  @override
  String get enterTransferNote => 'Enter transfer note';

  @override
  String get processing => 'Processing...';

  @override
  String get transferCoins => 'Transfer Diamonds';

  @override
  String get transferInformation => 'Transfer Information';

  @override
  String get transferInfo1 => 'Transfers are instant and cannot be reversed';

  @override
  String get transferInfo2 => 'Minimum transfer amount is 1 diamond';

  @override
  String get transferInfo3 => 'Make sure the recipient username is correct';

  @override
  String get transferSuccessful => 'Transfer Successful';

  @override
  String get coinsTransferredSuccessfully =>
      'Diamonds transferred successfully!';

  @override
  String get instagramConnectionFailed => 'Instagram connection failed';

  @override
  String get monthly => 'Monthly';

  @override
  String get monthlyRanking => 'Monthly Ranking';

  @override
  String get you => 'You';
}
