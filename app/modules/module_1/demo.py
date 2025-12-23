import os
import sys
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.modules.module_1.base import ChannelStatus, UserRole
from app.modules.module_1.implementations import PersonalChannel, BrandChannel, KidsChannel
from app.modules.module_1.repository import UserRepository, ChannelRepository


class Cancelled(Exception):
    pass


def _raw(prompt: str) -> str:
    return input(prompt).strip()


def ask_required(label: str) -> str:
    while True:
        v = _raw(f"{label}: ")
        if v.lower() == "iptal":
            raise Cancelled()
        if v:
            return v
        print("Boş bırakılamaz. (iptal yazabilirsiniz)")


def ask_choice(label: str, options: dict[str, str]) -> str:
    while True:
        print(f"\n{label}")
        for k, text in options.items():
            print(f"  {k}) {text}")
        v = _raw("Seçim: ")
        if v.lower() == "iptal":
            raise Cancelled()
        if v in options:
            return v
        print("Hatalı seçim. (iptal yazabilirsiniz)")


def ask_bool(label: str) -> bool:
    while True:
        raw = _raw(f"{label} (E/H): ")
        if raw.lower() == "iptal":
            raise Cancelled()
        raw = raw.lower()
        if raw in ("e", "evet", "y", "yes", "1", "true"):
            return True
        if raw in ("h", "hayır", "hayir", "n", "no", "0", "false"):
            return False
        print("Sadece E veya H girin. (iptal yazabilirsiniz)")


def pause():
    _raw("\nEnter ile devam...")


from app.modules.module_1.base import AdminUser, ContentCreatorUser, ViewerUser
def _make_user(user_id, username, email, password, role):
    if role == UserRole.ADMIN:
        return AdminUser(user_id, username, email, password, role)
    if role == UserRole.CONTENT_CREATOR:
        return ContentCreatorUser(user_id, username, email, password, role)
        # Default olarak ViewerUser döndür
    return ViewerUser(user_id, username, email, password, role)


def list_users(repo: UserRepository):
    users = repo.get_all_users()
    if not users:
        print("Kullanıcı yok")
        return
    print("\n--- USERS ---")
    for u in users:
        print(f"{u.user_id} | {u.username} | {u.role.value} | active={u.is_active} | {u.mail}")


def add_user(repo: UserRepository):
    user_id = ask_required("User ID")
    username = ask_required("Username")
    email = ask_required("Email")
    password = ask_required("Password (En az 8 karakter)")
    role_key = ask_choice("Rol", {"1": "admin", "2": "content_creator", "3": "viewer"})
    role = UserRole.ADMIN if role_key == "1" else (UserRole.CONTENT_CREATOR if role_key == "2" else UserRole.VIEWER)

    try:
        # Nesne oluşturma ve kaydetme işlemi
        new_user = _make_user(user_id, username, email, password, role)
        repo.create_user(new_user)
        print("Kullanıcı başarıyla eklendi.")
    except ValueError as e:
        print(f"\n[DOĞRULAMA HATASI]: {e}")


def edit_user(repo: UserRepository):
    user_id = ask_required("User ID")
    u = repo.get_user_by_id(user_id)

    new_username = ask_required(f"Yeni username (mevcut: {u.username})")
    new_email = ask_required(f"Yeni email (mevcut: {u.mail})")

    # Yazım hatası düzeltildi: passsword -> password
    new_password = u.password
    if ask_bool("Şifre değişsin mi?"):
        new_password = ask_required("Yeni password (8+ karakter)")

    new_role = u.role
    if ask_bool("Rol değişsin mi?"):
        role_key = ask_choice("Rol", {"1": "admin", "2": "content_creator", "3": "viewer"})
        new_role = UserRole.ADMIN if role_key == "1" else (
            UserRole.CONTENT_CREATOR if role_key == "2" else UserRole.VIEWER)

    new_active = u.is_active
    if ask_bool("Aktiflik değişsin mi?"):
        new_active = ask_bool("Aktif mi?")

    # --- KORUMA BLOĞU ---
    try:
        # Yeni nesneyi oluşturmayı deniyoruz (Hata varsa burada fırlayacak)
        new_user = _make_user(u.user_id, new_username, new_email, new_password, new_role)
        new_user.created_at = u.created_at
        new_user.is_active = new_active

        # Kayıt ve Index Güncelleme
        users = getattr(repo, "_UserRepository__users")
        username_index = getattr(repo, "_UserRepository__username_index")
        email_index = getattr(repo, "_UserRepository__email_index")

        username_index.pop(u.username.lower(), None)
        email_index.pop(u.mail.lower(), None)

        users[user_id] = new_user
        username_index[new_user.username.lower()] = new_user.user_id
        email_index[new_user.mail.lower()] = new_user.user_id

        setattr(repo, "_UserRepository__last_modified", datetime.now())
        getattr(repo, "_save_to_file")()

        print("Kullanıcı başarıyla güncellendi.")

    except ValueError as e:
        print(f"\n[HATA]: Güncelleme başarısız! {e}")

def delete_user(repo: UserRepository):
    user_id = ask_required("User ID")

    users = getattr(repo, "_UserRepository__users")
    if user_id not in users:
        print("Kullanıcı bulunamadı")
        return

    username_index = getattr(repo, "_UserRepository__username_index")
    email_index = getattr(repo, "_UserRepository__email_index")
    u = users[user_id]

    username_index.pop(u.username.lower(), None)
    email_index.pop(u.mail.lower(), None)
    del users[user_id]

    setattr(repo, "_UserRepository__last_modified", datetime.now())
    getattr(repo, "_save_to_file")()

    print("Kullanıcı silindi")



def list_channels(repo: ChannelRepository):
    chans = repo.get_all_channels()
    if not chans:
        print("Kanal yok")
        return
    print("\n--- CHANNELS ---")
    for ch in chans:
        print(
            f"{ch.channel_id} | {type(ch).__name__} | {ch.name} | owner={ch.owner_id} | {ch.status.value} | cat={getattr(ch, 'category', 'other')}"
        )


def add_channel(repo: ChannelRepository):
    t = ask_choice("Kanal tipi", {"1": "Personal", "2": "Brand", "3": "Kids"})

    channel_id = ask_required("Channel ID")
    owner_id = ask_required("Owner ID")
    name = ask_required("Name")
    desc = ask_required("Description")
    cat = ask_required("Category")

    if t == "2":
        ch = BrandChannel(channel_id, name, desc, owner_id)
    elif t == "3":
        ch = KidsChannel(channel_id, name, desc, owner_id)
    else:
        ch = PersonalChannel(channel_id, name, desc, owner_id)

    ch.category = cat
    repo.create_channel(ch)
    print("Kanal eklendi")


def edit_channel(repo: ChannelRepository):
    channel_id = ask_required("Channel ID")
    ch = repo.get_channel_by_id(channel_id)

    ch.name = ask_required(f"Name (mevcut: {ch.name})")
    ch.description = ask_required("Description")
    ch.category = ask_required(f"Category (mevcut: {getattr(ch, 'category', 'other')})")
    ch.updated_at = datetime.now()

    channels = getattr(repo, "_ChannelRepository__channels")
    channels[ch.channel_id] = ch

    setattr(repo, "_ChannelRepository__last_modified", datetime.now())
    getattr(repo, "_save_to_file")()

    print("Kanal güncellendi")


def change_channel_status(repo: ChannelRepository):
    channel_id = ask_required("Channel ID")
    ch = repo.get_channel_by_id(channel_id)

    st_key = ask_choice(
        f"Yeni durum (mevcut: {ch.status.value})",
        {"1": "active", "2": "suspended", "3": "archived"},
    )

    st = ChannelStatus.ACTIVE if st_key == "1" else (ChannelStatus.SUSPENDED if st_key == "2" else ChannelStatus.ARCHIVED)
    repo.set_channel_status(ch.channel_id, st)
    print("Durum güncellendi")


def delete_channel(repo: ChannelRepository):
    channel_id = ask_required("Channel ID")

    channels = getattr(repo, "_ChannelRepository__channels")
    if channel_id not in channels:
        print("Kanal bulunamadı")
        return

    owner_index = getattr(repo, "_ChannelRepository__owner_index")
    type_index = getattr(repo, "_ChannelRepository__type_index")
    ch = channels[channel_id]

    if ch.owner_id in owner_index and channel_id in owner_index[ch.owner_id]:
        owner_index[ch.owner_id].remove(channel_id)
    if ch.channel_type in type_index and channel_id in type_index[ch.channel_type]:
        type_index[ch.channel_type].remove(channel_id)

    del channels[channel_id]

    setattr(repo, "_ChannelRepository__last_modified", datetime.now())
    getattr(repo, "_save_to_file")()

    print("Kanal silindi")



def dashboard(channel_repo: ChannelRepository):
    channel_id = ask_required("Channel ID")
    ch = channel_repo.get_channel_by_id(channel_id)

    print("\n--- CHANNEL DASHBOARD ---")
    print(f"ID: {ch.channel_id}")
    print(f"Type: {type(ch).__name__}")
    print(f"Name: {ch.name}")
    print(f"Owner: {ch.owner_id}")
    print(f"Status: {ch.status.value}")
    print(f"Category: {getattr(ch, 'category', 'other')}")

    # polimorfiz
    print(f"Access Level (polymorphic): {ch.get_access_level()}")

    # Basit istatisstk
    try:
        stats = ch.get_channel_statistics()
        if isinstance(stats, dict):
            print("Statistics:")
            for k, v in stats.items():
                print(f"  {k}: {v}")
        else:
            print("Statistics:", stats)
    except Exception as e:
        print("Statistics alınamadı:", e)

def run_demo_cli():
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    user_repo = UserRepository(os.path.join(data_dir, "users.json"))
    channel_repo = ChannelRepository(os.path.join(data_dir, "channels.json"))

    print("\nMODULE 1 - DEMO iptal --> iptal yazın \n")

    while True:
        print("\n=== ANA MENÜ ===")
        print("1) Kullanıcı")
        print("2) Kanal")
        print("3) Dashboard")
        print("0) Çıkış")

        sec = _raw("Seçim: ").strip()

        try:
            if sec == "1":
                while True:
                    print("\n--- USER MENU ---")
                    print("1) Listele  2) Ekle  3) Düzenle  4) Sil  0) Geri")
                    c = _raw("Seçim: ").strip()
                    try:
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
                        else:
                            print("Hatalı seçim")
                    except Cancelled:
                        print("İşlem iptal edildi.")
                        pause()

            elif sec == "2":
                while True:
                    print("\n--- CHANNEL MENU ---")
                    print("1) Listele  2) Oluştur  3) Düzenle  4) Durum  5) Sil  0) Geri")
                    c = _raw("Seçim: ").strip()
                    try:
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
                        else:
                            print("Hatalı seçim")
                    except Cancelled:
                        print("İşlem iptal edildi.")
                        pause()

            elif sec == "3":
                try:
                    dashboard(channel_repo)
                except Cancelled:
                    print("İşlem iptal edildi.")
                pause()

            elif sec == "0":
                print("Çıkış")
                break

            else:
                print("Hatalı seçim")

        except Exception as e:
            print(f"Hata: {type(e).__name__}: {e}")
            pause()


if __name__ == "__main__":
    run_demo_cli()
