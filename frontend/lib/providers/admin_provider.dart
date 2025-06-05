import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:instagram_puan_app/services/api_client.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'dart:developer' as developer;

// Admin paneli için genel state
@immutable
class AdminState {
  final List<Map<String, dynamic>> users;
  final List<Map<String, dynamic>> orders;
  final List<Map<String, dynamic>> tasks;
  final List<Map<String, dynamic>> coinTransactions;
  final List<Map<String, dynamic>> adminLogs;

  final List<Map<String, dynamic>> filteredUsers;
  final List<Map<String, dynamic>> filteredOrders;
  final List<Map<String, dynamic>> filteredTasks;
  final List<Map<String, dynamic>> filteredCoinTransactions;
  final List<Map<String, dynamic>> filteredAdminLogs;

  final String userSearch;
  final String userFilter; // 'all', 'admin', 'user'
  final String userSortKey;
  final bool userSortAsc;

  final String orderSearch;
  final String orderFilter; // 'all', 'pending', 'active', 'completed', 'failed', 'cancelled'
  final String orderSortKey;
  final bool orderSortAsc;

  final String taskSearch;
  final String taskFilter; // 'all', 'pending', 'assigned', 'completed', 'failed', 'expired'
  final String taskSortKey;
  final bool taskSortAsc;

  final String coinTransactionSearch;
  final String coinTransactionFilter; // 'all', 'earn', 'spend', 'withdraw', 'admin_add', 'admin_remove'
  final String coinTransactionSortKey;
  final bool coinTransactionSortAsc;

  final String adminLogSearch;
  final String adminLogFilter; // 'all', 'user_ban', 'user_unban', 'coin_adjust', 'order_cancel', 'task_reset'
  final String adminLogSortKey;
  final bool adminLogSortAsc;


  const AdminState({
    this.users = const [],
    this.orders = const [],
    this.tasks = const [],
    this.coinTransactions = const [],
    this.adminLogs = const [],
    this.filteredUsers = const [],
    this.filteredOrders = const [],
    this.filteredTasks = const [],
    this.filteredCoinTransactions = const [],
    this.filteredAdminLogs = const [],
    this.userSearch = '',
    this.userFilter = 'all',
    this.userSortKey = 'id',
    this.userSortAsc = true,
    this.orderSearch = '',
    this.orderFilter = 'all',
    this.orderSortKey = 'id',
    this.orderSortAsc = true,
    this.taskSearch = '',
    this.taskFilter = 'all',
    this.taskSortKey = 'id',
    this.taskSortAsc = true,
    this.coinTransactionSearch = '',
    this.coinTransactionFilter = 'all',
    this.coinTransactionSortKey = 'id',
    this.coinTransactionSortAsc = true,
    this.adminLogSearch = '',
    this.adminLogFilter = 'all',
    this.adminLogSortKey = 'created_at',
    this.adminLogSortAsc = false,
  });

  AdminState copyWith({
    List<Map<String, dynamic>>? users,
    List<Map<String, dynamic>>? orders,
    List<Map<String, dynamic>>? tasks,
    List<Map<String, dynamic>>? coinTransactions,
    List<Map<String, dynamic>>? adminLogs,
    List<Map<String, dynamic>>? filteredUsers,
    List<Map<String, dynamic>>? filteredOrders,
    List<Map<String, dynamic>>? filteredTasks,
    List<Map<String, dynamic>>? filteredCoinTransactions,
    List<Map<String, dynamic>>? filteredAdminLogs,
    String? userSearch,
    String? userFilter,
    String? userSortKey,
    bool? userSortAsc,
    String? orderSearch,
    String? orderFilter,
    String? orderSortKey,
    bool? orderSortAsc,
    String? taskSearch,
    String? taskFilter,
    String? taskSortKey,
    bool? taskSortAsc,
    String? coinTransactionSearch,
    String? coinTransactionFilter,
    String? coinTransactionSortKey,
    bool? coinTransactionSortAsc,
    String? adminLogSearch,
    String? adminLogFilter,
    String? adminLogSortKey,
    bool? adminLogSortAsc,
  }) {
    return AdminState(
      users: users ?? this.users,
      orders: orders ?? this.orders,
      tasks: tasks ?? this.tasks,
      coinTransactions: coinTransactions ?? this.coinTransactions,
      adminLogs: adminLogs ?? this.adminLogs,
      filteredUsers: filteredUsers ?? this.filteredUsers,
      filteredOrders: filteredOrders ?? this.filteredOrders,
      filteredTasks: filteredTasks ?? this.filteredTasks,
      filteredCoinTransactions: filteredCoinTransactions ?? this.filteredCoinTransactions,
      filteredAdminLogs: filteredAdminLogs ?? this.filteredAdminLogs,
      userSearch: userSearch ?? this.userSearch,
      userFilter: userFilter ?? this.userFilter,
      userSortKey: userSortKey ?? this.userSortKey,
      userSortAsc: userSortAsc ?? this.userSortAsc,
      orderSearch: orderSearch ?? this.orderSearch,
      orderFilter: orderFilter ?? this.orderFilter,
      orderSortKey: orderSortKey ?? this.orderSortKey,
      orderSortAsc: orderSortAsc ?? this.orderSortAsc,
      taskSearch: taskSearch ?? this.taskSearch,
      taskFilter: taskFilter ?? this.taskFilter,
      taskSortKey: taskSortKey ?? this.taskSortKey,
      taskSortAsc: taskSortAsc ?? this.taskSortAsc,
      coinTransactionSearch: coinTransactionSearch ?? this.coinTransactionSearch,
      coinTransactionFilter: coinTransactionFilter ?? this.coinTransactionFilter,
      coinTransactionSortKey: coinTransactionSortKey ?? this.coinTransactionSortKey,
      coinTransactionSortAsc: coinTransactionSortAsc ?? this.coinTransactionSortAsc,
      adminLogSearch: adminLogSearch ?? this.adminLogSearch,
      adminLogFilter: adminLogFilter ?? this.adminLogFilter,
      adminLogSortKey: adminLogSortKey ?? this.adminLogSortKey,
      adminLogSortAsc: adminLogSortAsc ?? this.adminLogSortAsc,
    );
  }
}

class AdminNotifier extends StateNotifier<AsyncValue<AdminState>> {
  final ApiClient _apiClient;
  AdminState _internalState = const AdminState(); // Senkron state yönetimi için

  AdminNotifier(this._apiClient) : super(const AsyncLoading()) {
    fetchAllData();
  }

  Future<void> fetchAllData() async {
    state = const AsyncLoading();
    try {
      final users = await _apiClient.get('/admin/users');
      final orders = await _apiClient.get('/admin/orders');
      final tasks = await _apiClient.get('/admin/tasks');
      final coinTransactions = await _apiClient.get('/admin/coin-transactions');
      final adminLogs = await _apiClient.get('/admin/logs');

      _internalState = _internalState.copyWith(
        users: List<Map<String, dynamic>>.from(users['users'] ?? []),
        orders: List<Map<String, dynamic>>.from(orders['orders'] ?? []),
        tasks: List<Map<String, dynamic>>.from(tasks['tasks'] ?? []),
        coinTransactions: List<Map<String, dynamic>>.from(coinTransactions['transactions'] ?? []),
        adminLogs: List<Map<String, dynamic>>.from(adminLogs['logs'] ?? []),
      );
      _applyAllFiltersAndSorts();
      state = AsyncData(_internalState);
    } catch (e, s) {
      developer.log("AdminNotifier fetchAllData error: $e", name: 'AdminProvider', error: e, stackTrace: s);
      state = AsyncError(e, s);
    }
  }
  
  void _applyAllFiltersAndSorts() {
    _filterAndSortUsers();
    _filterAndSortOrders();
    _filterAndSortTasks();
    _filterAndSortCoinTransactions();
    _filterAndSortAdminLogs();
  }

  // USER operations
  void _filterAndSortUsers() {
    List<Map<String, dynamic>> temp = List.from(_internalState.users);
    if (_internalState.userSearch.isNotEmpty) {
      temp = temp.where((u) => 
        (u['username']?.toString().toLowerCase().contains(_internalState.userSearch.toLowerCase()) ?? false) ||
        (u['full_name']?.toString().toLowerCase().contains(_internalState.userSearch.toLowerCase()) ?? false) ||
        (u['email']?.toString().toLowerCase().contains(_internalState.userSearch.toLowerCase()) ?? false) || // Backend User modelinde email varsa
        (u['id']?.toString().contains(_internalState.userSearch) ?? false)
      ).toList();
    }
    if (_internalState.userFilter != 'all') {
       if (_internalState.userFilter == 'admin') {
        temp = temp.where((u) => u['is_admin_platform'] == true).toList();
      } else if (_internalState.userFilter == 'user') {
        temp = temp.where((u) => u['is_admin_platform'] != true).toList();
      } else if (_internalState.userFilter == 'banned') {
        temp = temp.where((u) => u['is_banned'] == true).toList();
      }
    }
    temp.sort((a, b) => _dynamicSort(a, b, _internalState.userSortKey, _internalState.userSortAsc));
    _internalState = _internalState.copyWith(filteredUsers: temp);
  }

  void searchUsers(String query) {
    _internalState = _internalState.copyWith(userSearch: query);
    _filterAndSortUsers();
    state = AsyncData(_internalState);
  }

  void filterUsers(String? filter) {
    if (filter == null) return;
    _internalState = _internalState.copyWith(userFilter: filter);
    _filterAndSortUsers();
    state = AsyncData(_internalState);
  }

  void sortUsers(String key, bool ascending) {
    _internalState = _internalState.copyWith(userSortKey: key, userSortAsc: ascending);
    _filterAndSortUsers();
    state = AsyncData(_internalState);
  }
  
  Future<void> toggleUserBan(int userId) async {
    try {
      await _apiClient.post('/admin/user/$userId/toggle-ban', {});
      await fetchAllData(); // Re-fetch to update state
    } catch (e) {
      // Handle error appropriately, maybe update state with error
      developer.log("Error toggling user ban: $e", name: 'AdminProvider');
    }
  }

  Future<void> adjustUserCoin(int userId, int amount) async {
    try {
      await _apiClient.post('/admin/user/$userId/adjust-coin', {'amount': amount});
      await fetchAllData();
    } catch (e) {
      developer.log("Error adjusting user coin: $e", name: 'AdminProvider');
    }
  }
  
  Future<void> toggleUserAdmin(int userId) async {
    try {
      await _apiClient.post('/admin/user/$userId/toggle-admin', {});
      await fetchAllData();
    } catch (e) {
      developer.log("Error toggling user admin status: $e", name: 'AdminProvider');
    }
  }


  // ORDER operations
  void _filterAndSortOrders() {
    List<Map<String, dynamic>> temp = List.from(_internalState.orders);
    if (_internalState.orderSearch.isNotEmpty) {
      temp = temp.where((o) => 
        (o['id']?.toString().contains(_internalState.orderSearch) ?? false) ||
        (o['user_id']?.toString().contains(_internalState.orderSearch) ?? false) ||
        (o['post_url']?.toString().toLowerCase().contains(_internalState.orderSearch.toLowerCase()) ?? false) ||
        (o['order_type']?.toString().toLowerCase().contains(_internalState.orderSearch.toLowerCase()) ?? false)
      ).toList();
    }
    if (_internalState.orderFilter != 'all') {
      temp = temp.where((o) => o['status'] == _internalState.orderFilter).toList();
    }
    temp.sort((a, b) => _dynamicSort(a, b, _internalState.orderSortKey, _internalState.orderSortAsc));
    _internalState = _internalState.copyWith(filteredOrders: temp);
  }
  void searchOrders(String query) {
    _internalState = _internalState.copyWith(orderSearch: query);
    _filterAndSortOrders();
    state = AsyncData(_internalState);
  }
  void filterOrders(String? filter) {
    if (filter == null) return;
    _internalState = _internalState.copyWith(orderFilter: filter);
    _filterAndSortOrders();
    state = AsyncData(_internalState);
  }
  void sortOrders(String key, bool ascending) {
    _internalState = _internalState.copyWith(orderSortKey: key, orderSortAsc: ascending);
    _filterAndSortOrders();
    state = AsyncData(_internalState);
  }

  // TASK operations
  void _filterAndSortTasks() {
    List<Map<String, dynamic>> temp = List.from(_internalState.tasks);
     if (_internalState.taskSearch.isNotEmpty) {
      temp = temp.where((t) => 
        (t['id']?.toString().contains(_internalState.taskSearch) ?? false) ||
        (t['order_id']?.toString().contains(_internalState.taskSearch) ?? false) ||
        (t['assigned_user_id']?.toString().contains(_internalState.taskSearch) ?? false) ||
        (t['status']?.toString().toLowerCase().contains(_internalState.taskSearch.toLowerCase()) ?? false)
      ).toList();
    }
    if (_internalState.taskFilter != 'all') {
      temp = temp.where((t) => t['status'] == _internalState.taskFilter).toList();
    }
    temp.sort((a,b) => _dynamicSort(a, b, _internalState.taskSortKey, _internalState.taskSortAsc));
    _internalState = _internalState.copyWith(filteredTasks: temp);
  }
  void searchTasks(String query) {
    _internalState = _internalState.copyWith(taskSearch: query);
    _filterAndSortTasks();
    state = AsyncData(_internalState);
  }
  void filterTasks(String? filter) {
     if (filter == null) return;
    _internalState = _internalState.copyWith(taskFilter: filter);
    _filterAndSortTasks();
    state = AsyncData(_internalState);
  }
  void sortTasks(String key, bool ascending) {
    _internalState = _internalState.copyWith(taskSortKey: key, taskSortAsc: ascending);
    _filterAndSortTasks();
    state = AsyncData(_internalState);
  }


  // COIN TRANSACTION operations
  void _filterAndSortCoinTransactions() {
    List<Map<String, dynamic>> temp = List.from(_internalState.coinTransactions);
    if (_internalState.coinTransactionSearch.isNotEmpty) {
      temp = temp.where((t) => 
        (t['id']?.toString().contains(_internalState.coinTransactionSearch) ?? false) ||
        (t['user_id']?.toString().contains(_internalState.coinTransactionSearch) ?? false) ||
        (t['transaction_type']?.toString().toLowerCase().contains(_internalState.coinTransactionSearch.toLowerCase()) ?? false) ||
        (t['related_order_id']?.toString().contains(_internalState.coinTransactionSearch) ?? false) ||
        (t['related_task_id']?.toString().contains(_internalState.coinTransactionSearch) ?? false) ||
        (t['description']?.toString().toLowerCase().contains(_internalState.coinTransactionSearch.toLowerCase()) ?? false)
      ).toList();
    }
    if (_internalState.coinTransactionFilter != 'all') {
      temp = temp.where((t) => t['transaction_type'] == _internalState.coinTransactionFilter).toList();
    }
    temp.sort((a,b) => _dynamicSort(a, b, _internalState.coinTransactionSortKey, _internalState.coinTransactionSortAsc));
    _internalState = _internalState.copyWith(filteredCoinTransactions: temp);
  }

  void searchCoinTransactions(String query) {
    _internalState = _internalState.copyWith(coinTransactionSearch: query);
    _filterAndSortCoinTransactions();
    state = AsyncData(_internalState);
  }
  void filterCoinTransactions(String? filter) {
    if (filter == null) return;
    _internalState = _internalState.copyWith(coinTransactionFilter: filter);
    _filterAndSortCoinTransactions();
    state = AsyncData(_internalState);
  }
  void sortCoinTransactions(String key, bool ascending) {
    _internalState = _internalState.copyWith(coinTransactionSortKey: key, coinTransactionSortAsc: ascending);
    _filterAndSortCoinTransactions();
    state = AsyncData(_internalState);
  }

  // ADMIN LOG operations
   void _filterAndSortAdminLogs() {
    List<Map<String, dynamic>> temp = List.from(_internalState.adminLogs);
    if (_internalState.adminLogSearch.isNotEmpty) {
      temp = temp.where((l) => 
        (l['id']?.toString().contains(_internalState.adminLogSearch) ?? false) ||
        (l['admin_username']?.toString().toLowerCase().contains(_internalState.adminLogSearch.toLowerCase()) ?? false) ||
        (l['target_username']?.toString().toLowerCase().contains(_internalState.adminLogSearch.toLowerCase()) ?? false) ||
        (l['action']?.toString().toLowerCase().contains(_internalState.adminLogSearch.toLowerCase()) ?? false) ||
        (l['description']?.toString().toLowerCase().contains(_internalState.adminLogSearch.toLowerCase()) ?? false)
      ).toList();
    }
    if (_internalState.adminLogFilter != 'all') {
      temp = temp.where((l) => l['action'] == _internalState.adminLogFilter).toList();
    }
    temp.sort((a,b) => _dynamicSort(a, b, _internalState.adminLogSortKey, _internalState.adminLogSortAsc));
    _internalState = _internalState.copyWith(filteredAdminLogs: temp);
  }
  void searchAdminLogs(String query) {
    _internalState = _internalState.copyWith(adminLogSearch: query);
    _filterAndSortAdminLogs();
    state = AsyncData(_internalState);
  }
  void filterAdminLogs(String? filter) {
    if (filter == null) return;
    _internalState = _internalState.copyWith(adminLogFilter: filter);
    _filterAndSortAdminLogs();
    state = AsyncData(_internalState);
  }
  void sortAdminLogs(String key, bool ascending) {
    _internalState = _internalState.copyWith(adminLogSortKey: key, adminLogSortAsc: ascending);
    _filterAndSortAdminLogs();
    state = AsyncData(_internalState);
  }

  Future<void> rollbackAction(int logId) async {
    try {
      await _apiClient.post('/admin/log/$logId/rollback', {});
      await fetchAllData();
    } catch (e) {
      developer.log("Error rolling back action: $e", name: 'AdminProvider');
    }
  }
  
  // Helper for sorting
  int _dynamicSort(Map<String, dynamic> a, Map<String, dynamic> b, String key, bool ascending) {
    dynamic valA = a[key];
    dynamic valB = b[key];

    if (valA == null && valB == null) return 0;
    if (valA == null) return ascending ? -1 : 1;
    if (valB == null) return ascending ? 1 : -1;

    int compareResult;
    if (valA is Comparable && valB is Comparable) {
      compareResult = valA.compareTo(valB);
    } else {
      compareResult = valA.toString().compareTo(valB.toString());
    }
    return ascending ? compareResult : -compareResult;
  }

  // UI Helper methods (moved from AdminPanelScreen) - Can be expanded
  List<DataColumn> userColumns(BuildContext context, Function(String, bool)? onSort, [bool forExport = false]) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DataColumn(label: Text(localizations.id), onSort: forExport ? null : (i, asc) => onSort?.call('id', asc)),
      DataColumn(label: Text(localizations.username), onSort: forExport ? null : (i, asc) => onSort?.call('username', asc)),
      DataColumn(label: Text(localizations.fullName), onSort: forExport ? null : (i, asc) => onSort?.call('full_name', asc)),
      DataColumn(label: Text(localizations.platformAdmin), onSort: forExport ? null : (i, asc) => onSort?.call('is_admin_platform', asc)),
      DataColumn(label: Text(localizations.banned), onSort: forExport ? null : (i, asc) => onSort?.call('is_banned', asc)),
      DataColumn(label: Text(localizations.coin), onSort: forExport ? null : (i, asc) => onSort?.call('coin', asc)),
      if (!forExport) DataColumn(label: Text(localizations.actions)),
    ];
  }

  List<DataRow> userRows(BuildContext context, List<Map<String,dynamic>> users, Function(BuildContext, Map<String,dynamic>) onActions) {
     final localizations = AppLocalizations.of(context);
     
    return users.map((user) => DataRow(cells: [
      DataCell(Text(user['id']?.toString() ?? 'N/A')),
      DataCell(Text(user['username'] ?? 'N/A')),
      DataCell(Text(user['full_name'] ?? 'N/A')),
      DataCell(Text(user['is_admin_platform'] == true ? localizations.yes : localizations.no)),
      DataCell(Text(user['is_banned'] == true ? localizations.yes : localizations.no)),
      DataCell(Text(user['coin']?.toString() ?? '0')),
      DataCell(IconButton(icon: const Icon(Icons.more_vert), onPressed: () => onActions(context, user))),
    ])).toList();
  }
  
  List<DropdownMenuItem<String>> userFilterItems(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DropdownMenuItem(value: 'all', child: Text(localizations.all)),
      DropdownMenuItem(value: 'admin', child: Text(localizations.admins)),
      DropdownMenuItem(value: 'user', child: Text(localizations.users)),
      DropdownMenuItem(value: 'banned', child: Text(localizations.bannedUsers)),
    ];
  }
  
  List<DataColumn> orderColumns(BuildContext context, Function(String, bool)? onSort, [bool forExport = false]) {
    final localizations = AppLocalizations.of(context);
    
    return [
        DataColumn(label: Text(localizations.id), onSort: forExport ? null : (i, asc) => onSort?.call('id', asc)),
        DataColumn(label: Text(localizations.user), onSort: forExport ? null : (i, asc) => onSort?.call('user_id', asc)),
        DataColumn(label: Text(localizations.postUrl), onSort: forExport ? null : (i, asc) => onSort?.call('post_url', asc)),
        DataColumn(label: Text(localizations.orderType), onSort: forExport ? null : (i, asc) => onSort?.call('order_type', asc)),
        DataColumn(label: Text(localizations.targetCount), onSort: forExport ? null : (i, asc) => onSort?.call('target_count', asc)),
        DataColumn(label: Text(localizations.completedCount), onSort: forExport ? null : (i, asc) => onSort?.call('completed_count', asc)),
        DataColumn(label: Text(localizations.status), onSort: forExport ? null : (i, asc) => onSort?.call('status', asc)),
        DataColumn(label: Text(localizations.createdAt), onSort: forExport ? null : (i, asc) => onSort?.call('created_at', asc)),
    ];
  }

  List<DataRow> orderRows(BuildContext context, List<Map<String,dynamic>> orders) {
    return orders.map((order) => DataRow(cells: [
      DataCell(Text(order['id']?.toString() ?? 'N/A')),
      DataCell(Text(order['user_id']?.toString() ?? 'N/A')),
      DataCell(SelectableText(order['post_url'] ?? 'N/A')),
      DataCell(Text(order['order_type'] ?? 'N/A')),
      DataCell(Text(order['target_count']?.toString() ?? 'N/A')),
      DataCell(Text(order['completed_count']?.toString() ?? 'N/A')),
      DataCell(Text(order['status'] ?? 'N/A')),
      DataCell(Text(order['created_at']?.toString() ?? 'N/A')),
    ])).toList();
  }

  List<DropdownMenuItem<String>> orderFilterItems(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DropdownMenuItem(value: 'all', child: Text(localizations.orderFilterStatusAll)),
      DropdownMenuItem(value: 'pending', child: Text(localizations.orderFilterStatusPending)),
      DropdownMenuItem(value: 'active', child: Text(localizations.orderFilterStatusActive)),
      DropdownMenuItem(value: 'completed', child: Text(localizations.orderFilterStatusCompleted)),
      DropdownMenuItem(value: 'failed', child: Text(localizations.orderFilterStatusFailed)),
      DropdownMenuItem(value: 'cancelled', child: Text(localizations.orderFilterStatusCancelled)),
    ];
  }


  List<DataColumn> taskColumns(BuildContext context, Function(String, bool)? onSort, [bool forExport = false]) {
    final localizations = AppLocalizations.of(context);
    
    return [
        DataColumn(label: Text(localizations.id), onSort: forExport ? null : (i, asc) => onSort?.call('id', asc)),
        DataColumn(label: Text(localizations.orderId), onSort: forExport ? null : (i, asc) => onSort?.call('order_id', asc)),
        DataColumn(label: Text(localizations.assignedUser), onSort: forExport ? null : (i, asc) => onSort?.call('assigned_user_id', asc)),
        DataColumn(label: Text(localizations.status), onSort: forExport ? null : (i, asc) => onSort?.call('status', asc)),
        DataColumn(label: Text(localizations.assignedAt), onSort: forExport ? null : (i, asc) => onSort?.call('assigned_at', asc)),
        DataColumn(label: Text(localizations.expiresAtLabel)), // label-only
        DataColumn(label: Text(localizations.completedAtLabel)), // label-only
    ];
  }
  List<DataRow> taskRows(BuildContext context, List<Map<String,dynamic>> tasks) {
     return tasks.map((task) => DataRow(cells: [
      DataCell(Text(task['id']?.toString() ?? 'N/A')),
      DataCell(Text(task['order_id']?.toString() ?? 'N/A')),
      DataCell(Text(task['assigned_user_id']?.toString() ?? 'N/A')),
      DataCell(Text(task['status'] ?? 'N/A')),
      DataCell(Text(task['assigned_at']?.toString() ?? 'N/A')),
      DataCell(Text(task['expires_at']?.toString() ?? 'N/A')),
      DataCell(Text(task['completed_at']?.toString() ?? 'N/A')),
    ])).toList();
  }
   List<DropdownMenuItem<String>> taskFilterItems(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DropdownMenuItem(value: 'all', child: Text(localizations.taskFilterStatusAll)),
      DropdownMenuItem(value: 'pending', child: Text(localizations.taskFilterStatusPending)),
      DropdownMenuItem(value: 'assigned', child: Text(localizations.taskFilterStatusAssigned)),
      DropdownMenuItem(value: 'completed', child: Text(localizations.taskFilterStatusCompleted)),
      DropdownMenuItem(value: 'failed', child: Text(localizations.taskFilterStatusFailed)),
      DropdownMenuItem(value: 'expired', child: Text(localizations.taskFilterStatusExpired)),
    ];
  }

  List<DataColumn> coinTransactionColumns(BuildContext context, Function(String, bool)? onSort, [bool forExport = false]) {
    final localizations = AppLocalizations.of(context);
    
    return [
        DataColumn(label: Text(localizations.id), onSort: forExport ? null : (i, asc) => onSort?.call('id', asc)),
        DataColumn(label: Text(localizations.userId), onSort: forExport ? null : (i, asc) => onSort?.call('user_id', asc)),
        DataColumn(label: Text(localizations.transactionType), onSort: forExport ? null : (i, asc) => onSort?.call('transaction_type', asc)),
        DataColumn(label: Text(localizations.amount), onSort: forExport ? null : (i, asc) => onSort?.call('amount', asc)),
        DataColumn(label: Text(localizations.balanceAfter), onSort: forExport ? null : (i, asc) => onSort?.call('balance_after', asc)),
        DataColumn(label: Text(localizations.description), onSort: forExport ? null : (i, asc) => onSort?.call('description', asc)),
        DataColumn(label: Text(localizations.createdAt), onSort: forExport ? null : (i, asc) => onSort?.call('created_at', asc)),
    ];
  }
  List<DataRow> coinTransactionRows(BuildContext context, List<Map<String,dynamic>> transactions) {
    return transactions.map((tr) => DataRow(cells: [
      DataCell(Text(tr['id']?.toString() ?? 'N/A')),
      DataCell(Text(tr['user_id']?.toString() ?? 'N/A')),
      DataCell(Text(tr['transaction_type'] ?? 'N/A')),
      DataCell(Text(tr['amount']?.toString() ?? 'N/A')),
      DataCell(Text(tr['balance_after']?.toString() ?? 'N/A')),
      DataCell(Text(tr['description'] ?? 'N/A')),
      DataCell(Text(tr['created_at']?.toString() ?? 'N/A')),
    ])).toList();
  }
  List<DropdownMenuItem<String>> coinTransactionFilterItems(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DropdownMenuItem(value: 'all', child: Text(localizations.coinTransactionFilterAll)),
      DropdownMenuItem(value: 'earn', child: Text(localizations.coinTransactionFilterEarn)),
      DropdownMenuItem(value: 'spend', child: Text(localizations.coinTransactionFilterSpend)),
      DropdownMenuItem(value: 'withdraw', child: Text(localizations.coinTransactionFilterWithdraw)),
      DropdownMenuItem(value: 'admin_add', child: Text(localizations.coinTransactionFilterAdminAdd)),
      DropdownMenuItem(value: 'admin_remove', child: Text(localizations.coinTransactionFilterAdminRemove)),
    ];
  }


  List<DataColumn> adminLogColumns(BuildContext context, Function(String, bool)? onSort, [bool forExport = false]) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DataColumn(label: Text(localizations.id), onSort: forExport ? null : (i, asc) => onSort?.call('id', asc)),
      DataColumn(label: Text(localizations.adminUsername), onSort: forExport ? null : (i, asc) => onSort?.call('admin_username', asc)),
      DataColumn(label: Text(localizations.targetUsername), onSort: forExport ? null : (i, asc) => onSort?.call('target_username', asc)),
      DataColumn(label: Text(localizations.action), onSort: forExport ? null : (i, asc) => onSort?.call('action', asc)),
      DataColumn(label: Text(localizations.description), onSort: forExport ? null : (i, asc) => onSort?.call('description', asc)),
      DataColumn(label: Text(localizations.createdAt), onSort: forExport ? null : (i, asc) => onSort?.call('created_at', asc)),
      if (!forExport) DataColumn(label: Text(localizations.details)),
      if (!forExport) DataColumn(label: Text(localizations.rollback)),
    ];
  }
  List<DataRow> adminLogRows(BuildContext context, List<Map<String,dynamic>> logs, Function(BuildContext, Map<String,dynamic>) onDetails, Function(BuildContext, Map<String,dynamic>) onRollback) {
    return logs.map((log) => DataRow(cells: [
      DataCell(Text(log['id']?.toString() ?? 'N/A')),
      DataCell(Text(log['admin_username'] ?? 'N/A')),
      DataCell(Text(log['target_username'] ?? 'N/A')),
      DataCell(Text(log['action'] ?? 'N/A')),
      DataCell(SelectableText(log['description'] ?? 'N/A')),
      DataCell(Text(log['created_at'] ?? 'N/A')),
      DataCell(IconButton(icon: const Icon(Icons.info_outline), onPressed: () => onDetails(context, log))),
      DataCell(
        log['can_rollback'] == true
        ? IconButton(icon: const Icon(Icons.undo, color: Colors.orange), onPressed: () => onRollback(context, log))
        : Container()
      ),
    ])).toList();
  }
  List<DropdownMenuItem<String>> adminLogFilterItems(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    
    return [
      DropdownMenuItem(value: 'all', child: Text(localizations.adminLogFilterAll)),
      DropdownMenuItem(value: 'user_ban', child: Text(localizations.logActionUserBan)),
      DropdownMenuItem(value: 'user_unban', child: Text(localizations.logActionUserUnban)),
      DropdownMenuItem(value: 'coin_adjust', child: Text(localizations.logActionCoinAdjust)),
      DropdownMenuItem(value: 'admin_promote', child: Text(localizations.logActionAdminPromote)),
      DropdownMenuItem(value: 'admin_demote', child: Text(localizations.logActionAdminDemote)),
    ];
  }

}

final adminDataProvider = StateNotifierProvider<AdminNotifier, AsyncValue<AdminState>>((ref) {
  final apiClient = ref.watch(apiClientProvider); // ApiClient provider'ı global olmalı
  return AdminNotifier(apiClient);
});

// Global apiClientProvider (eğer yoksa)
// final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
// Bu zaten notification_provider.dart içinde vardı, eğer aynıysa tekrar tanımlamaya gerek yok.
// Emin olmak için global bir yerde tanımlanmalı, örneğin services/api_client.dart içinde. 