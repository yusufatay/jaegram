import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';

import 'package:instagram_puan_app/providers/admin_provider.dart';
import 'package:instagram_puan_app/providers/user_provider.dart';

class AdminPanelScreen extends ConsumerStatefulWidget {
  const AdminPanelScreen({super.key});

  @override
  ConsumerState<AdminPanelScreen> createState() => _AdminPanelScreenState();
}

class _AdminPanelScreenState extends ConsumerState<AdminPanelScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  WebSocketChannel? _logChannel;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _connectLogWebSocket();
  }

  void _connectLogWebSocket() {
    final userToken = ref.read(userProvider).value?.token;

    if (userToken == null) {
      return;
    }
    try {
      _logChannel = WebSocketChannel.connect(Uri.parse('wss://jaegram-production.up.railway.app/ws/admin/logs?token=$userToken'));
      _logChannel!.stream.listen(
        (event) async {
          await ref.refresh(adminDataProvider);
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(AppLocalizations.of(context).newLogArrived)),
            );
          }        },
        onError: (error) {
          // WebSocket error - handle gracefully
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(AppLocalizations.of(context).webSocketConnectionError)),
            );
          }
       },
        onDone: () {
          // WebSocket connection closed
        }
      );
    } catch (e) {
       // WebSocket connection failed - handle gracefully
       if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(AppLocalizations.of(context).webSocketConnectionError)),
            );
       }
    }
  }

  @override
  void dispose() {
    _logChannel?.sink.close();
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final adminDataAsync = ref.watch(adminDataProvider);
    final adminNotifier = ref.read(adminDataProvider.notifier);
    final localizations = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.adminPanel),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: [
            Tab(text: localizations.users),
            Tab(text: localizations.orders),
            Tab(text: localizations.tasks),
            Tab(text: localizations.coinTransactions),
            Tab(text: localizations.logs),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
              onPressed: () async {
            await ref.refresh(adminDataProvider);
          },
            tooltip: localizations.refresh,
          ),
        ],
      ),
      body: adminDataAsync.when(
        data: (adminState) {
          return TabBarView(
            controller: _tabController,
            children: [
              _buildDataTable(
                context: context,
                columns: adminNotifier.userColumns(context, (key, asc) => adminNotifier.sortUsers(key, asc)),
                rows: adminNotifier.userRows(context, adminState.filteredUsers, _showUserActionsDialog),
                searchHint: localizations.searchInUsers,
                onSearchChanged: adminNotifier.searchUsers,
                currentSearchTerm: adminState.userSearch,
                filterValue: adminState.userFilter,
                filterItems: adminNotifier.userFilterItems(context),
                onFilterChanged: adminNotifier.filterUsers,
                exportToCsvCallback: () => _exportToCsv(context, 'users', adminState.users, adminNotifier.userColumns(context, null, true)),
              ),
              _buildDataTable(
                context: context,
                columns: adminNotifier.orderColumns(context, (key, asc) => adminNotifier.sortOrders(key, asc)),
                rows: adminNotifier.orderRows(context, adminState.filteredOrders),
                searchHint: localizations.searchInOrders,
                onSearchChanged: adminNotifier.searchOrders,
                currentSearchTerm: adminState.orderSearch,
                filterValue: adminState.orderFilter,
                filterItems: adminNotifier.orderFilterItems(context),
                onFilterChanged: adminNotifier.filterOrders,
                exportToCsvCallback: () => _exportToCsv(context, 'orders', adminState.orders, adminNotifier.orderColumns(context, null, true)),
              ),
              _buildDataTable(
                context: context,
                columns: adminNotifier.taskColumns(context, (key, asc) => adminNotifier.sortTasks(key, asc)),
                rows: adminNotifier.taskRows(context, adminState.filteredTasks),
                searchHint: localizations.searchInTasks,
                onSearchChanged: adminNotifier.searchTasks,
                currentSearchTerm: adminState.taskSearch,
                filterValue: adminState.taskFilter,
                filterItems: adminNotifier.taskFilterItems(context),
                onFilterChanged: adminNotifier.filterTasks,
                exportToCsvCallback: () => _exportToCsv(context, 'tasks', adminState.tasks, adminNotifier.taskColumns(context, null, true)),
              ),
              _buildDataTable(
                context: context,
                columns: adminNotifier.coinTransactionColumns(context, (key, asc) => adminNotifier.sortCoinTransactions(key, asc)),
                rows: adminNotifier.coinTransactionRows(context, adminState.filteredCoinTransactions),
                searchHint: localizations.searchInCoinTransactions,
                onSearchChanged: adminNotifier.searchCoinTransactions,
                currentSearchTerm: adminState.coinTransactionSearch,
                filterValue: adminState.coinTransactionFilter,
                filterItems: adminNotifier.coinTransactionFilterItems(context),
                onFilterChanged: adminNotifier.filterCoinTransactions,
                exportToCsvCallback: () => _exportToCsv(context, 'coin_transactions', adminState.coinTransactions, adminNotifier.coinTransactionColumns(context, null, true)),
              ),
              _buildDataTable(
                context: context,
                columns: adminNotifier.adminLogColumns(context, (key, asc) => adminNotifier.sortAdminLogs(key, asc)),
                rows: adminNotifier.adminLogRows(context, adminState.filteredAdminLogs, _showLogDetailsDialog, _showRollbackDialog),
                searchHint: localizations.searchInLogs,
                onSearchChanged: adminNotifier.searchAdminLogs,
                currentSearchTerm: adminState.adminLogSearch,
                filterValue: adminState.adminLogFilter,
                filterItems: adminNotifier.adminLogFilterItems(context),
                onFilterChanged: adminNotifier.filterAdminLogs,
                exportToCsvCallback: () => _exportToCsv(context, 'admin_logs', adminState.adminLogs, adminNotifier.adminLogColumns(context, null, true)),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('${localizations.error}: $e\n$s', style: const TextStyle(color: Colors.red))),
      ),
    );
  }

  Widget _buildDataTable({
    required BuildContext context,
    required List<DataColumn> columns,
    required List<DataRow> rows,
    required String searchHint,
    required ValueChanged<String> onSearchChanged,
    required String currentSearchTerm,
    String? filterValue,
    List<DropdownMenuItem<String>>? filterItems,
    ValueChanged<String?>? onFilterChanged,
    VoidCallback? exportToCsvCallback,
  }) {
    final localizations = AppLocalizations.of(context);
    
    final TextEditingController searchController = TextEditingController(text: currentSearchTerm);
    searchController.addListener(() {
        final String text = searchController.text;
        searchController.value = searchController.value.copyWith(
            text: text,
            selection: TextSelection(baseOffset: text.length, extentOffset: text.length),
            composing: TextRange.empty,
        );
    });

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: searchController,
                  decoration: InputDecoration(
                    labelText: searchHint,
                    prefixIcon: const Icon(Icons.search),
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: onSearchChanged,
                ),
              ),
              if (filterValue != null && filterItems != null && onFilterChanged != null) ...[
                const SizedBox(width: 12),
                DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: filterValue,
                    items: filterItems,
                    onChanged: onFilterChanged,
                  ),
                ),
              ],
              if (exportToCsvCallback != null) ...[
                const SizedBox(width: 12),
                ElevatedButton.icon(
                  icon: const Icon(Icons.download_outlined),
                  label: Text(localizations.exportCsvShort),
                  onPressed: exportToCsvCallback,
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 12)),
                ),
              ]
            ],
          ),
        ),
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SingleChildScrollView(
              scrollDirection: Axis.vertical,
              child: DataTable(
                columns: columns,
                rows: rows,
                sortAscending: true,
                sortColumnIndex: null,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _exportToCsv(BuildContext context, String fileNamePrefix, List<Map<String, dynamic>> data, List<DataColumn> columnsForHeader) async {
    if (data.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(AppLocalizations.of(context).noDataToExport)),
      );
      return;
    }

    final headers = columnsForHeader.map((col) {
      if (col.label is Text) {
        return (col.label as Text).data ?? '';
      }
      return '';
    }).where((header) => header.isNotEmpty && header != AppLocalizations.of(context).actions && header != AppLocalizations.of(context).details && header != AppLocalizations.of(context).rollback )
    .toList();

    List<List<dynamic>> csvDataList = [headers];
    List<List<dynamic>> rowsForCsv = data.map((item) {
      return headers.map((header) {
        final localizations = AppLocalizations.of(context);
        String fieldName = '';
        if(header == localizations.id) {
          fieldName = 'id';
        } else if(header == localizations.username) {
          fieldName = 'username';
        } else if(header == localizations.fullName) {
          fieldName = 'full_name';
        } else if(header == localizations.platformAdmin) {
          fieldName = 'is_admin_platform';
        } else if(header == localizations.banned) {
          fieldName = 'is_banned';
        } else if(header == localizations.coin) {
          fieldName = 'coin';
        } else if(header == localizations.user) {
          fieldName = 'user_id';
        } else if(header == localizations.postUrl) {
          fieldName = 'post_url';
        } else if(header == localizations.orderType) {
          fieldName = 'order_type';
        } else if(header == localizations.targetCount) {
          fieldName = 'target_count';
        } else if(header == localizations.completedCount) {
          fieldName = 'completed_count';
        } else if(header == localizations.status) {
          fieldName = 'status';
        } else if(header == localizations.createdAt) {
          fieldName = 'created_at';
        } else if(header == localizations.orderId) {
          fieldName = 'order_id';
        } else if(header == localizations.assignedUser) {
          fieldName = 'assigned_user_id';
        } else if(header == localizations.assignedAt) {
          fieldName = 'assigned_at';
        } else if(header == localizations.expiresAtLabel) {
          fieldName = 'expires_at';
        } else if(header == localizations.completedAt) {
          fieldName = 'completed_at';
        } else if(header == localizations.userId) {
          fieldName = 'user_id';
        } else if(header == localizations.transactionType) {
          fieldName = 'transaction_type';
        } else if(header == localizations.amount) {
          fieldName = 'amount';
        } else if(header == localizations.balanceAfter) {
          fieldName = 'balance_after';
        } else if(header == localizations.description) {
          fieldName = 'description';
        } else if(header == localizations.adminUsername) {
          fieldName = 'admin_username';
        } else if(header == localizations.targetUsername) {
          fieldName = 'target_username';
        } else if(header == localizations.action) {
          fieldName = 'action';
        }

        var value = item[fieldName];
         if (value is List || value is Map) {
          return jsonEncode(value);
        }
        return value?.toString() ?? '';

      }).toList();
    }).toList();
    csvDataList.addAll(rowsForCsv); // Add rows to CSV list
  } // End of _exportToCsv function

  void _showUserActionsDialog(BuildContext context, Map<String, dynamic> user) {
  final localizations = AppLocalizations.of(context);
  final adminNotifier = ref.read(adminDataProvider.notifier);
  showDialog(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(localizations.userActionsFor(user['username'] ?? 'N/A')),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.block, color: user['is_banned'] == true ? Colors.green : Colors.red),
              title: Text(user['is_banned'] == true ? localizations.unbanUser : localizations.banUser),
              onTap: () async {
                Navigator.pop(ctx);
                final confirm = await _showConfirmationDialog(
                  context,
                  title: user['is_banned'] == true ? localizations.confirmUnban : localizations.confirmBan,
                  content: localizations.areYouSureBan(user['username'] ?? 'N/A', user['is_banned'] == true ? localizations.unbanVerb.toLowerCase() : localizations.banVerb.toLowerCase()),
                );
                if (confirm == true) {
                  await adminNotifier.toggleUserBan(user['id'] as int); // Use local adminNotifier
                }
              },
            ),
            ListTile(
              leading: const Icon(Icons.diamond, color: Colors.blue),
              title: Text(localizations.addRemoveCoin),
              onTap: () async {
                Navigator.pop(ctx);
                final controller = TextEditingController();
                final amount = await showDialog<int>(
                  context: context,
                  builder: (dCtx) => AlertDialog(
                    title: Text(localizations.addRemoveCoinFor(user['username'] ?? 'N/A')),
                    content: TextField(
                      controller: controller,
                      decoration: InputDecoration(labelText: localizations.coinAmountInfo),
                      keyboardType: const TextInputType.numberWithOptions(signed: true),
                    ),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(dCtx), child: Text(localizations.cancel)),
                      TextButton(
                        onPressed: () => Navigator.pop(dCtx, int.tryParse(controller.text)),
                        child: Text(localizations.confirm),
                      ),
                    ],
                  ),
                );
                if (amount != null && amount != 0) {
                  await adminNotifier.adjustUserCoin(user['id'] as int, amount); // Use local adminNotifier
                }
              },
            ),
            if (user['is_admin'] != true)
             ListTile(
              leading: Icon(Icons.admin_panel_settings, color: user['is_admin_platform'] == true ? Colors.grey : Colors.blue),
              title: Text(user['is_admin_platform'] == true ? localizations.demoteFromAdmin : localizations.promoteToAdmin),
              onTap: () async {
                Navigator.pop(ctx);
                 final confirm = await _showConfirmationDialog(
                  context,
                  title: user['is_admin_platform'] == true ? localizations.confirmDemote : localizations.confirmPromote,
                  content: localizations.areYouSureAdmin(user['username'] ?? 'N/A', user['is_admin_platform'] == true ? localizations.demoteVerb.toLowerCase() : localizations.promoteVerb.toLowerCase()),
                );
                if (confirm == true) {
                  await adminNotifier.toggleUserAdmin(user['id'] as int); // Use local adminNotifier
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showLogDetailsDialog(BuildContext context, Map<String, dynamic> log) {
    final localizations = AppLocalizations.of(context);
    showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
              title: Text(localizations.logDetails),
              content: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('${localizations.date}: ${log['created_at'] ?? ''}'),
                    Text('${localizations.action}: ${log['action'] ?? ''}'),
                    Text('${localizations.admin}: ${log['admin_username'] ?? ''}'),
                    Text('${localizations.targetUser}: ${log['target_username'] ?? ''}'),
                    SelectableText('${localizations.description}: ${log['description'] ?? ''}'),
                    if (log['details'] != null && (log['details'] as Map).isNotEmpty) ...[
                       const SizedBox(height: 8),
                       Text('${localizations.details}:', style: const TextStyle(fontWeight: FontWeight.bold)),
                       SelectableText(jsonEncode(log['details'])),
                    ],
                  ],
                ),
              ),
              actions: [
                TextButton(onPressed: () => Navigator.pop(ctx), child: Text(localizations.closeButton)),
              ],
            ));
  }

  void _showRollbackDialog(BuildContext context, Map<String, dynamic> log) {
    final localizations = AppLocalizations.of(context);
    final adminNotifier = ref.read(adminDataProvider.notifier);
     if (log['can_rollback'] != true) {
       ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(localizations.cannotRollback)));
       return;
     }

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(localizations.confirmRollback),
        content: Text(localizations.areYouSureRollback(log['description'] ?? localizations.thisAction)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(localizations.cancel)),
          TextButton(
            onPressed: () async {
              Navigator.pop(ctx, true);
              await adminNotifier.rollbackAction(log['id'] as int);
            },
            child: Text(localizations.rollback, style: const TextStyle(color: Colors.orange)),
          ),
        ],
      ),
    );
  }

  Future<bool?> _showConfirmationDialog(BuildContext context, {required String title, required String content}) async {
    final localizations = AppLocalizations.of(context);
    return showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(localizations.cancel)),
          TextButton(onPressed: () => Navigator.pop(ctx, true), child: Text(localizations.confirm, style: const TextStyle(color: Colors.red))),
        ],
      ),
    );
  }
}