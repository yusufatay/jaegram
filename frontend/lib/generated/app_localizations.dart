import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_tr.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you'll need to edit this
/// file.
///
/// First, open your project's ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project's Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('tr')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'JAEGram'**
  String get appTitle;

  /// No description provided for @switchToLight.
  ///
  /// In en, this message translates to:
  /// **'Switch to Light Mode'**
  String get switchToLight;

  /// No description provided for @switchToDark.
  ///
  /// In en, this message translates to:
  /// **'Switch to Dark Mode'**
  String get switchToDark;

  /// No description provided for @followers.
  ///
  /// In en, this message translates to:
  /// **'Followers'**
  String get followers;

  /// No description provided for @following.
  ///
  /// In en, this message translates to:
  /// **'Following'**
  String get following;

  /// No description provided for @systemStats.
  ///
  /// In en, this message translates to:
  /// **'System Statistics'**
  String get systemStats;

  /// No description provided for @newLogArrived.
  ///
  /// In en, this message translates to:
  /// **'New log arrived!'**
  String get newLogArrived;

  /// No description provided for @webSocketConnectionError.
  ///
  /// In en, this message translates to:
  /// **'WebSocket connection error. Please try again later.'**
  String get webSocketConnectionError;

  /// No description provided for @expiresAt.
  ///
  /// In en, this message translates to:
  /// **'Expires at: {dateTime}'**
  String expiresAt(Object dateTime);

  /// No description provided for @expiresAtLabel.
  ///
  /// In en, this message translates to:
  /// **'Expires At'**
  String get expiresAtLabel;

  /// No description provided for @completedAtLabel.
  ///
  /// In en, this message translates to:
  /// **'Completed At'**
  String get completedAtLabel;

  /// No description provided for @completedAt.
  ///
  /// In en, this message translates to:
  /// **'Completed At'**
  String get completedAt;

  /// No description provided for @id.
  ///
  /// In en, this message translates to:
  /// **'ID'**
  String get id;

  /// No description provided for @orderId.
  ///
  /// In en, this message translates to:
  /// **'Order ID'**
  String get orderId;

  /// No description provided for @assignedUser.
  ///
  /// In en, this message translates to:
  /// **'Assigned User'**
  String get assignedUser;

  /// No description provided for @status.
  ///
  /// In en, this message translates to:
  /// **'Status'**
  String get status;

  /// No description provided for @assignedAt.
  ///
  /// In en, this message translates to:
  /// **'Assigned At'**
  String get assignedAt;

  /// No description provided for @loginTitle.
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get loginTitle;

  /// No description provided for @mainScreenTitle.
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get mainScreenTitle;

  /// No description provided for @tasks.
  ///
  /// In en, this message translates to:
  /// **'Tasks'**
  String get tasks;

  /// No description provided for @orders.
  ///
  /// In en, this message translates to:
  /// **'Orders'**
  String get orders;

  /// No description provided for @profile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profile;

  /// No description provided for @notifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notifications;

  /// No description provided for @statistics.
  ///
  /// In en, this message translates to:
  /// **'Statistics'**
  String get statistics;

  /// No description provided for @admin.
  ///
  /// In en, this message translates to:
  /// **'Admin'**
  String get admin;

  /// No description provided for @logout.
  ///
  /// In en, this message translates to:
  /// **'Logout'**
  String get logout;

  /// No description provided for @coin.
  ///
  /// In en, this message translates to:
  /// **'Diamond'**
  String get coin;

  /// No description provided for @completedTasks.
  ///
  /// In en, this message translates to:
  /// **'Completed Tasks'**
  String completedTasks(Object count);

  /// No description provided for @completedTasksLabel.
  ///
  /// In en, this message translates to:
  /// **'Completed Tasks'**
  String get completedTasksLabel;

  /// No description provided for @activeTasksLabel.
  ///
  /// In en, this message translates to:
  /// **'Active Tasks'**
  String get activeTasksLabel;

  /// No description provided for @activeTasks.
  ///
  /// In en, this message translates to:
  /// **'Active Tasks'**
  String get activeTasks;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @theme.
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get theme;

  /// No description provided for @darkTheme.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get darkTheme;

  /// No description provided for @lightTheme.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get lightTheme;

  /// No description provided for @loginSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Access your account'**
  String get loginSubtitle;

  /// No description provided for @username.
  ///
  /// In en, this message translates to:
  /// **'Username'**
  String get username;

  /// No description provided for @password.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get password;

  /// No description provided for @loginButton.
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get loginButton;

  /// No description provided for @twoFACode.
  ///
  /// In en, this message translates to:
  /// **'2FA Code'**
  String get twoFACode;

  /// No description provided for @continueWith2FA.
  ///
  /// In en, this message translates to:
  /// **'Continue with 2FA'**
  String get continueWith2FA;

  /// No description provided for @usernamePasswordRequired.
  ///
  /// In en, this message translates to:
  /// **'Username and password are required.'**
  String get usernamePasswordRequired;

  /// No description provided for @twoFARequired.
  ///
  /// In en, this message translates to:
  /// **'2FA code is required.'**
  String get twoFARequired;

  /// No description provided for @selectTab.
  ///
  /// In en, this message translates to:
  /// **'Select a Tab'**
  String get selectTab;

  /// No description provided for @takeNewTask.
  ///
  /// In en, this message translates to:
  /// **'Take New Task'**
  String get takeNewTask;

  /// No description provided for @taskTakenSuccess.
  ///
  /// In en, this message translates to:
  /// **'Task taken successfully!'**
  String get taskTakenSuccess;

  /// No description provided for @taskTakeFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to take task: {error}'**
  String taskTakeFailed(Object error);

  /// No description provided for @noAssignedTask.
  ///
  /// In en, this message translates to:
  /// **'No assigned task currently.'**
  String get noAssignedTask;

  /// No description provided for @complete.
  ///
  /// In en, this message translates to:
  /// **'Complete'**
  String get complete;

  /// No description provided for @noNotifications.
  ///
  /// In en, this message translates to:
  /// **'No notifications yet.'**
  String get noNotifications;

  /// No description provided for @markAsRead.
  ///
  /// In en, this message translates to:
  /// **'Mark as Read'**
  String get markAsRead;

  /// No description provided for @orderCreatedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Order created successfully!'**
  String get orderCreatedSuccessfully;

  /// No description provided for @orderCreationError.
  ///
  /// In en, this message translates to:
  /// **'Failed to create order. Please try again.'**
  String get orderCreationError;

  /// No description provided for @myOrders.
  ///
  /// In en, this message translates to:
  /// **'My Orders'**
  String get myOrders;

  /// No description provided for @createOrder.
  ///
  /// In en, this message translates to:
  /// **'Create Order'**
  String get createOrder;

  /// No description provided for @errorWithMessage.
  ///
  /// In en, this message translates to:
  /// **'Error: {message}'**
  String errorWithMessage(Object message);

  /// No description provided for @settingsTitle.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settingsTitle;

  /// No description provided for @changeLanguage.
  ///
  /// In en, this message translates to:
  /// **'Change Language'**
  String get changeLanguage;

  /// No description provided for @changeTheme.
  ///
  /// In en, this message translates to:
  /// **'Change Theme'**
  String get changeTheme;

  /// No description provided for @notificationSettings.
  ///
  /// In en, this message translates to:
  /// **'Notification Settings'**
  String get notificationSettings;

  /// No description provided for @editProfile.
  ///
  /// In en, this message translates to:
  /// **'Edit Profile'**
  String get editProfile;

  /// No description provided for @changePassword.
  ///
  /// In en, this message translates to:
  /// **'Change Password'**
  String get changePassword;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @save.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @dark.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get dark;

  /// No description provided for @light.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get light;

  /// No description provided for @system.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get system;

  /// No description provided for @selectLanguage.
  ///
  /// In en, this message translates to:
  /// **'Select Language'**
  String get selectLanguage;

  /// No description provided for @selectTheme.
  ///
  /// In en, this message translates to:
  /// **'Select Theme'**
  String get selectTheme;

  /// No description provided for @profileUpdated.
  ///
  /// In en, this message translates to:
  /// **'Profile updated successfully!'**
  String get profileUpdated;

  /// No description provided for @passwordChanged.
  ///
  /// In en, this message translates to:
  /// **'Password changed successfully!'**
  String get passwordChanged;

  /// No description provided for @errorOccurred.
  ///
  /// In en, this message translates to:
  /// **'An error occurred!'**
  String get errorOccurred;

  /// No description provided for @confirmLogout.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to logout?'**
  String get confirmLogout;

  /// No description provided for @yes.
  ///
  /// In en, this message translates to:
  /// **'Yes'**
  String get yes;

  /// No description provided for @no.
  ///
  /// In en, this message translates to:
  /// **'No'**
  String get no;

  /// No description provided for @rollback.
  ///
  /// In en, this message translates to:
  /// **'Rollback'**
  String get rollback;

  /// No description provided for @rollbackSuccess.
  ///
  /// In en, this message translates to:
  /// **'Rollback successful!'**
  String get rollbackSuccess;

  /// No description provided for @userBanned.
  ///
  /// In en, this message translates to:
  /// **'User banned.'**
  String get userBanned;

  /// No description provided for @coinOperationSuccess.
  ///
  /// In en, this message translates to:
  /// **'Diamond operation successful.'**
  String get coinOperationSuccess;

  /// No description provided for @adminPanel.
  ///
  /// In en, this message translates to:
  /// **'Admin Panel'**
  String get adminPanel;

  /// No description provided for @instagramLogin.
  ///
  /// In en, this message translates to:
  /// **'Login with Instagram'**
  String get instagramLogin;

  /// No description provided for @platformLogin.
  ///
  /// In en, this message translates to:
  /// **'Platform Login'**
  String get platformLogin;

  /// No description provided for @register.
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get register;

  /// No description provided for @fullName.
  ///
  /// In en, this message translates to:
  /// **'Full Name'**
  String get fullName;

  /// No description provided for @registerSuccess.
  ///
  /// In en, this message translates to:
  /// **'Registration successful! Please login.'**
  String get registerSuccess;

  /// No description provided for @registerFailed.
  ///
  /// In en, this message translates to:
  /// **'Registration failed: {error}'**
  String registerFailed(Object error);

  /// No description provided for @requiredField.
  ///
  /// In en, this message translates to:
  /// **'This field is required.'**
  String get requiredField;

  /// No description provided for @minCommentLength.
  ///
  /// In en, this message translates to:
  /// **'Comment must be at least {length} characters.'**
  String minCommentLength(Object length);

  /// No description provided for @maxCommentLength.
  ///
  /// In en, this message translates to:
  /// **'Comment can be at most {length} characters.'**
  String maxCommentLength(Object length);

  /// No description provided for @orderTypeLike.
  ///
  /// In en, this message translates to:
  /// **'Like'**
  String get orderTypeLike;

  /// No description provided for @orderTypeFollow.
  ///
  /// In en, this message translates to:
  /// **'Follow'**
  String get orderTypeFollow;

  /// No description provided for @orderTypeComment.
  ///
  /// In en, this message translates to:
  /// **'Comment'**
  String get orderTypeComment;

  /// No description provided for @postUrl.
  ///
  /// In en, this message translates to:
  /// **'Post URL'**
  String get postUrl;

  /// No description provided for @targetCount.
  ///
  /// In en, this message translates to:
  /// **'Target Count'**
  String get targetCount;

  /// No description provided for @commentText.
  ///
  /// In en, this message translates to:
  /// **'Comment Text (for comment orders)'**
  String get commentText;

  /// No description provided for @orderCreationSuccess.
  ///
  /// In en, this message translates to:
  /// **'Order created successfully!'**
  String get orderCreationSuccess;

  /// No description provided for @orderCreationFailed.
  ///
  /// In en, this message translates to:
  /// **'Order creation failed: {error}'**
  String orderCreationFailed(Object error);

  /// No description provided for @taskStatusPending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get taskStatusPending;

  /// No description provided for @taskStatusAssigned.
  ///
  /// In en, this message translates to:
  /// **'Assigned'**
  String get taskStatusAssigned;

  /// No description provided for @taskStatusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get taskStatusCompleted;

  /// No description provided for @taskStatusExpired.
  ///
  /// In en, this message translates to:
  /// **'Expired'**
  String get taskStatusExpired;

  /// No description provided for @taskStatusFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get taskStatusFailed;

  /// No description provided for @taskCompletedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Task completed successfully!'**
  String get taskCompletedSuccess;

  /// No description provided for @taskCompletionFailed.
  ///
  /// In en, this message translates to:
  /// **'Task completion failed: {error}'**
  String taskCompletionFailed(Object error);

  /// No description provided for @withdrawCoins.
  ///
  /// In en, this message translates to:
  /// **'Withdraw Diamonds'**
  String get withdrawCoins;

  /// No description provided for @amount.
  ///
  /// In en, this message translates to:
  /// **'Amount'**
  String get amount;

  /// No description provided for @minCompletedTasksRequired.
  ///
  /// In en, this message translates to:
  /// **'You need to complete at least {count} tasks to withdraw.'**
  String minCompletedTasksRequired(Object count);

  /// No description provided for @insufficientCoins.
  ///
  /// In en, this message translates to:
  /// **'Insufficient diamonds.'**
  String get insufficientCoins;

  /// No description provided for @positiveAmountRequired.
  ///
  /// In en, this message translates to:
  /// **'Amount must be positive.'**
  String get positiveAmountRequired;

  /// No description provided for @withdrawalSuccess.
  ///
  /// In en, this message translates to:
  /// **'Withdrawal successful!'**
  String get withdrawalSuccess;

  /// No description provided for @withdrawalFailed.
  ///
  /// In en, this message translates to:
  /// **'Withdrawal failed: {error}'**
  String withdrawalFailed(Object error);

  /// No description provided for @coins.
  ///
  /// In en, this message translates to:
  /// **'Diamonds'**
  String get coins;

  /// No description provided for @activeTask.
  ///
  /// In en, this message translates to:
  /// **'Active Task'**
  String get activeTask;

  /// No description provided for @appName.
  ///
  /// In en, this message translates to:
  /// **'Instagram Score App'**
  String get appName;

  /// No description provided for @usernameHint.
  ///
  /// In en, this message translates to:
  /// **'Enter your Instagram username'**
  String get usernameHint;

  /// No description provided for @passwordHint.
  ///
  /// In en, this message translates to:
  /// **'Enter your Instagram password'**
  String get passwordHint;

  /// No description provided for @turkish.
  ///
  /// In en, this message translates to:
  /// **'Turkish'**
  String get turkish;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @error.
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @genericErrorEncountered.
  ///
  /// In en, this message translates to:
  /// **'An error occurred.'**
  String get genericErrorEncountered;

  /// No description provided for @details.
  ///
  /// In en, this message translates to:
  /// **'Details'**
  String get details;

  /// No description provided for @systemDefault.
  ///
  /// In en, this message translates to:
  /// **'System Default'**
  String get systemDefault;

  /// No description provided for @appSettings.
  ///
  /// In en, this message translates to:
  /// **'App Settings'**
  String get appSettings;

  /// No description provided for @users.
  ///
  /// In en, this message translates to:
  /// **'Users'**
  String get users;

  /// No description provided for @coinTransactions.
  ///
  /// In en, this message translates to:
  /// **'Diamond Transactions'**
  String get coinTransactions;

  /// No description provided for @logs.
  ///
  /// In en, this message translates to:
  /// **'Logs'**
  String get logs;

  /// No description provided for @refresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh'**
  String get refresh;

  /// No description provided for @searchInUsers.
  ///
  /// In en, this message translates to:
  /// **'Search in users (ID, username, name, email)'**
  String get searchInUsers;

  /// No description provided for @searchInOrders.
  ///
  /// In en, this message translates to:
  /// **'Search in orders (ID, user ID, post URL, type)'**
  String get searchInOrders;

  /// No description provided for @searchInTasks.
  ///
  /// In en, this message translates to:
  /// **'Search in tasks (ID, order ID, user ID, status)'**
  String get searchInTasks;

  /// No description provided for @searchInCoinTransactions.
  ///
  /// In en, this message translates to:
  /// **'Search in diamond transactions (ID, user ID, type, description)'**
  String get searchInCoinTransactions;

  /// No description provided for @searchInLogs.
  ///
  /// In en, this message translates to:
  /// **'Search in logs (ID, admin, target, action, description)'**
  String get searchInLogs;

  /// No description provided for @exportCsv.
  ///
  /// In en, this message translates to:
  /// **'Export to CSV'**
  String get exportCsv;

  /// No description provided for @exportCsvShort.
  ///
  /// In en, this message translates to:
  /// **'Export'**
  String get exportCsvShort;

  /// No description provided for @all.
  ///
  /// In en, this message translates to:
  /// **'All Time'**
  String get all;

  /// No description provided for @admins.
  ///
  /// In en, this message translates to:
  /// **'Admins'**
  String get admins;

  /// No description provided for @bannedUsers.
  ///
  /// In en, this message translates to:
  /// **'Banned Users'**
  String get bannedUsers;

  /// No description provided for @platformAdmin.
  ///
  /// In en, this message translates to:
  /// **'Platform Admin?'**
  String get platformAdmin;

  /// No description provided for @banned.
  ///
  /// In en, this message translates to:
  /// **'Banned?'**
  String get banned;

  /// No description provided for @actions.
  ///
  /// In en, this message translates to:
  /// **'Actions'**
  String get actions;

  /// No description provided for @userActionsFor.
  ///
  /// In en, this message translates to:
  /// **'Actions for {username}'**
  String userActionsFor(Object username);

  /// No description provided for @banUser.
  ///
  /// In en, this message translates to:
  /// **'Ban User'**
  String get banUser;

  /// No description provided for @unbanUser.
  ///
  /// In en, this message translates to:
  /// **'Unban User'**
  String get unbanUser;

  /// No description provided for @confirmBan.
  ///
  /// In en, this message translates to:
  /// **'Confirm Ban'**
  String get confirmBan;

  /// No description provided for @confirmUnban.
  ///
  /// In en, this message translates to:
  /// **'Confirm Unban'**
  String get confirmUnban;

  /// No description provided for @areYouSureBan.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to {banUnban} user {username}?'**
  String areYouSureBan(Object banUnban, Object username);

  /// No description provided for @banVerb.
  ///
  /// In en, this message translates to:
  /// **'ban'**
  String get banVerb;

  /// No description provided for @unbanVerb.
  ///
  /// In en, this message translates to:
  /// **'unban'**
  String get unbanVerb;

  /// No description provided for @userUnbanned.
  ///
  /// In en, this message translates to:
  /// **'User unbanned.'**
  String get userUnbanned;

  /// No description provided for @addRemoveCoin.
  ///
  /// In en, this message translates to:
  /// **'Add/Remove Diamond'**
  String get addRemoveCoin;

  /// No description provided for @addRemoveCoinFor.
  ///
  /// In en, this message translates to:
  /// **'Add/Remove diamond for {username}'**
  String addRemoveCoinFor(Object username);

  /// No description provided for @coinAmount.
  ///
  /// In en, this message translates to:
  /// **'Diamond Amount'**
  String get coinAmount;

  /// No description provided for @coinAmountInfo.
  ///
  /// In en, this message translates to:
  /// **'Coin Amount (negative to remove)'**
  String get coinAmountInfo;

  /// No description provided for @confirm.
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get confirm;

  /// No description provided for @promoteToAdmin.
  ///
  /// In en, this message translates to:
  /// **'Promote to Admin'**
  String get promoteToAdmin;

  /// No description provided for @demoteFromAdmin.
  ///
  /// In en, this message translates to:
  /// **'Demote from Admin'**
  String get demoteFromAdmin;

  /// No description provided for @confirmPromote.
  ///
  /// In en, this message translates to:
  /// **'Confirm Promotion'**
  String get confirmPromote;

  /// No description provided for @confirmDemote.
  ///
  /// In en, this message translates to:
  /// **'Confirm Demotion'**
  String get confirmDemote;

  /// No description provided for @areYouSureAdmin.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to {promoteDemote} user {username} as a platform admin?'**
  String areYouSureAdmin(Object promoteDemote, Object username);

  /// No description provided for @promoteVerb.
  ///
  /// In en, this message translates to:
  /// **'promote'**
  String get promoteVerb;

  /// No description provided for @demoteVerb.
  ///
  /// In en, this message translates to:
  /// **'demote'**
  String get demoteVerb;

  /// No description provided for @userPromoted.
  ///
  /// In en, this message translates to:
  /// **'User promoted to admin.'**
  String get userPromoted;

  /// No description provided for @userDemoted.
  ///
  /// In en, this message translates to:
  /// **'User demoted from admin.'**
  String get userDemoted;

  /// No description provided for @logDetails.
  ///
  /// In en, this message translates to:
  /// **'Log Details'**
  String get logDetails;

  /// No description provided for @date.
  ///
  /// In en, this message translates to:
  /// **'Date'**
  String get date;

  /// No description provided for @action.
  ///
  /// In en, this message translates to:
  /// **'Action'**
  String get action;

  /// No description provided for @adminUsername.
  ///
  /// In en, this message translates to:
  /// **'Admin Username'**
  String get adminUsername;

  /// No description provided for @targetUser.
  ///
  /// In en, this message translates to:
  /// **'Target User'**
  String get targetUser;

  /// No description provided for @targetUsername.
  ///
  /// In en, this message translates to:
  /// **'Target Username'**
  String get targetUsername;

  /// No description provided for @description.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get description;

  /// No description provided for @closeButton.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get closeButton;

  /// No description provided for @confirmRollback.
  ///
  /// In en, this message translates to:
  /// **'Confirm Rollback'**
  String get confirmRollback;

  /// No description provided for @areYouSureRollback.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to rollback \"{actionDescription}\"? This cannot be undone.'**
  String areYouSureRollback(Object actionDescription);

  /// No description provided for @cannotRollback.
  ///
  /// In en, this message translates to:
  /// **'This action cannot be rolled back.'**
  String get cannotRollback;

  /// No description provided for @thisAction.
  ///
  /// In en, this message translates to:
  /// **'this action'**
  String get thisAction;

  /// No description provided for @noDataToExport.
  ///
  /// In en, this message translates to:
  /// **'No data to export.'**
  String get noDataToExport;

  /// No description provided for @csvDownloadStarting.
  ///
  /// In en, this message translates to:
  /// **'CSV download starting...'**
  String get csvDownloadStarting;

  /// No description provided for @csvExportNotSupportedOnMobileYet.
  ///
  /// In en, this message translates to:
  /// **'CSV export is not supported on this platform yet.'**
  String get csvExportNotSupportedOnMobileYet;

  /// No description provided for @user.
  ///
  /// In en, this message translates to:
  /// **'User'**
  String get user;

  /// No description provided for @orderType.
  ///
  /// In en, this message translates to:
  /// **'Order Type'**
  String get orderType;

  /// No description provided for @completedCount.
  ///
  /// In en, this message translates to:
  /// **'Completed Count'**
  String get completedCount;

  /// No description provided for @createdAt.
  ///
  /// In en, this message translates to:
  /// **'Created At'**
  String get createdAt;

  /// No description provided for @userId.
  ///
  /// In en, this message translates to:
  /// **'User ID'**
  String get userId;

  /// No description provided for @transactionType.
  ///
  /// In en, this message translates to:
  /// **'Transaction Type'**
  String get transactionType;

  /// No description provided for @balanceAfter.
  ///
  /// In en, this message translates to:
  /// **'Balance After'**
  String get balanceAfter;

  /// No description provided for @logActionUserBan.
  ///
  /// In en, this message translates to:
  /// **'User Ban'**
  String get logActionUserBan;

  /// No description provided for @logActionUserUnban.
  ///
  /// In en, this message translates to:
  /// **'User Unban'**
  String get logActionUserUnban;

  /// No description provided for @logActionCoinAdjust.
  ///
  /// In en, this message translates to:
  /// **'Coin Adjustment'**
  String get logActionCoinAdjust;

  /// No description provided for @logActionAdminPromote.
  ///
  /// In en, this message translates to:
  /// **'Admin Promotion'**
  String get logActionAdminPromote;

  /// No description provided for @logActionAdminDemote.
  ///
  /// In en, this message translates to:
  /// **'Admin Demotion'**
  String get logActionAdminDemote;

  /// No description provided for @errorFetchingCoin.
  ///
  /// In en, this message translates to:
  /// **'Error fetching diamond balance'**
  String get errorFetchingCoin;

  /// No description provided for @tasksTab.
  ///
  /// In en, this message translates to:
  /// **'Tasks'**
  String get tasksTab;

  /// No description provided for @ordersTab.
  ///
  /// In en, this message translates to:
  /// **'Orders'**
  String get ordersTab;

  /// No description provided for @profileTab.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profileTab;

  /// No description provided for @orderFilterStatusAll.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get orderFilterStatusAll;

  /// No description provided for @orderFilterStatusPending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get orderFilterStatusPending;

  /// No description provided for @orderFilterStatusActive.
  ///
  /// In en, this message translates to:
  /// **'Active'**
  String get orderFilterStatusActive;

  /// No description provided for @orderFilterStatusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get orderFilterStatusCompleted;

  /// No description provided for @orderFilterStatusFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get orderFilterStatusFailed;

  /// No description provided for @orderFilterStatusCancelled.
  ///
  /// In en, this message translates to:
  /// **'Cancelled'**
  String get orderFilterStatusCancelled;

  /// No description provided for @taskFilterStatusAll.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get taskFilterStatusAll;

  /// No description provided for @taskFilterStatusPending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get taskFilterStatusPending;

  /// No description provided for @taskFilterStatusAssigned.
  ///
  /// In en, this message translates to:
  /// **'Assigned'**
  String get taskFilterStatusAssigned;

  /// No description provided for @taskFilterStatusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get taskFilterStatusCompleted;

  /// No description provided for @taskFilterStatusFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get taskFilterStatusFailed;

  /// No description provided for @taskFilterStatusExpired.
  ///
  /// In en, this message translates to:
  /// **'Expired'**
  String get taskFilterStatusExpired;

  /// No description provided for @coinTransactionFilterAll.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get coinTransactionFilterAll;

  /// No description provided for @coinTransactionFilterEarn.
  ///
  /// In en, this message translates to:
  /// **'Earn'**
  String get coinTransactionFilterEarn;

  /// No description provided for @coinTransactionFilterSpend.
  ///
  /// In en, this message translates to:
  /// **'Spend'**
  String get coinTransactionFilterSpend;

  /// No description provided for @coinTransactionFilterWithdraw.
  ///
  /// In en, this message translates to:
  /// **'Withdrawal'**
  String get coinTransactionFilterWithdraw;

  /// No description provided for @coinTransactionFilterAdminAdd.
  ///
  /// In en, this message translates to:
  /// **'Admin Add'**
  String get coinTransactionFilterAdminAdd;

  /// No description provided for @coinTransactionFilterAdminRemove.
  ///
  /// In en, this message translates to:
  /// **'Admin Remove'**
  String get coinTransactionFilterAdminRemove;

  /// No description provided for @adminLogFilterAll.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get adminLogFilterAll;

  /// No description provided for @badges.
  ///
  /// In en, this message translates to:
  /// **'Badges'**
  String get badges;

  /// No description provided for @viewAll.
  ///
  /// In en, this message translates to:
  /// **'View All'**
  String get viewAll;

  /// No description provided for @noBadgesEarned.
  ///
  /// In en, this message translates to:
  /// **'No badges earned yet'**
  String get noBadgesEarned;

  /// No description provided for @noBadgesAvailable.
  ///
  /// In en, this message translates to:
  /// **'No badges available'**
  String get noBadgesAvailable;

  /// No description provided for @earnedOn.
  ///
  /// In en, this message translates to:
  /// **'Earned On'**
  String get earnedOn;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @badgeStats.
  ///
  /// In en, this message translates to:
  /// **'Badge Statistics'**
  String get badgeStats;

  /// No description provided for @totalBadges.
  ///
  /// In en, this message translates to:
  /// **'Total Badges'**
  String get totalBadges;

  /// No description provided for @categories.
  ///
  /// In en, this message translates to:
  /// **'Categories'**
  String get categories;

  /// No description provided for @earnedBadges.
  ///
  /// In en, this message translates to:
  /// **'Earned Badges'**
  String get earnedBadges;

  /// No description provided for @allBadges.
  ///
  /// In en, this message translates to:
  /// **'All Badges'**
  String get allBadges;

  /// No description provided for @progressStatus.
  ///
  /// In en, this message translates to:
  /// **'Progress Status'**
  String get progressStatus;

  /// No description provided for @badgeEarned.
  ///
  /// In en, this message translates to:
  /// **'Badge Earned!'**
  String get badgeEarned;

  /// No description provided for @congratulations.
  ///
  /// In en, this message translates to:
  /// **'Congratulations!'**
  String get congratulations;

  /// No description provided for @youEarnedBadge.
  ///
  /// In en, this message translates to:
  /// **'You earned the badge:'**
  String get youEarnedBadge;

  /// No description provided for @instagramIntegration.
  ///
  /// In en, this message translates to:
  /// **'Instagram Integration'**
  String get instagramIntegration;

  /// No description provided for @instagramDashboard.
  ///
  /// In en, this message translates to:
  /// **'Instagram Dashboard'**
  String get instagramDashboard;

  /// No description provided for @connectInstagram.
  ///
  /// In en, this message translates to:
  /// **'Connect Instagram'**
  String get connectInstagram;

  /// No description provided for @disconnectInstagram.
  ///
  /// In en, this message translates to:
  /// **'Disconnect Instagram'**
  String get disconnectInstagram;

  /// No description provided for @instagramConnected.
  ///
  /// In en, this message translates to:
  /// **'Instagram Connected'**
  String get instagramConnected;

  /// No description provided for @instagramNotConnected.
  ///
  /// In en, this message translates to:
  /// **'Instagram Not Connected'**
  String get instagramNotConnected;

  /// No description provided for @syncProfile.
  ///
  /// In en, this message translates to:
  /// **'Sync Profile'**
  String get syncProfile;

  /// No description provided for @syncPosts.
  ///
  /// In en, this message translates to:
  /// **'Sync Posts'**
  String get syncPosts;

  /// No description provided for @connectionStatus.
  ///
  /// In en, this message translates to:
  /// **'Connection Status'**
  String get connectionStatus;

  /// No description provided for @connectedSince.
  ///
  /// In en, this message translates to:
  /// **'Connected since'**
  String get connectedSince;

  /// No description provided for @lastSync.
  ///
  /// In en, this message translates to:
  /// **'Last sync'**
  String get lastSync;

  /// No description provided for @followersCount.
  ///
  /// In en, this message translates to:
  /// **'Followers'**
  String get followersCount;

  /// No description provided for @followingCount.
  ///
  /// In en, this message translates to:
  /// **'Following'**
  String get followingCount;

  /// No description provided for @mediaCount.
  ///
  /// In en, this message translates to:
  /// **'Posts'**
  String get mediaCount;

  /// No description provided for @profileInfo.
  ///
  /// In en, this message translates to:
  /// **'Profile Information'**
  String get profileInfo;

  /// No description provided for @postGrid.
  ///
  /// In en, this message translates to:
  /// **'Recent Posts'**
  String get postGrid;

  /// No description provided for @accountInfo.
  ///
  /// In en, this message translates to:
  /// **'Account Information'**
  String get accountInfo;

  /// No description provided for @verified.
  ///
  /// In en, this message translates to:
  /// **'Verified'**
  String get verified;

  /// No description provided for @private.
  ///
  /// In en, this message translates to:
  /// **'Private'**
  String get private;

  /// No description provided for @connectYourAccount.
  ///
  /// In en, this message translates to:
  /// **'Connect Your Instagram Account'**
  String get connectYourAccount;

  /// No description provided for @enterCredentials.
  ///
  /// In en, this message translates to:
  /// **'Enter your Instagram credentials to connect your account'**
  String get enterCredentials;

  /// No description provided for @connecting.
  ///
  /// In en, this message translates to:
  /// **'Connecting...'**
  String get connecting;

  /// No description provided for @connectionFailed.
  ///
  /// In en, this message translates to:
  /// **'Connection Failed'**
  String get connectionFailed;

  /// No description provided for @tryAgain.
  ///
  /// In en, this message translates to:
  /// **'Try Again'**
  String get tryAgain;

  /// No description provided for @connectionSuccessful.
  ///
  /// In en, this message translates to:
  /// **'Connection Successful'**
  String get connectionSuccessful;

  /// No description provided for @accountConnectedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Your Instagram account has been connected successfully!'**
  String get accountConnectedSuccessfully;

  /// No description provided for @dailyReward.
  ///
  /// In en, this message translates to:
  /// **'Daily Reward'**
  String get dailyReward;

  /// No description provided for @claimReward.
  ///
  /// In en, this message translates to:
  /// **'Claim Reward'**
  String get claimReward;

  /// No description provided for @rewardClaimed.
  ///
  /// In en, this message translates to:
  /// **'Reward Claimed'**
  String get rewardClaimed;

  /// No description provided for @comeBackTomorrow.
  ///
  /// In en, this message translates to:
  /// **'Come back tomorrow for your next reward!'**
  String get comeBackTomorrow;

  /// No description provided for @streak.
  ///
  /// In en, this message translates to:
  /// **'Streak'**
  String get streak;

  /// No description provided for @days.
  ///
  /// In en, this message translates to:
  /// **'days'**
  String get days;

  /// No description provided for @emailVerification.
  ///
  /// In en, this message translates to:
  /// **'Email Verification'**
  String get emailVerification;

  /// No description provided for @verifyEmail.
  ///
  /// In en, this message translates to:
  /// **'Verify Email'**
  String get verifyEmail;

  /// No description provided for @emailVerified.
  ///
  /// In en, this message translates to:
  /// **'Email Verified'**
  String get emailVerified;

  /// No description provided for @emailNotVerified.
  ///
  /// In en, this message translates to:
  /// **'Email Not Verified'**
  String get emailNotVerified;

  /// No description provided for @twoFactorAuth.
  ///
  /// In en, this message translates to:
  /// **'Two-Factor Authentication'**
  String get twoFactorAuth;

  /// No description provided for @enable2FA.
  ///
  /// In en, this message translates to:
  /// **'Enable 2FA'**
  String get enable2FA;

  /// No description provided for @disable2FA.
  ///
  /// In en, this message translates to:
  /// **'Disable 2FA'**
  String get disable2FA;

  /// No description provided for @twoFactorEnabled.
  ///
  /// In en, this message translates to:
  /// **'2FA Enabled'**
  String get twoFactorEnabled;

  /// No description provided for @twoFactorDisabled.
  ///
  /// In en, this message translates to:
  /// **'2FA Disabled'**
  String get twoFactorDisabled;

  /// No description provided for @logoutConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to logout?'**
  String get logoutConfirmation;

  /// No description provided for @logoutError.
  ///
  /// In en, this message translates to:
  /// **'An error occurred while logging out'**
  String get logoutError;

  /// No description provided for @aboutAppDescription.
  ///
  /// In en, this message translates to:
  /// **'JAEGram is a comprehensive social media management application that helps you track your Instagram performance, earn points through various activities, and compete with other users.'**
  String get aboutAppDescription;

  /// No description provided for @accountLevel.
  ///
  /// In en, this message translates to:
  /// **'Level'**
  String get accountLevel;

  /// No description provided for @joinDate.
  ///
  /// In en, this message translates to:
  /// **'Join Date'**
  String get joinDate;

  /// No description provided for @totalCoins.
  ///
  /// In en, this message translates to:
  /// **'Diamonds'**
  String get totalCoins;

  /// No description provided for @totalPoints.
  ///
  /// In en, this message translates to:
  /// **'Points'**
  String get totalPoints;

  /// No description provided for @leaderboard.
  ///
  /// In en, this message translates to:
  /// **'Leaderboard'**
  String get leaderboard;

  /// No description provided for @weeklyRanking.
  ///
  /// In en, this message translates to:
  /// **'Weekly Ranking'**
  String get weeklyRanking;

  /// No description provided for @rank.
  ///
  /// In en, this message translates to:
  /// **'Rank'**
  String get rank;

  /// No description provided for @progress.
  ///
  /// In en, this message translates to:
  /// **'Progress'**
  String get progress;

  /// No description provided for @accountSettings.
  ///
  /// In en, this message translates to:
  /// **'Account Settings'**
  String get accountSettings;

  /// No description provided for @privacySettings.
  ///
  /// In en, this message translates to:
  /// **'Privacy Settings'**
  String get privacySettings;

  /// No description provided for @displaySettings.
  ///
  /// In en, this message translates to:
  /// **'Display Settings'**
  String get displaySettings;

  /// No description provided for @generalSettings.
  ///
  /// In en, this message translates to:
  /// **'General Settings'**
  String get generalSettings;

  /// No description provided for @aboutApp.
  ///
  /// In en, this message translates to:
  /// **'About App'**
  String get aboutApp;

  /// No description provided for @enableNotifications.
  ///
  /// In en, this message translates to:
  /// **'Enable Notifications'**
  String get enableNotifications;

  /// No description provided for @userProfile.
  ///
  /// In en, this message translates to:
  /// **'User Profile'**
  String get userProfile;

  /// No description provided for @instagramPosts.
  ///
  /// In en, this message translates to:
  /// **'Instagram Posts'**
  String get instagramPosts;

  /// No description provided for @recentPosts.
  ///
  /// In en, this message translates to:
  /// **'Recent Posts'**
  String get recentPosts;

  /// No description provided for @viewDetails.
  ///
  /// In en, this message translates to:
  /// **'View Details'**
  String get viewDetails;

  /// No description provided for @loadInstagramDataFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to load Instagram data'**
  String get loadInstagramDataFailed;

  /// No description provided for @instagramConnectionError.
  ///
  /// In en, this message translates to:
  /// **'Error connecting Instagram account'**
  String get instagramConnectionError;

  /// No description provided for @instagramSyncSuccess.
  ///
  /// In en, this message translates to:
  /// **'Instagram profile synced successfully'**
  String get instagramSyncSuccess;

  /// No description provided for @instagramSyncFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to sync Instagram profile'**
  String get instagramSyncFailed;

  /// No description provided for @instagramSyncError.
  ///
  /// In en, this message translates to:
  /// **'Error syncing Instagram profile'**
  String get instagramSyncError;

  /// No description provided for @instagramDisconnected.
  ///
  /// In en, this message translates to:
  /// **'Instagram account disconnected'**
  String get instagramDisconnected;

  /// No description provided for @instagramDisconnectionFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to disconnect Instagram account'**
  String get instagramDisconnectionFailed;

  /// No description provided for @confirmDisconnect.
  ///
  /// In en, this message translates to:
  /// **'Confirm Disconnect'**
  String get confirmDisconnect;

  /// No description provided for @disconnectConfirmText.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to disconnect your Instagram account? You\'ll need to reconnect it later to resume syncing.'**
  String get disconnectConfirmText;

  /// No description provided for @disconnect.
  ///
  /// In en, this message translates to:
  /// **'Disconnect'**
  String get disconnect;

  /// No description provided for @connect.
  ///
  /// In en, this message translates to:
  /// **'Connect'**
  String get connect;

  /// No description provided for @syncing.
  ///
  /// In en, this message translates to:
  /// **'Syncing...'**
  String get syncing;

  /// No description provided for @lastSynced.
  ///
  /// In en, this message translates to:
  /// **'Last Synced'**
  String get lastSynced;

  /// No description provided for @disconnectDescription.
  ///
  /// In en, this message translates to:
  /// **'Disconnecting will stop syncing your Instagram account with the app.'**
  String get disconnectDescription;

  /// No description provided for @instagramConnectedStatus.
  ///
  /// In en, this message translates to:
  /// **'Your Instagram account is connected and synced with the app'**
  String get instagramConnectedStatus;

  /// No description provided for @instagramDisconnectedStatus.
  ///
  /// In en, this message translates to:
  /// **'Your Instagram account is not connected to the app'**
  String get instagramDisconnectedStatus;

  /// No description provided for @posts.
  ///
  /// In en, this message translates to:
  /// **'Posts'**
  String get posts;

  /// No description provided for @instagramDisclaimerText.
  ///
  /// In en, this message translates to:
  /// **'We never store your Instagram credentials and use them only to sync your public profile data.'**
  String get instagramDisclaimerText;

  /// No description provided for @yourBadges.
  ///
  /// In en, this message translates to:
  /// **'Your Badges'**
  String get yourBadges;

  /// No description provided for @earnBadgesDescription.
  ///
  /// In en, this message translates to:
  /// **'Complete tasks and connect your Instagram account to earn badges'**
  String get earnBadgesDescription;

  /// No description provided for @viewAllBadges.
  ///
  /// In en, this message translates to:
  /// **'View All Badges'**
  String get viewAllBadges;

  /// No description provided for @badgesEarned.
  ///
  /// In en, this message translates to:
  /// **'Badges Earned'**
  String get badgesEarned;

  /// No description provided for @goldBadges.
  ///
  /// In en, this message translates to:
  /// **'Gold'**
  String get goldBadges;

  /// No description provided for @silverBadges.
  ///
  /// In en, this message translates to:
  /// **'Silver'**
  String get silverBadges;

  /// No description provided for @bronzeBadges.
  ///
  /// In en, this message translates to:
  /// **'Bronze'**
  String get bronzeBadges;

  /// No description provided for @instagramBadges.
  ///
  /// In en, this message translates to:
  /// **'Instagram'**
  String get instagramBadges;

  /// No description provided for @achievementBadges.
  ///
  /// In en, this message translates to:
  /// **'Achievement'**
  String get achievementBadges;

  /// No description provided for @specialBadges.
  ///
  /// In en, this message translates to:
  /// **'Special'**
  String get specialBadges;

  /// No description provided for @badgeDetails.
  ///
  /// In en, this message translates to:
  /// **'Badge Details'**
  String get badgeDetails;

  /// No description provided for @category.
  ///
  /// In en, this message translates to:
  /// **'Category'**
  String get category;

  /// No description provided for @earned.
  ///
  /// In en, this message translates to:
  /// **'Earned'**
  String get earned;

  /// No description provided for @locked.
  ///
  /// In en, this message translates to:
  /// **'Locked'**
  String get locked;

  /// No description provided for @addedOn.
  ///
  /// In en, this message translates to:
  /// **'Added On'**
  String get addedOn;

  /// No description provided for @requirements.
  ///
  /// In en, this message translates to:
  /// **'Requirements to Earn'**
  String get requirements;

  /// No description provided for @specialRequirements.
  ///
  /// In en, this message translates to:
  /// **'This badge has special requirements'**
  String get specialRequirements;

  /// No description provided for @daysStreak.
  ///
  /// In en, this message translates to:
  /// **'Daily Streaks'**
  String get daysStreak;

  /// No description provided for @notificationsWillAppearHere.
  ///
  /// In en, this message translates to:
  /// **'Your notifications will appear here'**
  String get notificationsWillAppearHere;

  /// No description provided for @newBadgeEarned.
  ///
  /// In en, this message translates to:
  /// **'New Badge Earned'**
  String get newBadgeEarned;

  /// No description provided for @levelUp.
  ///
  /// In en, this message translates to:
  /// **'Level Up'**
  String get levelUp;

  /// No description provided for @coinsReceived.
  ///
  /// In en, this message translates to:
  /// **'Coins Received'**
  String get coinsReceived;

  /// No description provided for @instagramUpdate.
  ///
  /// In en, this message translates to:
  /// **'Instagram Update'**
  String get instagramUpdate;

  /// No description provided for @systemNotification.
  ///
  /// In en, this message translates to:
  /// **'System Notification'**
  String get systemNotification;

  /// No description provided for @notification.
  ///
  /// In en, this message translates to:
  /// **'Notification'**
  String get notification;

  /// No description provided for @month.
  ///
  /// In en, this message translates to:
  /// **'month'**
  String get month;

  /// No description provided for @months.
  ///
  /// In en, this message translates to:
  /// **'months'**
  String get months;

  /// No description provided for @day.
  ///
  /// In en, this message translates to:
  /// **'day'**
  String get day;

  /// No description provided for @hour.
  ///
  /// In en, this message translates to:
  /// **'hour'**
  String get hour;

  /// No description provided for @hours.
  ///
  /// In en, this message translates to:
  /// **'hours'**
  String get hours;

  /// No description provided for @minute.
  ///
  /// In en, this message translates to:
  /// **'minute'**
  String get minute;

  /// No description provided for @minutes.
  ///
  /// In en, this message translates to:
  /// **'minutes'**
  String get minutes;

  /// No description provided for @ago.
  ///
  /// In en, this message translates to:
  /// **'ago'**
  String get ago;

  /// No description provided for @justNow.
  ///
  /// In en, this message translates to:
  /// **'Just Now'**
  String get justNow;

  /// No description provided for @viewBadge.
  ///
  /// In en, this message translates to:
  /// **'View Badge'**
  String get viewBadge;

  /// No description provided for @viewProfile.
  ///
  /// In en, this message translates to:
  /// **'View Profile'**
  String get viewProfile;

  /// No description provided for @viewInstagram.
  ///
  /// In en, this message translates to:
  /// **'View Instagram'**
  String get viewInstagram;

  /// No description provided for @collectCoins.
  ///
  /// In en, this message translates to:
  /// **'Collect Coins'**
  String get collectCoins;

  /// No description provided for @view.
  ///
  /// In en, this message translates to:
  /// **'View'**
  String get view;

  /// No description provided for @markAllAsRead.
  ///
  /// In en, this message translates to:
  /// **'Mark All as Read'**
  String get markAllAsRead;

  /// No description provided for @allNotificationsMarkedAsRead.
  ///
  /// In en, this message translates to:
  /// **'All notifications marked as read'**
  String get allNotificationsMarkedAsRead;

  /// No description provided for @filterNotifications.
  ///
  /// In en, this message translates to:
  /// **'Filter Notifications'**
  String get filterNotifications;

  /// No description provided for @showBadgeNotifications.
  ///
  /// In en, this message translates to:
  /// **'Show Badge Notifications'**
  String get showBadgeNotifications;

  /// No description provided for @showLevelNotifications.
  ///
  /// In en, this message translates to:
  /// **'Show Level Notifications'**
  String get showLevelNotifications;

  /// No description provided for @showCoinNotifications.
  ///
  /// In en, this message translates to:
  /// **'Show Coin Notifications'**
  String get showCoinNotifications;

  /// No description provided for @showInstagramNotifications.
  ///
  /// In en, this message translates to:
  /// **'Show Instagram Notifications'**
  String get showInstagramNotifications;

  /// No description provided for @showSystemNotifications.
  ///
  /// In en, this message translates to:
  /// **'Show System Notifications'**
  String get showSystemNotifications;

  /// No description provided for @resetFilters.
  ///
  /// In en, this message translates to:
  /// **'Reset Filters'**
  String get resetFilters;

  /// No description provided for @apply.
  ///
  /// In en, this message translates to:
  /// **'Apply'**
  String get apply;

  /// No description provided for @coinsCollected.
  ///
  /// In en, this message translates to:
  /// **'Coins collected!'**
  String get coinsCollected;

  /// No description provided for @errorLoadingNotifications.
  ///
  /// In en, this message translates to:
  /// **'Error loading notifications'**
  String get errorLoadingNotifications;

  /// No description provided for @badgeNotifications.
  ///
  /// In en, this message translates to:
  /// **'Badge Notifications'**
  String get badgeNotifications;

  /// No description provided for @soundNotifications.
  ///
  /// In en, this message translates to:
  /// **'Sound Notifications'**
  String get soundNotifications;

  /// No description provided for @themeMode.
  ///
  /// In en, this message translates to:
  /// **'Theme Mode'**
  String get themeMode;

  /// No description provided for @systemTheme.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get systemTheme;

  /// No description provided for @privacyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy;

  /// No description provided for @termsOfService.
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfService;

  /// No description provided for @help.
  ///
  /// In en, this message translates to:
  /// **'Help'**
  String get help;

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'Version'**
  String get version;

  /// No description provided for @logoutConfirmationText.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to log out of your account?'**
  String get logoutConfirmationText;

  /// No description provided for @errorLoadingSettings.
  ///
  /// In en, this message translates to:
  /// **'Error loading settings'**
  String get errorLoadingSettings;

  /// No description provided for @integrations.
  ///
  /// In en, this message translates to:
  /// **'Integrations'**
  String get integrations;

  /// No description provided for @connected.
  ///
  /// In en, this message translates to:
  /// **'Connected'**
  String get connected;

  /// No description provided for @notConnected.
  ///
  /// In en, this message translates to:
  /// **'Not Connected'**
  String get notConnected;

  /// No description provided for @unknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown'**
  String get unknown;

  /// No description provided for @accountDetails.
  ///
  /// In en, this message translates to:
  /// **'Account Details'**
  String get accountDetails;

  /// No description provided for @errorLoadingProfile.
  ///
  /// In en, this message translates to:
  /// **'Error loading profile'**
  String get errorLoadingProfile;

  /// No description provided for @errorLoadingBadges.
  ///
  /// In en, this message translates to:
  /// **'Error loading badges'**
  String get errorLoadingBadges;

  /// No description provided for @errorLoadingPosts.
  ///
  /// In en, this message translates to:
  /// **'Error loading posts'**
  String get errorLoadingPosts;

  /// No description provided for @noPostsFound.
  ///
  /// In en, this message translates to:
  /// **'No posts found'**
  String get noPostsFound;

  /// No description provided for @connectInstagramBenefits.
  ///
  /// In en, this message translates to:
  /// **'Connect your Instagram account to track your posts, followers, and earn special badges'**
  String get connectInstagramBenefits;

  /// No description provided for @loadingInstagramData.
  ///
  /// In en, this message translates to:
  /// **'Loading Instagram data...'**
  String get loadingInstagramData;

  /// No description provided for @coinTransfer.
  ///
  /// In en, this message translates to:
  /// **'Diamond Transfer'**
  String get coinTransfer;

  /// No description provided for @currentBalance.
  ///
  /// In en, this message translates to:
  /// **'Current Balance'**
  String get currentBalance;

  /// No description provided for @transferDetails.
  ///
  /// In en, this message translates to:
  /// **'Transfer Details'**
  String get transferDetails;

  /// No description provided for @recipientUsername.
  ///
  /// In en, this message translates to:
  /// **'Recipient Username'**
  String get recipientUsername;

  /// No description provided for @enterRecipientUsername.
  ///
  /// In en, this message translates to:
  /// **'Enter recipient username'**
  String get enterRecipientUsername;

  /// No description provided for @pleaseEnterRecipientUsername.
  ///
  /// In en, this message translates to:
  /// **'Please enter recipient username'**
  String get pleaseEnterRecipientUsername;

  /// No description provided for @cannotTransferToYourself.
  ///
  /// In en, this message translates to:
  /// **'Cannot transfer to yourself'**
  String get cannotTransferToYourself;

  /// No description provided for @enterAmount.
  ///
  /// In en, this message translates to:
  /// **'Enter amount'**
  String get enterAmount;

  /// No description provided for @pleaseEnterAmount.
  ///
  /// In en, this message translates to:
  /// **'Please enter amount'**
  String get pleaseEnterAmount;

  /// No description provided for @pleaseEnterValidAmount.
  ///
  /// In en, this message translates to:
  /// **'Please enter a valid amount'**
  String get pleaseEnterValidAmount;

  /// No description provided for @insufficientBalance.
  ///
  /// In en, this message translates to:
  /// **'Insufficient balance'**
  String get insufficientBalance;

  /// No description provided for @note.
  ///
  /// In en, this message translates to:
  /// **'Note'**
  String get note;

  /// No description provided for @optional.
  ///
  /// In en, this message translates to:
  /// **'Optional'**
  String get optional;

  /// No description provided for @enterTransferNote.
  ///
  /// In en, this message translates to:
  /// **'Enter transfer note'**
  String get enterTransferNote;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Processing...'**
  String get processing;

  /// No description provided for @transferCoins.
  ///
  /// In en, this message translates to:
  /// **'Transfer Diamonds'**
  String get transferCoins;

  /// No description provided for @transferInformation.
  ///
  /// In en, this message translates to:
  /// **'Transfer Information'**
  String get transferInformation;

  /// No description provided for @transferInfo1.
  ///
  /// In en, this message translates to:
  /// **'Transfers are instant and cannot be reversed'**
  String get transferInfo1;

  /// No description provided for @transferInfo2.
  ///
  /// In en, this message translates to:
  /// **'Minimum transfer amount is 1 diamond'**
  String get transferInfo2;

  /// No description provided for @transferInfo3.
  ///
  /// In en, this message translates to:
  /// **'Make sure the recipient username is correct'**
  String get transferInfo3;

  /// No description provided for @transferSuccessful.
  ///
  /// In en, this message translates to:
  /// **'Transfer Successful'**
  String get transferSuccessful;

  /// No description provided for @coinsTransferredSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Diamonds transferred successfully!'**
  String get coinsTransferredSuccessfully;

  /// No description provided for @instagramConnectionFailed.
  ///
  /// In en, this message translates to:
  /// **'Instagram connection failed'**
  String get instagramConnectionFailed;

  /// No description provided for @monthly.
  ///
  /// In en, this message translates to:
  /// **'Monthly'**
  String get monthly;

  /// No description provided for @monthlyRanking.
  ///
  /// In en, this message translates to:
  /// **'Monthly Ranking'**
  String get monthlyRanking;

  /// No description provided for @you.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get you;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'tr'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'tr':
      return AppLocalizationsTr();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
