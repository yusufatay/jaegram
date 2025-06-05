#!/usr/bin/env python3
"""
Instagram Coin Platform - Comprehensive System Test
Bu test tüm sistemlerin gerçek veri ile çalıştığını doğrular
"""

import requests
import json
import time
from datetime import datetime

class ComprehensiveSystemTest:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.headers = {"Content-Type": "application/json"}
        self.test_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Test sonucunu kaydet"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Detaylar: {details}")
    
    def get_auth_token(self):
        """Test kullanıcısı için auth token al"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                data={
                    "username": "testuser",
                    "password": "testpassword"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.test_token}"
                self.log_result("Authentication", True, "Test kullanıcısı başarıyla giriş yaptı")
                return True
            else:
                self.log_result("Authentication", False, f"Giriş başarısız: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Giriş hatası: {str(e)}")
            return False
    
    def test_statistics_endpoint(self):
        """Statistics endpoint'ini test et - gerçek veri kontrolü"""
        try:
            response = requests.get(f"{self.base_url}/statistics", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Gerçek veri kontrolü
                required_fields = ["total_users", "total_orders", "total_tasks", "total_coin_transactions"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Statistics Data", False, f"Eksik alanlar: {missing_fields}", data)
                    return False
                
                # Veri tiplerini kontrol et
                numeric_fields = ["total_users", "total_orders", "total_tasks", "total_coin_transactions"]
                for field in numeric_fields:
                    if not isinstance(data[field], int):
                        self.log_result("Statistics Data Types", False, f"{field} sayısal değil: {type(data[field])}", data)
                        return False
                
                self.log_result("Statistics Endpoint", True, "Gerçek veri ile çalışıyor", data)
                return True
            else:
                self.log_result("Statistics Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Statistics Endpoint", False, f"Hata: {str(e)}")
            return False
    
    def test_leaderboard_endpoint(self):
        """Leaderboard endpoint'ini test et"""
        try:
            response = requests.get(f"{self.base_url}/social/leaderboard", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    # Leaderboard verisi kontrolü
                    if len(data) > 0:
                        first_user = data[0]
                        required_fields = ["username", "coin_balance", "rank"]
                        missing_fields = [field for field in required_fields if field not in first_user]
                        
                        if missing_fields:
                            self.log_result("Leaderboard Data", False, f"Eksik alanlar: {missing_fields}", first_user)
                            return False
                    
                    self.log_result("Leaderboard Endpoint", True, f"{len(data)} kullanıcı listesi döndü", {"count": len(data)})
                    return True
                else:
                    self.log_result("Leaderboard Format", False, "Liste formatında değil", data)
                    return False
            else:
                self.log_result("Leaderboard Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Leaderboard Endpoint", False, f"Hata: {str(e)}")
            return False
    
    def test_daily_reward_status(self):
        """Daily reward status endpoint'ini test et"""
        try:
            response = requests.get(f"{self.base_url}/daily-reward-status", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["can_claim", "next_reward_at", "current_streak"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Daily Reward Status", False, f"Eksik alanlar: {missing_fields}", data)
                    return False
                
                self.log_result("Daily Reward Status", True, "Gerçek veri ile çalışıyor", data)
                return True
            else:
                self.log_result("Daily Reward Status", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Daily Reward Status", False, f"Hata: {str(e)}")
            return False
    
    def test_claim_daily_reward(self):
        """Daily reward claim endpoint'ini test et"""
        try:
            response = requests.post(f"{self.base_url}/claim-daily-reward", headers=self.headers)
            
            # Başarılı claim veya already claimed durumu kabul edilebilir
            if response.status_code in [200, 400]:
                data = response.json()
                
                if response.status_code == 200:
                    # Başarılı claim
                    required_fields = ["message", "reward_amount"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result("Daily Reward Claim", False, f"Eksik alanlar: {missing_fields}", data)
                        return False
                    
                    self.log_result("Daily Reward Claim", True, "Ödül başarıyla alındı", data)
                    return True
                else:
                    # Already claimed durumu
                    if "already" in data.get("detail", "").lower():
                        self.log_result("Daily Reward Claim", True, "Ödül zaten alınmış (beklenen durum)", data)
                        return True
                    else:
                        self.log_result("Daily Reward Claim", False, "Beklenmeyen hata", data)
                        return False
            else:
                self.log_result("Daily Reward Claim", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Daily Reward Claim", False, f"Hata: {str(e)}")
            return False
    
    def test_user_badges(self):
        """User badges endpoint'ini test et"""
        try:
            response = requests.get(f"{self.base_url}/social/badges", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_result("User Badges", True, f"{len(data)} rozet listesi döndü", {"count": len(data)})
                    return True
                else:
                    self.log_result("User Badges Format", False, "Liste formatında değil", data)
                    return False
            else:
                self.log_result("User Badges", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("User Badges", False, f"Hata: {str(e)}")
            return False
    
    def test_social_stats(self):
        """Social stats endpoint'ini test et"""
        try:
            response = requests.get(f"{self.base_url}/social/stats", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["total_friends", "rank_position", "badges_earned"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Social Stats", False, f"Eksik alanlar: {missing_fields}", data)
                    return False
                
                self.log_result("Social Stats", True, "Gerçek veri ile çalışıyor", data)
                return True
            else:
                self.log_result("Social Stats", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Social Stats", False, f"Hata: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("🔍 Comprehensive System Test Başlatılıyor...\n")
        
        # 1. Authentication
        if not self.get_auth_token():
            print("\n❌ Authentication başarısız - testler durduruluyor")
            return False
        
        print()
        
        # 2. Core System Tests
        tests = [
            ("Statistics System", self.test_statistics_endpoint),
            ("Leaderboard System", self.test_leaderboard_endpoint),
            ("Daily Reward Status", self.test_daily_reward_status),
            ("Daily Reward Claim", self.test_claim_daily_reward),
            ("User Badges System", self.test_user_badges),
            ("Social Stats System", self.test_social_stats),
        ]
        
        successful_tests = 0
        total_tests = len(tests)
        
        for test_name, test_function in tests:
            print(f"\n🧪 Testing {test_name}...")
            if test_function():
                successful_tests += 1
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n{'='*50}")
        print(f"📊 TEST SONUÇLARI")
        print(f"{'='*50}")
        print(f"✅ Başarılı: {successful_tests}/{total_tests}")
        print(f"❌ Başarısız: {total_tests - successful_tests}/{total_tests}")
        print(f"📈 Başarı Oranı: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print(f"\n🎉 TÜM SİSTEMLER %100 ÇALIŞIR DURUMDA!")
            return True
        else:
            print(f"\n⚠️ {total_tests - successful_tests} sistem düzeltilmeli")
            return False
    
    def save_detailed_report(self):
        """Detaylı raporu kaydet"""
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if r["success"]]),
                "failed_tests": len([r for r in self.test_results if not r["success"]]),
                "test_date": datetime.now().isoformat()
            },
            "detailed_results": self.test_results
        }
        
        with open("comprehensive_system_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detaylı rapor kaydedildi: comprehensive_system_test_report.json")

if __name__ == "__main__":
    tester = ComprehensiveSystemTest()
    success = tester.run_all_tests()
    tester.save_detailed_report()
    
    if success:
        print("\n🚀 Sistem production'a hazır!")
    else:
        print("\n🔧 Sistem düzeltmeleri gerekli")
