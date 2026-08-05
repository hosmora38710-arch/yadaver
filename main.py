# ==================================================
# main.py - نسخه نهایی با سیستم اعتبارسنجی - آماده برای اندروید و ویندوز
# ==================================================
#
# برای ساخت APK با Buildozer این وابستگی‌ها را در buildozer.spec قرار دهید:
# requirements = python3,kivy,plyer,jdatetime,arabic-reshaper,python-bidi,pyjnius,android
# android.permissions = VIBRATE,POST_NOTIFICATIONS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# orientation = portrait
# android.api = 33 (یا بالاتر)
# android.minapi = 21
#
# ==================================================

import os
import sys
import sqlite3
import shutil
import json
from datetime import datetime, timedelta
import jdatetime

# تنظیمات OpenGL فقط برای ویندوز
if sys.platform == 'win32':
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex, platform
from kivy.core.text import LabelBase
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import arabic_reshaper
from bidi.algorithm import get_display

# برای فعال کردن لاگ‌ها در کنسول، True کنید
DEBUG = True

def log(msg):
    if DEBUG:
        print(msg)

# ==================================================
# مشخصات تماس سازنده
# ==================================================
APP_INFO = {
    'app_name': 'یادآور',
    'version': '1.0',
    'developer': 'حسین مرادی',
    'phone': '0912xxxxxxx',
    'email': 'homo00021@gmail.com',
    'telegram': '@your_id',
    'bale': '@Hosein_morady',
    'note': 'در صورت بروز مشکل یا پیشنهاد با من درارتباط باشید',
}

# رمز تأیید برنامه (ثابت)
VERIFICATION_CODE = "SYah70521021@!05"

# ==================================================
# صدای سیستم - اصلاح شده برای اندروید
# ==================================================
HAS_WINSOUND = False
HAS_PLYER = False
HAS_VIBRATOR = False

# winsound فقط روی ویندوز
if sys.platform == 'win32':
    try:
        import winsound
        HAS_WINSOUND = True
        log("[OK] Winsound loaded")
    except ImportError:
        pass

# ویبره برای اندروید
try:
    from plyer import vibrator
    HAS_VIBRATOR = True
    log("[OK] Vibrator loaded")
except ImportError:
    pass

# اعلان‌ها
try:
    from plyer import notification
    HAS_PLYER = True
    log("[OK] Plyer loaded")
except ImportError:
    log("[WARN] Plyer not available")

# ==================================================
# تم‌ها (روشن / تاریک)
# ==================================================
THEMES = {
    'light': {
        # پس‌زمینه ملایم آبی-خاکستری برای کنتراست بهتر با کارت سفید
        'window_bg': '#E8EDF5',
        'header_title': (0.12, 0.16, 0.28, 1),
        'card_bg': (1.0, 1.0, 1.0, 1),
        'card_bg_done': (0.94, 0.95, 0.96, 1),
        'card_bg_today': (1.0, 0.96, 0.88, 1),
        'card_bg_overdue': (1.0, 0.93, 0.91, 1),
        # متن اصلی تیره برای خوانایی بالا
        'title_color': (0.10, 0.12, 0.18, 1),
        'title_color_done': (0.48, 0.50, 0.54, 1),
        'desc_color': (0.28, 0.32, 0.38, 1),
        'desc_color_done': (0.55, 0.57, 0.60, 1),
        'info_color': (0.35, 0.40, 0.48, 1),
        'empty_color': (0.42, 0.46, 0.52, 1),
        'search_hint': (0.50, 0.54, 0.60, 1),
        'input_bg': (1, 1, 1, 1),
        'input_fg': (0.08, 0.10, 0.14, 1),
        'popup_bg': (0.14, 0.16, 0.22, 1),
        'popup_title': (1, 1, 1, 1),
        'alert_bg': (0.12, 0.14, 0.10, 1),
        'badge_today': '#EF6C00',
        'badge_overdue': '#D32F2F',
        'calendar_bg': (1, 1, 1, 1),
        'calendar_day': (0.08, 0.10, 0.14, 1),
        'calendar_selected': '#1565C0',
        'calendar_today': '#EF6C00',
        'accent': '#1B5E20',
        'accent_soft': '#E8F5E9',
    },
    'dark': {
        'window_bg': '#0F1115',
        'header_title': (0.95, 0.96, 0.98, 1),
        'card_bg': (0.16, 0.17, 0.20, 1),
        'card_bg_done': (0.12, 0.13, 0.14, 1),
        'card_bg_today': (0.26, 0.22, 0.12, 1),
        'card_bg_overdue': (0.28, 0.14, 0.14, 1),
        'title_color': (0.96, 0.96, 0.98, 1),
        'title_color_done': (0.58, 0.60, 0.64, 1),
        'desc_color': (0.78, 0.80, 0.84, 1),
        'desc_color_done': (0.52, 0.54, 0.56, 1),
        'info_color': (0.68, 0.70, 0.74, 1),
        'empty_color': (0.60, 0.62, 0.66, 1),
        'search_hint': (0.55, 0.58, 0.62, 1),
        'input_bg': (0.22, 0.24, 0.28, 1),
        'input_fg': (0.96, 0.96, 0.98, 1),
        'popup_bg': (0.12, 0.13, 0.16, 1),
        'popup_title': (0.96, 0.96, 0.98, 1),
        'alert_bg': (0.10, 0.11, 0.08, 1),
        'badge_today': '#FFB74D',
        'badge_overdue': '#EF5350',
        'calendar_bg': (0.18, 0.19, 0.22, 1),
        'calendar_day': (0.94, 0.94, 0.96, 1),
        'calendar_selected': '#42A5F5',
        'calendar_today': '#FFB74D',
        'accent': '#66BB6A',
        'accent_soft': (0.12, 0.20, 0.14, 1),
    }
}

# ==================================================
# فونت فارسی — اولویت با Regular/Medium برای خوانایی، Bold برای عناوین
# ==================================================
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _pick_font(candidates):
    """اولین فایل فونت موجود را برمی‌گرداند"""
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None

# مسیر پایه فونت‌ها
if platform == 'android':
    try:
        from android import mActivity
        _ASSETS_DIR = os.path.join(os.path.dirname(mActivity.getPackageCodePath()), 'assets')
        _FONTS_DIR = os.path.join(_ASSETS_DIR, 'fonts')
    except Exception:
        _FONTS_DIR = os.path.join(_BASE_DIR, 'fonts')
else:
    _FONTS_DIR = os.path.join(_BASE_DIR, 'fonts')

# ترتیب اولویت: Regular/Medium خواناتر از Thin هستند
_REGULAR_CANDIDATES = [
    os.path.join(_FONTS_DIR, 'Vazirmatn-Regular.ttf'),
    os.path.join(_FONTS_DIR, 'Vazirmatn-Medium.ttf'),
    os.path.join(_FONTS_DIR, 'Vazirmatn.ttf'),
    os.path.join(_FONTS_DIR, 'Vazirmatn-Thin.ttf'),  # آخرین انتخاب
    os.path.join(_BASE_DIR, 'fonts', 'Vazirmatn-Regular.ttf'),
    os.path.join(_BASE_DIR, 'fonts', 'Vazirmatn-Medium.ttf'),
    os.path.join(_BASE_DIR, 'fonts', 'Vazirmatn-Thin.ttf'),
    '/system/fonts/NotoNaskhArabic-Regular.ttf',
    '/system/fonts/NotoSansArabic-Regular.ttf',
    '/system/fonts/DroidNaskh-Regular.ttf',
    '/system/fonts/Roboto-Regular.ttf',
]
_BOLD_CANDIDATES = [
    os.path.join(_FONTS_DIR, 'Vazirmatn-Bold.ttf'),
    os.path.join(_FONTS_DIR, 'Vazirmatn-ExtraBold.ttf'),
    os.path.join(_FONTS_DIR, 'Vazirmatn-SemiBold.ttf'),
    os.path.join(_BASE_DIR, 'fonts', 'Vazirmatn-Bold.ttf'),
    os.path.join(_BASE_DIR, 'fonts', 'Vazirmatn-ExtraBold.ttf'),
    '/system/fonts/NotoNaskhArabic-Bold.ttf',
    '/system/fonts/Roboto-Bold.ttf',
]

# پوشه داده‌های برنامه برای اندروید
_USER_DATA_DIR = None
if platform == 'android':
    try:
        from android.storage import app_storage_path
        _USER_DATA_DIR = app_storage_path()
        log(f"[OK] Android storage path: {_USER_DATA_DIR}")
    except Exception as e:
        log(f"[WARN] Could not get Android storage path: {e}")

try:
    regular_path = _pick_font(_REGULAR_CANDIDATES)
    bold_path = _pick_font(_BOLD_CANDIDATES) or regular_path

    if regular_path:
        LabelBase.register(name='PersianFont', fn_regular=regular_path)
        log(f"[OK] PersianFont: {regular_path}")
    else:
        LabelBase.register(name='PersianFont', fn_regular='Arial')
        log("[WARN] PersianFont fallback to Arial")

    if bold_path:
        LabelBase.register(name='PersianFontBold', fn_regular=bold_path)
        log(f"[OK] PersianFontBold: {bold_path}")
    else:
        LabelBase.register(name='PersianFontBold', fn_regular='Arial')
        log("[WARN] PersianFontBold fallback to Arial")
except Exception as e:
    log(f"[WARN] Font error: {e}")
    try:
        LabelBase.register(name='PersianFont', fn_regular='Arial')
        LabelBase.register(name='PersianFontBold', fn_regular='Arial')
    except Exception:
        pass


def reshape_persian(text):
    if not text:
        return ''
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except Exception:
        return str(text)

# ==================================================
# ترجمه‌ها
# ==================================================
TRANSLATIONS = {
    'fa': {
        'app_name': 'یادآور',
        'my_reminders': 'یادآورهای من',
        'add': '+ جدید',
        'settings': 'تنظیمات',
        'clear': 'پاک',
        'search_hint': 'جستجو در عنوان و توضیحات...',
        'all': 'همه',
        'today': 'امروز',
        'tomorrow': 'فردا',
        'this_week': 'این هفته',
        'active': 'فعال',
        'completed': 'تکمیل شده',
        'no_reminders': 'هیچ یادآوری وجود ندارد\nروی دکمه + جدید کلیک کنید',
        'no_search_result': 'هیچ یادآوری با این عبارت یافت نشد',
        'no_today': 'یادآوری برای امروز وجود ندارد',
        'no_tomorrow': 'یادآوری برای فردا وجود ندارد',
        'no_week': 'یادآوری در این هفته وجود ندارد',
        'edit': 'ویرایش',
        'restore': 'بازگردانی',
        'complete': 'تکمیل',
        'delete': 'حذف',
        'confirm_delete': 'آیا از حذف این یادآوری مطمئن هستید؟',
        'cancel': 'انصراف',
        'confirm': 'تأیید',
        'reminder_deleted': 'یادآوری حذف شد',
        'reminder_completed': 'یادآوری انجام شد',
        'reminder_updated': 'یادآوری با موفقیت ویرایش شد',
        'reminder_added': 'یادآوری با موفقیت اضافه شد',
        'error': 'خطا',
        'success': 'موفقیت',
        'reminder_not_found': 'یادآوری یافت نشد',
        'invalid_date': 'تاریخ نامعتبر است',
        'invalid_time': 'زمان نامعتبر است',
        'enter_title': 'لطفا عنوان را وارد کنید',
        'add_reminder': 'افزودن یادآوری جدید',
        'edit_reminder': 'ویرایش یادآوری',
        'title': 'عنوان یادآوری',
        'description': 'توضیحات (اختیاری)',
        'date': 'تاریخ',
        'time': 'زمان',
        'notify_before': 'اعلان قبل (دقیقه):',
        'repeat': 'تکرار:',
        'repeat_none': 'بدون تکرار',
        'repeat_daily': 'روزانه',
        'repeat_weekly': 'هفتگی',
        'repeat_monthly': 'ماهانه',
        'end_date': 'پایان:',
        'no_end': 'بدون پایان',
        'save': 'ذخیره',
        'update': 'به‌روزرسانی',
        'select_date': 'انتخاب تاریخ',
        'select_time': 'انتخاب زمان',
        'year': 'سال',
        'month': 'ماه',
        'day': 'روز',
        'hour': 'ساعت',
        'minute': 'دقیقه',
        'ok': 'تایید',
        'snooze': 'تاخیر',
        'snooze_5': '۵ دقیقه',
        'snooze_15': '۱۵ دقیقه',
        'snooze_30': '۳۰ دقیقه',
        'snooze_60': '۱ ساعت',
        'snoozed': 'یادآوری به {} موکول شد',
        'about': 'درباره برنامه و تماس با سازنده',
        'about_title': 'درباره برنامه',
        'close': 'بستن',
        'theme': 'ظاهر برنامه',
        'light': 'روشن',
        'dark': 'تاریک',
        'check_interval': 'فاصله زمانی بررسی (ثانیه)',
        'settings_saved': 'تنظیمات ذخیره شد',
        'min_interval': 'حداقل زمان ۵ ثانیه است',
        'enter_valid_number': 'لطفاً یک عدد معتبر وارد کنید',
        'reminder_due': 'زمان یادآوری رسید',
        'reminder': 'یادآوری',
        'overdue': 'گذشته از موعد',
        'today_label': 'امروز',
        'export': 'خروجی',
        'import': 'ورودی',
        'export_success': 'خروجی با موفقیت ذخیره شد',
        'import_success': 'ورودی با موفقیت انجام شد',
        'import_error': 'خطا در ورودی',
        'select_file': 'انتخاب فایل',
        'license_title': 'تأیید برنامه',
        'enter_code': 'کد تمدید را وارد کنید',
        'verify': 'تأیید',
        'later': 'بعداً',
        'contact': 'تماس با سازنده',
        'invalid_code': '❌ کد اشتباه است',
        'code_required': 'لطفاً کد را وارد کنید',
        'days_remaining': '{} روز استفاده رایگان باقی مانده',
        'few_days_remaining': '⚠️ تنها {} روز استفاده رایگان باقی مانده\nبرای ادامه، کد تمدید را وارد کنید',
        'grace_period': '⏰ دوره مهلت ۳۰ روزه\nلطفاً کد تمدید را وارد کنید',
        'expired': '❌ زمان استفاده به پایان رسیده\nبرای ادامه با سازنده تماس بگیرید',
        'exit': 'خروج',
        'contact_info': 'برای دریافت کد تمدید با ما تماس بگیرید',
    },
    'en': {
        'app_name': 'Yadavar',
        'my_reminders': 'My Reminders',
        'add': '+ Add',
        'settings': 'Settings',
        'clear': 'Clear',
        'search_hint': 'Search in title and description...',
        'all': 'All',
        'today': 'Today',
        'tomorrow': 'Tomorrow',
        'this_week': 'This Week',
        'active': 'Active',
        'completed': 'Completed',
        'no_reminders': 'No reminders\nClick + Add button',
        'no_search_result': 'No reminders found with this search',
        'no_today': 'No reminders for today',
        'no_tomorrow': 'No reminders for tomorrow',
        'no_week': 'No reminders this week',
        'edit': 'Edit',
        'restore': 'Restore',
        'complete': 'Complete',
        'delete': 'Delete',
        'confirm_delete': 'Are you sure you want to delete this reminder?',
        'cancel': 'Cancel',
        'confirm': 'Confirm',
        'reminder_deleted': 'Reminder deleted',
        'reminder_completed': 'Reminder completed',
        'reminder_updated': 'Reminder updated successfully',
        'reminder_added': 'Reminder added successfully',
        'error': 'Error',
        'success': 'Success',
        'reminder_not_found': 'Reminder not found',
        'invalid_date': 'Invalid date',
        'invalid_time': 'Invalid time',
        'enter_title': 'Please enter a title',
        'add_reminder': 'Add New Reminder',
        'edit_reminder': 'Edit Reminder',
        'title': 'Title',
        'description': 'Description (Optional)',
        'date': 'Date',
        'time': 'Time',
        'notify_before': 'Notify before (min):',
        'repeat': 'Repeat:',
        'repeat_none': 'No repeat',
        'repeat_daily': 'Daily',
        'repeat_weekly': 'Weekly',
        'repeat_monthly': 'Monthly',
        'end_date': 'End Date:',
        'no_end': 'No end',
        'save': 'Save',
        'update': 'Update',
        'select_date': 'Select Date',
        'select_time': 'Select Time',
        'year': 'Year',
        'month': 'Month',
        'day': 'Day',
        'hour': 'Hour',
        'minute': 'Minute',
        'ok': 'OK',
        'snooze': 'Snooze',
        'snooze_5': '5 min',
        'snooze_15': '15 min',
        'snooze_30': '30 min',
        'snooze_60': '1 hour',
        'snoozed': 'Reminder snoozed to {}',
        'about': 'About & Contact',
        'about_title': 'About App',
        'close': 'Close',
        'theme': 'Theme',
        'light': 'Light',
        'dark': 'Dark',
        'check_interval': 'Check interval (seconds):',
        'settings_saved': 'Settings saved',
        'min_interval': 'Minimum interval is 5 seconds',
        'enter_valid_number': 'Please enter a valid number',
        'reminder_due': 'Reminder Due!',
        'reminder': 'Reminder',
        'overdue': 'Overdue',
        'today_label': 'Today',
        'export': 'Export',
        'import': 'Import',
        'export_success': 'Export saved successfully',
        'import_success': 'Import completed successfully',
        'import_error': 'Import error',
        'select_file': 'Select File',
        'license_title': 'Verify License',
        'enter_code': 'Enter extension code',
        'verify': 'Verify',
        'later': 'Later',
        'contact': 'Contact Developer',
        'invalid_code': '❌ Invalid code',
        'code_required': 'Please enter the code',
        'days_remaining': '{} days of free use remaining',
        'few_days_remaining': '⚠️ Only {} days of free use remaining\nEnter extension code to continue',
        'grace_period': '⏰ 30 days grace period\nPlease enter extension code',
        'expired': '❌ Usage time has expired\nPlease contact the developer',
        'exit': 'Exit',
        'contact_info': 'Contact us to get the extension code',
    }
}


def _(key, lang='fa'):
    """تابع ترجمه"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['fa']).get(key, key)


# ==================================================
# سیستم اعتبارسنجی - اصلاح شده با data_dir
# ==================================================
class LicenseManager:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir
        self.filename = os.path.join(data_dir, 'license.json')
        self.TRIAL_DAYS = 365
        self.GRACE_DAYS = 30
        self.VERIFICATION_CODE = VERIFICATION_CODE
        self.data = self.load()

    def load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'first_run' not in data:
                        data['first_run'] = datetime.now().isoformat()
                    if 'is_verified' not in data:
                        data['is_verified'] = False
                    if 'verification_date' not in data:
                        data['verification_date'] = None
                    return data
        except Exception as e:
            log(f"[WARN] License load error: {e}")
        
        return {
            'first_run': datetime.now().isoformat(),
            'is_verified': False,
            'verification_date': None,
        }

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log(f"[WARN] License save error: {e}")
            return False

    def get_days_used(self):
        try:
            first_run = datetime.fromisoformat(self.data['first_run'])
            now = datetime.now()
            return (now - first_run).days
        except Exception:
            return 0

    def get_days_remaining(self):
        days_used = self.get_days_used()
        remaining = self.TRIAL_DAYS - days_used
        return max(0, remaining)

    def is_expired(self):
        return self.get_days_remaining() <= 0

    def is_in_grace_period(self):
        if not self.is_expired():
            return False
        days_used = self.get_days_used()
        days_over = days_used - self.TRIAL_DAYS
        return days_over <= self.GRACE_DAYS

    def verify_code(self, code):
        if code == self.VERIFICATION_CODE:
            self.data['is_verified'] = True
            self.data['verification_date'] = datetime.now().isoformat()
            self.data['first_run'] = datetime.now().isoformat()
            self.save()
            return True
        return False

    def is_verified(self):
        return self.data.get('is_verified', False)

    def get_status_message(self, lang='fa'):
        remaining = self.get_days_remaining()
        
        if self.is_verified():
            if lang == 'fa':
                return f"✅ تأیید شده - {remaining} روز استفاده رایگان باقی مانده"
            return f"✅ Verified - {remaining} days of free use remaining"
        elif remaining > 30:
            return _('days_remaining', lang).format(remaining)
        elif remaining > 0:
            return _('few_days_remaining', lang).format(remaining)
        elif self.is_in_grace_period():
            return _('grace_period', lang)
        else:
            return _('expired', lang)

    def get_status_color(self):
        if self.is_verified():
            return (0.4, 0.9, 0.4, 1)
        remaining = self.get_days_remaining()
        if remaining > 30:
            return (0.6, 1, 0.6, 1)
        elif remaining > 0:
            return (1, 0.9, 0.4, 1)
        elif self.is_in_grace_period():
            return (1, 0.7, 0.3, 1)
        else:
            return (1, 0.4, 0.4, 1)


# ==================================================
# اعتبارسنجی
# ==================================================
def is_valid_jalali_date(date_str):
    try:
        parts = date_str.replace('-', '/').strip().split('/')
        if len(parts) != 3:
            return False
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1300 <= y <= 1500):
            return False
        if not (1 <= m <= 12):
            return False
        max_day = days_in_jalali_month(y, m)
        if not (1 <= d <= max_day):
            return False
        jdatetime.date(y, m, d)
        return True
    except Exception:
        return False


def is_valid_time(time_str):
    try:
        parts = time_str.strip().split(':')
        if len(parts) != 2:
            return False
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except Exception:
        return False


# ==================================================
# پایگاه داده - اصلاح شده با data_dir
# ==================================================
class Database:
    MAX_BACKUPS = 5

    def __init__(self, db_name='reminders.db', data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir
        self.db_name = os.path.join(data_dir, db_name)
        self.create_table()
        self.upgrade_database()
        self._backup_counter = 0

    def _get_connection(self):
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            log(f"[ERROR] Failed to connect to database: {e}")
            return None

    def _execute_query(self, query, params=None, fetch=False):
        conn = self._get_connection()
        if not conn:
            return None if not fetch else []
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return True
        except sqlite3.Error as e:
            log(f"[ERROR] Database error: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            conn.close()
            return None if not fetch else []

    def create_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notify_before INTEGER DEFAULT 15,
                repeat_type TEXT DEFAULT 'none',
                repeat_end_date TEXT,
                original_date TEXT,
                original_time TEXT,
                category TEXT DEFAULT 'عمومی'
            )
        '''
        result = self._execute_query(query)
        if result is not None:
            self._execute_query('CREATE INDEX IF NOT EXISTS idx_reminders_date_time ON reminders(date, time)')
            self._execute_query('CREATE INDEX IF NOT EXISTS idx_reminders_completed ON reminders(is_completed)')
            self._execute_query('CREATE INDEX IF NOT EXISTS idx_reminders_category ON reminders(category)')
            log("[OK] Database ready")
        else:
            log("[ERROR] Failed to create table")

    def upgrade_database(self):
        conn = self._get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(reminders)")
            columns = [col[1] for col in cursor.fetchall()]
            new_columns = {
                'repeat_end_date': 'TEXT',
                'original_date': 'TEXT',
                'original_time': 'TEXT',
                'category': "TEXT DEFAULT 'عمومی'",
            }
            for col_name, col_type in new_columns.items():
                if col_name not in columns:
                    log(f"[INFO] Adding {col_name} column")
                    try:
                        cursor.execute(f'ALTER TABLE reminders ADD COLUMN {col_name} {col_type}')
                        conn.commit()
                        log(f"[OK] {col_name} added")
                    except sqlite3.Error as e:
                        log(f"[WARN] Database upgrade error for {col_name}: {e}")
                        conn.rollback()
            # پر کردن category خالی
            try:
                cursor.execute("UPDATE reminders SET category = 'عمومی' WHERE category IS NULL OR category = ''")
                conn.commit()
            except Exception:
                pass
            cursor.execute("SELECT id, date, time FROM reminders WHERE original_date IS NULL")
            old_records = cursor.fetchall()
            for record in old_records:
                rid, date_val, time_val = record
                cursor.execute(
                    "UPDATE reminders SET original_date = ?, original_time = ? WHERE id = ?",
                    (date_val, time_val, rid)
                )
            conn.commit()
            log(f"[OK] {len(old_records)} records updated with original_date/original_time")
            conn.close()
        except sqlite3.Error as e:
            log(f"[ERROR] Database upgrade error: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            conn.close()

    def _cleanup_old_backups(self):
        """پاک‌سازی بکاپ‌های قدیمی دیتابیس"""
        removed = 0
        try:
            backups = []
            for f in os.listdir(self.data_dir):
                if f.startswith('reminders_backup_') and f.endswith('.db'):
                    full = os.path.join(self.data_dir, f)
                    try:
                        mtime = os.path.getmtime(full)
                        backups.append((mtime, full))
                    except OSError:
                        pass
            backups.sort(key=lambda x: x[0], reverse=True)
            for _, path in backups[self.MAX_BACKUPS:]:
                try:
                    os.remove(path)
                    removed += 1
                    log(f"[OK] Old backup removed: {path}")
                except OSError as e:
                    log(f"[WARN] Could not remove backup {path}: {e}")
        except Exception as e:
            log(f"[WARN] Backup cleanup error: {e}")
        return removed

    def cleanup_extra_files(self, max_age_days=14, max_exports=5):
        """
        پاک‌سازی خودکار فایل‌های اضافی:
        - بکاپ‌های قدیمی دیتابیس (بیش از MAX_BACKUPS)
        - فایل‌های خروجی JSON قدیمی (yadavar_export_*)
        برمی‌گرداند تعداد فایل‌های حذف‌شده
        """
        removed = 0
        try:
            removed += self._cleanup_old_backups() or 0
        except Exception:
            pass

        try:
            now = datetime.now().timestamp()
            max_age_sec = max_age_days * 24 * 3600
            exports = []
            for f in os.listdir(self.data_dir):
                if f.startswith('yadavar_export_') and f.endswith('.json'):
                    full = os.path.join(self.data_dir, f)
                    try:
                        mtime = os.path.getmtime(full)
                        # حذف فایل‌های خیلی قدیمی
                        if now - mtime > max_age_sec:
                            os.remove(full)
                            removed += 1
                            log(f"[OK] Old export removed: {full}")
                        else:
                            exports.append((mtime, full))
                    except OSError as e:
                        log(f"[WARN] Could not process export {full}: {e}")
            # نگه داشتن فقط آخرین max_exports
            exports.sort(key=lambda x: x[0], reverse=True)
            for _, path in exports[max_exports:]:
                try:
                    os.remove(path)
                    removed += 1
                    log(f"[OK] Extra export removed: {path}")
                except OSError as e:
                    log(f"[WARN] Could not remove export {path}: {e}")
        except Exception as e:
            log(f"[WARN] Export cleanup error: {e}")
        return removed

    def backup(self, force=False):
        if not force:
            self._backup_counter += 1
            if self._backup_counter < 10:
                return None
        self._backup_counter = 0
        try:
            if not os.path.exists(self.db_name):
                return None
            backup_name = os.path.join(
                self.data_dir,
                f"reminders_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            shutil.copy2(self.db_name, backup_name)
            log(f"[OK] Backup: {backup_name}")
            self._cleanup_old_backups()
            return backup_name
        except Exception as e:
            log(f"[WARN] Backup error: {e}")
            return None

    def add_reminder(self, title, description, date, time, notify_before=15,
                     repeat_type='none', repeat_end_date=None, category='عمومی'):
        query = '''
            INSERT INTO reminders
            (title, description, date, time, notify_before, repeat_type, repeat_end_date,
             original_date, original_time, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (title, description, date, time, notify_before, repeat_type,
                  repeat_end_date, date, time, category or 'عمومی')
        result = self._execute_query(query, params)
        if result is not None:
            self.backup()
            return True
        return False

    def update_reminder(self, reminder_id, title, description, date, time,
                        repeat_type='none', repeat_end_date=None, notify_before=15,
                        category='عمومی'):
        query = '''
            UPDATE reminders
            SET title = ?, description = ?, date = ?, time = ?,
                repeat_type = ?, repeat_end_date = ?,
                original_date = ?, original_time = ?, notify_before = ?,
                category = ?
            WHERE id = ?
        '''
        params = (title, description, date, time, repeat_type, repeat_end_date,
                  date, time, notify_before, category or 'عمومی', reminder_id)
        result = self._execute_query(query, params)
        if result is not None:
            self.backup()
            return True
        return False

    def update_reminder_date_time(self, reminder_id, new_date, new_time):
        query = 'UPDATE reminders SET date = ?, time = ? WHERE id = ?'
        params = (new_date, new_time, reminder_id)
        result = self._execute_query(query, params)
        if result is not None:
            self.backup()
            return True
        return False

    def get_reminders(self, show_completed=False):
        try:
            if show_completed:
                query = 'SELECT * FROM reminders ORDER BY date, time'
            else:
                query = 'SELECT * FROM reminders WHERE is_completed = 0 ORDER BY date, time'
            result = self._execute_query(query, fetch=True)
            return result if result is not None else []
        except Exception as e:
            log(f"[ERROR] get_reminders error: {e}")
            return []

    def search_reminders(self, query_text, show_completed=False):
        try:
            search_pattern = f'%{query_text}%'
            sql_query = '''
                SELECT * FROM reminders
                WHERE (title LIKE ? OR description LIKE ?)
            '''
            params = [search_pattern, search_pattern]
            if not show_completed:
                sql_query += ' AND is_completed = 0'
            sql_query += ' ORDER BY date, time'
            result = self._execute_query(sql_query, params, fetch=True)
            return result if result is not None else []
        except Exception as e:
            log(f"[ERROR] search_reminders error: {e}")
            return []

    def count_active(self):
        try:
            result = self._execute_query(
                'SELECT COUNT(*) FROM reminders WHERE is_completed = 0',
                fetch=True
            )
            return result[0][0] if result else 0
        except Exception:
            return 0

    def delete_reminder(self, reminder_id):
        query = 'DELETE FROM reminders WHERE id = ?'
        result = self._execute_query(query, (reminder_id,))
        if result is not None:
            self.backup()
            return True
        return False

    def toggle_completed(self, reminder_id):
        query = '''
            UPDATE reminders
            SET is_completed = CASE WHEN is_completed = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        '''
        result = self._execute_query(query, (reminder_id,))
        if result is not None:
            self.backup()
            return True
        return False

    def get_reminder_by_id(self, reminder_id):
        try:
            query = 'SELECT * FROM reminders WHERE id = ?'
            conn = self._get_connection()
            if not conn:
                return None
            cursor = conn.cursor()
            cursor.execute(query, (reminder_id,))
            reminder = cursor.fetchone()
            conn.close()
            return reminder
        except sqlite3.Error as e:
            log(f"[ERROR] get_reminder_by_id error: {e}")
            return None

    def export_data(self):
        try:
            reminders = self.get_reminders(show_completed=True)
            data = {
                'version': '5.0',
                'export_date': datetime.now().isoformat(),
                'reminders': []
            }
            for r in reminders:
                data['reminders'].append({
                    'id': r[0],
                    'title': r[1],
                    'description': r[2],
                    'date': r[3],
                    'time': r[4],
                    'is_completed': r[5],
                    'created_at': r[6],
                    'notify_before': r[7],
                    'repeat_type': r[8],
                    'repeat_end_date': r[9],
                    'original_date': r[10],
                    'original_time': r[11],
                    'category': r[12] if len(r) > 12 else 'عمومی',
                })
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            log(f"[ERROR] Export error: {e}")
            return None

    def import_data(self, json_data):
        try:
            data = json.loads(json_data)
            reminders = data.get('reminders', [])
            if not reminders:
                return False

            conn = self._get_connection()
            if not conn:
                return False

            cursor = conn.cursor()
            imported = 0
            for r in reminders:
                try:
                    cursor.execute('''
                        INSERT INTO reminders
                        (title, description, date, time, is_completed, created_at,
                         notify_before, repeat_type, repeat_end_date, original_date, original_time, category)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r.get('title', ''),
                        r.get('description', ''),
                        r.get('date', ''),
                        r.get('time', ''),
                        r.get('is_completed', 0),
                        r.get('created_at', datetime.now().isoformat()),
                        r.get('notify_before', 15),
                        r.get('repeat_type', 'none'),
                        r.get('repeat_end_date'),
                        r.get('original_date', r.get('date', '')),
                        r.get('original_time', r.get('time', '')),
                        r.get('category', 'عمومی'),
                    ))
                    imported += 1
                except Exception as e:
                    log(f"[ERROR] Import item error: {e}")
                    continue

            conn.commit()
            conn.close()
            self.backup(force=True)
            log(f"[OK] Imported {imported} reminders")
            return imported > 0
        except Exception as e:
            log(f"[ERROR] Import error: {e}")
            return False


# ==================================================
# ویجت‌های سفارشی
# ==================================================
class ColoredBox(BoxLayout):
    def __init__(self, bg_color=(0.95, 0.95, 0.95, 1), radius=8, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(self.radius)]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class PersianLabel(Label):
    def __init__(self, text='', **kwargs):
        # پیش‌فرض ExtraBold؛ برای متن کم‌اهمیت thin=True بگذارید
        use_thin = kwargs.pop('thin', False)
        kwargs.pop('bold', None)  # مصرف شود تا به Label نرسد اشتباه
        if use_thin:
            kwargs['font_name'] = 'PersianFont'  # Thin
        else:
            kwargs.setdefault('font_name', 'PersianFontBold')  # ExtraBold
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'middle')
        if text:
            kwargs['text'] = reshape_persian(text)
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)

    def set_text(self, text):
        self.text = reshape_persian(text)


class PersianButton(Button):
    def __init__(self, text='', **kwargs):
        use_thin = kwargs.pop('thin', False)
        kwargs.pop('bold', None)
        if use_thin:
            kwargs['font_name'] = 'PersianFont'
        else:
            kwargs.setdefault('font_name', 'PersianFontBold')
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'middle')
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        if text:
            kwargs['text'] = reshape_persian(text)
        super().__init__(**kwargs)

    def set_text(self, text):
        self.text = reshape_persian(text)


class PersianTextInput(TextInput):
    def __init__(self, **kwargs):
        hint = kwargs.pop('hint_text', '')
        password = kwargs.pop('password', False)
        kwargs.setdefault('font_name', 'PersianFont')
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('padding', [dp(12), dp(10), dp(12), dp(10)])
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_active', '')
        kwargs.setdefault('background_color', (1, 1, 1, 1))
        kwargs.setdefault('foreground_color', (0.1, 0.1, 0.1, 1))
        kwargs.setdefault('cursor_color', (0.2, 0.5, 0.3, 1))
        kwargs.setdefault('hint_text_color', (0.55, 0.55, 0.6, 1))
        kwargs.setdefault('multiline', False)
        super().__init__(**kwargs)

        if password:
            self.password = True

        if hint:
            self.hint_text = reshape_persian(hint)

        self._logical = ''
        self._busy = False

    @property
    def value(self):
        return (self._logical or '').strip()

    @value.setter
    def value(self, new_value):
        self._logical = new_value or ''
        self._busy = True
        try:
            self.text = reshape_persian(self._logical) if self._logical else ''
        finally:
            self._busy = False

    def insert_text(self, substring, from_undo=False):
        if self._busy or not substring:
            return
        self._logical += substring
        self._refresh_display()

    def do_backspace(self, from_undo=False, mode='bkspc'):
        if self._busy:
            return
        if self._logical:
            self._logical = self._logical[:-1]
        self._refresh_display()

    def _refresh_display(self):
        self._busy = True
        try:
            visual = reshape_persian(self._logical) if self._logical else ''
            self.text = visual
            self.cursor = (len(self.text), 0)
        finally:
            self._busy = False

    def apply_theme(self, theme):
        self.background_color = theme['input_bg']
        self.foreground_color = theme['input_fg']
        self.hint_text_color = theme['search_hint']


# ==================================================
# تقویم گرافیکی
# ==================================================
class JalaliCalendar(BoxLayout):
    """تقویم شمسی با ظاهر مدرن شبیه تصویر (دایره‌ای، سبز)"""

    MONTH_NAMES = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                   'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']

    def __init__(self, selected_date=None, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(6)
        self.padding = dp(10)
        self.selected_date = selected_date
        self.callback = callback
        self.current_year, self.current_month = self._get_current_date()
        if selected_date:
            try:
                parts = selected_date.replace('-', '/').split('/')
                if len(parts) == 3:
                    self.current_year = int(parts[0])
                    self.current_month = int(parts[1])
            except Exception:
                pass
        # پس‌زمینه سبز
        with self.canvas.before:
            Color(0.05, 0.45, 0.40, 1)  # سبز تیره
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.build_calendar()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _get_current_date(self):
        try:
            now = jdatetime.datetime.now()
            return now.year, now.month
        except Exception:
            ny, nm, _, _, _ = now_jalali_tuple()
            return ny, nm

    def _get_days_in_month(self, year, month):
        return days_in_jalali_month(year, month)

    def _get_first_day_of_month(self, year, month):
        try:
            jd = jdatetime.date(year, month, 1)
            return jd.weekday()
        except Exception:
            return 0

    def build_calendar(self):
        self.clear_widgets()

        # ---- هدر: نام ماه + سال ----
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(4),
        )

        prev_btn = PersianButton(
            text='‹',
            size_hint_x=None,
            width=dp(40),
            background_color=(0, 0, 0, 0),
            color=(0.85, 0.95, 0.90, 1),
            font_size='26sp',
            bold=True,
        )
        prev_btn.bind(on_press=self.prev_month)

        month_name = self.MONTH_NAMES[self.current_month - 1] if 1 <= self.current_month <= 12 else str(self.current_month)
        self.month_year_label = PersianLabel(
            text=f'{month_name}  {self.current_year}',
            font_size='20sp',
            color=(1, 1, 1, 1),
            bold=True,
            size_hint_x=1,
        )

        next_btn = PersianButton(
            text='›',
            size_hint_x=None,
            width=dp(40),
            background_color=(0, 0, 0, 0),
            color=(0.85, 0.95, 0.90, 1),
            font_size='26sp',
            bold=True,
        )
        next_btn.bind(on_press=self.next_month)

        header.add_widget(prev_btn)
        header.add_widget(self.month_year_label)
        header.add_widget(next_btn)
        self.add_widget(header)

        # ---- ردیف نام روزها ----
        day_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(28),
            spacing=dp(2),
        )
        day_names = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
        for name in day_names:
            lbl = PersianLabel(
                text=name,
                font_size='14sp',
                color=(0.75, 0.90, 0.85, 1),
                bold=True,
                size_hint_x=1/7,
            )
            day_row.add_widget(lbl)
        self.add_widget(day_row)

        # ---- شبکه روزها ----
        days_grid = GridLayout(
            cols=7,
            spacing=dp(4),
            size_hint_y=None,
            height=dp(44 * 6),
            padding=[dp(2), 0],
        )

        first_day = self._get_first_day_of_month(self.current_year, self.current_month)
        days_in_month = self._get_days_in_month(self.current_year, self.current_month)

        for _ in range(first_day):
            days_grid.add_widget(Label(text='', size_hint_y=None, height=dp(42)))

        today = get_default_date()
        today_parts = today.split('/')
        today_tuple = (int(today_parts[0]), int(today_parts[1]), int(today_parts[2]))

        selected_tuple = None
        if self.selected_date:
            try:
                sp = self.selected_date.replace('-', '/').split('/')
                if len(sp) == 3:
                    selected_tuple = (int(sp[0]), int(sp[1]), int(sp[2]))
            except Exception:
                pass

        for day in range(1, days_in_month + 1):
            is_today = (self.current_year, self.current_month, day) == today_tuple
            is_selected = selected_tuple == (self.current_year, self.current_month, day)

            # رنگ‌ها مطابق تصویر
            if is_selected:
                bg = get_color_from_hex('#FF7043')  # نارنجی انتخاب‌شده
                fg = (1, 1, 1, 1)
            elif is_today:
                bg = get_color_from_hex('#26A69A')  # سبز روشن امروز
                fg = (1, 1, 1, 1)
            else:
                bg = (0.08, 0.50, 0.45, 0.6)  # دایره نیمه‌شفاف
                fg = (1, 1, 1, 1)

            btn = PersianButton(
                text=str(day),
                font_size='16sp',
                background_color=bg,
                color=fg,
                size_hint_y=None,
                height=dp(42),
                bold=is_today or is_selected,
            )
            # ظاهر گردتر
            btn.background_normal = ''
            btn.background_down = ''
            btn.bind(on_press=lambda inst, d=day: self.select_date(d))
            days_grid.add_widget(btn)

        self.add_widget(days_grid)

        # ---- انتخاب سریع سال ----
        year_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        year_prev = PersianButton(
            text='سال قبل',
            size_hint_x=0.4,
            background_color=get_color_from_hex('#00897B'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        year_prev.bind(on_press=self.prev_year)
        year_next = PersianButton(
            text='سال بعد',
            size_hint_x=0.4,
            background_color=get_color_from_hex('#00897B'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        year_next.bind(on_press=self.next_year)
        year_row.add_widget(Widget())
        year_row.add_widget(year_prev)
        year_row.add_widget(year_next)
        year_row.add_widget(Widget())
        self.add_widget(year_row)

    def select_date(self, day):
        date_str = f"{self.current_year:04d}/{self.current_month:02d}/{day:02d}"
        self.selected_date = date_str
        self.build_calendar()  # بازسازی برای نمایش انتخاب
        if self.callback:
            self.callback(date_str)

    def prev_month(self, instance):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.build_calendar()

    def next_month(self, instance):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.build_calendar()

    def prev_year(self, instance):
        self.current_year -= 1
        self.build_calendar()

    def next_year(self, instance):
        self.current_year += 1
        self.build_calendar()


# ==================================================
# ویجت ساعت
# ==================================================
class TimePickerWidget(BoxLayout):
    """انتخاب ساعت به سبک اسکرول‌چرخ (ساعت : دقیقه)"""

    def __init__(self, initial_time=None, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.callback = callback

        if initial_time:
            parts = str(initial_time).split(':')
            self.hour = int(parts[0]) % 24 if parts else 0
            self.minute = int(parts[1]) % 60 if len(parts) > 1 else 0
        else:
            now = datetime.now()
            self.hour = now.hour
            self.minute = now.minute

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._upd_bg, size=self._upd_bg)
        self.build_time_picker()

    def _upd_bg(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def build_time_picker(self):
        self.clear_widgets()

        # عنوان
        self.add_widget(PersianLabel(
            text='انتخاب ساعت',
            font_size='18sp',
            color=(0.1, 0.1, 0.12, 1),
            size_hint_y=None,
            height=dp(36),
        ))

        # سه ستون: ساعت : دقیقه  (با اعداد اطراف کم‌رنگ)
        wheels = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(200),
            spacing=dp(4),
            padding=[dp(8), 0],
        )

        # --- ستون ساعت ---
        hour_col = BoxLayout(orientation='vertical', size_hint_x=0.42, spacing=dp(2))
        self._hour_btns = {}
        for offset in range(-3, 4):
            h = (self.hour + offset) % 24
            is_center = (offset == 0)
            btn = PersianButton(
                text=f'{h:02d}',
                size_hint_y=None,
                height=dp(28) if not is_center else dp(40),
                background_color=(0, 0, 0, 0),
                color=(0.15, 0.15, 0.15, 1) if is_center else (0.65, 0.65, 0.68, 1),
                font_size='28sp' if is_center else '16sp',
            )
            if is_center:
                btn.font_name = 'PersianFontBold'
            btn.bind(on_press=lambda inst, o=offset: self._nudge_hour(o) if o != 0 else None)
            hour_col.add_widget(btn)
            self._hour_btns[offset] = btn

        # جداکننده
        sep = PersianLabel(
            text=':',
            font_size='32sp',
            color=(0.15, 0.15, 0.15, 1),
            size_hint_x=0.12,
        )

        # --- ستون دقیقه ---
        min_col = BoxLayout(orientation='vertical', size_hint_x=0.42, spacing=dp(2))
        self._min_btns = {}
        for offset in range(-3, 4):
            m = (self.minute + offset) % 60
            is_center = (offset == 0)
            btn = PersianButton(
                text=f'{m:02d}',
                size_hint_y=None,
                height=dp(28) if not is_center else dp(40),
                background_color=(0, 0, 0, 0),
                color=(0.15, 0.15, 0.15, 1) if is_center else (0.65, 0.65, 0.68, 1),
                font_size='28sp' if is_center else '16sp',
            )
            if is_center:
                btn.font_name = 'PersianFontBold'
            btn.bind(on_press=lambda inst, o=offset: self._nudge_minute(o) if o != 0 else None)
            min_col.add_widget(btn)
            self._min_btns[offset] = btn

        wheels.add_widget(hour_col)
        wheels.add_widget(sep)
        wheels.add_widget(min_col)
        self.add_widget(wheels)

        # دکمه‌های تنظیم سریع ±۱
        adj = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36), spacing=dp(8))
        for label, hdelta, mdelta in [('ساعت −', -1, 0), ('ساعت +', 1, 0), ('دقیقه −', 0, -1), ('دقیقه +', 0, 1)]:
            b = PersianButton(
                text=label,
                background_color=get_color_from_hex('#ECEFF1'),
                color=(0.2, 0.2, 0.25, 1),
                font_size='12sp',
                thin=True,
            )
            b.bind(on_press=lambda inst, hd=hdelta, md=mdelta: self._adjust(hd, md))
            adj.add_widget(b)
        self.add_widget(adj)

        # انتخاب اکنون
        now_btn = PersianButton(
            text='●  انتخاب اکنون',
            size_hint_y=None,
            height=dp(36),
            background_color=(0, 0, 0, 0),
            color=(0.15, 0.15, 0.18, 1),
            font_size='14sp',
        )
        now_btn.bind(on_press=self._set_now)
        self.add_widget(now_btn)

        # تأیید سبز
        ok_btn = PersianButton(
            text='تأیید',
            size_hint_y=None,
            height=dp(48),
            background_color=get_color_from_hex('#43A047'),
            color=(1, 1, 1, 1),
            font_size='16sp',
        )
        ok_btn.bind(on_press=self.on_ok)
        self.add_widget(ok_btn)

        # لغو
        cancel_btn = PersianButton(
            text='لغو',
            size_hint_y=None,
            height=dp(36),
            background_color=(0, 0, 0, 0),
            color=(0.45, 0.45, 0.5, 1),
            font_size='13sp',
            thin=True,
        )
        cancel_btn.bind(on_press=self.on_cancel)
        self.add_widget(cancel_btn)

    def _refresh_wheels(self):
        for offset, btn in self._hour_btns.items():
            h = (self.hour + offset) % 24
            is_center = (offset == 0)
            btn.set_text(f'{h:02d}')
            btn.color = (0.15, 0.15, 0.15, 1) if is_center else (0.65, 0.65, 0.68, 1)
            btn.font_size = '28sp' if is_center else '16sp'
            btn.font_name = 'PersianFontBold' if is_center else 'PersianFont'
            btn.height = dp(40) if is_center else dp(28)
        for offset, btn in self._min_btns.items():
            m = (self.minute + offset) % 60
            is_center = (offset == 0)
            btn.set_text(f'{m:02d}')
            btn.color = (0.15, 0.15, 0.15, 1) if is_center else (0.65, 0.65, 0.68, 1)
            btn.font_size = '28sp' if is_center else '16sp'
            btn.font_name = 'PersianFontBold' if is_center else 'PersianFont'
            btn.height = dp(40) if is_center else dp(28)

    def _nudge_hour(self, offset):
        self.hour = (self.hour + offset) % 24
        self._refresh_wheels()

    def _nudge_minute(self, offset):
        self.minute = (self.minute + offset) % 60
        self._refresh_wheels()

    def _adjust(self, hdelta, mdelta):
        self.hour = (self.hour + hdelta) % 24
        self.minute = (self.minute + mdelta) % 60
        self._refresh_wheels()

    def _set_now(self, *_):
        now = datetime.now()
        self.hour = now.hour
        self.minute = now.minute
        self._refresh_wheels()

    def on_ok(self, instance):
        time_str = f"{self.hour:02d}:{self.minute:02d}"
        if self.callback:
            self.callback(time_str)

    def on_cancel(self, instance):
        if self.callback:
            self.callback(None)


class LicenseVerificationPopup:
    def __init__(self, app, callback=None):
        self.app = app
        self.callback = callback
        self.license_manager = LicenseManager(app.data_dir)
        
        if self.license_manager.is_verified():
            if callback:
                callback(True)
            return
            
        if not self.license_manager.is_expired() or self.license_manager.is_in_grace_period():
            self.show_verification()
        else:
            self.show_expired()

    def show_verification(self):
        box = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        
        icon = PersianLabel(
            text='🔐',
            font_size='32sp',
            size_hint_y=None,
            height=dp(50),
        )
        box.add_widget(icon)
        
        status_msg = self.license_manager.get_status_message(self.app.language)
        status_lbl = PersianLabel(
            text=status_msg,
            font_size='15sp',
            color=self.license_manager.get_status_color(),
            size_hint_y=None,
            height=dp(50),
        )
        box.add_widget(status_lbl)
        
        code_input = PersianTextInput(
            hint_text=self.app._('enter_code'),
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size='15sp',
            password=True,
        )
        code_input.apply_theme(self.app.theme)
        box.add_widget(code_input)
        
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
        )
        
        if not self.license_manager.is_expired():
            skip_btn = PersianButton(
                text=self.app._('later'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
            )
            skip_btn.bind(on_press=self.skip_verification)
            btn_row.add_widget(skip_btn)
        
        verify_btn = PersianButton(
            text=self.app._('verify'),
            background_color=get_color_from_hex('#2E7D32'),
            color=(1, 1, 1, 1),
        )
        verify_btn.bind(on_press=lambda inst: self.verify_code(code_input.value))
        btn_row.add_widget(verify_btn)
        
        box.add_widget(btn_row)
        
        self.error_lbl = PersianLabel(
            text='',
            font_size='13sp',
            color=(1, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(30),
        )
        box.add_widget(self.error_lbl)
        
        contact_btn = PersianButton(
            text=self.app._('contact'),
            background_color=get_color_from_hex('#5C6BC0'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(36),
            font_size='12sp',
        )
        contact_btn.bind(on_press=lambda inst: self.show_contact_info())
        box.add_widget(contact_btn)
        
        self.popup = Popup(
            title=self.app._('license_title'),
            content=box,
            size_hint=(0.85, 0.6),
            auto_dismiss=False,
            title_font='PersianFont',
            title_size='18sp',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=self.app.theme['popup_bg'],
            separator_color=get_color_from_hex('#FF8F00'),
            separator_height=dp(3),
        )
        self.popup.open()

    def verify_code(self, code):
        if not code:
            self.error_lbl.set_text(self.app._('code_required'))
            return
        
        if self.license_manager.verify_code(code):
            self.popup.dismiss()
            if self.callback:
                self.callback(True)
        else:
            self.error_lbl.set_text(self.app._('invalid_code'))

    def skip_verification(self, instance):
        if self.license_manager.get_days_remaining() > 0:
            self.popup.dismiss()
            if self.callback:
                self.callback(True)
        else:
            self.error_lbl.set_text(self.app._('expired'))

    def show_contact_info(self):
        info = APP_INFO
        lines = [
            f"📧 {info['email']}",
            f"💬 {info.get('bale', '@your_id')}",
            '',
            self.app._('contact_info'),
        ]
        text = '\n'.join(lines)
        
        box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
        box.add_widget(PersianLabel(
            text=text,
            font_size='15sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=1,
        ))
        close_btn = PersianButton(
            text=self.app._('close'),
            background_color=get_color_from_hex('#5C6BC0'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(42),
            font_size='14sp',
        )
        box.add_widget(close_btn)
        
        popup = Popup(
            title=self.app._('contact'),
            content=box,
            size_hint=(0.85, 0.4),
            auto_dismiss=True,
            title_font='PersianFont',
            title_size='16sp',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=self.app.theme['popup_bg'],
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_expired(self):
        box = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        
        icon = PersianLabel(
            text='⛔',
            font_size='40sp',
            size_hint_y=None,
            height=dp(60),
        )
        box.add_widget(icon)
        
        msg = PersianLabel(
            text=self.app._('expired'),
            font_size='16sp',
            color=(1, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(60),
        )
        box.add_widget(msg)
        
        contact_btn = PersianButton(
            text=self.app._('contact'),
            background_color=get_color_from_hex('#5C6BC0'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(44),
            font_size='14sp',
        )
        contact_btn.bind(on_press=lambda inst: self.show_contact_info())
        box.add_widget(contact_btn)
        
        exit_btn = PersianButton(
            text=self.app._('exit'),
            background_color=get_color_from_hex('#C62828'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(44),
            font_size='14sp',
        )
        exit_btn.bind(on_press=lambda inst: App.get_running_app().stop())
        box.add_widget(exit_btn)
        
        popup = Popup(
            title=self.app._('license_title'),
            content=box,
            size_hint=(0.85, 0.5),
            auto_dismiss=False,
            title_font='PersianFont',
            title_size='18sp',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=self.app.theme['popup_bg'],
            separator_color=get_color_from_hex('#C62828'),
            separator_height=dp(3),
        )
        popup.open()


# ==================================================
# توابع تاریخ شمسی
# ==================================================
def now_jalali_tuple():
    now = datetime.now()
    try:
        jalali = jdatetime.datetime.fromgregorian(datetime=now)
        return (jalali.year, jalali.month, jalali.day, now.hour, now.minute)
    except Exception:
        return (now.year - 621, now.month, now.day, now.hour, now.minute)


def get_default_date():
    now = datetime.now()
    try:
        jalali = jdatetime.datetime.fromgregorian(datetime=now)
        return f"{jalali.year:04d}/{jalali.month:02d}/{jalali.day:02d}"
    except Exception:
        return f"{now.year-621:04d}/{now.month:02d}/{now.day:02d}"


def get_default_time():
    now = datetime.now()
    return f"{now.hour:02d}:{now.minute:02d}"


def jalali_to_gregorian(year, month, day):
    try:
        jd = jdatetime.date(year, month, day)
        return jd.togregorian()
    except Exception:
        return None


def days_in_jalali_month(year, month):
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    else:
        try:
            jd = jdatetime.date(year, month, 1)
            next_jd = jdatetime.date(year, month + 1, 1) if month < 12 else jdatetime.date(year + 1, 1, 1)
            return (next_jd - jd).days
        except Exception:
            return 29


def date_status(date_str):
    try:
        parts = date_str.replace('-', '/').split('/')
        if len(parts) != 3:
            return 'unknown'
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        ny, nm, nd, _, _ = now_jalali_tuple()
        if (y, m, d) < (ny, nm, nd):
            return 'overdue'
        if (y, m, d) == (ny, nm, nd):
            return 'today'
        return 'future'
    except Exception:
        return 'unknown'


def get_jalali_date_offset(days):
    try:
        target = datetime.now() + timedelta(days=days)
        jalali = jdatetime.datetime.fromgregorian(datetime=target)
        return f"{jalali.year:04d}/{jalali.month:02d}/{jalali.day:02d}"
    except Exception:
        ny, nm, nd, _, _ = now_jalali_tuple()
        return f"{ny:04d}/{nm:02d}/{nd:02d}"


def is_date_in_range(date_str, start_str, end_str):
    try:
        def parse(s):
            p = s.replace('-', '/').split('/')
            return (int(p[0]), int(p[1]), int(p[2]))
        d = parse(date_str)
        return parse(start_str) <= d <= parse(end_str)
    except Exception:
        return False


# ==================================================
# مدیریت دسته‌بندی‌ها
# ==================================================
DEFAULT_CATEGORIES = ['همه', 'کار', 'درس', 'خرید', 'تفریح', 'اقساط', 'عمومی']


class CategoriesManager:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir
        self.filename = os.path.join(data_dir, 'categories.json')
        self.categories = self.load()

    def load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cats = data.get('categories', [])
                    # همیشه «همه» اول باشد
                    if 'همه' not in cats:
                        cats.insert(0, 'همه')
                    elif cats[0] != 'همه':
                        cats = ['همه'] + [c for c in cats if c != 'همه']
                    return cats
        except Exception as e:
            log(f"[WARN] Categories load error: {e}")
        return list(DEFAULT_CATEGORIES)

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({'categories': self.categories}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log(f"[WARN] Categories save error: {e}")
            return False

    def get_all(self):
        return list(self.categories)

    def get_selectable(self):
        """دسته‌ها بدون «همه» برای فرم افزودن/ویرایش"""
        return [c for c in self.categories if c != 'همه']

    def add(self, name):
        name = (name or '').strip()
        if not name or name in self.categories:
            return False
        self.categories.append(name)
        self.save()
        return True

    def remove(self, name):
        if name in ('همه', 'عمومی') or name not in self.categories:
            return False
        self.categories = [c for c in self.categories if c != name]
        self.save()
        return True


# ==================================================
# مدیریت تنظیمات - اصلاح شده با data_dir
# ==================================================
class SettingsManager:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir
        self.filename = os.path.join(data_dir, 'settings.json')
        self.defaults = {
            'check_interval': 60,
            'theme': 'light',
            'last_snooze_minutes': 5,
            'language': 'fa',
        }
        self.settings = self.load()

    def load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in self.defaults.items():
                        if key not in data:
                            data[key] = value
                    return data
        except Exception as e:
            log(f"[WARN] Settings load error: {e}")
        return self.defaults.copy()

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log(f"[WARN] Settings save error: {e}")
            return False

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()


# ==================================================
# اپلیکیشن اصلی - اصلاح شده برای اندروید و ویندوز
# ==================================================
class ReminderApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # دریافت مسیر ذخیره‌سازی داده‌ها
        if platform == 'android' and _USER_DATA_DIR:
            self.data_dir = _USER_DATA_DIR
        else:
            self.data_dir = self.user_data_dir
            
        # اطمینان از وجود پوشه
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            log(f"[OK] Data directory: {self.data_dir}")
        except Exception as e:
            log(f"[WARN] Could not create data dir ({e}), using local dir")
            self.data_dir = os.path.dirname(os.path.abspath(__file__))
            try:
                os.makedirs(self.data_dir, exist_ok=True)
            except Exception:
                pass
        
        self.db = Database('reminders.db', self.data_dir)
        self.settings = SettingsManager(self.data_dir)
        self.categories = CategoriesManager(self.data_dir)
        self.current_filter = 'all'
        self.current_category = 'همه'
        self.search_query = ''
        self.title = 'Yadavar'
        self._notified_ids = set()
        self._alert_open = False
        self._processing_repeats = False
        self._alerting_ids = set()
        self._active_alerts = {}
        self.check_interval = self.settings.get('check_interval')
        self.theme_name = self.settings.get('theme') or 'light'
        self.theme = THEMES.get(self.theme_name, THEMES['light'])
        self.language = self.settings.get('language') or 'fa'
        self._license_checked = False
        self.category_buttons = {}

    def _(self, key):
        return _(key, self.language)

    def build(self):
        if platform not in ('android', 'ios'):
            Window.size = (420, 720)
            Window.minimum_width = 360
            Window.minimum_height = 500
        
        # تنظیمات ویژه اندروید
        if platform == 'android':
            self.request_android_permissions()
            try:
                from kivy.config import Config
                Config.set('kivy', 'keyboard_mode', 'system')
            except Exception:
                pass
            try:
                from android import mActivity
            except Exception:
                pass
        
        Window.clearcolor = get_color_from_hex(self.theme['window_bg'])

        Clock.schedule_interval(self.check_due_reminders, self.check_interval)
        Clock.schedule_once(self.check_due_reminders, 1)
        Clock.schedule_interval(self.process_repeat_reminders, 30)
        Clock.schedule_once(self.process_repeat_reminders, 5)

        self.root_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(6),
        )
        self.title_label = PersianLabel(
            text=self._('my_reminders'),
            font_size='17sp',
            color=self.theme['header_title'],
            bold=True,
            size_hint_x=0.48,
        )
        header.add_widget(self.title_label)

        add_btn = PersianButton(
            text=self._('add'),
            size_hint_x=0.26,
            background_color=get_color_from_hex('#2E7D32'),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True,
        )
        add_btn.bind(on_press=self.show_add_reminder)
        header.add_widget(add_btn)

        settings_btn = PersianButton(
            text=self._('settings'),
            size_hint_x=0.26,
            background_color=get_color_from_hex('#455A64'),
            color=(1, 1, 1, 1),
            font_size='12sp',
        )
        settings_btn.bind(on_press=self.show_settings)
        header.add_widget(settings_btn)

        # دکمه «پاک» از هدر حذف شد (طبق درخواست کاربر)

        self.root_layout.add_widget(header)

        search_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6),
        )

        self.search_input = PersianTextInput(
            hint_text=self._('search_hint'),
            multiline=False,
            size_hint_x=1,
            font_size='15sp',
        )
        self.search_input.apply_theme(self.theme)
        self.search_input.bind(text=self.on_search_text)
        search_box.add_widget(self.search_input)
        self.root_layout.add_widget(search_box)

        self.filter_buttons = {}
        self.filter_colors = {
            'all': '#1565C0',
            'today': '#E65100',
            'tomorrow': '#F9A825',
            'week': '#00838F',
            'active': '#2E7D32',
            'completed': '#6A1B9A',
        }
        self.filter_active_colors = {
            'all': '#0D47A1',
            'today': '#BF360C',
            'tomorrow': '#F57F17',
            'week': '#006064',
            'active': '#1B5E20',
            'completed': '#4A148C',
        }

        filter_row1 = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(34),
            spacing=dp(5),
        )
        filter_row2 = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(34),
            spacing=dp(5),
        )

        filters_row1 = [
            (self._('all'), 'all'),
            (self._('today'), 'today'),
            (self._('tomorrow'), 'tomorrow'),
        ]
        filters_row2 = [
            (self._('this_week'), 'week'),
            (self._('active'), 'active'),
            (self._('completed'), 'completed'),
        ]

        for label, ftype in filters_row1:
            btn = PersianButton(
                text=label,
                background_color=get_color_from_hex(self.filter_colors[ftype]),
                color=(1, 1, 1, 1),
                font_size='13sp',
            )
            btn.bind(on_press=lambda inst, ft=ftype: self.filter_reminders(ft))
            self.filter_buttons[ftype] = btn
            filter_row1.add_widget(btn)

        for label, ftype in filters_row2:
            btn = PersianButton(
                text=label,
                background_color=get_color_from_hex(self.filter_colors[ftype]),
                color=(1, 1, 1, 1),
                font_size='13sp',
            )
            btn.bind(on_press=lambda inst, ft=ftype: self.filter_reminders(ft))
            self.filter_buttons[ftype] = btn
            filter_row2.add_widget(btn)

        self.update_filter_buttons('all')
        self.root_layout.add_widget(filter_row1)
        self.root_layout.add_widget(filter_row2)

        # ردیف دسته‌بندی‌ها (مشابه تصویر)
        cat_header = PersianLabel(
            text='دسته‌بندی‌ها',
            font_size='13sp',
            color=self.theme['header_title'],
            size_hint_y=None,
            height=dp(24),
            bold=True,
            halign='right',
        )
        self.root_layout.add_widget(cat_header)

        self.category_scroll = ScrollView(
            do_scroll_y=False,
            do_scroll_x=True,
            size_hint_y=None,
            height=dp(42),
            bar_width=dp(3),
        )
        self.category_row = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(10),
            padding=[dp(4), dp(2)],
        )
        self.category_row.bind(minimum_width=self.category_row.setter('width'))
        self.category_scroll.add_widget(self.category_row)
        self.root_layout.add_widget(self.category_scroll)
        self._build_category_buttons()

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(6),
            bar_color=get_color_from_hex('#90A4AE'),
        )
        self.reminders_container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            padding=[0, dp(4), 0, dp(4)],
        )
        self.reminders_container.bind(
            minimum_height=self.reminders_container.setter('height')
        )
        self.scroll.add_widget(self.reminders_container)
        self.root_layout.add_widget(self.scroll)

        self.load_reminders()
        
        Clock.schedule_once(self.check_license, 0.5)
        # پاک‌سازی خودکار فایل‌های اضافی بعد از شروع
        Clock.schedule_once(self._run_auto_cleanup, 2.0)
        # فعال‌سازی اجرای خودکار در ویندوز (یک‌بار)
        if sys.platform == 'win32':
            Clock.schedule_once(self._ensure_windows_autostart, 1.5)
        
        return self.root_layout

    def _ensure_windows_autostart(self, dt):
        """اگر هنوز فعال نشده، اجرای خودکار با ویندوز را فعال کن"""
        try:
            if not self.is_autostart_enabled():
                if self.set_autostart(True):
                    log("[OK] Windows autostart enabled on first run")
        except Exception as e:
            log(f"[WARN] _ensure_windows_autostart: {e}")

    def _run_auto_cleanup(self, dt):
        """پاک‌سازی خودکار بکاپ‌ها و فایل‌های خروجی قدیمی"""
        try:
            removed = self.db.cleanup_extra_files(max_age_days=14, max_exports=5)
            if removed > 0:
                msg = f'{removed} فایل اضافی پاک شد' if self.language == 'fa' else f'{removed} extra file(s) cleaned'
                self._show_success(msg)
                log(f"[OK] Auto-cleanup removed {removed} file(s)")
        except Exception as e:
            log(f"[WARN] Auto-cleanup error: {e}")

    # --------------------------------------------------
    # اجرا در استارت‌آپ (ویندوز) / پیشنهاد برای اندروید
    # --------------------------------------------------
    def _windows_startup_path(self):
        """مسیر پوشه Startup ویندوز"""
        try:
            startup = os.path.join(
                os.environ.get('APPDATA', ''),
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            if os.path.isdir(startup):
                return startup
        except Exception:
            pass
        return None

    def is_autostart_enabled(self):
        if sys.platform != 'win32':
            return False
        startup = self._windows_startup_path()
        if not startup:
            return False
        return os.path.exists(os.path.join(startup, 'Yadavar.bat'))

    def set_autostart(self, enable=True):
        """فعال/غیرفعال کردن اجرای خودکار در ویندوز"""
        if sys.platform != 'win32':
            return False
        startup = self._windows_startup_path()
        if not startup:
            return False
        bat_path = os.path.join(startup, 'Yadavar.bat')
        try:
            if enable:
                # مسیر اجرای برنامه
                if getattr(sys, 'frozen', False):
                    exe = sys.executable
                    cmd = f'@echo off\r\nstart "" "{exe}"\r\n'
                else:
                    script = os.path.abspath(sys.argv[0] if sys.argv else __file__)
                    py = sys.executable
                    cmd = f'@echo off\r\nstart "" "{py}" "{script}"\r\n'
                with open(bat_path, 'w', encoding='utf-8') as f:
                    f.write(cmd)
                log(f"[OK] Autostart enabled: {bat_path}")
                return True
            else:
                if os.path.exists(bat_path):
                    os.remove(bat_path)
                    log("[OK] Autostart disabled")
                return True
        except Exception as e:
            log(f"[WARN] set_autostart error: {e}")
            return False

    def request_android_permissions(self):
        """درخواست مجوزهای لازم برای اندروید"""
        if platform != 'android':
            return
        try:
            from android.permissions import request_permissions, Permission
            from android import api_version
            perms = [Permission.VIBRATE]
            if api_version >= 33:
                perms.append(Permission.POST_NOTIFICATIONS)
            if api_version < 30:
                perms.extend([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ])
            if 29 <= api_version < 33:
                try:
                    perms.append(Permission.READ_EXTERNAL_STORAGE)
                except Exception:
                    pass
            request_permissions(perms)
            log(f"[OK] Android permissions requested (API {api_version}): {[str(p) for p in perms]}")
        except Exception as e:
            log(f"[WARN] Could not request permissions: {e}")

    def check_license(self, dt):
        if self._license_checked:
            return
        self._license_checked = True
        
        license_mgr = LicenseManager(self.data_dir)
        
        if license_mgr.is_verified():
            log("[OK] License already verified")
            return
            
        if license_mgr.is_expired() and not license_mgr.is_in_grace_period():
            LicenseVerificationPopup(self, self.license_callback)
            return
        
        if license_mgr.get_days_remaining() < 30 or license_mgr.is_in_grace_period():
            LicenseVerificationPopup(self, self.license_callback)

    def license_callback(self, verified):
        if verified:
            log("[OK] License verified successfully")
        else:
            log("[INFO] License check skipped")

    def apply_theme(self, theme_name):
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES['light'])
        self.settings.set('theme', theme_name)
        Window.clearcolor = get_color_from_hex(self.theme['window_bg'])
        if hasattr(self, 'title_label'):
            self.title_label.color = self.theme['header_title']
        if hasattr(self, 'search_input'):
            self.search_input.apply_theme(self.theme)
        self.load_reminders()

    def change_language(self, lang):
        self.language = lang
        self.settings.set('language', lang)
        if hasattr(self, 'search_input'):
            self.search_input.hint_text = reshape_persian(self._('search_hint'))
        filter_labels = [
            ('all', self._('all')),
            ('today', self._('today')),
            ('tomorrow', self._('tomorrow')),
            ('week', self._('this_week')),
            ('active', self._('active')),
            ('completed', self._('completed')),
        ]
        for ftype, label in filter_labels:
            if ftype in self.filter_buttons:
                self.filter_buttons[ftype].set_text(label)
        self.load_reminders()

    def on_stop(self):
        try:
            self.db.backup(force=True)
        except Exception:
            pass

    def on_pause(self):
        """وقتی اپ به پس‌زمینه می‌رود"""
        return True

    def on_resume(self):
        """وقتی اپ دوباره فعال می‌شود"""
        try:
            self.load_reminders()
            Clock.schedule_once(self.check_due_reminders, 0.5)
        except Exception as e:
            log(f"[WARN] on_resume error: {e}")

    def update_filter_buttons(self, active_filter):
        for ftype, btn in self.filter_buttons.items():
            if ftype == active_filter:
                btn.background_color = get_color_from_hex(self.filter_active_colors[ftype])
                btn.color = (1, 1, 1, 1)
                btn.font_size = '14sp'
                btn.bold = True
            else:
                btn.background_color = get_color_from_hex(self.filter_colors[ftype])
                btn.color = (1, 1, 1, 1)
                btn.font_size = '13sp'
                btn.bold = False

    def _show_error(self, message):
        popup = Popup(
            title=reshape_persian(self._('error')),
            content=PersianLabel(text=message, font_size='15sp', color=(1, 1, 1, 1)),
            size_hint=(0.8, 0.25),
            title_font='PersianFont',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=(0.25, 0.15, 0.15, 1),
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2.5)

    def _show_success(self, message):
        popup = Popup(
            title=reshape_persian(self._('success')),
            content=PersianLabel(text=message, font_size='15sp', color=(1, 1, 1, 1)),
            size_hint=(0.75, 0.22),
            title_font='PersianFont',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=(0.15, 0.25, 0.15, 1),
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def on_search_text(self, instance, value):
        try:
            self.search_query = instance.value
            self.load_reminders()
        except Exception as e:
            log(f"[ERROR] on_search_text error: {e}")

    def _update_header_count(self):
        try:
            count = self.db.count_active()
            if count > 0:
                self.title_label.set_text(f"{self._('my_reminders')} ({count})")
            else:
                self.title_label.set_text(self._('my_reminders'))
        except Exception:
            self.title_label.set_text(self._('my_reminders'))

    def load_reminders(self, *args):
        try:
            self.reminders_container.clear_widgets()
            self._update_header_count()

            show_completed = self.current_filter in ('all', 'completed')
            try:
                if self.search_query:
                    reminders = self.db.search_reminders(self.search_query, show_completed)
                else:
                    reminders = self.db.get_reminders(show_completed)
            except Exception as e:
                log(f"[ERROR] load_reminders query error: {e}")
                reminders = []

            if self.current_filter == 'completed':
                reminders = [r for r in reminders if r[5] == 1]
            elif self.current_filter == 'active':
                reminders = [r for r in reminders if r[5] == 0]
            elif self.current_filter == 'today':
                today_str = get_default_date()
                reminders = [r for r in reminders if r[5] == 0 and r[3].replace('-', '/') == today_str]
            elif self.current_filter == 'tomorrow':
                tomorrow_str = get_jalali_date_offset(1)
                reminders = [r for r in reminders if r[5] == 0 and r[3].replace('-', '/') == tomorrow_str]
            elif self.current_filter == 'week':
                start_str = get_default_date()
                end_str = get_jalali_date_offset(6)
                reminders = [
                    r for r in reminders
                    if r[5] == 0 and is_date_in_range(r[3], start_str, end_str)
                ]

            # فیلتر دسته‌بندی
            if self.current_category and self.current_category != 'همه':
                reminders = [
                    r for r in reminders
                    if (r[12] if len(r) > 12 else 'عمومی') == self.current_category
                ]

            if not reminders:
                if self.search_query:
                    empty_text = self._('no_search_result')
                elif self.current_filter == 'today':
                    empty_text = self._('no_today')
                elif self.current_filter == 'tomorrow':
                    empty_text = self._('no_tomorrow')
                elif self.current_filter == 'week':
                    empty_text = self._('no_week')
                else:
                    empty_text = self._('no_reminders')
                empty = PersianLabel(
                    text=empty_text,
                    font_size='16sp',
                    color=self.theme['empty_color'],
                    size_hint_y=None,
                    height=dp(100),
                )
                self.reminders_container.add_widget(empty)
                return

            repeat_fa = {
                'none': '',
                'daily': ' (روزانه)',
                'weekly': ' (هفتگی)',
                'monthly': ' (ماهانه)'
            }

            for reminder in reminders:
                try:
                    rid = reminder[0]
                    title_text = reminder[1]
                    description_text = reminder[2] or ''
                    date_text = reminder[3]
                    time_text = reminder[4]
                    is_done = reminder[5] == 1
                    notify_before = reminder[7] if len(reminder) > 7 else 15
                    repeat_type = reminder[8] if len(reminder) > 8 else 'none'
                    category = reminder[12] if len(reminder) > 12 else 'عمومی'

                    repeat_suffix = repeat_fa.get(repeat_type, '')
                    display_title = title_text + repeat_suffix

                    status = date_status(date_text) if not is_done else 'done'

                    title_height = 30
                    desc_lines = max(1, (len(description_text) // 35) + 1) if description_text else 0
                    desc_height = min(desc_lines * 20, 60) if description_text else 0
                    badge_height = 18 if status in ('today', 'overdue') else 0
                    cat_height = 18
                    btn_height = 36
                    padding = 28

                    card_height = dp(title_height + desc_height + badge_height + cat_height + btn_height + padding)
                    card_height = max(dp(120), min(card_height, dp(280)))

                    # کارت مدرن شبیه تصویر (سفید، گوشه گرد، دکمه‌های outline)
                    card_bg = (1, 1, 1, 1) if self.theme_name == 'light' else self.theme['card_bg']
                    if is_done:
                        card_bg = self.theme['card_bg_done']
                    elif status == 'overdue':
                        card_bg = self.theme.get('card_bg_overdue', card_bg)
                    elif status == 'today':
                        card_bg = self.theme.get('card_bg_today', card_bg)

                    card = ColoredBox(
                        orientation='vertical',
                        bg_color=card_bg,
                        radius=16,
                        size_hint_y=None,
                        height=card_height,
                        padding=[dp(14), dp(10), dp(14), dp(10)],
                        spacing=dp(6),
                    )

                    # ردیف عنوان + چک‌باکس
                    top_row = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=dp(title_height),
                        spacing=dp(8),
                    )
                    # چک‌باکس تکمیل (سمت چپ در LTR / راست در ظاهر RTL با ترتیب ویجت)
                    check_btn = PersianButton(
                        text='✓' if is_done else '☐',
                        size_hint_x=None,
                        width=dp(36),
                        background_color=(0, 0, 0, 0),
                        color=get_color_from_hex('#43A047'),
                        font_size='20sp',
                    )
                    check_btn.bind(on_press=lambda inst, r=rid: self._toggle(r))

                    title_lbl = PersianLabel(
                        text=display_title,
                        font_size='17sp',
                        color=self.theme['title_color_done'] if is_done else self.theme['title_color'],
                        halign='right',
                        size_hint_x=1,
                    )
                    top_row.add_widget(check_btn)
                    top_row.add_widget(title_lbl)
                    card.add_widget(top_row)

                    if description_text:
                        desc_lbl = PersianLabel(
                            text=description_text,
                            font_size='14sp',
                            color=self.theme['desc_color_done'] if is_done else self.theme['desc_color'],
                            halign='right',
                            size_hint_y=None,
                            height=dp(desc_height),
                            thin=True,
                        )
                        card.add_widget(desc_lbl)

                    # دسته
                    cat_lbl = PersianLabel(
                        text=category,
                        font_size='13sp',
                        color=get_color_from_hex('#00796B'),
                        halign='right',
                        size_hint_y=None,
                        height=dp(cat_height),
                        thin=True,
                    )
                    card.add_widget(cat_lbl)

                    if status in ('today', 'overdue') and not is_done:
                        st_text = self._('today_label') if status == 'today' else self._('overdue')
                        st_color = self.theme['badge_today'] if status == 'today' else self.theme['badge_overdue']
                        st_lbl = PersianLabel(
                            text=st_text,
                            font_size='12sp',
                            color=get_color_from_hex(st_color),
                            size_hint_y=None,
                            height=dp(18),
                            halign='right',
                        )
                        card.add_widget(st_lbl)

                    # ردیف دکمه‌ها: زمان | ویرایش | حذف
                    btn_row = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=dp(38),
                        spacing=dp(6),
                    )
                    time_btn = PersianButton(
                        text=f'🕒 {time_text}',
                        size_hint_x=0.34,
                        background_color=get_color_from_hex('#2E7D32'),
                        color=(1, 1, 1, 1),
                        font_size='13sp',
                    )
                    # فقط نمایش — با کلیک ویرایش باز شود
                    time_btn.bind(on_press=lambda inst, r=rid: self.show_edit_reminder(r))

                    edit_btn = PersianButton(
                        text=self._('edit'),
                        size_hint_x=0.33,
                        background_color=get_color_from_hex('#E8F5E9'),
                        color=get_color_from_hex('#1B5E20'),
                        font_size='13sp',
                    )
                    edit_btn.bind(on_press=lambda inst, r=rid: self.show_edit_reminder(r))

                    delete_btn = PersianButton(
                        text=self._('delete'),
                        size_hint_x=0.33,
                        background_color=get_color_from_hex('#FFEBEE'),
                        color=get_color_from_hex('#C62828'),
                        font_size='13sp',
                    )
                    delete_btn.bind(on_press=lambda inst, r=rid: self._delete(r))

                    btn_row.add_widget(time_btn)
                    btn_row.add_widget(edit_btn)
                    btn_row.add_widget(delete_btn)
                    card.add_widget(btn_row)

                    self.reminders_container.add_widget(card)

                except Exception as e:
                    log(f"[ERROR] Loading reminder {reminder[0] if reminder else 'unknown'}: {e}")
                    continue

        except Exception as e:
            log(f"[ERROR] load_reminders error: {e}")
            error_label = PersianLabel(
                text='خطا در بارگذاري يادآوري‌ها',
                font_size='16sp',
                color=(1, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(100),
            )
            self.reminders_container.add_widget(error_label)

    def _toggle(self, rid):
        try:
            result = self.db.toggle_completed(rid)
            if result:
                self._notified_ids.discard(rid)
                self._alerting_ids.discard(rid)
                if rid in self._active_alerts:
                    try:
                        self._active_alerts[rid].dismiss()
                    except Exception:
                        pass
                    del self._active_alerts[rid]
                self.load_reminders()
            else:
                self._show_error('خطا در تغییر وضعیت')
        except Exception as e:
            log(f"[ERROR] _toggle error: {e}")
            self._show_error('خطا در تغییر وضعیت')

    def _delete(self, rid):
        try:
            rem = self.db.get_reminder_by_id(rid)
            title_preview = rem[1] if rem else ''
            if len(title_preview) > 30:
                title_preview = title_preview[:30] + '...'

            box = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(14))
            box.add_widget(PersianLabel(
                text=self._('confirm_delete'),
                font_size='15sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(36),
            ))
            if title_preview:
                box.add_widget(PersianLabel(
                    text=title_preview,
                    font_size='14sp',
                    color=(1, 0.85, 0.4, 1),
                    size_hint_y=None,
                    height=dp(28),
                ))

            btn_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(44),
                spacing=dp(10),
            )
            cancel_btn = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
                font_size='14sp',
            )
            confirm_btn = PersianButton(
                text=self._('delete'),
                background_color=get_color_from_hex('#C62828'),
                color=(1, 1, 1, 1),
                font_size='14sp',
            )
            btn_row.add_widget(cancel_btn)
            btn_row.add_widget(confirm_btn)
            box.add_widget(btn_row)

            popup = Popup(
                title=reshape_persian(self._('confirm')),
                content=box,
                size_hint=(0.85, 0.35),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='16sp',
                title_color=(1, 1, 1, 1),
                background='',
                background_color=self.theme['popup_bg'],
                separator_color=get_color_from_hex('#C62828'),
                separator_height=dp(2),
            )

            def do_delete(_inst):
                try:
                    result = self.db.delete_reminder(rid)
                    popup.dismiss()
                    if result:
                        self._notified_ids.discard(rid)
                        self._alerting_ids.discard(rid)
                        if rid in self._active_alerts:
                            try:
                                self._active_alerts[rid].dismiss()
                            except Exception:
                                pass
                            del self._active_alerts[rid]
                        self.load_reminders()
                        self._show_success(self._('reminder_deleted'))
                    else:
                        self._show_error('خطا در حذف یادآوری')
                except Exception as e:
                    log(f"[ERROR] do_delete error: {e}")
                    popup.dismiss()
                    self._show_error('خطا در حذف یادآوری')

            cancel_btn.bind(on_press=popup.dismiss)
            confirm_btn.bind(on_press=do_delete)
            popup.open()
        except Exception as e:
            log(f"[ERROR] _delete error: {e}")
            self._show_error('خطا در حذف یادآوری')

    def filter_reminders(self, filter_type):
        try:
            self.current_filter = filter_type
            self.update_filter_buttons(filter_type)
            self.load_reminders()
        except Exception as e:
            log(f"[ERROR] filter_reminders error: {e}")

    def _build_category_buttons(self):
        """ساخت دکمه‌های دسته‌بندی به صورت چیپ گرد سفید (قابل اسکرول افقی)"""
        try:
            self.category_row.clear_widgets()
            self.category_buttons = {}
            cats = self.categories.get_all()
            for cat in cats:
                is_active = (cat == self.current_category)
                # شبیه تصویر: چیپ سفید گرد؛ فعال = آبی
                if is_active:
                    bg = get_color_from_hex('#1565C0')
                    fg = (1, 1, 1, 1)
                else:
                    bg = (1, 1, 1, 1)
                    fg = (0.12, 0.12, 0.15, 1)
                w = dp(max(64, len(cat) * 14 + 28))
                btn = PersianButton(
                    text=cat,
                    size_hint=(None, None),
                    size=(w, dp(38)),
                    background_color=bg,
                    color=fg,
                    font_size='14sp',
                )
                btn.background_normal = ''
                btn.background_down = ''
                btn.bind(on_press=lambda inst, c=cat: self.filter_by_category(c))
                self.category_buttons[cat] = btn
                self.category_row.add_widget(btn)

            # دکمه سبز افزودن دسته با علامت +
            add_cat_btn = PersianButton(
                text='+',
                size_hint=(None, None),
                size=(dp(40), dp(38)),
                background_color=get_color_from_hex('#2E7D32'),
                color=(1, 1, 1, 1),
                font_size='22sp',
                bold=True,
            )
            add_cat_btn.background_normal = ''
            add_cat_btn.background_down = ''
            add_cat_btn.bind(on_press=self.show_add_category)
            self.category_row.add_widget(add_cat_btn)

            # به‌روزرسانی عرض ردیف برای اسکرول افقی
            total_w = sum(c.width for c in self.category_row.children) + dp(10) * max(0, len(self.category_row.children) - 1)
            self.category_row.width = max(total_w + dp(8), dp(200))
        except Exception as e:
            log(f"[ERROR] _build_category_buttons: {e}")

    def filter_by_category(self, category):
        try:
            self.current_category = category
            for cat, btn in self.category_buttons.items():
                is_active = (cat == category)
                if is_active:
                    btn.background_color = get_color_from_hex('#1565C0')
                    btn.color = (1, 1, 1, 1)
                    btn.font_name = 'PersianFontBold'
                else:
                    btn.background_color = (1, 1, 1, 1)
                    btn.color = (0.15, 0.15, 0.2, 1)
                    btn.font_name = 'PersianFont'
            self.load_reminders()
        except Exception as e:
            log(f"[ERROR] filter_by_category: {e}")

    def show_add_category(self, instance):
        try:
            box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
            box.add_widget(PersianLabel(
                text='نام دسته جدید را وارد کنید',
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30),
            ))
            name_input = PersianTextInput(
                hint_text='مثال: ورزش، خانواده، ...',
                multiline=False,
                size_hint_y=None,
                height=dp(44),
                font_size='15sp',
            )
            name_input.apply_theme(self.theme)
            box.add_widget(name_input)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))
            cancel_btn = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
            )
            save_btn = PersianButton(
                text=self._('save'),
                background_color=get_color_from_hex('#2E7D32'),
                color=(1, 1, 1, 1),
            )
            btn_row.add_widget(cancel_btn)
            btn_row.add_widget(save_btn)
            box.add_widget(btn_row)

            popup = Popup(
                title=reshape_persian('افزودن دسته‌بندی'),
                content=box,
                size_hint=(0.85, 0.35),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='16sp',
                title_color=(1, 1, 1, 1),
                background='',
                background_color=self.theme['popup_bg'],
            )

            def do_save(_inst):
                name = name_input.value
                if not name:
                    self._show_error('نام دسته را وارد کنید')
                    return
                if self.categories.add(name):
                    popup.dismiss()
                    self._build_category_buttons()
                    self._show_success(f'دسته «{name}» اضافه شد')
                else:
                    self._show_error('این دسته از قبل وجود دارد')

            cancel_btn.bind(on_press=popup.dismiss)
            save_btn.bind(on_press=do_save)
            popup.open()
        except Exception as e:
            log(f"[ERROR] show_add_category: {e}")

    def _play_alert_sound(self):
        """پخش یک‌بار صدای ملایم یادآوری"""
        # اندروید: ویبره کوتاه یک‌بار
        if platform == 'android':
            try:
                if HAS_VIBRATOR:
                    vibrator.vibrate(0.35)
                return True
            except Exception as e:
                log(f"[WARN] Android vibrate error: {e}")
        
        # ویندوز: صدای ملایم‌تر (فرکانس پایین‌تر و کوتاه‌تر)
        if HAS_WINSOUND:
            try:
                # دو بوق کوتاه و ملایم به‌جای سه بوق تیز
                winsound.Beep(660, 180)   # نت E5 کوتاه
                winsound.Beep(880, 220)   # نت A5
                return True
            except Exception as e:
                log(f"[WARN] Winsound error: {e}")
                try:
                    winsound.MessageBeep(winsound.MB_OK)  # صدای سیستم ملایم‌تر
                    return True
                except Exception:
                    pass
        
        # سایر سیستم‌ها
        try:
            import subprocess
            subprocess.run(['beep', '-f', '660', '-l', '200'], check=False)
            return True
        except Exception:
            try:
                print('\a')
            except Exception:
                pass
        return False

    def _show_notification(self, title, message):
        """نمایش اعلان سیستم — روی ویندوز بدون reshape تا متن برعکس نشود"""
        try:
            if HAS_PLYER:
                # روی ویندوز و اکثر دسکتاپ‌ها، سیستم خودش RTL را هندل می‌کند
                # reshape باعث برعکس شدن متن در نوتیفیکیشن می‌شود
                if platform == 'android':
                    t = reshape_persian(str(title))
                    m = reshape_persian(str(message))
                    kwargs = dict(
                        title=t,
                        message=m,
                        timeout=15,
                        app_name='Yadavar',
                        ticker=t,
                    )
                else:
                    kwargs = dict(
                        title=str(title),
                        message=str(message),
                        timeout=15,
                        app_name='Yadavar',
                    )
                notification.notify(**kwargs)
                log(f"[NOTIFICATION] {title}: {message}")
        except Exception as e:
            log(f"[WARN] Notification error: {e}")

    def _parse_reminder_dt(self, date_str, time_str):
        try:
            parts = date_str.replace('-', '/').split('/')
            if len(parts) != 3:
                return None
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            tparts = time_str.strip().split(':')
            hh = int(tparts[0]) if tparts else 0
            mm = int(tparts[1]) if len(tparts) > 1 else 0
            return (y, m, d, hh, mm)
        except Exception:
            return None

    def check_due_reminders(self, *args):
        if self._alert_open:
            return
        try:
            now_t = now_jalali_tuple()
            ny, nm, nd, nh, nmin = now_t
            now_minutes = nh * 60 + nmin
            reminders = self.db.get_reminders(show_completed=False)

            due_reminders = []
            for rem in reminders:
                try:
                    rid = rem[0]
                    title = rem[1]
                    desc = rem[2] or ''
                    date_str = rem[3]
                    time_str = rem[4]
                    is_done = rem[5]
                    notify_before = rem[7] if len(rem) > 7 else 15
                    repeat_type = rem[8] if len(rem) > 8 else 'none'
                    original_date = rem[10] if len(rem) > 10 else date_str
                    original_time = rem[11] if len(rem) > 11 else time_str

                    if repeat_type != 'none':
                        continue
                    if is_done or rid in self._notified_ids or rid in self._alerting_ids:
                        continue

                    rt = self._parse_reminder_dt(date_str, time_str)
                    if not rt:
                        continue
                    ry, rm, rd, rh, rmin = rt
                    reminder_minutes = rh * 60 + rmin
                    trigger_minutes = reminder_minutes - max(0, int(notify_before or 0))

                    is_due = False
                    if (ry, rm, rd) == (ny, nm, nd):
                        if now_minutes >= trigger_minutes:
                            is_due = True
                    elif (ry, rm, rd) < (ny, nm, nd):
                        is_due = True

                    if is_due:
                        due_reminders.append((
                            rid, title, desc, date_str, time_str,
                            repeat_type, original_date, original_time, notify_before
                        ))
                except Exception as e:
                    log(f"[ERROR] check_due_reminders loop error: {e}")
                    continue

            for rem_data in due_reminders:
                rid = rem_data[0]
                self._notified_ids.add(rid)
                self._alerting_ids.add(rid)
                self._show_reminder_alert(*rem_data)

        except Exception as e:
            log(f"[ERROR] check_due_reminders error: {e}")

    def _calculate_next_date(self, date_str, repeat_type):
        try:
            parts = date_str.replace('-', '/').split('/')
            if len(parts) != 3:
                return None
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])

            if repeat_type == 'daily':
                gd = jalali_to_gregorian(y, m, d)
                if not gd:
                    return None
                new_gd = gd + timedelta(days=1)
            elif repeat_type == 'weekly':
                gd = jalali_to_gregorian(y, m, d)
                if not gd:
                    return None
                new_gd = gd + timedelta(days=7)
            elif repeat_type == 'monthly':
                new_month = m + 1
                new_year = y
                if new_month > 12:
                    new_month = 1
                    new_year += 1
                max_day = days_in_jalali_month(new_year, new_month)
                new_day = min(d, max_day)
                try:
                    new_jd = jdatetime.date(new_year, new_month, new_day)
                    new_gd = new_jd.togregorian()
                except Exception as e:
                    log(f"[WARN] مشکل در ساخت تاریخ: {e}")
                    gd = jalali_to_gregorian(y, m, d)
                    if not gd:
                        return None
                    new_gd = gd + timedelta(days=30)
            else:
                return None

            try:
                new_jd = jdatetime.date.fromgregorian(date=new_gd)
                return f"{new_jd.year:04d}/{new_jd.month:02d}/{new_jd.day:02d}"
            except Exception as e:
                log(f"[ERROR] تبدیل میلادی به شمسی: {e}")
                return None
        except Exception as e:
            log(f"[ERROR] _calculate_next_date error: {e}")
            return None

    def process_repeat_reminders(self, *args):
        if self._processing_repeats or self._alert_open:
            return
        self._processing_repeats = True
        try:
            now_t = now_jalali_tuple()
            ny, nm, nd, nh, nmin = now_t
            now_minutes = nh * 60 + nmin
            reminders = self.db.get_reminders(show_completed=False)

            for rem in reminders:
                try:
                    rid = rem[0]
                    title = rem[1]
                    desc = rem[2] or ''
                    date_str = rem[3]
                    time_str = rem[4]
                    is_done = rem[5]
                    notify_before = rem[7] if len(rem) > 7 else 15
                    repeat_type = rem[8] if len(rem) > 8 else 'none'
                    repeat_end = rem[9] if len(rem) > 9 else None
                    original_date = rem[10] if len(rem) > 10 else date_str
                    original_time = rem[11] if len(rem) > 11 else time_str

                    if repeat_type == 'none' or is_done:
                        continue
                    if rid in self._alerting_ids:
                        continue

                    if repeat_end:
                        end_parts = repeat_end.replace('-', '/').split('/')
                        if len(end_parts) == 3:
                            try:
                                ey, em, ed = int(end_parts[0]), int(end_parts[1]), int(end_parts[2])
                                if (ey, em, ed) < (ny, nm, nd):
                                    self.db.toggle_completed(rid)
                                    self._notified_ids.discard(rid)
                                    continue
                            except Exception:
                                pass

                    rt = self._parse_reminder_dt(date_str, time_str)
                    if not rt:
                        continue
                    ry, rm, rd, rh, rmin = rt
                    reminder_minutes = rh * 60 + rmin
                    trigger_minutes = reminder_minutes - max(0, int(notify_before or 0))

                    is_due = False
                    if (ry, rm, rd) == (ny, nm, nd):
                        if now_minutes >= trigger_minutes:
                            is_due = True
                    elif (ry, rm, rd) < (ny, nm, nd):
                        is_due = True

                    if not is_due:
                        continue

                    if rid not in self._notified_ids:
                        self._notified_ids.add(rid)
                        self._alerting_ids.add(rid)
                        self._show_reminder_alert(
                            rid, title, desc, date_str, time_str,
                            repeat_type=repeat_type,
                            repeat_end=repeat_end,
                            notify_before=notify_before,
                            original_date=original_date,
                            original_time=original_time
                        )
                except Exception as e:
                    log(f"[ERROR] process_repeat_reminders loop error: {e}")
                    continue
        except Exception as e:
            log(f"[ERROR] process_repeat_reminders error: {e}")
        finally:
            self._processing_repeats = False

    def _show_reminder_alert(self, rid, title, desc, date_str, time_str,
                             repeat_type='none', repeat_end=None, notify_before=15,
                             original_date=None, original_time=None):
        self._alert_open = True
        if original_date is None:
            original_date = date_str
        if original_time is None:
            original_time = time_str

        log(f"[ALERT] Showing reminder alert for ID {rid}...")
        self._play_alert_sound()
        self._show_notification(self._('reminder'), title)
        sound_ev = None  # صدا فقط یک‌بار پخش می‌شود (بدون تکرار)

        box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
        icon_lbl = PersianLabel(
            text=self._('reminder_due'),
            font_size='22sp',
            color=(1, 0.85, 0.2, 1),
            size_hint_y=None,
            height=dp(36),
            bold=True,
        )
        box.add_widget(icon_lbl)

        title_lbl = PersianLabel(
            text=title,
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(32),
        )
        box.add_widget(title_lbl)

        if desc:
            desc_lbl = PersianLabel(
                text=desc,
                font_size='14sp',
                color=(0.8, 0.8, 0.85, 1),
                size_hint_y=None,
                height=dp(40),
            )
            box.add_widget(desc_lbl)

        info_lbl = PersianLabel(
            text=f'{date_str}  |  {time_str}',
            font_size='13sp',
            color=(0.6, 0.7, 0.9, 1),
            size_hint_y=None,
            height=dp(28),
        )
        box.add_widget(info_lbl)

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8),
        )
        dismiss_btn = PersianButton(
            text=self._('close'),
            background_color=get_color_from_hex('#78909C'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        done_btn = PersianButton(
            text=self._('complete'),
            background_color=get_color_from_hex('#2E7D32'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        snooze_btn = PersianButton(
            text=self._('snooze'),
            background_color=get_color_from_hex('#FF9800'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        btn_row.add_widget(snooze_btn)
        btn_row.add_widget(dismiss_btn)
        btn_row.add_widget(done_btn)
        box.add_widget(btn_row)

        alert = Popup(
            title=reshape_persian(self._('reminder_due')),
            content=box,
            size_hint=(0.9, 0.52),
            auto_dismiss=False,
            title_font='PersianFont',
            title_size='16sp',
            title_color=(1, 1, 0.5, 1),
            background='',
            background_color=self.theme['alert_bg'],
            separator_color=get_color_from_hex('#FF8F00'),
            separator_height=dp(3),
        )

        self._active_alerts[rid] = alert

        def close_alert(_inst=None):
            try:
                if sound_ev is not None:
                    sound_ev.cancel()
                self._alert_open = False
                self._alerting_ids.discard(rid)
                if rid in self._active_alerts:
                    del self._active_alerts[rid]
                alert.dismiss()
                log(f"[ALERT] Alert closed for ID {rid}")
            except Exception as e:
                log(f"[ERROR] close_alert: {e}")

        def mark_done(_inst):
            try:
                if repeat_type != 'none':
                    next_date = self._calculate_next_date(original_date, repeat_type)
                    can_continue = next_date is not None
                    if can_continue and repeat_end:
                        end_parts = repeat_end.replace('-', '/').split('/')
                        if len(end_parts) == 3:
                            try:
                                ey, em, ed = int(end_parts[0]), int(end_parts[1]), int(end_parts[2])
                                next_parts = next_date.replace('-', '/').split('/')
                                if len(next_parts) == 3:
                                    ny2, nm2, nd2 = int(next_parts[0]), int(next_parts[1]), int(next_parts[2])
                                    if (ny2, nm2, nd2) > (ey, em, ed):
                                        can_continue = False
                            except Exception:
                                pass
                    self.db.toggle_completed(rid)
                    if can_continue:
                        # حفظ دسته‌بندی از یادآوری اصلی
                        orig = self.db.get_reminder_by_id(rid)
                        cat = orig[12] if orig and len(orig) > 12 else 'عمومی'
                        self.db.add_reminder(
                            title=title,
                            description=desc,
                            date=next_date,
                            time=original_time,
                            notify_before=notify_before,
                            repeat_type=repeat_type,
                            repeat_end_date=repeat_end,
                            category=cat,
                        )
                        self._show_success(f'یادآوری انجام شد؛ یادآوری بعدی: {next_date}')
                    else:
                        self._show_success('یادآوری انجام شد (پایان چرخه تکرار)')
                else:
                    self.db.toggle_completed(rid)
                    self._show_success(self._('reminder_completed'))

                self._notified_ids.discard(rid)
                self._alerting_ids.discard(rid)
                self.load_reminders()
                close_alert()
            except Exception as e:
                log(f"[ERROR] mark_done error: {e}")
                self._show_error('خطا در تکمیل یادآوری')

        def show_snooze_options(_inst):
            try:
                last_mins = int(self.settings.get('last_snooze_minutes') or 5)
                snooze_box = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))

                options = [
                    (5, self._('snooze_5')),
                    (15, self._('snooze_15')),
                    (30, self._('snooze_30')),
                    (60, self._('snooze_60')),
                ]

                for minutes, label in options:
                    is_last = (minutes == last_mins)
                    btn = PersianButton(
                        text=label + (' *' if is_last else ''),
                        background_color=get_color_from_hex('#FF6F00' if is_last else '#FF9800'),
                        color=(1, 1, 1, 1),
                        size_hint_y=None,
                        height=dp(42),
                        font_size='14sp',
                        bold=is_last,
                    )
                    btn.bind(on_press=lambda inst, m=minutes: do_snooze(m))
                    snooze_box.add_widget(btn)

                cancel_s = PersianButton(
                    text=self._('cancel'),
                    background_color=get_color_from_hex('#78909C'),
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=dp(36),
                )
                snooze_box.add_widget(cancel_s)

                snooze_popup = Popup(
                    title=reshape_persian(self._('snooze')),
                    content=snooze_box,
                    size_hint=(0.7, 0.58),
                    auto_dismiss=False,
                    title_font='PersianFont',
                    title_size='15sp',
                    title_color=(1, 1, 1, 1),
                    background='',
                    background_color=self.theme['popup_bg'],
                )

                def do_snooze(minutes):
                    try:
                        self.settings.set('last_snooze_minutes', minutes)

                        now = datetime.now()
                        new_time = now + timedelta(minutes=minutes)
                        try:
                            jalali = jdatetime.datetime.fromgregorian(datetime=new_time)
                            new_date = f"{jalali.year:04d}/{jalali.month:02d}/{jalali.day:02d}"
                            new_time_str = f"{new_time.hour:02d}:{new_time.minute:02d}"
                        except Exception:
                            new_date = f"{new_time.year-621:04d}/{new_time.month:02d}/{new_time.day:02d}"
                            new_time_str = f"{new_time.hour:02d}:{new_time.minute:02d}"

                        self.db.update_reminder_date_time(rid, new_date, new_time_str)
                        self._notified_ids.discard(rid)
                        self._alerting_ids.discard(rid)
                        self.load_reminders()
                        snooze_popup.dismiss()
                        close_alert()
                        self._show_success(self._('snoozed').format(new_time_str))
                        log(f"[ALERT] Reminder {rid} snoozed {minutes} min")
                    except Exception as e:
                        log(f"[ERROR] do_snooze error: {e}")
                        self._show_error('خطا در تاخیر یادآوری')

                cancel_s.bind(on_press=snooze_popup.dismiss)
                snooze_popup.open()
            except Exception as e:
                log(f"[ERROR] show_snooze_options error: {e}")
                self._show_error('خطا در نمایش گزینه‌های تاخیر')

        dismiss_btn.bind(on_press=close_alert)
        done_btn.bind(on_press=mark_done)
        snooze_btn.bind(on_press=show_snooze_options)
        alert.open()
        try:
            Window.raise_window()
        except Exception:
            pass

    def show_settings(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(12))
        scroll = ScrollView(do_scroll_x=False)
        settings_form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        settings_form.bind(minimum_height=settings_form.setter('height'))

        settings_form.add_widget(
            PersianLabel(
                text=self._('check_interval'),
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30),
            )
        )
        current_interval = self.check_interval
        spinner = Spinner(
            text=str(current_interval),
            values=['10', '15', '20', '30', '45', '60', '90', '120', '180', '300', '600'],
            font_name='PersianFont',
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=get_color_from_hex('#ECEFF1'),
            color=(0.1, 0.1, 0.1, 1),
            font_size='15sp',
        )
        settings_form.add_widget(spinner)

        settings_form.add_widget(
            PersianLabel(
                text=self._('theme'),
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30),
            )
        )
        theme_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        selected_theme = [self.theme_name]

        light_btn = PersianButton(
            text=self._('light') + (' *' if self.theme_name == 'light' else ''),
            background_color=get_color_from_hex('#1565C0' if self.theme_name == 'light' else '#546E7A'),
            color=(1, 1, 1, 1),
            font_size='14sp',
        )
        dark_btn = PersianButton(
            text=self._('dark') + (' *' if self.theme_name == 'dark' else ''),
            background_color=get_color_from_hex('#1565C0' if self.theme_name == 'dark' else '#546E7A'),
            color=(1, 1, 1, 1),
            font_size='14sp',
        )

        def select_light(_inst):
            selected_theme[0] = 'light'
            light_btn.background_color = get_color_from_hex('#1565C0')
            light_btn.set_text(self._('light') + ' *')
            dark_btn.background_color = get_color_from_hex('#546E7A')
            dark_btn.set_text(self._('dark'))

        def select_dark(_inst):
            selected_theme[0] = 'dark'
            dark_btn.background_color = get_color_from_hex('#1565C0')
            dark_btn.set_text(self._('dark') + ' *')
            light_btn.background_color = get_color_from_hex('#546E7A')
            light_btn.set_text(self._('light'))

        light_btn.bind(on_press=select_light)
        dark_btn.bind(on_press=select_dark)
        theme_row.add_widget(light_btn)
        theme_row.add_widget(dark_btn)
        settings_form.add_widget(theme_row)

        settings_form.add_widget(
            PersianLabel(
                text='زبان / Language',
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30),
            )
        )
        lang_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        selected_lang = [self.language]

        fa_btn = PersianButton(
            text='فارسی' + (' *' if self.language == 'fa' else ''),
            background_color=get_color_from_hex('#1565C0' if self.language == 'fa' else '#546E7A'),
            color=(1, 1, 1, 1),
            font_size='14sp',
        )
        en_btn = PersianButton(
            text='English' + (' *' if self.language == 'en' else ''),
            background_color=get_color_from_hex('#1565C0' if self.language == 'en' else '#546E7A'),
            color=(1, 1, 1, 1),
            font_size='14sp',
        )

        def select_fa(_inst):
            selected_lang[0] = 'fa'
            fa_btn.background_color = get_color_from_hex('#1565C0')
            fa_btn.set_text('فارسی *')
            en_btn.background_color = get_color_from_hex('#546E7A')
            en_btn.set_text('English')

        def select_en(_inst):
            selected_lang[0] = 'en'
            en_btn.background_color = get_color_from_hex('#1565C0')
            en_btn.set_text('English *')
            fa_btn.background_color = get_color_from_hex('#546E7A')
            fa_btn.set_text('فارسی')

        fa_btn.bind(on_press=select_fa)
        en_btn.bind(on_press=select_en)
        lang_row.add_widget(fa_btn)
        lang_row.add_widget(en_btn)
        settings_form.add_widget(lang_row)

        # اجرای خودکار در استارت‌آپ (ویندوز) + پاک‌سازی فایل‌های اضافی
        auto_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        auto_enabled = [self.is_autostart_enabled()]
        auto_label = 'اجرا با ویندوز' if self.language == 'fa' else 'Start with Windows'
        if platform == 'android':
            auto_label = 'اجرا در پس‌زمینه' if self.language == 'fa' else 'Background run'
        auto_btn = PersianButton(
            text=auto_label + (' ✓' if auto_enabled[0] else ''),
            background_color=get_color_from_hex('#1565C0' if auto_enabled[0] else '#546E7A'),
            color=(1, 1, 1, 1),
            font_size='12sp',
            size_hint_x=0.55,
        )

        def toggle_autostart(_inst):
            if platform == 'android':
                # در اندروید اجرای واقعی با بوت نیاز به سرویس دارد؛ فقط راهنما
                tip = (
                    'برای اجرای خودکار در اندروید:\n'
                    'تنظیمات گوشی → برنامه‌ها → یادآور → باتری → بدون محدودیت'
                    if self.language == 'fa' else
                    'For Android auto-start:\nSettings → Apps → Yadavar → Battery → Unrestricted'
                )
                self._show_success(tip)
                return
            new_state = not auto_enabled[0]
            if self.set_autostart(new_state):
                auto_enabled[0] = new_state
                auto_btn.background_color = get_color_from_hex('#1565C0' if new_state else '#546E7A')
                auto_btn.set_text(auto_label + (' ✓' if new_state else ''))
                msg = (
                    'اجرای خودکار فعال شد' if new_state else 'اجرای خودکار غیرفعال شد'
                ) if self.language == 'fa' else (
                    'Autostart enabled' if new_state else 'Autostart disabled'
                )
                self._show_success(msg)
            else:
                self._show_error('خطا در تنظیم اجرای خودکار' if self.language == 'fa' else 'Autostart error')

        auto_btn.bind(on_press=toggle_autostart)
        auto_row.add_widget(auto_btn)

        cleanup_btn = PersianButton(
            text='پاک‌سازی فایل‌ها' if self.language == 'fa' else 'Clean files',
            background_color=get_color_from_hex('#6A1B9A'),
            color=(1, 1, 1, 1),
            font_size='12sp',
            size_hint_x=0.45,
        )

        def do_manual_cleanup(_inst):
            try:
                n = self.db.cleanup_extra_files(max_age_days=7, max_exports=3)
                if n > 0:
                    self._show_success(
                        f'{n} فایل اضافی پاک شد' if self.language == 'fa' else f'{n} file(s) cleaned'
                    )
                else:
                    self._show_success(
                        'فایل اضافی برای پاک کردن نبود' if self.language == 'fa' else 'No extra files'
                    )
            except Exception as e:
                log(f"[ERROR] manual cleanup: {e}")
                self._show_error('خطا در پاک‌سازی')

        cleanup_btn.bind(on_press=do_manual_cleanup)
        auto_row.add_widget(cleanup_btn)
        settings_form.add_widget(auto_row)

        # دکمه‌های خروجی و ورودی
        io_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        export_btn = PersianButton(
            text=self._('export'),
            background_color=get_color_from_hex('#00838F'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        export_btn.bind(on_press=self.export_data)
        import_btn = PersianButton(
            text=self._('import'),
            background_color=get_color_from_hex('#E65100'),
            color=(1, 1, 1, 1),
            font_size='13sp',
        )
        import_btn.bind(on_press=self.import_data)
        io_row.add_widget(export_btn)
        io_row.add_widget(import_btn)
        settings_form.add_widget(io_row)

        about_btn = PersianButton(
            text=self._('about'),
            background_color=get_color_from_hex('#5C6BC0'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40),
            font_size='13sp',
        )
        about_btn.bind(on_press=lambda *_: self.show_about())
        settings_form.add_widget(about_btn)

        settings_form.add_widget(Widget(size_hint_y=None, height=dp(4)))

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
        )
        cancel_btn = PersianButton(
            text=self._('cancel'),
            background_color=get_color_from_hex('#78909C'),
            color=(1, 1, 1, 1),
        )
        save_btn = PersianButton(
            text=self._('save'),
            background_color=get_color_from_hex('#2E7D32'),
            color=(1, 1, 1, 1),
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        settings_form.add_widget(btn_row)

        scroll.add_widget(settings_form)
        content.add_widget(scroll)

        popup = Popup(
            title=reshape_persian(self._('settings')),
            content=content,
            size_hint=(0.85, 0.75),
            auto_dismiss=False,
            title_font='PersianFont',
            title_size='16sp',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=self.theme['popup_bg'],
            separator_color=get_color_from_hex('#1565C0'),
            separator_height=dp(2),
        )

        def save_settings(_inst):
            try:
                new_interval = int(spinner.text)
                if new_interval < 5:
                    self._show_error(self._('min_interval'))
                    return

                Clock.unschedule(self.check_due_reminders)
                self.check_interval = new_interval
                self.settings.set('check_interval', new_interval)
                Clock.schedule_interval(self.check_due_reminders, self.check_interval)

                new_theme = selected_theme[0]
                if new_theme != self.theme_name:
                    self.apply_theme(new_theme)

                new_lang = selected_lang[0]
                if new_lang != self.language:
                    self.change_language(new_lang)

                popup.dismiss()

                if new_interval >= 60:
                    minutes = new_interval // 60
                    seconds = new_interval % 60
                    time_text = f'{minutes} دقیقه' if seconds == 0 else f'{minutes} دقیقه و {seconds} ثانیه'
                else:
                    time_text = f'{new_interval} ثانیه'
                self._show_success(f"{self._('settings_saved')} ({time_text})")
            except ValueError:
                self._show_error(self._('enter_valid_number'))

        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=save_settings)
        popup.open()

    def export_data(self, instance):
        try:
            data = self.db.export_data()
            if not data:
                self._show_error('خطا در خروجی گرفتن')
                return

            # روی اندروید فایل را مستقیماً در data_dir ذخیره می‌کنیم (امن‌تر و بدون مشکل Scoped Storage)
            if platform == 'android':
                try:
                    filename = f"yadavar_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    file_path = os.path.join(self.data_dir, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(data)
                    self._show_success(f"{self._('export_success')}\n{filename}")
                    log(f"[OK] Exported to {file_path}")
                except Exception as e:
                    log(f"[ERROR] Android export error: {e}")
                    self._show_error('خطا در ذخیره فایل')
                return

            # دسکتاپ: انتخاب مسیر با FileChooser
            from kivy.uix.filechooser import FileChooserListView
            from kivy.uix.modalview import ModalView

            filechooser = FileChooserListView(
                path=self.data_dir,
                filters=['*.json'],
                size_hint=(0.9, 0.7),
            )

            def save_file(selection):
                if selection:
                    file_path = selection[0]
                    if not file_path.endswith('.json'):
                        file_path += '.json'
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(data)
                        self._show_success(self._('export_success'))
                    except Exception as e:
                        log(f"[ERROR] Export save error: {e}")
                        self._show_error('خطا در ذخیره فایل')
                view.dismiss()

            view = ModalView(size_hint=(0.95, 0.8))
            box = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
            box.add_widget(PersianLabel(
                text='انتخاب مسیر برای ذخیره خروجی',
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(30),
            ))
            box.add_widget(filechooser)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))
            cancel_btn = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
            )
            cancel_btn.bind(on_press=view.dismiss)

            save_btn = PersianButton(
                text=self._('save'),
                background_color=get_color_from_hex('#2E7D32'),
                color=(1, 1, 1, 1),
            )
            save_btn.bind(on_press=lambda inst: save_file(filechooser.selection))

            btn_row.add_widget(cancel_btn)
            btn_row.add_widget(save_btn)
            box.add_widget(btn_row)

            view.add_widget(box)
            view.open()

        except Exception as e:
            log(f"[ERROR] export_data error: {e}")
            self._show_error('خطا در خروجی گرفتن')

    def import_data(self, instance):
        try:
            from kivy.uix.filechooser import FileChooserListView
            from kivy.uix.modalview import ModalView

            # روی اندروید و دسکتاپ از data_dir شروع می‌کنیم
            start_path = self.data_dir

            filechooser = FileChooserListView(
                path=start_path,
                filters=['*.json'],
                size_hint=(0.9, 0.7),
            )

            def load_file(selection):
                if selection:
                    file_path = selection[0]
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = f.read()
                        if self.db.import_data(data):
                            self.load_reminders()
                            self._show_success(self._('import_success'))
                        else:
                            self._show_error(self._('import_error'))
                    except Exception as e:
                        log(f"[ERROR] Import load error: {e}")
                        self._show_error('خطا در خواندن فایل')
                view.dismiss()

            view = ModalView(size_hint=(0.95, 0.8))
            box = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
            hint = 'انتخاب فایل JSON برای ورودی (فایل‌های خروجی داخل همین پوشه)'
            if platform == 'android':
                hint = 'فایل‌های خروجی برنامه در همین پوشه ذخیره می‌شوند\nیکی را انتخاب کنید'
            box.add_widget(PersianLabel(
                text=hint,
                font_size='13sp',
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(40),
            ))
            box.add_widget(filechooser)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))
            cancel_btn = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
            )
            cancel_btn.bind(on_press=view.dismiss)

            load_btn = PersianButton(
                text=self._('import'),
                background_color=get_color_from_hex('#E65100'),
                color=(1, 1, 1, 1),
            )
            load_btn.bind(on_press=lambda inst: load_file(filechooser.selection))

            btn_row.add_widget(cancel_btn)
            btn_row.add_widget(load_btn)
            box.add_widget(btn_row)

            view.add_widget(box)
            view.open()

        except Exception as e:
            log(f"[ERROR] import_data error: {e}")
            self._show_error('خطا در ورودی گرفتن')

    def show_about(self, *args):
        info = APP_INFO
        lines = [
            f"{info['app_name']}  —  نسخه {info['version']}",
            '',
            f"سازنده: {info['developer']}",
            f"ایمیل: {info['email']}",
            f"بله: {info.get('bale', '@your_id')}",
            '',
            info['note'],
        ]
        text = '\n'.join(lines)

        box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(14))
        box.add_widget(PersianLabel(
            text=text,
            font_size='14sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=1,
        ))
        close_btn = PersianButton(
            text=self._('close'),
            background_color=get_color_from_hex('#5C6BC0'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(42),
            font_size='14sp',
        )
        box.add_widget(close_btn)

        popup = Popup(
            title=reshape_persian(self._('about_title')),
            content=box,
            size_hint=(0.88, 0.55),
            auto_dismiss=True,
            title_font='PersianFont',
            title_size='16sp',
            title_color=(1, 1, 1, 1),
            background='',
            background_color=self.theme['popup_bg'],
            separator_color=get_color_from_hex('#5C6BC0'),
            separator_height=dp(2),
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _open_end_date_picker(self, end_date_btn):
        """انتخاب تاریخ پایان تکرار — با امکان انتخاب روز/ماه/سال"""
        try:
            current = getattr(end_date_btn, 'selected_value', None)
            if not current or not is_valid_jalali_date(str(current)):
                # پیش‌فرض: دو سال بعد (مناسب برای اقساط)
                try:
                    ny, nm, nd, _, _ = now_jalali_tuple()
                    current = f"{ny + 2:04d}/{nm:02d}/{min(nd, 28):02d}"
                except Exception:
                    current = get_default_date()

            box = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))

            def calendar_callback(date_str):
                end_date_btn.selected_value = date_str
                end_date_btn.set_text(date_str)

            calendar = JalaliCalendar(
                selected_date=current,
                callback=calendar_callback,
                size_hint_y=1,
            )
            box.add_widget(calendar)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))

            no_end_b = PersianButton(
                text=self._('no_end'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
                font_size='13sp',
            )
            cancel_b = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#546E7A'),
                color=(1, 1, 1, 1),
                font_size='13sp',
            )
            ok_b = PersianButton(
                text=self._('ok'),
                background_color=get_color_from_hex('#FF7043'),
                color=(1, 1, 1, 1),
                font_size='13sp',
            )
            btn_row.add_widget(no_end_b)
            btn_row.add_widget(cancel_b)
            btn_row.add_widget(ok_b)
            box.add_widget(btn_row)

            picker = Popup(
                title=reshape_persian('تاریخ پایان تکرار'),
                content=box,
                size_hint=(0.92, 0.82),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='16sp',
                title_color=(1, 1, 1, 1),
                background='',
                background_color=get_color_from_hex('#0D7377'),
                separator_color=get_color_from_hex('#FF7043'),
                separator_height=dp(3),
            )

            def on_no_end(_inst):
                end_date_btn.selected_value = None
                end_date_btn.set_text('تاریخ پایان')
                picker.dismiss()

            def on_ok(_inst):
                selected = getattr(end_date_btn, 'selected_value', None)
                if not selected:
                    # اگر هنوز انتخاب نشده، تاریخ فعلی تقویم را بگیر
                    selected = f"{calendar.current_year:04d}/{calendar.current_month:02d}/01"
                if selected and not is_valid_jalali_date(selected):
                    self._show_error(self._('invalid_date'))
                    return
                end_date_btn.selected_value = selected
                end_date_btn.set_text(selected)
                picker.dismiss()

            no_end_b.bind(on_press=on_no_end)
            cancel_b.bind(on_press=picker.dismiss)
            ok_b.bind(on_press=on_ok)
            picker.open()
        except Exception as e:
            log(f"[ERROR] _open_end_date_picker error: {e}")

    def _open_date_picker(self, date_btn):
        try:
            current_date = getattr(date_btn, 'selected_value', get_default_date())
            parts = current_date.replace('-', '/').split('/')
            default_year = int(parts[0]) if len(parts) == 3 else int(get_default_date().split('/')[0])
            default_month = int(parts[1]) if len(parts) == 3 else int(get_default_date().split('/')[1])
            default_day = int(parts[2]) if len(parts) == 3 else int(get_default_date().split('/')[2])

            box = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))

            def calendar_callback(date_str):
                date_btn.selected_value = date_str
                date_btn.set_text(date_str)

            calendar = JalaliCalendar(
                selected_date=f"{default_year:04d}/{default_month:02d}/{default_day:02d}",
                callback=calendar_callback,
                size_hint_y=1,
            )
            box.add_widget(calendar)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(10))
            cancel_b = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#546E7A'),
                color=(1, 1, 1, 1),
            )
            ok_b = PersianButton(
                text=self._('ok'),
                background_color=get_color_from_hex('#FF7043'),
                color=(1, 1, 1, 1),
            )
            btn_row.add_widget(cancel_b)
            btn_row.add_widget(ok_b)
            box.add_widget(btn_row)

            picker = Popup(
                title=reshape_persian(self._('select_date')),
                content=box,
                size_hint=(0.92, 0.82),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='17sp',
                title_color=(1, 1, 1, 1),
                background='',
                background_color=get_color_from_hex('#0D7377'),  # سبز هماهنگ با تقویم
                separator_color=get_color_from_hex('#FF7043'),
                separator_height=dp(3),
            )

            def on_ok(_inst):
                try:
                    selected = getattr(date_btn, 'selected_value', None)
                    if not selected:
                        selected = f"{calendar.current_year:04d}/{calendar.current_month:02d}/01"
                    if not is_valid_jalali_date(selected):
                        self._show_error(self._('invalid_date'))
                        return
                    date_btn.selected_value = selected
                    date_btn.set_text(selected)
                    picker.dismiss()
                except Exception as e:
                    log(f"[ERROR] date picker on_ok error: {e}")

            def on_cancel(_inst):
                picker.dismiss()

            cancel_b.bind(on_press=on_cancel)
            ok_b.bind(on_press=on_ok)
            picker.open()

        except Exception as e:
            log(f"[ERROR] _open_date_picker error: {e}")

    def _open_time_picker(self, time_btn):
        try:
            current_time = getattr(time_btn, 'selected_value', get_default_time())
            parts = str(current_time).split(':')
            default_hour = int(parts[0]) if len(parts) >= 1 else int(get_default_time().split(':')[0])
            default_minute = int(parts[1]) if len(parts) >= 2 else int(get_default_time().split(':')[1])
            initial_time = f"{default_hour:02d}:{default_minute:02d}"

            def time_callback(time_str):
                if time_str:
                    time_btn.selected_value = time_str
                    time_btn.set_text(time_str)
                picker.dismiss()

            time_picker = TimePickerWidget(
                initial_time=initial_time,
                callback=time_callback,
            )

            picker = Popup(
                title='',
                content=time_picker,
                size_hint=(0.88, 0.72),
                auto_dismiss=False,
                background='',
                background_color=(1, 1, 1, 1),
                separator_height=0,
            )
            picker.open()

        except Exception as e:
            log(f"[ERROR] _open_time_picker error: {e}")


    def _open_category_picker(self, cat_btn):
        """انتخاب دسته‌بندی با نمایش صحیح فارسی"""
        try:
            options = self.categories.get_selectable()
            if not options:
                options = ['عمومی']
            current = getattr(cat_btn, 'selected_value', None) or 'عمومی'

            box = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(12))
            box.add_widget(PersianLabel(
                text='دسته را انتخاب کنید',
                font_size='14sp',
                color=(0.9, 0.9, 0.95, 1),
                size_hint_y=None,
                height=dp(28),
            ))

            scroll = ScrollView(do_scroll_x=False, size_hint_y=1)
            list_box = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
            list_box.bind(minimum_height=list_box.setter('height'))

            picker = Popup(
                title=reshape_persian('دسته‌بندی'),
                content=box,
                size_hint=(0.8, 0.6),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='16sp',
                title_color=(1, 1, 1, 1),
                background='',
                background_color=self.theme['popup_bg'],
                separator_color=get_color_from_hex('#00838F'),
                separator_height=dp(2),
            )

            for cat in options:
                is_current = (cat == current)
                btn = PersianButton(
                    text=cat + ('  ✓' if is_current else ''),
                    background_color=get_color_from_hex('#00838F' if is_current else '#455A64'),
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=dp(42),
                    font_size='14sp',
                    bold=is_current,
                )

                def make_handler(c):
                    def handler(_inst):
                        cat_btn.selected_value = c
                        cat_btn.set_text(c)
                        picker.dismiss()
                    return handler

                btn.bind(on_press=make_handler(cat))
                list_box.add_widget(btn)

            scroll.add_widget(list_box)
            box.add_widget(scroll)

            cancel_b = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(38),
                font_size='13sp',
            )
            cancel_b.bind(on_press=picker.dismiss)
            box.add_widget(cancel_b)
            picker.open()
        except Exception as e:
            log(f"[ERROR] _open_category_picker error: {e}")

    def _open_repeat_picker(self, repeat_btn):
        try:
            options = [
                ('none', self._('repeat_none')),
                ('daily', self._('repeat_daily')),
                ('weekly', self._('repeat_weekly')),
                ('monthly', self._('repeat_monthly')),
            ]
            current = getattr(repeat_btn, 'selected_value', 'none')

            box = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))
            box.add_widget(PersianLabel(
                text='نوع تکرار را انتخاب کنید',
                font_size='14sp',
                color=(0.9, 0.9, 0.95, 1),
                size_hint_y=None,
                height=dp(28),
            ))

            picker = Popup(
                title=reshape_persian('تکرار یادآوری'),
                content=box,
                size_hint=(0.8, 0.55),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='16sp',
                title_color=(1, 1, 1, 1),
                background='',
                background_color=self.theme['popup_bg'],
                separator_color=get_color_from_hex('#00838F'),
                separator_height=dp(2),
            )

            for key, label in options:
                is_current = (key == current)
                btn = PersianButton(
                    text=label + ('  *' if is_current else ''),
                    background_color=get_color_from_hex('#00695C' if is_current else '#455A64'),
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=dp(42),
                    font_size='14sp',
                    bold=is_current,
                )

                def make_handler(k, lab):
                    def handler(_inst):
                        repeat_btn.selected_value = k
                        repeat_btn.set_text(lab)
                        picker.dismiss()
                    return handler

                btn.bind(on_press=make_handler(key, label))
                box.add_widget(btn)

            cancel_b = PersianButton(
                text=self._('cancel'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(38),
                font_size='13sp',
            )
            cancel_b.bind(on_press=picker.dismiss)
            box.add_widget(cancel_b)
            picker.open()
        except Exception as e:
            log(f"[ERROR] _open_repeat_picker error: {e}")

    def show_add_reminder(self, instance):
        try:
            self._show_reminder_form(
                title='', description='', date=get_default_date(), time=get_default_time(),
                repeat_type='none', repeat_end_date=None, notify_before=15,
                category='عمومی', is_edit=False, reminder_id=None
            )
        except Exception as e:
            log(f"[ERROR] show_add_reminder error: {e}")

    def show_edit_reminder(self, reminder_id):
        try:
            reminder = self.db.get_reminder_by_id(reminder_id)
            if not reminder:
                self._show_error(self._('reminder_not_found'))
                return
            self._show_reminder_form(
                title=reminder[1],
                description=reminder[2] or '',
                date=reminder[3],
                time=reminder[4],
                notify_before=reminder[7] if len(reminder) > 7 else 15,
                repeat_type=reminder[8] if len(reminder) > 8 else 'none',
                repeat_end_date=reminder[9] if len(reminder) > 9 else None,
                category=reminder[12] if len(reminder) > 12 else 'عمومی',
                is_edit=True,
                reminder_id=reminder_id
            )
        except Exception as e:
            log(f"[ERROR] show_edit_reminder error: {e}")
            self._show_error('خطا در ویرایش یادآوری')

    def _show_reminder_form(self, title='', description='', date='', time='',
                            repeat_type='none', repeat_end_date=None, notify_before=15,
                            category='عمومی', is_edit=False, reminder_id=None):
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))
            scroll = ScrollView(do_scroll_x=False)
            form_content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
            form_content.bind(minimum_height=form_content.setter('height'))

            title_input = PersianTextInput(
                hint_text=self._('title'), multiline=False,
                size_hint_y=None, height=dp(42), font_size='15sp',
            )
            title_input.apply_theme(self.theme)
            if title:
                title_input.value = title
            form_content.add_widget(title_input)

            desc_input = PersianTextInput(
                hint_text=self._('description'), multiline=True,
                size_hint_y=None, height=dp(60), font_size='14sp',
            )
            desc_input.apply_theme(self.theme)
            if description:
                desc_input.value = description
            form_content.add_widget(desc_input)

            # انتخاب دسته‌بندی (با دکمه برای نمایش صحیح فارسی)
            selectable_cats = self.categories.get_selectable()
            if not selectable_cats:
                selectable_cats = ['عمومی']
            current_cat = category if category in selectable_cats else (selectable_cats[0] if selectable_cats else 'عمومی')

            cat_row = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(40))
            cat_row.add_widget(
                PersianLabel(text='دسته‌بندی:', font_size='13sp',
                             color=(0.85, 0.85, 0.9, 1), size_hint_x=0.28)
            )
            cat_btn = PersianButton(
                text=current_cat,
                background_color=get_color_from_hex('#00838F'),
                color=(1, 1, 1, 1),
                font_size='13sp',
                size_hint_x=0.72,
            )
            cat_btn.selected_value = current_cat
            cat_btn.bind(on_press=lambda inst: self._open_category_picker(cat_btn))
            cat_row.add_widget(cat_btn)
            form_content.add_widget(cat_row)

            datetime_row = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(42))
            default_date = date if date else get_default_date()
            default_time = time if time else get_default_time()

            date_btn = PersianButton(
                text=default_date, background_color=get_color_from_hex('#1565C0'),
                color=(1, 1, 1, 1), font_size='13sp', size_hint_x=0.5,
            )
            date_btn.selected_value = default_date
            date_btn.bind(on_press=lambda inst: self._open_date_picker(date_btn))

            time_btn = PersianButton(
                text=default_time, background_color=get_color_from_hex('#6A1B9A'),
                color=(1, 1, 1, 1), font_size='13sp', size_hint_x=0.5,
            )
            time_btn.selected_value = default_time
            time_btn.bind(on_press=lambda inst: self._open_time_picker(time_btn))

            datetime_row.add_widget(date_btn)
            datetime_row.add_widget(time_btn)
            form_content.add_widget(datetime_row)

            repeat_labels = {
                'none': self._('repeat_none'),
                'daily': self._('repeat_daily'),
                'weekly': self._('repeat_weekly'),
                'monthly': self._('repeat_monthly'),
            }
            repeat_display = repeat_labels.get(repeat_type, self._('repeat_none'))
            repeat_btn = PersianButton(
                text=repeat_display,
                background_color=get_color_from_hex('#37474F'),
                color=(1, 1, 1, 1),
                font_size='13sp',
                size_hint_y=None,
                height=dp(38),
            )
            repeat_btn.selected_value = repeat_type
            repeat_btn.bind(on_press=lambda inst: self._open_repeat_picker(repeat_btn))
            form_content.add_widget(repeat_btn)

            # تاریخ پایان تکرار: فقط دو دکمه — انتخاب تاریخ | بدون پایان
            end_date_row = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(40))
            end_date_row.add_widget(
                PersianLabel(text=self._('end_date'), font_size='13sp', color=(0.8, 0.8, 0.9, 1), size_hint_x=0.20)
            )
            # دکمه انتخاب تاریخ پایان (اگر خالی باشد متن «تاریخ پایان» نشان می‌دهد)
            if repeat_end_date:
                end_date_text = repeat_end_date
            else:
                end_date_text = 'تاریخ پایان'
            end_date_btn = PersianButton(
                text=end_date_text,
                background_color=get_color_from_hex('#00838F'),
                color=(1, 1, 1, 1),
                font_size='12sp',
                size_hint_x=0.48,
            )
            end_date_btn.selected_value = repeat_end_date  # None یعنی بدون پایان
            end_date_btn.bind(on_press=lambda inst: self._open_end_date_picker(end_date_btn))
            end_date_row.add_widget(end_date_btn)

            clear_end_btn = PersianButton(
                text=self._('no_end'),
                background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1),
                font_size='12sp',
                size_hint_x=0.32,
            )
            def clear_end(_inst):
                end_date_btn.selected_value = None
                end_date_btn.set_text('تاریخ پایان')
            clear_end_btn.bind(on_press=clear_end)
            end_date_row.add_widget(clear_end_btn)
            form_content.add_widget(end_date_row)

            form_content.add_widget(Widget(size_hint_y=None, height=dp(4)))

            btn_row = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(42))
            cancel_btn = PersianButton(
                text=self._('cancel'), background_color=get_color_from_hex('#78909C'),
                color=(1, 1, 1, 1), font_size='14sp',
            )
            save_text = self._('update') if is_edit else self._('save')
            save_btn = PersianButton(
                text=save_text, background_color=get_color_from_hex('#2E7D32'),
                color=(1, 1, 1, 1), font_size='14sp',
            )
            btn_row.add_widget(cancel_btn)
            btn_row.add_widget(save_btn)
            form_content.add_widget(btn_row)

            scroll.add_widget(form_content)
            content.add_widget(scroll)

            title_text = self._('edit_reminder') if is_edit else self._('add_reminder')
            popup = Popup(
                title=reshape_persian(title_text),
                content=content,
                size_hint=(0.92, 0.88),
                auto_dismiss=False,
                title_font='PersianFont',
                title_size='16sp',
                title_color=(1, 1, 1, 1),
                separator_color=get_color_from_hex('#2E7D32'),
                separator_height=dp(2),
                background='',
                background_color=self.theme['popup_bg'],
            )

            def save_reminder(_inst):
                try:
                    title_val = title_input.value
                    if not title_val:
                        self._show_error(self._('enter_title'))
                        return

                    date_val = getattr(date_btn, 'selected_value', default_date)
                    time_val = getattr(time_btn, 'selected_value', default_time)
                    if not is_valid_jalali_date(date_val):
                        self._show_error(self._('invalid_date'))
                        return
                    if not is_valid_time(time_val):
                        self._show_error(self._('invalid_time'))
                        return

                    desc_val = desc_input.value
                    notify_val = 0  # اعلان قبل حذف شده؛ در زمان مقرر هشدار می‌دهد

                    cat_val = getattr(cat_btn, 'selected_value', None) or 'عمومی'

                    repeat_val = getattr(repeat_btn, 'selected_value', 'none') or 'none'
                    if repeat_val not in ('none', 'daily', 'weekly', 'monthly'):
                        repeat_val = 'none'

                    end_date = getattr(end_date_btn, 'selected_value', None)
                    if end_date == self._('no_end') or not end_date:
                        end_date = None
                    elif end_date and not is_valid_jalali_date(end_date):
                        self._show_error('تاریخ پایان نامعتبر است')
                        return

                    if is_edit and reminder_id:
                        self._notified_ids.discard(reminder_id)
                        self._alerting_ids.discard(reminder_id)
                        if reminder_id in self._active_alerts:
                            try:
                                self._active_alerts[reminder_id].dismiss()
                            except Exception:
                                pass
                            del self._active_alerts[reminder_id]
                        result = self.db.update_reminder(
                            reminder_id=reminder_id, title=title_val, description=desc_val,
                            date=date_val, time=time_val, repeat_type=repeat_val,
                            repeat_end_date=end_date, notify_before=notify_val,
                            category=cat_val,
                        )
                        if not result:
                            self._show_error('خطا در ویرایش یادآوری')
                            return
                        success_msg = self._('reminder_updated')
                    else:
                        result = self.db.add_reminder(
                            title=title_val, description=desc_val, date=date_val, time=time_val,
                            notify_before=notify_val, repeat_type=repeat_val, repeat_end_date=end_date,
                            category=cat_val,
                        )
                        if not result:
                            self._show_error('خطا در افزودن یادآوری')
                            return
                        success_msg = self._('reminder_added')

                    popup.dismiss()
                    self.load_reminders()
                    self._show_success(success_msg)
                except Exception as e:
                    log(f"[ERROR] save_reminder error: {e}")
                    self._show_error('خطا در ذخیره یادآوری')

            cancel_btn.bind(on_press=popup.dismiss)
            save_btn.bind(on_press=save_reminder)
            popup.open()
        except Exception as e:
            log(f"[ERROR] _show_reminder_form error: {e}")
            self._show_error('خطا در نمایش فرم')


if __name__ == '__main__':
    try:
        ReminderApp().run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
