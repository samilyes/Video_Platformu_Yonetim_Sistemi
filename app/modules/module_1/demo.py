# kanal türlerinin polimorfik davranışlarını gösterir.
import sys
import os
from datetime import datetime
from typing import List

# Modül import'ları
try:
    from base import (
        BaseChannel, BaseUser, UserRole, ChannelType, ChannelStatus,
        AdminUser, ContentCreatorUser, ViewerUser
    )
    from implementations import (
        PersonalChannel, BrandChannel, KidsChannel,
        InvalidNameError, ChannelLimitReachedError,
        InvalidAgeRangeError, ContentNotAllowedError
    )
    from repository import UserRepository, ChannelRepository

    print("System: All modules imported successfully for demo")
except ImportError as e:
    print(f"System >> Import hatası demoda : {e}")
    sys.exit(1)


def print_section_header(title: str):
    # Bölüm başlığı yazdır
    print(f"\n{' ' * 60}")
    print(f" {title} ".center(60, "="))
    print(f"{' ' * 60}")


def create_sample_users() -> List[BaseUser]:
    # Örnek kullanıcılar oluştur
    print_section_header("Ornek kullanici olusturma")
    users = []
    try:
        # Admin kullanıcısı
        admin = AdminUser(
            "admin_demo_001",
            "demo_admin",
            "admin@demo.com",
            "hashed_admin_password",
            UserRole.ADMIN
        )
        users.append(admin)
        print(f"System >> Admin olusturuldu : {admin.username}")
        # Content creator kullanıcısı
        creator = ContentCreatorUser(
            "creator_demo_001",
            "demo_creator",
            "creator@demo.com",
            "hashed_creator_password",
            UserRole.CONTENT_CREATOR
        )
        users.append(creator)
        print(f"System >> Icerik ureticisi olusturldu : {creator.username}")
        # Viewer kullanıcısı
        viewer = ViewerUser(
            "viewer_demo_001",
            "demo_viewer",
            "viewer@demo.com",
            "hashed_viewer_password",
            UserRole.VIEWER
        )
        users.append(viewer)
        print(f"System >> Izleyici olusturuldu : {viewer.username}")
        print(f"\nSystem >> Basariyla olusturuldu {len(users)} ornek kullanicilar ")
    except Exception as e:
        print(f"System >> HATA ornek kullanici olustururken : {e}")
        return []
    return users


def create_sample_channels() -> List[BaseChannel]:
    # Örnek kanallar oluştur
    print_section_header("ORNEK KANALLAR OLUSTURMA")
    channels = []
    try:
        # PersonalChannel oluştur
        personal_channel = PersonalChannel(
            "demo_personal_001",
            "Demo Gaming Channel",
            "Oyun kanalima hoş geldiniz! Burada en son oyun incelemelerini, eğitimleri ve canli yayinlari bulacaksiniz.",
            "creator_demo_001"
        )
        channels.append(personal_channel)
        print(f"System >> OLUSTURLDU kisisel kanal : {personal_channel.name}")
        # BrandChannel oluştur
        brand_channel = BrandChannel(
            "demo_brand_001",
            "TechCorp Official",
            "TechCorp'un resmi kanalı - güvenilir teknoloji ortağınız. En son ürünlerimizi, yeniliklerimizi ve sektör analizlerimizi keşfedin.",
            "creator_demo_001"
        )
        channels.append(brand_channel)
        print(f"System >> OLUSTURULDU BrandChannel : {brand_channel.name}")
        # KidsChannel oluştur
        kids_channel = KidsChannel(
            "demo_kids_001",
            "Fun Learning Adventures",
            "5-10 yas arasi cocuklara yonelik egitici icerikler. Cocuklarin harika vakit gecirirken ögrenmelerine yardimci olan güvenli, eglenceli ve ilgi cekici videolar.",
            "creator_demo_001"
        )
        channels.append(kids_channel)
        print(f"System >> OLUSTURULDU KidsChannel: {kids_channel.name}")
        print(f"\nSystem >> Basariyla olusturuldu {len(channels)} ornek kanal")
    except Exception as e:
        print(f"System >> HATA ornek kanal olusturulurken: {e}")
        return []
    return channels


def demonstrate_polymorphism(channels: List[BaseChannel], users: List[BaseUser]):
    # Polimorfizm gösterimi
    print_section_header("POLYMORPHISM GOSTERİMİ ")
    print("\n1. POLYMORPHIC METHOD CAGRILDI - get_access_level()")
    print("-" * 50)
    for i, channel in enumerate(channels, 1):
        channel_type = type(channel).__name__
        access_level = channel.get_access_level()
        print(f"{i}. {channel_type}: '{channel.name}'")
        print(f"   Access Level: {access_level}")
        print()
    print("\n2. POLYMORPHIC METHOD CAGRILDI - can_user_access()")
    print("-" * 50)
    # Her kanal için farklı kullanıcı erişim testleri
    test_users = [
        ("admin_demo_001", UserRole.ADMIN),
        ("creator_demo_001", UserRole.CONTENT_CREATOR),
        ("viewer_demo_001", UserRole.VIEWER),
        ("random_user_001", UserRole.VIEWER)
    ]
    for channel in channels:
        print(f"\nSunlara erisim test ediliyor : {type(channel).__name__}: '{channel.name}'")
        for user_id, user_role in test_users:
            try:
                can_access = channel.can_user_access(user_id, user_role)
                status = "izin verildi" if can_access else "reddedildi"
                print(f"  {user_id} ({user_role.value}): {status}")
            except Exception as e:
                print(f"  {user_id} ({user_role.value}): ERROR - {e}")
    print("\n3. POLYMORPHIC DAVRANIS - Kanal Bilgisi")
    print("-" * 50)
    for channel in channels:
        print(f"\nChannel: {type(channel).__name__}")
        print(f"  ID: {channel.channel_id}")
        print(f"  Name: {channel.name}")
        print(f"  Owner: {channel.owner_id}")
        print(f"  Type: {channel.channel_type.value}")
        print(f"  Status: {channel.status.value}")
        print(f"  Subscribers: {channel.subscriber_count}")
        print(f"  Videos: {channel.video_count}")
        print(f"  Created: {channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}")


def demonstrate_encapsulation(channels: List[BaseChannel]):
    # Kapsülleme gösterimi
    print_section_header("ENCAPSULATION DEMONSTRATION")

    for channel in channels:
        channel_type = type(channel).__name__
        print(f"\n{channel_type}: {channel.name}")

        if isinstance(channel, PersonalChannel):
            print(f"  Max Videos Per Day: {channel.max_videos_per_day}")
            channel.max_videos_per_day = 7
            print(f"  Updated Max Videos Per Day: {channel.max_videos_per_day}")
            channel.add_hobby("gaming")
            print(f"  Current hobbies: {channel.get_hobbies()}")
        elif isinstance(channel, BrandChannel):
            print(f"  Company Name: '{channel.company_name}'")
            print(f"  Brand Verified: {channel.brand_verified}")
            channel.company_name = "TechCorp Industries Ltd."
            channel.marketing_budget = 50000.0
            print(f"  Updated Company Name: {channel.company_name}")
        elif isinstance(channel, KidsChannel):
            print(f"  Age Range: {channel.min_age}-{channel.max_age}")
            print(f"  Parental Control: {channel.parental_control_enabled}")
            channel.min_age = 4
            channel.max_age = 9
            print(f"  Updated Age Range: {channel.min_age}-{channel.max_age}")


def demonstrate_inheritance(channels: List[BaseChannel]):
    # Kalıtım gösterimi
    print_section_header("INHERITANCE DEMONSTRATION")
    print("\n1. INHERITED METHODS FROM BaseChannel")
    print("-" * 50)

    for channel in channels:
        channel_type = type(channel).__name__
        print(f"\n{channel_type}: {channel.name}")
        # BaseChannel'dan kalıtılan metodlar
        print(f"  Channel ID: {channel.channel_id}")
        print(f"  Status: {channel.status.value}")
        print(f"  Subscriber Count: {channel.subscriber_count}")
        # Inherited method - add_moderator
        old_moderators = len(channel.moderators)
        channel.add_moderator("test_moderator_001")
        new_moderators = len(channel.moderators)
        print(f"  Moderators: {old_moderators} -> {new_moderators}")
        # Inherited attribute - tags
        channel.tags.append("demo")
        channel.tags.append("educational")
        print(f"  Tags: {channel.tags}")
    print("\n2. METHOD RESOLUTION ORDER (MRO)")
    print("-" * 50)

    for channel in channels:
        channel_type = type(channel).__name__
        mro = [cls.__name__ for cls in type(channel).__mro__]
        print(f"{channel_type} MRO: {' -> '.join(mro)}")


def demonstrate_static_and_class_methods():
    # Statik ve sınıf metodları gösterimi
    print_section_header("STATIC AND CLASS METHODS DEMONSTRATION")
    # Static methods
    categories = PersonalChannel.get_recommended_categories()
    print(f"PersonalChannel Categories: {categories}")
    industries = BrandChannel.get_valid_industries()
    print(f"BrandChannel Industries: {industries}")
    roi = BrandChannel.calculate_campaign_roi(1000, 1500)
    print(f"Campaign ROI: {roi}%")
    kids_categories = KidsChannel.get_valid_content_categories()
    print(f"KidsChannel Categories: {kids_categories}")
    # Class methods
    try:
        default_personal = PersonalChannel.create_default_personal_channel("demo_user_002", "DemoUser")
        print(f"Default PersonalChannel: {default_personal.name}")
        verified_brand = BrandChannel.create_verified_brand_channel("demo_brand_002", "Demo Corp",
                                                                    "contact@democorp.com")
        print(f"Onaylanmis BrandChannel: {verified_brand.name}")
        educational_kids = KidsChannel.create_educational_kids_channel("demo_edu_002", "mathematics", (6, 10))
        print(f"Educational KidsChannel: {educational_kids.name}")
    except Exception as e:
        print(f"HATA kanal olusturulurken: {e}")


def demonstrate_exception_handling():
    # Exception handling gösterimi
    print_section_header("ISTISNA ISLEME GOSTERIMI")
    # InvalidNameError test
    try:
        PersonalChannel("invalid_001", "x", "Valid description", "user_001")
    except InvalidNameError as e:
        print(f"✓ InvalidNameError caught: {e}")
    # Property validation test
    try:
        test_brand = BrandChannel(
            "test_brand_001", "Test Brand",
            "This is a test brand channel for demonstration purposes", "user_003"
        )
        test_brand.marketing_budget = -1000  # Invalid: negative budget
    except ValueError as e:
        print(f"✓ ValueError caught: {e}")
    # Validation tests
    tests = [("Empty name", lambda: PersonalChannel("test", "", "Valid desc", "user")),
             ("Short desc", lambda: BrandChannel("test", "Valid Name", "Short", "user"))]
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✗ {test_name}: No exception raised")
        except Exception as e:
            print(f"✓ {test_name}: {type(e).__name__}")


def main():
    print("=" * 60)
    print(" CHANNEL MANAGEMENT MODULE - POLYMORPHISM DEMO ".center(60, "="))
    print("=" * 60)
    print(f"\nSystem: Demo started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        users = create_sample_users()
        if not users:
            print("System: Failed to create sample users, exiting demo")
            return 1
        channels = create_sample_channels()
        if not channels:
            print("System: Failed to create sample channels, exiting demo")
            return 1
        demonstrate_polymorphism(channels, users)
        demonstrate_encapsulation(channels)
        demonstrate_inheritance(channels)
        demonstrate_static_and_class_methods()
        demonstrate_exception_handling()
        # Demo tamamlandı
        print_section_header("DEMO COMPLETED SUCCESSFULLY")
        print(f"\nSystem: Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("System: All OOP principles demonstrated successfully!")
        print("\nKey Concepts Demonstrated:")
        print("  ✓ Polymorphism - Same methods, different behaviors")
        print("  ✓ Encapsulation - Private attributes with property access")
        print("  ✓ Inheritance - Shared functionality from BaseChannel")
        print("  ✓ Abstraction - Abstract methods implemented differently")
        print("  ✓ Static Methods - Utility functions without instance")
        print("  ✓ Class Methods - Factory methods for object creation")
        print("  ✓ Exception Handling - Custom exceptions and validation")
        return 0
    except Exception as e:
        print(f"\nSystem: Critical error during demo: {e}")
        print("System: Demo terminated unexpectedly")
        return 1


if __name__ == "__main__":
    # Demo'yu çalıştır
    exit_code = main()
    sys.exit(exit_code)