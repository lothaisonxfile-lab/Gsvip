import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import json
import os
import re
import random
import sys

# ================= CẤU HÌNH TRỰC TIẾP TẠI ĐÂY =================
TOKEN = "TOKEN_BOT_CUA_BAN"  # Thay bằng Token bot của Đại ca
OWNER_ID = 123456789         # Thay bằng ID Telegram của Đại ca (Đka)

# Danh sách câu chửi mẫu (Đại ca có thể tự do chỉnh sửa hoặc thêm cho đủ 500 câu)
CHUI_LIST = [
    "Khôn ba năm dại một giờ, block bớt nói nhiều!",
    "Trình độ thì giới hạn mà lựu đạn thì vô biên.",
    "Ăn cơm mắm mà bày đặt nói chuyện thế giới.",
    "Bớt sủa lại cho sang nha con.",
    "Đầu để mọc tóc chứ không có não à?",
    "Não dạo này có bật công tắc không thế?",
    "Nói chuyện thì sang mà cái gan thì nhỏ.",
    "Bớt tỏ ra nguy hiểm đi nha con gà.",
    "Nhìn mặt thì thông minh mà phát ngôn thì kém tinh tế.",
    "Sống sao cho người ta nể, chứ đừng để người ta khinh nha con."
]
# ==============================================================

try:
    bot = telebot.TeleBot(TOKEN)
    # Thử nghiệm gửi một request giả lập để kiểm tra Token có hoạt động hay không
    bot_info = bot.get_me()
    print(f"\033[92m[✓] Bot VIP đã chạy thành công! Username: @{bot_info.username}\033[0m")
except Exception as e:
    print(f"\033[91m[X] Khởi động thất bại! Lỗi cấu hình hoặc Token sai: {e}\033[0m")
    sys.exit(1)

DATA_FILE = "bot_data.json"
data = {"allowed_groups": [], "mvip_users": {}, "bvip_users": {}}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try: data = json.load(f)
        except: pass

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_target_user_and_args(message):
    target_user_id = None
    target_name = "Người dùng"
    args = message.text.split()
    
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        time_arg = args[1:] if len(args) > 1 else None
        return target_user_id, target_name, time_arg

    time_arg = None
    if len(args) > 1:
        last_arg = args[-1].lower()
        if re.match(r'^\d+[dmy]$', last_arg) or last_arg == 'max':
            time_arg = [last_arg]
            user_part = args[1:-1]
        else:
            user_part = args[1:]
            
        user_str = "".join(user_part)
        if user_str.isdigit():
            target_user_id = int(user_str)
            return target_user_id, f"ID: {target_user_id}", time_arg

    if message.entities:
        for ent in message.entities:
            if ent.type == "text_mention":
                return ent.user.id, ent.user.first_name, time_arg
                
    return None, None, None

def is_owner(user_id):
    return user_id == OWNER_ID

vip_status = {} 
vippro_status = {} 

@bot.message_handler(func=lambda msg: True, content_types=['text', 'photo', 'sticker', 'video', 'document'])
def handle_all_messages(message):
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
    
    if message.chat.type in ['group', 'supergroup']:
        if chat_id not in data["allowed_groups"] and not is_owner(user_id):
            return
            
        if chat_id in data["mvip_users"] and user_id in data["mvip_users"][chat_id]:
            try:
                bot.restrict_chat_member(message.chat.id, user_id, until_date=time.time() + 3600)
                bot.delete_message(message.chat.id, message.message_id)
            except: pass
            return

        if chat_id in data["bvip_users"] and user_id in data["bvip_users"][chat_id]:
            try:
                bot.ban_chat_member(message.chat.id, user_id)
                bot.delete_message(message.chat.id, message.message_id)
            except: pass
            return

        if vippro_status.get(chat_id, False) and not is_owner(user_id):
            if any(word in message.text.lower() for word in ["óc", "gà", "sủa", "cl", "dcm"]):
                try: bot.delete_message(message.chat.id, message.message_id)
                except: pass
                
    bot.process_new_messages([message])

@bot.message_handler(commands=['add'])
def add_box(message):
    if not is_owner(message.from_user.id): return
    cid = str(message.chat.id)
    if cid not in data["allowed_groups"]:
        data["allowed_groups"].append(cid)
        save_data()
        bot.reply_to(message, "Tuân lệnh Đka! Nhóm này đã được phép dùng bot.")

@bot.message_handler(commands=['badd'])
def badd_box(message):
    if not is_owner(message.from_user.id): return
    cid = str(message.chat.id)
    if cid in data["allowed_groups"]:
        data["allowed_groups"].remove(cid)
        save_data()
        bot.reply_to(message, "Tuân lệnh Đại ca! Đã hủy kích hoạt bot tại nhóm này.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "📜 **DANH SÁCH LỆNH CỦA BOT:**\n"
        "/menu - Menu troll nhận quyền API\n"
        "/m - Mute người dùng (36 phút)\n"
        "/um - Mở mute thông thường\n"
        "/b - Ban khỏi nhóm\n"
        "/mtsieuvip - LỆNH VIP: Mute cả Admin (Gỡ bằng /um)\n"
        "/gs [Time] - Giam giữ Siêu cấp tối đa 36 năm (Mặc định 36p. Ví dụ: /gs 5d, /gs max)\n"
        "/vip /vip2 - Bật/Tắt chửi viết tắt tự động\n"
        "/vippro /vippro2 - Bật/Tắt chửi + xóa tin phản bác\n"
        "/mvip /umvip - Mute vĩnh viễn không thể gỡ\n"
        "/bvip /ubvip - Ban vĩnh viễn ra vào đều bị ban\n"
        "/xoa [1-50] - Xóa hàng loạt tin nhắn\n"
        "--- HỆ THỐNG CHỦ SỞ HỮU ---\n"
        "/mcsh - Tự khóa mõm Đại ca (Gỡ tại Chat Riêng)\n"
        "/bcsh - Tự trục xuất Đại ca (Gỡ tại Chat Riêng)\n"
        "👉 Cách gỡ tại Chat Riêng với bot:\n"
        "`/mgsvip <id_Đại_ca> <id_phòng>` để gỡ Mute\n"
        "`/bgsvip <id_Đại_ca> <id_phòng>` để gỡ Ban"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['menu'])
def menu_cmd(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🎁 Nhận API / Quyền Admin FREE 1 Ngày", callback_data="troll_1"))
    markup.row(InlineKeyboardButton("💎 Liên hệ Admin Mua API / Quyền Vĩnh Viễn", callback_data="troll_2"))
    bot.send_message(message.chat.id, "Chọn gói dịch vụ bạn muốn nâng cấp:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("troll_"))
def handle_troll_buttons(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    if is_owner(uid):
        bot.answer_callback_query(call.id, "Đka đang bấm nút troll làm gì thế!", show_alert=True)
        return
        
    if call.data == "troll_1":
        try:
            bot.restrict_chat_member(cid, uid, until_date=time.time() + 2160) 
            bot.send_message(cid, f"🤣 Đã dính bẫy! Mute thanh niên {call.from_user.first_name} 36 phút vì tội tham lam.")
        except: pass
    elif call.data == "troll_2":
        try:
            bot.ban_chat_member(cid, uid)
            bot.send_message(cid, f"⚡ Đại gia nửa mùa {call.from_user.first_name} đã bị sút khỏi kênh!")
        except: pass

@bot.message_handler(commands=['m', 'um', 'b', 'mtsieuvip', 'gs'])
def admin_actions(message):
    cmd = message.text.split().replace("/", "")
    target_id, target_name, time_arg = get_target_user_and_args(message)
    if not target_id: 
        return bot.reply_to(message, "Vui lòng tag, reply hoặc điền ID người cần xử lý.")

    if cmd in ["mtsieuvip", "gs"] and not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Tuổi gì đòi dùng lệnh này! Chỉ dành cho Đại ca.")
        return

    try:
        if cmd == "m":
            bot.restrict_chat_member(message.chat.id, target_id, until_date=time.time() + 2160)
            bot.reply_to(message, f"🤐 Đã khóa mõm {target_name} 36 phút.")
        elif cmd == "mtsieuvip":
            bot.restrict_chat_member(message.chat.id, target_id, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
            bot.reply_to(message, f"⚡ Lệnh từ Đại ca! Đã khóa mõm SIÊU CẤP đối với {target_name} (Chấp cả Admin).")
        elif cmd == "gs":
            duration = 2160 
            time_text = "36 phút"
            if time_arg:
                arg_str = "".join(time_arg).lower()
                if arg_str == 'max' or 'y' in arg_str:
                    duration = 36 * 365 * 24 * 3600 
                    time_text = "36 NĂM (THIÊN THU)"
                elif 'd' in arg_str:
                    days = int(arg_str.replace('d', ''))
                    duration = days * 24 * 3600
                    time_text = f"{days} ngày"
                elif 'm' in arg_str:
                    minutes = int(arg_str.replace('m', ''))
                    duration = minutes * 60
                    time_text = f"{minutes} phút"
            bot.restrict_chat_member(message.chat.id, target_id, until_date=time.time() + duration, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
            bot.reply_to(message, f"⚖️ **LỆNH GIAM GIỮ TỪ ĐẠI CA:**\nĐã tống giam chỉnh đốn {target_name} vào ngục tối trong vòng **{time_text}**!")
        elif cmd == "um":
            bot.restrict_chat_member(message.chat.id, target_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            bot.reply_to(message, f"🔓 Đã mở khóa mõm bình thường cho {target_name}.")
        elif cmd == "b":
            bot.ban_chat_member(message.chat.id, target_id)
            bot.reply_to(message, f"✈️ Đã tiễn {target_name} lên đường bay màu khỏi nhóm.")
    except Exception as e:
        bot.reply_to(message, "Lỗi phân quyền bot hoặc Telegram giới hạn quyền trên user này!")

@bot.message_handler(commands=['mvip', 'umvip', 'bvip', 'ubvip'])
def vip_lock_cmds(message):
    if not is_owner(message.from_user.id): return
    cid = str(message.chat.id)
