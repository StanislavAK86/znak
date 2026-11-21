"""
Middleware для автоматического трекинга посещений сайта.
"""
import time
import threading
import re
from django.utils.deprecation import MiddlewareMixin


# Паттерны для определения браузера и ОС
BROWSER_PATTERNS = [
    ('Edge', r'Edg(?:e|A|iOS)?/([\d.]+)'),
    ('Chrome', r'Chrome/([\d.]+)'),
    ('Firefox', r'Firefox/([\d.]+)'),
    ('Safari', r'Version/([\d.]+).*Safari'),
    ('Opera', r'OPR/([\d.]+)'),
    ('Yandex', r'YaBrowser/([\d.]+)'),
    ('IE', r'MSIE ([\d.]+)'),
]

OS_PATTERNS = [
    ('Windows', r'Windows NT ([\d.]+)'),
    ('macOS', r'Mac OS X ([\d_]+)'),
    ('Linux', r'Linux'),
    ('Android', r'Android ([\d.]+)'),
    ('iOS', r'(?:iPhone|iPad).*OS ([\d_]+)'),
]

MOBILE_PATTERN = re.compile(
    r'Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini',
    re.IGNORECASE
)


def parse_user_agent(user_agent):
    """Парсит User-Agent и возвращает (browser, os, is_mobile)."""
    if not user_agent:
        return '', '', False

    browser = ''
    os_name = ''

    for name, pattern in BROWSER_PATTERNS:
        match = re.search(pattern, user_agent)
        if match:
            version = match.group(1).split('.')[0] if match.groups() else ''
            browser = f"{name} {version}".strip()
            break

    for name, pattern in OS_PATTERNS:
        match = re.search(pattern, user_agent)
        if match:
            os_name = name
            break

    is_mobile = bool(MOBILE_PATTERN.search(user_agent))
    return browser, os_name, is_mobile


def get_client_ip(request):
    """Получает реальный IP клиента (учитывает прокси)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def save_visit_async(visit_data):
    """Сохраняет посещение в отдельном потоке."""
    try:
        from .models import SiteVisit
        SiteVisit.objects.create(**visit_data)
    except Exception as e:
        print(f"[SiteVisit Middleware] Ошибка сохранения: {e}")


class SiteVisitMiddleware(MiddlewareMixin):
    """Middleware для трекинга посещений."""

    EXCLUDED_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/robots.txt',
        '/sitemap.xml',
    ]

    EXCLUDED_EXTENSIONS = [
        '.css', '.js', '.map', '.png', '.jpg', '.jpeg',
        '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf',
    ]

    BOT_PATTERNS = [
        'bot', 'crawler', 'spider', 'yandex', 'google',
        'bing', 'baidu', 'duckduck', 'facebookexternalhit',
        'semrush', 'ahrefs', 'mj12bot', 'dotbot',
    ]

    def should_track(self, request):
        if request.method not in ('GET', 'POST'):
            return False

        path = request.path

        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return False

        for ext in self.EXCLUDED_EXTENSIONS:
            if path.endswith(ext):
                return False

        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        for bot in self.BOT_PATTERNS:
            if bot in user_agent:
                return False

        if path.startswith('/api/visits'):
            return False
        return True

    def process_request(self, request):
        """Запоминаем время начала запроса."""
        request._visit_start_time = time.time()
        return None

    def process_response(self, request, response):
        """Сохраняем данные о посещении после обработки запроса."""
        if not self.should_track(request):
            return response

        try:
            response_time_ms = None
            if hasattr(request, '_visit_start_time'):
                response_time_ms = int((time.time() - request._visit_start_time) * 1000)

            user_agent = request.META.get('HTTP_USER_AGENT', '')
            browser, os_name, is_mobile = parse_user_agent(user_agent)

            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user

            visit_data = {
                'ip_address': get_client_ip(request),
                'user': user,
                'path': request.path[:500],
                'method': request.method,
                'user_agent': user_agent[:1000],
                'referer': request.META.get('HTTP_REFERER', '')[:500],
                'session_key': request.session.session_key or '',
                'language': request.META.get('HTTP_ACCEPT_LANGUAGE', '')[:20],
                'is_mobile': is_mobile,
                'browser': browser[:100],
                'os': os_name[:100],
                'response_time_ms': response_time_ms,
                'status_code': response.status_code,
            }

            thread = threading.Thread(target=save_visit_async, args=(visit_data,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"[SiteVisit Middleware] Ошибка: {e}")

        return response