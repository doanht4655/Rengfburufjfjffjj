import hashlib
import random
import requests
import time
from datetime import datetime
import json
import sys
import urllib3
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = {
    'api_key': '882a8490361da98702bf97a021ddc14d',
    'secret': '62f8ce9f74b12f84c123cc23437a4a32',
    'key': ['ChanHungCoder_KeyRegFBVIP_9999', 'DCHVIPKEYREG']
}

# Token Telegram Bot đã được cấu hình sẵn
TELEGRAM_BOT_TOKEN = "8001493342:AAFRuoL0XmPuPMj4d8448YOUOATCW2OQvMI"

email_prefix = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com']

def create_account():
    random_birth_day = datetime.strftime(datetime.fromtimestamp(random.randint(
        int(time.mktime(datetime.strptime('1980-01-01', '%Y-%m-%d').timetuple())),
        int(time.mktime(datetime.strptime('1995-12-30', '%Y-%m-%d').timetuple()))
    )), '%Y-%m-%d')

    names = {
        'first': ['JAMES', 'JOHN', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID'],
        'last': ['SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'MILLER'],
        'mid': ['Alexander', 'Anthony', 'Charles', 'Dash', 'David', 'Edward']
    }

    random_first_name = random.choice(names['first'])
    random_name = f"{random.choice(names['mid'])} {random.choice(names['last'])}"
    password = f'HelloReg{random.randint(0, 9999999)}?#@'
    full_name = f"{random_first_name} {random_name}"
    md5_time = hashlib.md5(str(time.time()).encode()).hexdigest()
    hash_ = f"{md5_time[0:8]}-{md5_time[8:12]}-{md5_time[12:16]}-{md5_time[16:20]}-{md5_time[20:32]}"
    email_rand = f"{full_name.replace(' ', '').lower()}{hashlib.md5((str(time.time()) + datetime.strftime(datetime.now(), '%Y%m%d')).encode()).hexdigest()[0:6]}@{random.choice(email_prefix)}"
    gender = 'M' if random.randint(0, 10) > 5 else 'F'

    req = {
        'api_key': app['api_key'],
        'attempt_login': True,
        'birthday': random_birth_day,
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': random_first_name,
        'format': 'json',
        'gender': gender,
        'lastname': random_name,
        'email': email_rand,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': hash_,
        'return_multiple_errors': True
    }

    sig = ''.join([f'{k}={v}' for k, v in sorted(req.items())])
    ensig = hashlib.md5((sig + app['secret']).encode()).hexdigest()
    req['sig'] = ensig

    api = 'https://b-api.facebook.com/method/user.register'

    def _call(url='', params=None, post=True):
        headers = {
            'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'
        }
        if post:
            response = requests.post(url, data=params, headers=headers, verify=False)
        else:
            response = requests.get(url, params=params, headers=headers, verify=False)
        return response.text

    reg = _call(api, req)
    reg_json = json.loads(reg)
    uid = reg_json.get('session_info', {}).get('uid')
    access_token = reg_json.get('session_info', {}).get('access_token')
    error_code = reg_json.get('error_code')
    error_msg = reg_json.get('error_msg')

    result = {
        'success': False,
        'message': '',
        'data': {}
    }

    if uid is not None and access_token is not None:
        data_to_save = f"{random_birth_day}:{full_name}:{email_rand}:{password}:{uid}:{access_token}"
        with open("facebook.txt", "a") as file:
            file.write(data_to_save + "\n")

        result['success'] = True
        result['data'] = {
            'date_of_birth': random_birth_day,
            'name': full_name,
            'email': email_rand,
            'password': password,
            'uid': uid,
            'access_token': access_token
        }
        
        console_output = "Tạo thành công:\n"
        console_output += f"  Date of Birth: {random_birth_day}\n"
        console_output += f"  Name         : {full_name}\n"
        console_output += f"  Mail         : {email_rand}\n"
        console_output += f"  Password     : {password}\n"
        console_output += f"  Id           : {uid}\n"
        console_output += f"  Token        : {access_token}\n"
        
        result['message'] = console_output
    else:
        if error_code and error_msg:
            result['message'] = f"Lỗi: {error_code} - {error_msg}"
        else:
            result['message'] = "Lỗi không xác định"

    return result

# Hàm tạo nhiều tài khoản
def create_multiple_accounts(count):
    results = []
    for i in range(count):
        result = create_account()
        results.append(result)
        time.sleep(5)  # Giữ thời gian nghỉ giữa các lần tạo tài khoản
    
    return results

# Xử lý lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Chào mừng đến với Bot tạo tài khoản Facebook!\n'
        'Sử dụng /fb [số lượng] để tạo tài khoản (ví dụ: /fb 5)'
    )

# Xử lý lệnh /fb
async def fb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Lấy số lượng tài khoản từ lệnh
        if not context.args:
            account_count = 1  # Mặc định tạo 1 tài khoản nếu không có tham số
        else:
            account_count = int(context.args[0])
            
        if account_count <= 0:
            await update.message.reply_text("Số lượng không được thấp hơn 0.")
            return
            
        # Thông báo bắt đầu tạo tài khoản
        await update.message.reply_text(f"Đang tạo {account_count} tài khoản Facebook, vui lòng đợi...")
        
        # Tạo tài khoản
        results = create_multiple_accounts(account_count)
        
        # Gửi kết quả từng tài khoản
        for i, result in enumerate(results):
            if result['success']:
                await update.message.reply_text(f"Tài khoản #{i+1}:\n{result['message']}")
            else:
                await update.message.reply_text(f"Tài khoản #{i+1} thất bại: {result['message']}")
        
        # Gửi thông báo hoàn thành
        await update.message.reply_text(f"Đã tạo xong {account_count} tài khoản. Đã gửi")
        
    except ValueError:
        await update.message.reply_text("Tham số không hợp lệ. Sử dụng: /fb [số lượng]")
    except Exception as e:
        logger.error(f"Lỗi: {str(e)}")
        await update.message.reply_text(f"Có lỗi xảy ra: {str(e)}")

# Xử lý tin nhắn không rõ
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Lệnh không hợp lệ. Sử dụng /help để xem danh sách lệnh.")

# Xử lý lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Danh sách lệnh:\n"
        "/start - Bắt đầu bot\n"
        "/fb [số lượng] - Tạo tài khoản Facebook (mặc định: 1)\n"
        "/help - Hiển thị trợ giúp"
    )
    await update.message.reply_text(help_text)

def main() -> None:
    # Sử dụng token đã cấu hình sẵn
    token = TELEGRAM_BOT_TOKEN
    
    # Tạo ứng dụng
    application = Application.builder().token(token).build()

    # Thêm các handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fb", fb_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Xử lý các lệnh không rõ
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Chạy bot
    print("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    # Kiểm tra nếu chạy trực tiếp từ dòng lệnh
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        try:
            account_count = int(input("Nhập số lượng acc muốn reg: "))
            if account_count <= 0:
                print("Số lượng không được thấp hơn 0.")
                sys.exit(1)
        except ValueError:
            print("Tham số không hợp lệ.")
            sys.exit(1)

        results = create_multiple_accounts(account_count)
        for result in results:
            if result['success']:
                print(result['message'])
            else:
                print(result['message'])

        print("Đã gửi")
    else:
        # Chạy bot Telegram
        main()