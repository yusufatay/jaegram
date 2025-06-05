// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Turkish (`tr`).
class AppLocalizationsTr extends AppLocalizations {
  AppLocalizationsTr([String locale = 'tr']) : super(locale);

  @override
  String get appTitle => 'JAEGram';

  @override
  String get switchToLight => 'Açık Moda Geç';

  @override
  String get switchToDark => 'Koyu Moda Geç';

  @override
  String get followers => 'Takipçi';

  @override
  String get following => 'Takip Edilen';

  @override
  String get systemStats => 'Sistem İstatistikleri';

  @override
  String get newLogArrived => 'Yeni admin logu geldi. Lütfen yenileyin.';

  @override
  String get webSocketConnectionError =>
      'WebSocket bağlantı hatası. Lütfen daha sonra tekrar deneyin.';

  @override
  String expiresAt(Object dateTime) {
    return 'Bitiş tarihi: $dateTime';
  }

  @override
  String get expiresAtLabel => 'Bitiş Tarihi';

  @override
  String get completedAtLabel => 'Tamamlanma Tarihi';

  @override
  String get completedAt => 'Tamamlanma Tarihi';

  @override
  String get id => 'Kimlik';

  @override
  String get orderId => 'Sipariş No';

  @override
  String get assignedUser => 'Atanan Kullanıcı';

  @override
  String get status => 'Durum';

  @override
  String get assignedAt => 'Atanma Tarihi';

  @override
  String get loginTitle => 'Giriş Yap';

  @override
  String get mainScreenTitle => 'Ana Sayfa';

  @override
  String get tasks => 'Görevler';

  @override
  String get orders => 'Siparişler';

  @override
  String get profile => 'Profil';

  @override
  String get notifications => 'Bildirimler';

  @override
  String get statistics => 'İstatistikler';

  @override
  String get admin => 'Admin';

  @override
  String get logout => 'Çıkış Yap';

  @override
  String get coin => 'Elmas';

  @override
  String completedTasks(Object count) {
    return 'Tamamlanan Görevler: $count';
  }

  @override
  String get completedTasksLabel => 'Tamamlanan Görevler';

  @override
  String get activeTasksLabel => 'Aktif Görevler';

  @override
  String get activeTasks => 'Aktif Görev';

  @override
  String get settings => 'Ayarlar';

  @override
  String get about => 'Hakkında';

  @override
  String get theme => 'Tema';

  @override
  String get darkTheme => 'Koyu';

  @override
  String get lightTheme => 'Açık';

  @override
  String get loginSubtitle => 'Hesabınıza erişin';

  @override
  String get username => 'Kullanıcı Adı';

  @override
  String get password => 'Şifre';

  @override
  String get loginButton => 'Instagram ile Giriş Yap';

  @override
  String get twoFACode => '2FA Kodu';

  @override
  String get continueWith2FA => '2FA Kodu ile Devam Et';

  @override
  String get usernamePasswordRequired => 'Kullanıcı adı ve şifre gerekli.';

  @override
  String get twoFARequired => '2FA kodu gerekli.';

  @override
  String get selectTab => 'Aşağıdan bir sekme seçin';

  @override
  String get takeNewTask => 'Yeni Görev Al';

  @override
  String get taskTakenSuccess => 'Görev başarıyla alındı!';

  @override
  String taskTakeFailed(Object error) {
    return 'Görev alınamadı: $error';
  }

  @override
  String get noAssignedTask => 'Şu anda atanmış göreviniz yok.';

  @override
  String get complete => 'Tamamla';

  @override
  String get noNotifications => 'Henüz bildirim yok.';

  @override
  String get markAsRead => 'Okundu olarak İşaretle';

  @override
  String get orderCreatedSuccessfully => 'Sipariş başarıyla oluşturuldu!';

  @override
  String get orderCreationError =>
      'Sipariş oluşturulamadı. Lütfen tekrar deneyin.';

  @override
  String get myOrders => 'Siparişlerim';

  @override
  String get createOrder => 'Sipariş Oluştur';

  @override
  String errorWithMessage(Object message) {
    return 'Hata: $message';
  }

  @override
  String get settingsTitle => 'Ayarlar';

  @override
  String get changeLanguage => 'Dili Değiştir';

  @override
  String get changeTheme => 'Temayı Değiştir';

  @override
  String get notificationSettings => 'Bildirim Ayarları';

  @override
  String get editProfile => 'Profili Düzenle';

  @override
  String get changePassword => 'Şifreyi Değiştir';

  @override
  String get language => 'Dil';

  @override
  String get save => 'Kaydet';

  @override
  String get cancel => 'İptal';

  @override
  String get dark => 'Koyu';

  @override
  String get light => 'Açık';

  @override
  String get system => 'Sistem';

  @override
  String get selectLanguage => 'Dil Seçin';

  @override
  String get selectTheme => 'Tema Seçin';

  @override
  String get profileUpdated => 'Profil başarıyla güncellendi!';

  @override
  String get passwordChanged => 'Şifre başarıyla değiştirildi!';

  @override
  String get errorOccurred => 'Bir hata oluştu!';

  @override
  String get confirmLogout => 'Çıkış yapmak istediğinize emin misiniz?';

  @override
  String get yes => 'Evet';

  @override
  String get no => 'Hayır';

  @override
  String get rollback => 'Geri Al';

  @override
  String get rollbackSuccess => 'Eylem başarıyla geri alındı.';

  @override
  String get userBanned => 'Kullanıcı yasaklandı.';

  @override
  String get coinOperationSuccess => 'Elmas işlemi başarılı.';

  @override
  String get adminPanel => 'Admin Paneli';

  @override
  String get instagramLogin => 'Instagram ile Giriş Yap';

  @override
  String get platformLogin => 'Platform Girişi';

  @override
  String get register => 'Kayıt Ol';

  @override
  String get fullName => 'Tam Adınız';

  @override
  String get registerSuccess => 'Kayıt başarılı! Lütfen giriş yapın.';

  @override
  String registerFailed(Object error) {
    return 'Kayıt başarısız: $error';
  }

  @override
  String get requiredField => 'Bu alan zorunludur.';

  @override
  String minCommentLength(Object length) {
    return 'Yorum en az $length karakter olmalıdır.';
  }

  @override
  String maxCommentLength(Object length) {
    return 'Yorum en fazla $length karakter olabilir.';
  }

  @override
  String get orderTypeLike => 'Beğeni';

  @override
  String get orderTypeFollow => 'Takip';

  @override
  String get orderTypeComment => 'Yorum';

  @override
  String get postUrl => 'Gönderi URL';

  @override
  String get targetCount => 'Hedef Sayısı';

  @override
  String get commentText => 'Yorum Metni (yorum siparişleri için)';

  @override
  String get orderCreationSuccess => 'Sipariş başarıyla oluşturuldu!';

  @override
  String orderCreationFailed(Object error) {
    return 'Sipariş oluşturulamadı: $error';
  }

  @override
  String get taskStatusPending => 'Beklemede';

  @override
  String get taskStatusAssigned => 'Atanmış';

  @override
  String get taskStatusCompleted => 'Tamamlanmış';

  @override
  String get taskStatusExpired => 'Süresi Dolmuş';

  @override
  String get taskStatusFailed => 'Başarısız';

  @override
  String get taskCompletedSuccess => 'Görev başarıyla tamamlandı!';

  @override
  String taskCompletionFailed(Object error) {
    return 'Görev tamamlanamadı: $error';
  }

  @override
  String get withdrawCoins => 'Elmas Çek';

  @override
  String get amount => 'Miktar';

  @override
  String minCompletedTasksRequired(Object count) {
    return 'Çekim yapabilmek için en az $count görev tamamlamalısınız.';
  }

  @override
  String get insufficientCoins => 'Yetersiz elmas.';

  @override
  String get positiveAmountRequired => 'Miktar pozitif olmalı.';

  @override
  String get withdrawalSuccess => 'Çekim başarılı!';

  @override
  String withdrawalFailed(Object error) {
    return 'Çekim başarısız: $error';
  }

  @override
  String get coins => 'Jeton';

  @override
  String get activeTask => 'Aktif Görev';

  @override
  String get appName => 'Instagram Puan Uygulaması';

  @override
  String get usernameHint => 'Instagram kullanıcı adınızı girin';

  @override
  String get passwordHint => 'Instagram şifrenizi girin';

  @override
  String get turkish => 'Türkçe';

  @override
  String get english => 'İngilizce';

  @override
  String get error => 'Hata';

  @override
  String get retry => 'Tekrar Dene';

  @override
  String get genericErrorEncountered => 'Bir hata oluştu.';

  @override
  String get details => 'Detaylar';

  @override
  String get systemDefault => 'Sistem Varsayılanı';

  @override
  String get appSettings => 'Uygulama Ayarları';

  @override
  String get users => 'Kullanıcılar';

  @override
  String get coinTransactions => 'Elmas İşlemleri';

  @override
  String get logs => 'Loglar';

  @override
  String get refresh => 'Yenile';

  @override
  String get searchInUsers =>
      'Kullanıcılarda ara (ID, kullanıcı adı, isim, email)';

  @override
  String get searchInOrders =>
      'Siparişlerde ara (ID, kullanıcı ID, gönderi URL, tip)';

  @override
  String get searchInTasks =>
      'Görevlerde ara (ID, sipariş ID, kullanıcı ID, durum)';

  @override
  String get searchInCoinTransactions =>
      'Elmas işlemlerinde ara (ID, kullanıcı ID, tip, açıklama)';

  @override
  String get searchInLogs => 'Loglarda ara (ID, admin, hedef, eylem, açıklama)';

  @override
  String get exportCsv => 'CSV Olarak Dışa Aktar';

  @override
  String get exportCsvShort => 'Dışa Aktar';

  @override
  String get all => 'Tüm Zamanlar';

  @override
  String get admins => 'Adminler';

  @override
  String get bannedUsers => 'Yasaklı Kullanıcılar';

  @override
  String get platformAdmin => 'Platform Admini Mi?';

  @override
  String get banned => 'Yasaklı Mı?';

  @override
  String get actions => 'Eylemler';

  @override
  String userActionsFor(Object username) {
    return '$username için eylemler';
  }

  @override
  String get banUser => 'Kullanıcıyı Yasakla';

  @override
  String get unbanUser => 'Kullanıcının Yasağını Kaldır';

  @override
  String get confirmBan => 'Yasaklamayı Onayla';

  @override
  String get confirmUnban => 'Yasağı Kaldırmayı Onayla';

  @override
  String areYouSureBan(Object banUnban, Object username) {
    return '$username adlı kullanıcıyı $banUnban istediğinizden emin misiniz?';
  }

  @override
  String get banVerb => 'yasaklamak';

  @override
  String get unbanVerb => 'yasağını kaldırmak';

  @override
  String get userUnbanned => 'Kullanıcının yasağı kaldırıldı.';

  @override
  String get addRemoveCoin => 'Elmas Ekle/Çıkar';

  @override
  String addRemoveCoinFor(Object username) {
    return '$username için elmas ekle/çıkar';
  }

  @override
  String get coinAmount => 'Elmas Miktarı';

  @override
  String get coinAmountInfo => 'Elmas Miktarı (çıkarmak için negatif)';

  @override
  String get confirm => 'Onayla';

  @override
  String get promoteToAdmin => 'Admin Yap';

  @override
  String get demoteFromAdmin => 'Adminlikten Al';

  @override
  String get confirmPromote => 'Admin Yapmayı Onayla';

  @override
  String get confirmDemote => 'Adminlikten Almayı Onayla';

  @override
  String areYouSureAdmin(Object promoteDemote, Object username) {
    return '$username adlı kullanıcıyı platform admini olarak $promoteDemote istediğinizden emin misiniz?';
  }

  @override
  String get promoteVerb => 'admin yapmak';

  @override
  String get demoteVerb => 'adminlikten almak';

  @override
  String get userPromoted => 'Kullanıcı admin yapıldı.';

  @override
  String get userDemoted => 'Kullanıcı adminlikten alındı.';

  @override
  String get logDetails => 'Log Detayları';

  @override
  String get date => 'Tarih';

  @override
  String get action => 'Eylem';

  @override
  String get adminUsername => 'Admin Kullanıcı Adı';

  @override
  String get targetUser => 'Hedef Kullanıcı';

  @override
  String get targetUsername => 'Hedef Kullanıcı Adı';

  @override
  String get description => 'Açıklama';

  @override
  String get closeButton => 'Kapat';

  @override
  String get confirmRollback => 'Geri Almayı Onayla';

  @override
  String areYouSureRollback(Object actionDescription) {
    return '\"$actionDescription\" eylemini geri almak istediğinizden emin misiniz? Bu işlem geri alınamaz.';
  }

  @override
  String get cannotRollback => 'Bu eylem geri alınamaz.';

  @override
  String get thisAction => 'bu eylem';

  @override
  String get noDataToExport => 'Dışa aktarılacak veri yok.';

  @override
  String get csvDownloadStarting => 'CSV indirme başlıyor...';

  @override
  String get csvExportNotSupportedOnMobileYet =>
      'CSV dışa aktarma bu platformda henüz desteklenmiyor.';

  @override
  String get user => 'Kullanıcı';

  @override
  String get orderType => 'Sipariş Tipi';

  @override
  String get completedCount => 'Tamamlanan Sayısı';

  @override
  String get createdAt => 'Oluşturulma Tarihi';

  @override
  String get userId => 'Kullanıcı ID';

  @override
  String get transactionType => 'İşlem Tipi';

  @override
  String get balanceAfter => 'Sonraki Bakiye';

  @override
  String get logActionUserBan => 'Kullanıcı Yasaklama';

  @override
  String get logActionUserUnban => 'Kullanıcı Yasağı Kaldırma';

  @override
  String get logActionCoinAdjust => 'Elmas Düzenleme';

  @override
  String get logActionAdminPromote => 'Admin Yetkisi Verme';

  @override
  String get logActionAdminDemote => 'Admin Yetkisi Alma';

  @override
  String get errorFetchingCoin => 'Elmas bakiyesi alınırken hata oluştu';

  @override
  String get tasksTab => 'Görevler';

  @override
  String get ordersTab => 'Siparişler';

  @override
  String get profileTab => 'Profil';

  @override
  String get orderFilterStatusAll => 'Tümü';

  @override
  String get orderFilterStatusPending => 'Beklemede';

  @override
  String get orderFilterStatusActive => 'Aktif';

  @override
  String get orderFilterStatusCompleted => 'Tamamlandı';

  @override
  String get orderFilterStatusFailed => 'Başarısız';

  @override
  String get orderFilterStatusCancelled => 'İptal Edildi';

  @override
  String get taskFilterStatusAll => 'Tümü';

  @override
  String get taskFilterStatusPending => 'Beklemede';

  @override
  String get taskFilterStatusAssigned => 'Atanmış';

  @override
  String get taskFilterStatusCompleted => 'Tamamlandı';

  @override
  String get taskFilterStatusFailed => 'Başarısız';

  @override
  String get taskFilterStatusExpired => 'Süresi Dolmuş';

  @override
  String get coinTransactionFilterAll => 'Tümü';

  @override
  String get coinTransactionFilterEarn => 'Kazanma';

  @override
  String get coinTransactionFilterSpend => 'Harcama';

  @override
  String get coinTransactionFilterWithdraw => 'Çekim';

  @override
  String get coinTransactionFilterAdminAdd => 'Admin Ekleme';

  @override
  String get coinTransactionFilterAdminRemove => 'Admin Çıkarma';

  @override
  String get adminLogFilterAll => 'Tümü';

  @override
  String get badges => 'Rozetler';

  @override
  String get viewAll => 'Tümünü Gör';

  @override
  String get noBadgesEarned => 'Henüz rozet kazanılmadı';

  @override
  String get noBadgesAvailable => 'Mevcut rozet yok';

  @override
  String get earnedOn => 'Kazanılma Tarihi';

  @override
  String get close => 'Kapat';

  @override
  String get badgeStats => 'Rozet İstatistikleri';

  @override
  String get totalBadges => 'Toplam Rozet';

  @override
  String get categories => 'Kategoriler';

  @override
  String get earnedBadges => 'Kazanılan Rozetler';

  @override
  String get allBadges => 'Tüm Rozetler';

  @override
  String get progressStatus => 'İlerleme Durumu';

  @override
  String get badgeEarned => 'Rozet Kazandınız!';

  @override
  String get congratulations => 'Tebrikler!';

  @override
  String get youEarnedBadge => 'Bu rozeti kazandınız:';

  @override
  String get instagramIntegration => 'Instagram Entegrasyonu';

  @override
  String get instagramDashboard => 'Instagram Paneli';

  @override
  String get connectInstagram => 'Instagram Bağla';

  @override
  String get disconnectInstagram => 'Instagram Bağlantısını Kes';

  @override
  String get instagramConnected => 'Instagram Bağlandı';

  @override
  String get instagramNotConnected => 'Instagram Bağlı Değil';

  @override
  String get syncProfile => 'Profili Güncelle';

  @override
  String get syncPosts => 'Gönderileri Güncelle';

  @override
  String get connectionStatus => 'Bağlantı Durumu';

  @override
  String get connectedSince => 'Bağlantı tarihi';

  @override
  String get lastSync => 'Son güncelleme';

  @override
  String get followersCount => 'Takipçi';

  @override
  String get followingCount => 'Takip';

  @override
  String get mediaCount => 'Gönderi';

  @override
  String get profileInfo => 'Profil Bilgileri';

  @override
  String get postGrid => 'Son Gönderiler';

  @override
  String get accountInfo => 'Hesap Bilgileri';

  @override
  String get verified => 'Doğrulanmış';

  @override
  String get private => 'Özel';

  @override
  String get connectYourAccount => 'Instagram Hesabınızı Bağlayın';

  @override
  String get enterCredentials =>
      'Hesabınızı bağlamak için Instagram bilgilerinizi girin';

  @override
  String get connecting => 'Bağlanıyor...';

  @override
  String get connectionFailed => 'Bağlantı Başarısız';

  @override
  String get tryAgain => 'Tekrar Dene';

  @override
  String get connectionSuccessful => 'Bağlantı Başarılı';

  @override
  String get accountConnectedSuccessfully =>
      'Instagram hesabınız başarıyla bağlandı!';

  @override
  String get dailyReward => 'Günlük Ödül';

  @override
  String get claimReward => 'Ödül Al';

  @override
  String get rewardClaimed => 'Ödül Alındı';

  @override
  String get comeBackTomorrow => 'Bir sonraki ödülünüz için yarın gelin!';

  @override
  String get streak => 'Seri';

  @override
  String get days => 'gün';

  @override
  String get emailVerification => 'E-posta Doğrulama';

  @override
  String get verifyEmail => 'E-posta Doğrula';

  @override
  String get emailVerified => 'E-posta Doğrulandı';

  @override
  String get emailNotVerified => 'E-posta Doğrulanmadı';

  @override
  String get twoFactorAuth => 'İki Faktörlü Doğrulama';

  @override
  String get enable2FA => '2FA Etkinleştir';

  @override
  String get disable2FA => '2FA Devre Dışı Bırak';

  @override
  String get twoFactorEnabled => '2FA Etkinleştirildi';

  @override
  String get twoFactorDisabled => '2FA Devre Dışı Bırakıldı';

  @override
  String get logoutConfirmation => 'Çıkış yapmak istediğinize emin misiniz?';

  @override
  String get logoutError => 'Çıkış yapılırken bir hata oluştu';

  @override
  String get aboutAppDescription =>
      'JAEGram, Instagram performansınızı takip etmenize, çeşitli etkinliklerle puan kazanmanıza ve diğer kullanıcılarla rekabet etmenize yardımcı olan kapsamlı bir sosyal medya yönetim uygulamasıdır.';

  @override
  String get accountLevel => 'Seviye';

  @override
  String get joinDate => 'Katılma Tarihi';

  @override
  String get totalCoins => 'Elmas';

  @override
  String get totalPoints => 'Puan';

  @override
  String get leaderboard => 'Liderlik Tablosu';

  @override
  String get weeklyRanking => 'Haftalık Sıralama';

  @override
  String get rank => 'Sıralama';

  @override
  String get progress => 'İlerleme';

  @override
  String get accountSettings => 'Hesap Ayarları';

  @override
  String get privacySettings => 'Gizlilik Ayarları';

  @override
  String get displaySettings => 'Görüntü Ayarları';

  @override
  String get generalSettings => 'Genel Ayarlar';

  @override
  String get aboutApp => 'Uygulama Hakkında';

  @override
  String get enableNotifications => 'Bildirimleri Etkinleştir';

  @override
  String get userProfile => 'Kullanıcı Profili';

  @override
  String get instagramPosts => 'Instagram Gönderileri';

  @override
  String get recentPosts => 'Son Gönderiler';

  @override
  String get viewDetails => 'Detayları Gör';

  @override
  String get loadInstagramDataFailed => 'Instagram verileri yüklenemedi';

  @override
  String get instagramConnectionError =>
      'Instagram hesabı bağlanırken hata oluştu';

  @override
  String get instagramSyncSuccess => 'Instagram profili başarıyla güncellendi';

  @override
  String get instagramSyncFailed => 'Instagram profili güncellenemedi';

  @override
  String get instagramSyncError =>
      'Instagram profili güncellenirken hata oluştu';

  @override
  String get instagramDisconnected => 'Instagram hesabı bağlantısı kesildi';

  @override
  String get instagramDisconnectionFailed =>
      'Instagram hesabı bağlantısı kesilemedi';

  @override
  String get confirmDisconnect => 'Bağlantıyı Kesmeyi Onayla';

  @override
  String get disconnectConfirmText =>
      'Instagram hesabınızın bağlantısını kesmek istediğinizden emin misiniz? Senkronizasyona devam etmek için daha sonra yeniden bağlanmanız gerekecek.';

  @override
  String get disconnect => 'Bağlantıyı Kes';

  @override
  String get connect => 'Bağlan';

  @override
  String get syncing => 'Güncelleniyor...';

  @override
  String get lastSynced => 'Son Güncelleme';

  @override
  String get disconnectDescription =>
      'Bağlantıyı kesmek, Instagram hesabınızın uygulamayla senkronizasyonunu durdurur.';

  @override
  String get instagramConnectedStatus =>
      'Instagram hesabınız bağlı ve uygulama ile senkronize edildi';

  @override
  String get instagramDisconnectedStatus =>
      'Instagram hesabınız uygulamaya bağlı değil';

  @override
  String get posts => 'Gönderiler';

  @override
  String get instagramDisclaimerText =>
      'Instagram kimlik bilgilerinizi asla saklamayız ve yalnızca herkese açık profil verilerinizi senkronize etmek için kullanırız.';

  @override
  String get yourBadges => 'Rozetlerim';

  @override
  String get earnBadgesDescription =>
      'Görevleri tamamlayın ve Instagram hesabınızı bağlayarak rozetler kazanın';

  @override
  String get viewAllBadges => 'Tüm Rozetleri Gör';

  @override
  String get badgesEarned => 'Kazanılan Rozetler';

  @override
  String get goldBadges => 'Altın';

  @override
  String get silverBadges => 'Gümüş';

  @override
  String get bronzeBadges => 'Bronz';

  @override
  String get instagramBadges => 'Instagram';

  @override
  String get achievementBadges => 'Başarı';

  @override
  String get specialBadges => 'Özel';

  @override
  String get badgeDetails => 'Rozet Detayları';

  @override
  String get category => 'Kategori';

  @override
  String get earned => 'Kazanıldı';

  @override
  String get locked => 'Kilitli';

  @override
  String get addedOn => 'Eklenme Tarihi';

  @override
  String get requirements => 'Kazanma Şartları';

  @override
  String get specialRequirements => 'Bu rozetin özel gereksinimleri var';

  @override
  String get daysStreak => 'Günlük Seri';

  @override
  String get notificationsWillAppearHere => 'Bildirimleriniz burada görünecek';

  @override
  String get newBadgeEarned => 'Yeni Rozet Kazanıldı';

  @override
  String get levelUp => 'Seviye Atlandı';

  @override
  String get coinsReceived => 'Coin Alındı';

  @override
  String get instagramUpdate => 'Instagram Güncellemesi';

  @override
  String get systemNotification => 'Sistem Bildirimi';

  @override
  String get notification => 'Bildirim';

  @override
  String get month => 'ay';

  @override
  String get months => 'ay';

  @override
  String get day => 'gün';

  @override
  String get hour => 'saat';

  @override
  String get hours => 'saat';

  @override
  String get minute => 'dakika';

  @override
  String get minutes => 'dakika';

  @override
  String get ago => 'önce';

  @override
  String get justNow => 'Az Önce';

  @override
  String get viewBadge => 'Rozeti Gör';

  @override
  String get viewProfile => 'Profili Gör';

  @override
  String get viewInstagram => 'Instagram\'ı Gör';

  @override
  String get collectCoins => 'Coinleri Topla';

  @override
  String get view => 'Görüntüle';

  @override
  String get markAllAsRead => 'Tümünü Okundu İşaretle';

  @override
  String get allNotificationsMarkedAsRead =>
      'Tüm bildirimler okundu olarak işaretlendi';

  @override
  String get filterNotifications => 'Bildirimleri Filtrele';

  @override
  String get showBadgeNotifications => 'Rozet Bildirimlerini Göster';

  @override
  String get showLevelNotifications => 'Seviye Bildirimlerini Göster';

  @override
  String get showCoinNotifications => 'Coin Bildirimlerini Göster';

  @override
  String get showInstagramNotifications => 'Instagram Bildirimlerini Göster';

  @override
  String get showSystemNotifications => 'Sistem Bildirimlerini Göster';

  @override
  String get resetFilters => 'Filtreleri Sıfırla';

  @override
  String get apply => 'Uygula';

  @override
  String get coinsCollected => 'Coinler toplandı!';

  @override
  String get errorLoadingNotifications => 'Bildirimler yüklenirken hata oluştu';

  @override
  String get badgeNotifications => 'Rozet Bildirimleri';

  @override
  String get soundNotifications => 'Ses Bildirimleri';

  @override
  String get themeMode => 'Tema Modu';

  @override
  String get systemTheme => 'Sistem';

  @override
  String get privacyPolicy => 'Gizlilik Politikası';

  @override
  String get termsOfService => 'Kullanım Şartları';

  @override
  String get help => 'Yardım';

  @override
  String get version => 'Versiyon';

  @override
  String get logoutConfirmationText =>
      'Hesabınızdan çıkış yapmak istediğinizden emin misiniz?';

  @override
  String get errorLoadingSettings => 'Ayarlar yüklenirken hata oluştu';

  @override
  String get integrations => 'Entegrasyonlar';

  @override
  String get connected => 'Bağlı';

  @override
  String get notConnected => 'Bağlı Değil';

  @override
  String get unknown => 'Bilinmiyor';

  @override
  String get accountDetails => 'Hesap Detayları';

  @override
  String get errorLoadingProfile => 'Profil yüklenirken hata oluştu';

  @override
  String get errorLoadingBadges => 'Rozetler yüklenirken hata oluştu';

  @override
  String get errorLoadingPosts => 'Gönderiler yüklenirken hata oluştu';

  @override
  String get noPostsFound => 'Gönderi bulunamadı';

  @override
  String get connectInstagramBenefits =>
      'Gönderilerinizi ve takipçilerinizi takip etmek ve özel rozetler kazanmak için Instagram hesabınızı bağlayın';

  @override
  String get loadingInstagramData => 'Instagram verileri yükleniyor...';

  @override
  String get coinTransfer => 'Elmas Transferi';

  @override
  String get currentBalance => 'Mevcut Bakiye';

  @override
  String get transferDetails => 'Transfer Detayları';

  @override
  String get recipientUsername => 'Alıcı Kullanıcı Adı';

  @override
  String get enterRecipientUsername => 'Alıcı kullanıcı adını girin';

  @override
  String get pleaseEnterRecipientUsername =>
      'Lütfen alıcı kullanıcı adını girin';

  @override
  String get cannotTransferToYourself => 'Kendinize transfer yapamazsınız';

  @override
  String get enterAmount => 'Miktarı girin';

  @override
  String get pleaseEnterAmount => 'Lütfen miktarı girin';

  @override
  String get pleaseEnterValidAmount => 'Lütfen geçerli bir miktar girin';

  @override
  String get insufficientBalance => 'Yetersiz bakiye';

  @override
  String get note => 'Not';

  @override
  String get optional => 'İsteğe bağlı';

  @override
  String get enterTransferNote => 'Transfer notu girin';

  @override
  String get processing => 'İşleniyor...';

  @override
  String get transferCoins => 'Elmas Transfer Et';

  @override
  String get transferInformation => 'Transfer Bilgileri';

  @override
  String get transferInfo1 => 'Transferler anında gerçekleşir ve geri alınamaz';

  @override
  String get transferInfo2 => 'Minimum transfer miktarı 1 elmasdır';

  @override
  String get transferInfo3 =>
      'Alıcı kullanıcı adının doğru olduğundan emin olun';

  @override
  String get transferSuccessful => 'Transfer Başarılı';

  @override
  String get coinsTransferredSuccessfully =>
      'Elmaslar başarıyla transfer edildi!';

  @override
  String get instagramConnectionFailed => 'Instagram connection failed';

  @override
  String get monthly => 'Aylık';

  @override
  String get monthlyRanking => 'Aylık Sıralama';

  @override
  String get you => 'You';
}
