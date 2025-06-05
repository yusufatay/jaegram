# Instagram Etkileşim Uygulaması Proje İskeleti (Gramelle/Topfollow Benzeri)

Bu proje iskeleti, Instagram ile giriş yapılan, görev tamamlayarak coin kazanılan ve coinlerle takipçi/beğeni siparişi verilen bir mobil uygulama geliştirmek için hazırlanmıştır.

## Klasör ve Dosya Açıklamaları

- `/backend/` : Backend kaynak kodları (örn. Flask + Instagrapi). **Bu klasörde sadece iskelet dosyalar ve açıklamalar bulunur. Kodlar ileride eklenecektir.**
  - `app.py` : Flask uygulama ana dosyası (boş şablon + açıklama)
  - `models.py` : Veritabanı modelleri için şablon
  - `instagram_utils.py` : Instagrapi ile ilgili yardımcı fonksiyonlar için şablon
- `/frontend/` : Flutter mobil uygulama kaynak kodları.
  - `lib/` : Ana Flutter kodları
    - `main.dart` : Uygulama giriş noktası (şablon ve açıklama)
    - `screens/` : Ekranlar (giriş, ana ekran, görev, sipariş, profil)
    - `providers/` : State yönetimi için şablon dosyalar
  - `test/` : Flutter test dosyaları için şablon
  - `pubspec.yaml` : Flutter bağımlılıkları (örnek şablon)
- `/docs/` : Türkçe dokümantasyon dosyaları
- `/tests/` : Backend ve frontend testlerinin şablonları
- `.gitignore` : Gereksiz dosyaları hariç tutar (örnek şablon)
- `requirements.txt` : Python bağımlılıkları için örnek şablon
- `README.md` : Bu dosya, proje hakkında genel bilgi ve açıklamalar içerir.

## Kullanım
- Her klasör ve dosya, ileride kod eklenmeye hazır şekilde açıklamalar içerir.
- Kodun tamamı ve arayüzler Türkçedir.
- Geliştiriciler için notlar ve doldurulacak alanlar belirtilmiştir.

## Katkı
- Bu iskelet, modüler ve genişletilebilir bir yapı sunar.
- Yeni özellikler ve ekranlar kolayca eklenebilir.

---

> **Not:** Backend kodları ve detayları bu iskelette yer almaz. Sadece şablon ve açıklamalar bulunur. Kodlar ve fonksiyonlar daha sonra geliştirici tarafından eklenecektir.
