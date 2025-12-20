import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Any
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestResult:

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_true(self, condition: bool, message: str = ""):

        if condition:
            self.passed += 1
            print(f"basarili >>  {message}")

        else:
            self.failed += 1
            error_msg = f"hata >> {message}"
            self.errors.append(error_msg)
            print(f"hata >> {error_msg}")

    def assert_equal(self, actual, expected, message: str = ""):

        condition = actual == expected

        if not condition:
            message = f"{message} (Expected: {expected}, Got: {actual})"

        self.assert_true(condition, message)

    def assert_raises(self, exception_type, func, *args, **kwargs):

        try:
            func(*args, **kwargs)
            self.failed += 1
            error_msg = f"hata: Expected {exception_type.__name__} but no exception was raised"
            self.errors.append(error_msg)
            print(f"hata >> {error_msg}")

        except exception_type:
            self.passed += 1
            print(f"basarili >> {exception_type.__name__} raised as expected")

        except Exception as e:

            self.failed += 1
            error_msg = f"hata >> Expected {exception_type.__name__} but got {type(e).__name__}"
            self.errors.append(error_msg)
            print(f"hata >> {error_msg}")

    def print_summary(self):

        total = self.passed + self.failed
        print(f"\nTest sonuclari >> {self.passed}/{total} basarili, {self.failed} basarisiz")


# Modül import'ları
try:

    from app.modules.module_1.base import*

    from app.modules.module_1.implementations import*

    from app.modules.module_1.repository import*

    print("System >> Tum moduller basarili bir sekilde içeri aktarildi")

except ImportError as e:

    print(f"System >> Import hatasi : {e}")
    sys.exit(1)


def print_test_header(test_name: str):
    print(f"\n{' ' * 60}")
    print(f" {test_name} ")
    print(f"{' ' * 60}")


def test_personal_channel():
    # PersonalChannel testleri
    print_test_header("Kisisel Kanal Testleri Siralandi")
    result = TestResult()

    try:
        personal = PersonalChannel(
            "test_personal_001", "Test Personal Channel",
            "This is a test personal channel for unit testing purposes", "test_user_001"
        )

        result.assert_true(True, "Kisisel kanal olusturuldu (basarili)")
        result.assert_equal(personal.name, "Test Personal Channel", "Kanal adi doğru ayarlandi (basarili)")

        # Property tests
        result.assert_equal(personal.max_videos_per_day, 5, "Gunluk maks 5 video (varsayilan)")
        personal.max_videos_per_day = 8
        result.assert_equal(personal.max_videos_per_day, 8, "Gunuk video guncellendi (maksimum)")

        # Method tests
        result.assert_true(personal.add_hobby("gaming"), "Gaming hobby eklendi")
        result.assert_true(len(personal.get_hobbies()) == 1, "One hobby stored")

        # Static method tests
        categories = PersonalChannel.get_recommended_categories()
        result.assert_true(len(categories) > 0, "Onerilen kanallar retur edildi ")

        # Class method test
        default_channel = PersonalChannel.create_default_personal_channel("test_user_007", "TestUser")
        result.assert_true(default_channel is not None, "Kanal olusturuldu (varsayilan)")

    except Exception as e:
        result.assert_true(False, f"Kisisel Kanal Test Hatasi : {e}")
    # Exception test
    result.assert_raises(InvalidNameError, PersonalChannel, "test_invalid_001", "x", "Valid description",
                         "test_user_002")
    result.print_summary()
    return result


def test_brand_channel():
    # BrandChannel testleri
    print_test_header("BRAND KANAL TESTLERI")
    result = TestResult()

    try:
        brand = BrandChannel(
            "test_brand_001", "Test Brand KANALI",
            "Bu, birim testi ve doğrulama amaçlarına yönelik kapsamlı bir test markası kanalıdır",
            "test_brand_user_001"
        )
        result.assert_true(True, "BrandChannel basriyla olusturuldu")
        result.assert_true(not brand.brand_verified, "Brand varsayilan olarak dogrulanmadi")
        # Property tests
        brand.company_name = "Test Sirketi Ltd."
        result.assert_equal(brand.company_name, "Test Sirketi Ltd.", "Sirket adi dogru ayarlanmis")
        brand.marketing_budget = 25000.50
        result.assert_equal(brand.marketing_budget, 25000.50, "Pazarlama butcesi dogru ayarlanmis")
        # Method tests
        result.assert_true(brand.set_industry("technology"), "Teknoloji endüstrisi seti")
        result.assert_true(brand.add_target_audience("young_adults"), "Genc yetiskin izleyici eklendi")
        # Static method tests
        industries = BrandChannel.get_valid_industries()
        result.assert_true(len(industries) > 0, "Geçerli sektörler döndürüldü")
        roi = BrandChannel.calculate_campaign_roi(1000, 1500)
        result.assert_equal(roi, 50.0, "Yatirim getirisi dogru hesaplandi")

        # Class method test
        verified_brand = BrandChannel.create_verified_brand_channel(
            "test_brand_user_009", "Test Verified Corp", "verified@testcorp.com"
        )
        result.assert_true(verified_brand is not None, "Verified brand channel created")

    except Exception as e:
        result.assert_true(False, f"BrandChannel testing failed: {e}")
    result.print_summary()
    return result


def test_kids_channel():
    # KidsChannel testleri
    print_test_header("KIDS KANAL TESTI")
    result = TestResult()

    try:
        kids = KidsChannel(
            "test_kids_001", "Test Kids Channel",
            "This is a comprehensive test kids channel for educational content and entertainment",
            "test_educator_001"
        )
        result.assert_true(True, "KidsChannel created successfully")
        result.assert_true(kids.parental_control_enabled, "Parental control enabled by default")
        result.assert_equal(kids.content_rating, "G", "Default content rating is G")
        # Property tests
        result.assert_equal(kids.min_age, 3, "Default minimum age is 3")
        result.assert_equal(kids.max_age, 12, "Default maximum age is 12")
        kids.content_rating = "PG"
        result.assert_equal(kids.content_rating, "PG", "Content rating updated to PG")
        # Method tests
        result.assert_true(kids.set_age_range(4, 8), "Age range set successfully")
        result.assert_equal(kids.get_age_range(), (4, 8), "Age range retrieved correctly")
        result.assert_true(kids.add_approved_educator("educator_001"), "Educator added successfully")
        result.assert_true(
            kids.is_content_appropriate("G", ["educational", "fun"]),
            "Appropriate content accepted"
        )
        categories = KidsChannel.get_valid_content_categories()
        result.assert_true(len(categories) > 0, "Valid content categories returned")
        screen_time = KidsChannel.get_age_appropriate_screen_time(5)
        result.assert_true(screen_time > 0, "Screen time recommendation returned")
        educational_channel = KidsChannel.create_educational_kids_channel("test_educator_008", "science", (6, 10))
        result.assert_true(educational_channel is not None, "Educational kids channel created")

    except Exception as e:
        result.assert_true(False, f"KidsChannel testing failed: {e}")
    result.print_summary()
    return result


def test_polymorphism():
    # Polimorfizm testleri
    print_test_header("POLIMORFIZM TESTİ")
    result = TestResult()
    print("\n1. Polimorfik davranışın test edilmesi : ")

    try:
        # Farklı kanal türleri oluştur
        channels = [
            PersonalChannel(
                "poly_personal_001",
                "Polymorphism Personal",
                "Personal channel for polymorphism testing",
                "poly_user_001"
            ),
            BrandChannel(
                "poly_brand_001",
                "Polymorphism Brand",
                "Brand channel for comprehensive polymorphism testing and validation",
                "poly_brand_001"
            ),
            KidsChannel(
                "poly_kids_001",
                "Polymorphism Kids",
                "Kids channel for polymorphism testing with educational content",
                "poly_edu_001"
            )
        ]

        # Polimorfik davranış testi - get_access_level
        access_levels = [channel.get_access_level() for channel in channels]
        result.assert_equal(len(set(access_levels)), 3, "Different access levels for different channel types")
        # Polimorfik davranış testi - can_user_access

        for channel in channels:
            # Owner erişimi
            owner_access = channel.can_user_access(channel.owner_id, UserRole.VIEWER)
            result.assert_true(owner_access, f"{type(channel).__name__} owner can access")
            # Admin erişimi
            admin_access = channel.can_user_access("admin_001", UserRole.ADMIN)
            result.assert_true(admin_access, f"{type(channel).__name__} admin can access")
        # Polimorfik davranış testi - update_info

        for channel in channels:
            old_updated_at = channel.updated_at
            channel.update_info(description=f"Updated {type(channel).__name__} description")
            result.assert_true(channel.updated_at >= old_updated_at, f"{type(channel).__name__} updated_at changed")

        for channel in channels:
            # 1. Istatistik testi
            stats = channel.get_channel_statistics()
            result.assert_true(isinstance(stats, dict), f"{type(channel).__name__} istatistik verisi donuyor")

            # 2. Politika doğrulama testi
            policy_check = channel.validate_content_policy({"type": "video", "quality": "high"})
            result.assert_true(policy_check is True, f"{type(channel).__name__} icerik politikasi onaylandi")

    except Exception as e:
        result.assert_true(False, f"Polymorphism testing failed: {e}")

    result.print_summary()
    return result


def test_repository_basic():
    # Repository temel testleri
    print_test_header("Repo basic testleri")
    result = TestResult()
    temp_dir = tempfile.mkdtemp()

    try:
        # UserRepository testi
        user_repo = UserRepository(os.path.join(temp_dir, "test_users.json"))
        result.assert_true(True, "UserRepository created successfully")
        admin_user = AdminUser("admin_001", "testadmin", "admin@test.com", "hashed_password", UserRole.ADMIN)
        result.assert_true(user_repo.create_user(admin_user) is not None, "Admin user created")
        retrieved_admin = user_repo.get_user_by_id("admin_001")
        result.assert_equal(retrieved_admin.username, "testadmin", "Admin user retrieved correctly")
        # ChannelRepository test
        channel_repo = ChannelRepository(os.path.join(temp_dir, "test_channels.json"))
        result.assert_true(True, "ChannelRepository created successfully")
        personal_channel = PersonalChannel(
            "personal_repo_001", "Repository Personal Test",
            "Personal channel for repository testing purposes", "admin_001"
        )
        result.assert_true(channel_repo.create_channel(personal_channel) is not None,
                           "Personal channel created in repo")
        retrieved_personal = channel_repo.get_channel_by_id("personal_repo_001")
        result.assert_equal(retrieved_personal.name, "Repository Personal Test", "Personal channel retrieved correctly")

    except Exception as e:
        result.assert_true(False, f"Repository testing failed: {e}")

    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    result.print_summary()
    return result


def test_status_and_category():
    # Yeni Şartlar (Kategori ve Durum) testleri
    print_test_header("KATEGORI VE DURUM TESTLERI")
    result = TestResult()

    try:
        # Örnek bir kanal oluştur (Kategori ile birlikte)
        test_channel = PersonalChannel("cat_test_01", "Oyun Kanali", "Kategori testi", "owner_01")
        test_channel.category = "gaming"  # Manuel atama veya init ile

        # Kategori kontrolü
        result.assert_equal(test_channel.category, "gaming", "Kanal kategorisi basariyla ayarlandi")

        # Durum değiştirme kontrolü
        test_channel.change_status(ChannelStatus.SUSPENDED)
        result.assert_equal(test_channel.status, ChannelStatus.SUSPENDED, "Durum degistirildi >> ASKIYA ALINDI")

        test_channel.change_status(ChannelStatus.ACTIVE)
        result.assert_equal(test_channel.status, ChannelStatus.ACTIVE, "Durum degistirilidi >> AKTIF")

        # Video sayısı artırma kontrolü (Arkadaşın için eklediğimiz metot)
        old_count = test_channel.video_count
        test_channel.increment_video_count()
        result.assert_equal(test_channel.video_count, old_count + 1, "Video sayisi arttirildi")

    except Exception as e:
        result.assert_true(False, f"Status and Category testing failed: {e}")

    result.print_summary()
    return result


def run_all_tests():
    # Tüm testleri çalıştır
    print(" " * 60)
    print(" Kanal yonetim modulu test paketi ")
    print(" " * 60)
    print(f"\nsistem -->> test paketi baslatildi {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test sonuçlarını topla
    all_results = []

    try:
        # 1. PersonalChannel testleri
        personal_result = test_personal_channel()
        all_results.append(("PersonalChannel", personal_result))

        # 2. BrandChannel testleri
        brand_result = test_brand_channel()
        all_results.append(("BrandChannel", brand_result))

        # 3. KidsChannel testleri
        kids_result = test_kids_channel()
        all_results.append(("KidsChannel", kids_result))

        # 4. Polimorfizm testleri
        poly_result = test_polymorphism()
        all_results.append(("Polymorphism", poly_result))

        # 5. Repository testleri
        repo_result = test_repository_basic()
        all_results.append(("Repository", repo_result))

        # --- YENİ EKLENEN KISIM BURASI ---
        # 6. Yeni Şartlar (Kategori ve Durum) testleri
        new_req_result = test_status_and_category()  # Yukarıda tanımladığımız fonksiyon
        all_results.append(("Status & Category", new_req_result))
        # --------------------------------

    except Exception as e:
        print(f"\nSystem >> Test yurutulurken kritik hata : {e}")
        return 1

    # ... (Geri kalan raporlama kodları aynı kalıyor)
    else:
        print(f"System >> tum testler tamamlandı")
        return 0


if __name__ == "__main__":
    # Test suite'i çalıştır
    exit_code = run_all_tests()
    print(f"\nSystem >> test paketi tamamlandi {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(exit_code)