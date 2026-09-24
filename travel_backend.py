import argparse
import json
import os
import ssl
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ROOT = os.path.dirname(__file__)
CERT_DIR = os.path.join(ROOT, "certs")
CERT_FILE = os.path.join(CERT_DIR, "server.pem")
KEY_FILE = os.path.join(CERT_DIR, "server.key")
CONTACTS_PATH = os.path.join(ROOT, "data", "contacts.json")
BOOKINGS_PATH = os.path.join(ROOT, "data", "bookings.json")

TOURS = [
    {
        "id": "maldives",
        "name": "Мальдіви",
        "country": "Мальдіви",
        "summary": "Райські пляжі, прозоре море та ексклюзивний відпочинок.",
        "description": "Незабутній тур для тих, хто хоче відпочити у приватному бунгало на воді, зануритися в кришталево чисту воду та насолодитися вишуканою кухнею.",
        "highlights": ["Приватний трансфер", "Сніданки включені", "Спа-пакет", "Дайвінг-екскурсія"],
        "duration": "7 днів",
        "price": "від 89 000 ₴",
        "category": "sea",
        "categoryTitle": "Море",
        "image": "/images/maldives.jpg"
    },
    {
        "id": "paris",
        "name": "Париж",
        "country": "Франція",
        "summary": "Класичний романтичний відпочинок у серці Європи.",
        "description": "Тур по Парижу з відвіданням Ейфелевої вежі, Лувру, затишних кав'ярень і нічних прогулянок уздовж Сени.",
        "highlights": ["Ейфелева вежа", "Лувр", "Круїз по Сені", "Готель 4*"],
        "duration": "5 днів",
        "price": "від 54 000 ₴",
        "category": "city",
        "categoryTitle": "Місто",
        "image": "/images/paris.jpg"
    },
    {
        "id": "tokyo",
        "name": "Токіо",
        "country": "Японія",
        "summary": "Сучасність, технології, гастрономія і неймовірний ритм життя.",
        "description": "Тур по Токіо з відвіданням старих кварталів, сучасних районів, храмів і найкращих ресторанів японської кухні.",
        "highlights": ["Шібуя", "Асакуса", "Суші-тур", "Парк Уено"],
        "duration": "8 днів",
        "price": "від 71 000 ₴",
        "category": "city",
        "categoryTitle": "Місто",
        "image": "/images/tokyo.jpeg"
    },
    {
        "id": "bali",
        "name": "Балі",
        "country": "Індонезія",
        "summary": "Пляжі, спа та закохані вітрини тайських храмів.",
        "description": "Комбінація відпочинку, культурних екскурсій і унікальної природи: рисові тераси, храми, водоспади й живописні пляжі.",
        "highlights": ["Пляж Улувату", "Тераси Джатілуру", "Спа-тур", "Супер-вайфай"],
        "duration": "9 днів",
        "price": "від 63 000 ₴",
        "category": "sea",
        "categoryTitle": "Море",
        "image": "/images/bali.jpg"
    },
    {
        "id": "iceland",
        "name": "Ісландія",
        "country": "Ісландія",
        "summary": "Льодовики, фіорди та північне сяйво в одному турі.",
        "description": "Вражаючий маршрут для любителів природи: водоспади, чорний пісок, гейзери та зоряне небо над льодовиками.",
        "highlights": ["Голуба лагуна", "Рейк'явік", "Фіорди", "Північне сяйво"],
        "duration": "10 днів",
        "price": "від 98 000 ₴",
        "category": "mountain",
        "categoryTitle": "Гори",
        "image": "/images/iceland.jpg"
    },
    {
        "id": "newyork",
        "name": "Нью-Йорк",
        "country": "США",
        "summary": "Класичний мегаполіс з небоскребами, музеями та ресторанами.",
        "description": "Тур для тих, хто хоче відчути справжній американський ритм: Центральний парк, Статуя Свободи, Бруклін і модні квартали.",
        "highlights": ["Музей модерного мистецтва", "Статуя Свободи", "Центральний парк", "Нічна прогулянка"],
        "duration": "6 днів",
        "price": "від 68 000 ₴",
        "category": "city",
        "categoryTitle": "Місто",
        "image": "/images/newyork.jpg"
    },
    {
        "id": "capetown",
        "name": "Кейптаун",
        "country": "ПАР",
        "summary": "Пляжі, гірські панорами й унікальна африканська атмосфера.",
        "description": "Комбінований тур із оглядом міста, підйомами на гори, пляжним відпочинком та смачною місцевою кухнею.",
        "highlights": ["Пляж Клондейк", "Гора Кабоун", "Віндсёрфінг", "Марина"],
        "duration": "8 днів",
        "price": "від 74 000 ₴",
        "category": "sea",
        "categoryTitle": "Море",
        "image": "/images/capetown.jpg"
    },
    {
        "id": "venice",
        "name": "Венеція",
        "country": "Італія",
        "summary": "Романтика каналів, гондоли та історичні площі.",
        "description": "Тур по Венеції з прогулянками по Гранд-каналу, відвідинами Сан-Марко і секретними двориками.",
        "highlights": ["Гранд-канал", "Площа Сан-Марко", "Гондольна прогулянка", "Франческанські музеї"],
        "duration": "5 днів",
        "price": "від 58 000 ₴",
        "category": "city",
        "categoryTitle": "Місто",
        "image": "/images/hero.jpg"
    },
    {
        "id": "hawaii",
        "name": "Гаваї",
        "country": "США",
        "summary": "Пляжі, вулкани й тропічний релакс на островах.",
        "description": "Тур по Гаваях з відпочинком на пляжі, прогулянками по вулканічним паркам і серфінгом.",
        "highlights": ["Пляж Вайкікі", "Національний парк Гавайї", "Серфінг", "Полінезійська культура"],
        "duration": "7 днів",
        "price": "від 82 000 ₴",
        "category": "sea",
        "categoryTitle": "Море",
        "image": "/images/bali.jpg"
    },
    {
        "id": "egypt",
        "name": "Єгипет",
        "country": "Єгипет",
        "summary": "Історія древніх пірамід та круїз по Нілу.",
        "description": "Тур до Каїру з відвідуванням пірамід, музеїв та круїзом по Нілу на розкішній яхті.",
        "highlights": ["Піраміди Гізи", "Музей Єгипту", "Круїз по Нілу", "Каїрський базар"],
        "duration": "6 днів",
        "price": "від 66 000 ₴",
        "category": "mountain",
        "categoryTitle": "Гори",
        "image": "/images/capetown.jpg"
    }
]

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon"
}


def ensure_data_files():
    os.makedirs(os.path.dirname(CONTACTS_PATH), exist_ok=True)
    if not os.path.exists(CONTACTS_PATH):
        with open(CONTACTS_PATH, "w", encoding="utf-8") as handle:
            json.dump([], handle, ensure_ascii=False, indent=2)
    if not os.path.exists(BOOKINGS_PATH):
        with open(BOOKINGS_PATH, "w", encoding="utf-8") as handle:
            json.dump([], handle, ensure_ascii=False, indent=2)


def ensure_ssl_certificates(cert_path=CERT_FILE, key_path=KEY_FILE):
    os.makedirs(os.path.dirname(cert_path), exist_ok=True)
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"localhost")]))
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"localhost")]))
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"127.0.0.1")
            ]),
            critical=False
        )
        .sign(key, hashes.SHA256(), default_backend())
    )

    with open(key_path, "wb") as handle:
        handle.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(cert_path, "wb") as handle:
        handle.write(cert.public_bytes(serialization.Encoding.PEM))


def build_ssl_context(certfile=CERT_FILE, keyfile=KEY_FILE):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return context


class TravelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/tours":
            self._send_json(200, TOURS)
            return

        if parsed.path.startswith("/api/tours/"):
            tour_id = parsed.path[len("/api/tours/"):].strip("/")
            tour = next((item for item in TOURS if item["id"] == tour_id), None)
            if tour is None:
                self._send_json(404, {"success": False, "message": "Тур не знайдено"})
                return
            self._send_json(200, tour)
            return

        if parsed.path == "/api/contacts":
            self._send_json(200, self._read_json(CONTACTS_PATH))
            return

        if parsed.path == "/api/bookings":
            self._send_json(200, self._read_json(BOOKINGS_PATH))
            return

        if parsed.path == "/api/health":
            self._send_json(200, {"status": "ok"})
            return

        if parsed.path.startswith("/tour/"):
            tour_id = parsed.path[len("/tour/"):].strip("/")
            tour = next((item for item in TOURS if item["id"] == tour_id), None)
            if tour is None:
                self._send_html(self._render_not_found_page("Тур не знайдено"))
                return
            self._send_html(self._render_tour_page(tour))
            return

        file_path = self._resolve_path(parsed.path)
        self._serve_file(file_path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/contacts":
            payload = self._read_payload_json()
            if payload is None:
                self._send_json(400, {"success": False, "message": "Некоректний запит"})
                return

            entry = {
                "id": str(len(self._read_json(CONTACTS_PATH)) + 1),
                "name": payload.get("name", ""),
                "email": payload.get("email", ""),
                "message": payload.get("message", ""),
                "createdAt": self._now()
            }
            contacts = self._read_json(CONTACTS_PATH)
            contacts.append(entry)
            self._write_json(CONTACTS_PATH, contacts)
            self._send_json(200, {"success": True, "message": "Повідомлення успішно надіслано!"})
            return

        if parsed.path == "/api/bookings":
            payload = self._read_payload_json()
            if payload is None:
                self._send_json(400, {"success": False, "message": "Некоректний запит"})
                return

            errors = self._validate_booking_payload(payload)
            if errors:
                self._send_json(400, {"success": False, "message": errors[0]})
                return

            booking = {
                "id": str(len(self._read_json(BOOKINGS_PATH)) + 1),
                "tourId": payload.get("tourId", ""),
                "tourName": payload.get("tourName", ""),
                "name": payload.get("name", ""),
                "email": payload.get("email", ""),
                "date": payload.get("date", ""),
                "guests": payload.get("guests", ""),
                "message": payload.get("message", ""),
                "createdAt": self._now()
            }
            bookings = self._read_json(BOOKINGS_PATH)
            bookings.append(booking)
            self._write_json(BOOKINGS_PATH, bookings)
            self._send_json(200, {"success": True, "message": "Бронювання успішно створено!"})
            return

        self._send_json(404, {"success": False, "message": "Not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _read_payload_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return None
        body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def _validate_booking_payload(self, payload):
        if not isinstance(payload, dict):
            return ["Некоректні дані бронювання"]

        required_fields = [
            ("tourId", "Оберіть тур"),
            ("tourName", "Невідомий тур"),
            ("name", "Вкажіть ім'я"),
            ("email", "Вкажіть email"),
            ("date", "Вкажіть дату"),
            ("guests", "Вкажіть кількість гостей")
        ]

        for key, message in required_fields:
            if not payload.get(key):
                return [message]

        if not any(item["id"] == payload["tourId"] for item in TOURS):
            return ["Тур не знайдено"]

        email = payload.get("email", "")
        if "@" not in email or "." not in email:
            return ["Вкажіть коректний email"]

        return []

    def _read_json(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return []

    def _write_json(self, file_path, payload):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _resolve_path(self, path):
        if path == "/":
            return os.path.join(ROOT, "index.html")
        safe_path = path.lstrip("/")
        if safe_path.endswith("/"):
            safe_path = safe_path.rstrip("/")
        full_path = os.path.abspath(os.path.join(ROOT, safe_path))
        if not full_path.startswith(ROOT):
            full_path = os.path.join(ROOT, "index.html")
        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, "index.html")
        return full_path

    def _serve_file(self, file_path):
        if not os.path.exists(file_path):
            file_path = os.path.join(ROOT, "index.html")

        extension = os.path.splitext(file_path)[1].lower()
        content_type = MIME_TYPES.get(extension, "application/octet-stream")
        with open(file_path, "rb") as handle:
            content = handle.read()

        self._send_headers(200, content_type, len(content))
        self.wfile.write(content)

    def _send_headers(self, status_code, content_type, content_length=None):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if content_length is not None:
            self.send_header("Content-Length", str(content_length))
        self.end_headers()

    def _send_html(self, html):
        body = html.encode("utf-8")
        self._send_headers(200, "text/html; charset=utf-8", len(body))
        self.wfile.write(body)

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_headers(status_code, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

    def _now(self):
        return datetime.utcnow().isoformat() + "Z"

    def _render_tour_page(self, tour):
        highlights = "".join(f"<li>{item}</li>" for item in tour["highlights"])
        return """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%s — TravelWay</title>
  <link rel="stylesheet" href="/style.css">
  <style>
    .tour-detail { padding: 120px 10%% 80px; }
    .tour-header { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:18px; margin-bottom:28px; }
    .tour-header h1 { margin:0; font-size:clamp(2rem, 3vw, 3rem); }
    .tour-header a { display:inline-block; padding:12px 20px; border-radius:999px; background:#111827; color:white; text-decoration:none; font-weight:700; }
    .tour-grid { display:grid; grid-template-columns:1.15fr .85fr; gap:28px; }
    .tour-image { width:100%%; border-radius:24px; overflow:hidden; box-shadow:0 28px 70px rgba(15,23,42,0.1); }
    .tour-image img { width:100%%; height:auto; display:block; object-fit:cover; }
    .tour-sidebar { display:flex; flex-direction:column; gap:18px; }
    .tour-card { background:white; border-radius:24px; padding:24px; box-shadow:0 24px 60px rgba(15,23,42,0.08); }
    .tour-badge { display:inline-flex; align-items:center; gap:10px; padding:10px 14px; border-radius:999px; background:#dbeafe; color:#1d4ed8; font-weight:700; text-transform:uppercase; font-size:0.8rem; }
    .tour-meta { display:flex; gap:14px; flex-wrap:wrap; color:#475569; font-weight:600; margin:18px 0; }
    .tour-meta span { background:#f8fafc; padding:10px 14px; border-radius:16px; }
    .tour-card h2 { margin-top:0; }
    .tour-card ul { margin:0; padding-left:20px; }
    .tour-card li { margin-bottom:10px; line-height:1.8; }
    .tour-card form { display:grid; gap:14px; }
    .tour-card button { width:100%%; }
    .tour-info p { margin:18px 0 0; line-height:1.8; color:#334155; }
    @media (max-width: 900px) { .tour-grid { grid-template-columns:1fr; } .tour-header { flex-direction:column; align-items:flex-start; } }
  </style>
</head>
<body>
  <div class="tour-detail">
    <div class="tour-header">
      <div>
        <a class="btn secondary" href="/">← Назад</a>
      </div>
      <div class="tour-badge">%s</div>
    </div>
    <div class="tour-grid">
      <section class="tour-image">
        <img src="%s" alt="%s">
      </section>
      <aside class="tour-sidebar">
        <div class="tour-card">
          <h2>%s</h2>
          <p><strong>Країна:</strong> %s</p>
          <div class="tour-meta"><span>%s</span><span>%s</span></div>
          <p class="tour-info">%s</p>
          <h3>Що входить</h3>
          <ul>%s</ul>
        </div>
        <div class="tour-card">
          <h3>Бронювання</h3>
          <form id="bookingForm" onsubmit="return false;">
            <input id="bookingName" type="text" placeholder="Ваше ім'я" required>
            <input id="bookingEmail" type="email" placeholder="Email" required>
            <input id="bookingDate" type="date" required>
            <input id="bookingGuests" type="number" min="1" max="12" placeholder="Кількість гостей" required>
            <textarea id="bookingMessage" rows="4" placeholder="Додаткові побажання"></textarea>
            <button class="btn" type="submit">Забронювати тур</button>
            <p id="bookingStatus" class="status"></p>
          </form>
        </div>
      </aside>
    </div>
  </div>
  <script>
    const form = document.getElementById('bookingForm');
    const status = document.getElementById('bookingStatus');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      status.textContent = '';
      const payload = {
        tourId: '%s',
        tourName: '%s',
        name: document.getElementById('bookingName').value.trim(),
        email: document.getElementById('bookingEmail').value.trim(),
        date: document.getElementById('bookingDate').value,
        guests: document.getElementById('bookingGuests').value,
        message: document.getElementById('bookingMessage').value.trim()
      };

      try {
        const response = await fetch('/api/bookings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        status.textContent = result.message;
        status.className = 'status ' + (response.ok ? 'success' : 'error');
        if (response.ok) {
          form.reset();
        }
      } catch (error) {
        status.textContent = 'Помилка при відправці бронювання';
        status.className = 'status error';
      }
    });
  </script>
</body>
</html>""" % (
            tour['name'],
            tour['categoryTitle'],
            tour['image'],
            tour['name'],
            tour['name'],
            tour['country'],
            tour['duration'],
            tour['price'],
            tour['description'],
            highlights,
            tour['id'],
            tour['name']
        )

    def _render_not_found_page(self, message="Сторінку не знайдено"):
        return f"""<!DOCTYPE html>
<html lang=\"ru\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{message} — TravelWay</title>
  <link rel=\"stylesheet\" href=\"/style.css\">
  <style>
    .notfound-container {{ padding: 120px 10%; display: flex; justify-content: center; align-items: center; min-height: 80vh; }}
    .notfound-card {{ max-width: 760px; background: #fff; border-radius: 32px; padding: 42px; box-shadow: 0 28px 70px rgba(15,23,42,0.1); text-align: center; }}
    .notfound-card h1 {{ margin: 0 0 18px; font-size: clamp(2rem, 4vw, 3rem); }}
    .notfound-card p {{ margin: 0 0 24px; color: #475569; line-height: 1.9; font-size: 1.05rem; }}
    .notfound-card a {{ display: inline-flex; padding: 14px 24px; border-radius: 999px; background: #2563eb; color: white; text-decoration: none; font-weight: 700; }}
  </style>
</head>
<body>
  <div class=\"notfound-container\">
    <div class=\"notfound-card\">
      <h1>{message}</h1>
      <p>Схоже, такого туру не існує. Поверніться на головну сторінку та оберіть інший напрямок.</p>
      <a href=\"/\">Повернутися на головну</a>
    </div>
  </div>
</body>
</html>"""


def run_server(host="0.0.0.0", port=3000, ssl_context=None):
    ensure_data_files()
    server = ThreadingHTTPServer((host, port), TravelHandler)
    if ssl_context is not None:
        print(f"TravelWay backend is running on https://{host}:{port}")
        server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    else:
        print(f"TravelWay backend is running on http://{host}:{port}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="TravelWay web server")
    parser.add_argument("command", nargs="?", default="runserver", choices=["runserver", "start"], help="Start the server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--https", action="store_true", help="Run server over HTTPS")
    parser.add_argument("--https-port", type=int, default=3443, help="Port for HTTPS when --https is used")
    parser.add_argument("--certfile", default=CERT_FILE, help="Path to TLS certificate PEM file")
    parser.add_argument("--keyfile", default=KEY_FILE, help="Path to TLS private key PEM file")
    args = parser.parse_args()

    if args.https:
        ensure_ssl_certificates(args.certfile, args.keyfile)
        ssl_context = build_ssl_context(args.certfile, args.keyfile)
        run_server(args.host, args.https_port, ssl_context)
    else:
        run_server(args.host, args.port)


if __name__ == "__main__":
    main()
