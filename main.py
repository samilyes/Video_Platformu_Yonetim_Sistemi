import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Module-1 (User/Channel)
from app.modules.module_1.base import ChannelStatus, UserRole
from app.modules.module_1.implementations import PersonalChannel, BrandChannel, KidsChannel,AdminUser
from app.modules.module_1.repository import UserRepository, ChannelRepository

# Module-2 (Video)
from app.modules.module_2.base import VideoStatus, VideoVisibility
from app.modules.module_2.repository import VideoRepository
from app.modules.module_2.services import VideoService

def ask(msg, default=None):
    if default is None:
        return input(f"{msg}: ").strip()
    val = input(f"{msg} [{default}]: ").strip()
    return val if val else str(default)


def ask_int(msg, default=0):
    while True:
        raw = ask(msg, default)
        try:
            return int(raw)
        except ValueError:
            print("Sayı giriniz.")


def pause():
    input("\nEnter ile devam...")


def make_user(user_id, username, email, password, role):
    from app.modules.module_1.base import AdminUser, ContentCreatorUser, ViewerUser

    if role == UserRole.ADMIN:
        return AdminUser(user_id, username, email, password, role)
    if role == UserRole.CONTENT_CREATOR:
        return ContentCreatorUser(user_id, username, email, password, role)
    return ViewerUser(user_id, username, email, password, role)


def choose_role(default=UserRole.VIEWER):
    print("\nRol seç:")
    print("1) admin")
    print("2) content_creator")
    print("3) viewer")
    d = "3" if default == UserRole.VIEWER else ("2" if default == UserRole.CONTENT_CREATOR else "1")
    c = ask("seçim : ", d)
    if c == "1":
        return UserRole.ADMIN
    if c == "2":
        return UserRole.CONTENT_CREATOR
    return UserRole.VIEWER


def list_users(user_repo):
    users = user_repo.get_all_users()
    if not users:
        print("Kullanıcı yok")
        return
    print("\n--> USERS\n")
    for u in users:
        print(f"{u.user_id} | {u.username} | {u.role.value} | active={u.is_active} | {u.email}")


def add_user(user_repo):
    print("\n--> USER EKLE\n")
    user_id = ask("User ID")
    username = ask("Username")

    # Email için ayrı döngü
    while True:
        email = ask("Email")
        if "@" in email: # Basit kontrol, istersen base'deki gibi try-except de yapabilirsin
            break
        print("[HATA]: Geçersiz e-posta formatı!")

    # Şifre için ayrı döngü (Kritik nokta burası)
    while True:
        password = ask("Password")
        try:
            # Geçici bir nesne oluşturarak setter'ı test ediyoruz
            # Ya da doğrudan uzunluk kontrolü yapabiliriz:
            if len(password) < 8:
                raise ValueError("Şifre en az 8 karakter olmalıdır!")
            break # Hata yoksa döngüden çıkar
        except ValueError as e:
            print(f"[HATA]: {e}")

    # Her şey tamamsa rol seç ve kaydet
    role = choose_role(UserRole.VIEWER)
    new_user = make_user(user_id, username, email, password, role)
    user_repo.create_user(new_user)
    print("Kullanıcı başarıyla eklendi.")

def edit_user(user_repo):
    print("\n--> KULLANICI DÜZENLE\n")
    user_id = ask("User ID")
    u = user_repo.get_user_by_id(user_id)

    # Değişmeyecek verileri baştan alalım
    new_username = ask("Username", u.username)

    # Kural sağlanana kadar dönen döngü
    while True:
        new_email = ask("Email", u.email)

        change_pwd = ask("Şifre değişsin mi? (E/H)", "H").lower() in ("e", "evet")
        # Eğer değişmeyecekse eski şifreyi, değişecekse yeni girişi al
        new_password = ask("Yeni password") if change_pwd else u.password

        change_role = ask("Rol değişsin mi? (E/H)", "H").lower() in ("e", "evet")
        new_role = choose_role(u.role) if change_role else u.role

        change_active = ask("Aktiflik değişsin mi? (E/H)", "H").lower() in ("e", "evet")
        new_active = (ask("Aktif mi? (true/false)", str(u.is_active)).lower() in (
        "true", "1", "e", "evet")) if change_active else u.is_active

        try:
            # Validasyon kontrolü: Yeni nesne oluşturmayı dene
            new_user = make_user(u.user_id, new_username, new_email, new_password, new_role)
            new_user.created_at = u.created_at
            new_user.is_active = new_active

            # Eğer buraya kadar geldiyse veriler GEÇERLİDİR. Kayda geçebiliriz.
            users = getattr(user_repo, "_UserRepository__users")
            username_index = getattr(user_repo, "_UserRepository__username_index")
            email_index = getattr(user_repo, "_UserRepository__email_index")

            # Eski indeksleri temizle ve yenilerini yaz
            username_index.pop(u.username.lower(), None)
            email_index.pop(u.email.lower(), None)

            users[user_id] = new_user
            username_index[new_user.username.lower()] = new_user.user_id
            email_index[new_user.email.lower()] = new_user.user_id

            setattr(user_repo, "_UserRepository__last_modified", datetime.now())
            getattr(user_repo, "_save_to_file")()

            print("Kullanıcı başarıyla güncellendi.")
            break  # BAŞARILI: Döngüden çık

        except ValueError as e:
            print(f"\n[DÜZENLEME HATASI]: {e}")
            print("Lütfen bilgileri kurallara uygun şekilde tekrar giriniz.\n")


def delete_user(user_repo):
    print("\n--> USER SİL\n")
    user_id = ask("User ID")

    users = getattr(user_repo, "_UserRepository__users")
    if user_id not in users:
        print("Kullanıcı bulunamadı")
        return

    username_index = getattr(user_repo, "_UserRepository__username_index")
    email_index = getattr(user_repo, "_UserRepository__email_index")
    u = users[user_id]

    username_index.pop(u.username.lower(), None)
    email_index.pop(u.email.lower(), None)
    del users[user_id]

    setattr(user_repo, "_UserRepository__last_modified", datetime.now())
    getattr(user_repo, "_save_to_file")()

    print("Kullanıcı silindi")


def list_channels(channel_repo):
    chans = channel_repo.get_all_channels()
    if not chans:
        print("Kanal yok")
        return
    print("\n--> Kanallar ---")
    for ch in chans:
        print(
            f"{ch.channel_id} | {type(ch).__name__} | {ch.name} | owner={ch.owner_id} | {ch.status.value} | cat={getattr(ch, 'category', 'other')}")


def add_channel(channel_repo):
    print("\n--> KANAL OLUŞTUR\n")
    print("1) Kişisel\n2) Marka\n3) Cocuk")
    t = ask("Tip", "1")

    channel_id = ask("Channel ID")
    owner_id = ask("Owner ID")
    name = ask("Name")
    desc = ask("Description")
    cat = ask("Category", "other")

    if t == "2":
        ch = BrandChannel(channel_id, name, desc, owner_id)
    elif t == "3":
        ch = KidsChannel(channel_id, name, desc, owner_id)
    else:
        ch = PersonalChannel(channel_id, name, desc, owner_id)

    ch.category = cat
    channel_repo.create_channel(ch)
    print("Kanal eklendi")


def edit_channel(channel_repo):
    print("\n--> KANAL DÜZENLE\n")
    channel_id = ask("Channel ID")
    ch = channel_repo.get_channel_by_id(channel_id)

    ch.name = ask("Name", ch.name)
    ch.description = ask("Description", ch.description)
    ch.category = ask("Category", getattr(ch, "category", "other"))
    ch.updated_at = datetime.now()

    channels = getattr(channel_repo, "_ChannelRepository__channels")
    channels[ch.channel_id] = ch

    setattr(channel_repo, "_ChannelRepository__last_modified", datetime.now())
    getattr(channel_repo, "_save_to_file")()

    print("Kanal güncellendi")


def change_channel_status(channel_repo):
    print("\n--> KANAL DURUM\n")
    channel_id = ask("Channel ID")
    ch = channel_repo.get_channel_by_id(channel_id)

    print("1) active\n2) suspended\n3) archived")
    c = ask("Yeni durum", "1")
    if c == "2":
        st = ChannelStatus.SUSPENDED
    elif c == "3":
        st = ChannelStatus.ARCHIVED
    else:
        st = ChannelStatus.ACTIVE

    channel_repo.set_channel_status(ch.channel_id, st)
    print("Durum güncellendi")


def delete_channel(channel_repo):
    print("\n--> KANAL SİL\n")
    channel_id = ask("Channel ID")

    channels = getattr(channel_repo, "_ChannelRepository__channels")
    if channel_id not in channels:
        print("Kanal bulunamadı")
        return

    owner_index = getattr(channel_repo, "_ChannelRepository__owner_index")
    type_index = getattr(channel_repo, "_ChannelRepository__type_index")
    ch = channels[channel_id]

    if ch.owner_id in owner_index and channel_id in owner_index[ch.owner_id]:
        owner_index[ch.owner_id].remove(channel_id)
    if ch.channel_type in type_index and channel_id in type_index[ch.channel_type]:
        type_index[ch.channel_type].remove(channel_id)

    del channels[channel_id]

    setattr(channel_repo, "_ChannelRepository__last_modified", datetime.now())
    getattr(channel_repo, "_save_to_file")()

    print("Kanal silindi")


def choose_visibility(default=VideoVisibility.PRIVATE):
    print("\nGörünürlük: 1) public  2) private  3) listedısı")
    d = "2" if default == VideoVisibility.PRIVATE else ("1" if default == VideoVisibility.PUBLIC else "3")
    c = ask("seçim : ", d)
    if c == "1":
        return VideoVisibility.PUBLIC
    if c == "3":
        return VideoVisibility.UNLISTED
    return VideoVisibility.PRIVATE


def upload_video(video_service, channel_repo):
    print("\n--> VİDEO YÜKLE\n")
    channel_id = ask("Channel ID")
    channel_obj = channel_repo.get_channel_by_id(channel_id)

    if channel_obj.status != ChannelStatus.ACTIVE:
        print("Kanal aktif değil, video yüklenemez")
        return

    print("1) Standard\n2) Short\n3) Live")
    t = ask("Tip", "1")
    title = ask("Title")

    if t == "2":
        duration = ask_int("Duration (<=60)", 30)
        visibility = choose_visibility(VideoVisibility.PUBLIC)
        video = video_service.create_short_video(channel_id, title, duration_seconds=duration, visibility=visibility)
    elif t == "3":
        planned = ask("Planlı mı? (E/H)", "H").lower() in ("e", "evet")
        scheduled = None
        if planned:
            raw = ask("Tarih (YYYY-MM-DD HH:MM)")
            scheduled = datetime.strptime(raw, "%Y-%m-%d %H:%M")
        video = video_service.create_live_stream(channel_id, title, scheduled_time=scheduled)
    else:
        desc = ask("Description")
        duration = ask_int("Duration", 60)
        visibility = choose_visibility(VideoVisibility.PRIVATE)
        resolution = ask("Resolution", "1080p")
        video = video_service.create_standard_video(channel_id, title, desc, duration, visibility=visibility,
                                                    resolution=resolution)

    video_service.upload_video(video.video_id, b"fake_file")
    video_service.process_video(video.video_id, channel_obj=channel_obj)

    if video.status == VideoStatus.PUBLISHED:
        try:
            channel_repo.increment_channel_video_count(channel_id, 1)
        except Exception:
            pass

    print(f"Video oluşturuldu: {video.video_id} | {video.get_video_type()} | status={video.status.value}")


def list_videos(video_service):
    print("\n--> VİDEO LİSTELE\n")
    channel_id = ask("Channel ID")
    vids = video_service.list_videos_by_channel(channel_id)
    if not vids:
        print("Video yok")
        return
    for v in vids:
        print(
            f"{v.video_id} | {v.get_video_type()} | {v.title} | {v.status.value} | {v.visibility.value} | {v.duration_seconds}")


def delete_video(video_repo):
    print("\n--> VİDEO SİL\n")
    video_id = ask("Video ID")
    ok = video_repo.delete(video_id)
    print("Silindi" if ok else "Bulunamadı")


def block_video(video_service, video_repo):
    print("\n--> VİDEO ENGELLE\n")
    video_id = ask("Video ID")
    reason = ask("Reason", "policy")
    video_service.block_video(video_id, reason)
    v = video_repo.get_by_id(video_id)
    print(f"Yeni status: {v.status.value}")


def unblock_video(video_repo):
    print("\n--> VİDEO ENGEL KALDIR\n")
    video_id = ask("Video ID")
    v = video_repo.get_by_id(video_id)
    v.transition_status(VideoStatus.PUBLISHED)
    video_repo.save(v)
    print("Yayınlandı (PUBLISHED)")


def dashboard(channel_repo, video_repo):
    print("\n--> Kontrol Merkezi\n")
    channel_id = ask("Channel ID")
    ch = channel_repo.get_channel_by_id(channel_id)

    try:
        stats = ch.get_channel_statistics(repo=video_repo)
    except TypeError:
        stats = ch.get_channel_statistics()

    print(f"Kanal: {ch.channel_id} | {type(ch).__name__} | {ch.name} | status={ch.status.value}")
    if isinstance(stats, dict):
        for k, v in stats.items():
            print(f"{k}: {v}")
    else:
        print(stats)


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    user_repo = UserRepository(os.path.join(data_dir, "users.json"))
    channel_repo = ChannelRepository(os.path.join(data_dir, "channels.json"))

    video_repo = VideoRepository()  # RAM
    video_service = VideoService(video_repo)

    while True:
        print("\n--> ANA MENU\n")
        print("1) Kullanıcı")
        print("2) Kanal")
        print("3) Video")
        print("4) Kontrol Merkezi")
        print("0) Çıkış")

        sec = ask("seçim : ")

        try:
            if sec == "1":
                while True:
                    print("\n--> KULLANICI MENU\n")
                    print("1) Listele  2) Ekle  3) Düzenle  4) Sil  0) Geri")
                    c = ask("seçim : ")
                    if c == "1":
                        list_users(user_repo)
                        pause()
                    elif c == "2":
                        add_user(user_repo)
                        pause()
                    elif c == "3":
                        edit_user(user_repo)
                        pause()
                    elif c == "4":
                        delete_user(user_repo)
                        pause()
                    elif c == "0":
                        break

            elif sec == "2":
                while True:
                    print("\n--> KANAL MENU\n")
                    print("1) Listele  2) Oluştur  3) Düzenle  4) Durum  5) Sil  0) Geri")
                    c = ask("seçim : ")
                    if c == "1":
                        list_channels(channel_repo)
                        pause()
                    elif c == "2":
                        add_channel(channel_repo)
                        pause()
                    elif c == "3":
                        edit_channel(channel_repo)
                        pause()
                    elif c == "4":
                        change_channel_status(channel_repo)
                        pause()
                    elif c == "5":
                        delete_channel(channel_repo)
                        pause()
                    elif c == "0":
                        break

            elif sec == "3":
                while True:
                    print("\n--> VIDEO MENU\n")
                    print("1) Yükle  2) Listele  3) Sil  4) Engelle  5) Engel kaldır  0) Geri")
                    c = ask("seçim : ")
                    if c == "1":
                        upload_video(video_service, channel_repo)
                        pause()
                    elif c == "2":
                        list_videos(video_service)
                        pause()
                    elif c == "3":
                        delete_video(video_repo)
                        pause()
                    elif c == "4":
                        block_video(video_service, video_repo)
                        pause()
                    elif c == "5":
                        unblock_video(video_repo)
                        pause()
                    elif c == "0":
                        break

            elif sec == "4":
                dashboard(channel_repo, video_repo)
                pause()

            elif sec == "0":
                print("Çıkış")
                break

        except Exception as e:
            print(f"Hata: {type(e).__name__}: {e}")
            pause()


if __name__ == "__main__":
    main()
