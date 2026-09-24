const http = require("http");
const fs = require("fs");
const path = require("path");

const rootDir = __dirname;
const contactsPath = path.join(rootDir, "data", "contacts.json");
const bookingsPath = path.join(rootDir, "data", "bookings.json");

const tours = [
  {
    id: "maldives",
    name: "Мальдіви",
    country: "Мальдіви",
    summary: "Райські пляжі, прозоре море та ексклюзивний відпочинок.",
    description: "Незабутній тур для тих, хто хоче відпочити у приватному бунгало на воді, зануритися в кришталево чисту воду та насолодитися вишуканою кухнею.",
    highlights: ["Приватний трансфер", "Сніданки включені", "Спа-пакет", "Дайвінг-екскурсія"],
    duration: "7 днів",
    price: "від 89 000 ₴",
    category: "sea",
    categoryTitle: "Море",
    image: "/images/maldives.jpg"
  },
  {
    id: "paris",
    name: "Париж",
    country: "Франція",
    summary: "Класичний романтичний відпочинок у серці Європи.",
    description: "Тур по Парижу з відвіданням Ейфелевої вежі, Лувру, затишних кав'ярень і нічних прогулянок уздовж Сени.",
    highlights: ["Ейфелева вежа", "Лувр", "Круїз по Сені", "Готель 4*"],
    duration: "5 днів",
    price: "від 54 000 ₴",
    category: "city",
    categoryTitle: "Місто",
    image: "/images/paris.jpg"
  },
  {
    id: "tokyo",
    name: "Токіо",
    country: "Японія",
    summary: "Сучасність, технології, гастрономія і неймовірний ритм життя.",
    description: "Тур по Токіо з відвіданням старих кварталів, сучасних районів, храмів і найкращих ресторанів японської кухні.",
    highlights: ["Шібуя", "Асакуса", "Суші-тур", "Парк Уено"],
    duration: "8 днів",
    price: "від 71 000 ₴",
    category: "city",
    categoryTitle: "Місто",
    image: "/images/tokyo.jpeg"
  },
  {
    id: "bali",
    name: "Балі",
    country: "Індонезія",
    summary: "Пляжі, спа та закохані вітрини тайських храмів.",
    description: "Комбінація відпочинку, культурних екскурсій і унікальної природи: рисові тераси, храми, водоспади й живописні пляжі.",
    highlights: ["Пляж Улувату", "Тераси Джатілуру", "Спа-тур", "Супер-вайфай"],
    duration: "9 днів",
    price: "від 63 000 ₴",
    category: "sea",
    categoryTitle: "Море",
    image: "/images/bali.jpg"
  },
  {
    id: "iceland",
    name: "Ісландія",
    country: "Ісландія",
    summary: "Льодовики, фіорди та північне сяйво в одному турі.",
    description: "Вражаючий маршрут для любителів природи: водоспади, чорний пісок, гейзери та зоряне небо над льодовиками.",
    highlights: ["Голуба лагуна", "Рейк'явік", "Фіорди", "Північне сяйво"],
    duration: "10 днів",
    price: "від 98 000 ₴",
    category: "mountain",
    categoryTitle: "Гори",
    image: "/images/iceland.jpg"
  },
  {
    id: "newyork",
    name: "Нью-Йорк",
    country: "США",
    summary: "Класичний мегаполіс з небоскребами, музеями та ресторанами.",
    description: "Тур для тих, хто хоче відчути справжній американський ритм: Центральний парк, Статуя Свободи, Бруклін і модні квартали.",
    highlights: ["Музей модерного мистецтва", "Статуя Свободи", "Центральний парк", "Нічна прогулянка"],
    duration: "6 днів",
    price: "від 68 000 ₴",
    category: "city",
    categoryTitle: "Місто",
    image: "/images/newyork.jpg"
  },
  {
    id: "capetown",
    name: "Кейптаун",
    country: "ПАР",
    summary: "Пляжі, гірські панорами й унікальна африканська атмосфера.",
    description: "Комбінований тур із оглядом міста, підйомами на гори, пляжним відпочинком та смачною місцевою кухнею.",
    highlights: ["Пляж Клондейк", "Гора Кабоун", "Віндсёрфінг", "Марина"],
    duration: "8 днів",
    price: "від 74 000 ₴",
    category: "sea",
    categoryTitle: "Море",
    image: "/images/capetown.jpg"
  }
];

let contacts = [];

if (fs.existsSync(contactsPath)) {
  try {
    contacts = JSON.parse(fs.readFileSync(contactsPath, "utf8"));
  } catch (error) {
    contacts = [];
  }
}

let bookings = [];

if (fs.existsSync(bookingsPath)) {
  try {
    bookings = JSON.parse(fs.readFileSync(bookingsPath, "utf8"));
  } catch (error) {
    bookings = [];
  }
}

const mimeTypes = {
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
};

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(payload));
}

function sendHtml(res, statusCode, html) {
  res.writeHead(statusCode, { "Content-Type": "text/html; charset=utf-8" });
  res.end(html);
}

function renderTourPage(tour) {
  const highlights = (tour.highlights || []).map(item => `<li>${item}</li>`).join("");

  return `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${tour.name} | TravelWay</title>
  <base href="/">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <main style="max-width: 960px; margin: 0 auto; padding: 48px 24px;">
    <a href="/" style="display:inline-block; margin-bottom:24px; color:#2563eb; font-weight:600;">← Назад на головну</a>
    <article class="card" style="overflow:hidden;">
      <img src="${tour.image}" alt="${tour.name}" style="width:100%; height:320px; object-fit:cover;">
      <div class="card-content">
        <p class="card-category">${tour.categoryTitle}</p>
        <h1>${tour.name}</h1>
        <p>${tour.country}</p>
        <p>${tour.description}</p>
        <ul>${highlights}</ul>
        <div class="card-meta">
          <span>${tour.duration}</span>
          <span>${tour.price}</span>
        </div>
        <a href="/" class="btn" style="display:inline-block; margin-top:20px;">Забронювати цей тур</a>
      </div>
    </article>
  </main>
</body>
</html>`;
}

function serveStaticFile(res, filePath) {
  const extension = path.extname(filePath).toLowerCase();
  const contentType = mimeTypes[extension] || "application/octet-stream";

  fs.readFile(filePath, extension === ".jpg" || extension === ".jpeg" || extension === ".png" || extension === ".gif" || extension === ".svg" || extension === ".ico" ? undefined : "utf8", (error, content) => {
    if (error) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Not found");
      return;
    }

    res.writeHead(200, { "Content-Type": contentType });
    res.end(content);
  });
}

const server = http.createServer((req, res) => {
  const requestUrl = new URL(req.url, `http://${req.headers.host}`);

  if (requestUrl.pathname === "/api/tours") {
    sendJson(res, 200, tours);
    return;
  }

  if (requestUrl.pathname === "/api/contacts") {
    if (req.method === "POST") {
      let body = "";

      req.on("data", chunk => {
        body += chunk.toString();
      });

      req.on("end", () => {
        try {
          const payload = JSON.parse(body);
          const entry = {
            id: Date.now().toString(),
            name: payload.name || "",
            email: payload.email || "",
            message: payload.message || "",
            createdAt: new Date().toISOString()
          };

          contacts.push(entry);
          fs.mkdirSync(path.dirname(contactsPath), { recursive: true });
          fs.writeFileSync(contactsPath, JSON.stringify(contacts, null, 2), "utf8");

          sendJson(res, 200, { success: true, message: "Повідомлення успішно надіслано!" });
        } catch (error) {
          sendJson(res, 400, { success: false, message: "Некоректний запит" });
        }
      });
      return;
    }

    sendJson(res, 200, contacts);
    return;
  }

  if (requestUrl.pathname === "/api/bookings") {
    if (req.method === "POST") {
      let body = "";

      req.on("data", chunk => {
        body += chunk.toString();
      });

      req.on("end", () => {
        try {
          const payload = JSON.parse(body);

          if (!payload.tourId || !payload.tourName || !payload.name || !payload.email || !payload.date || !payload.guests) {
            sendJson(res, 400, { success: false, message: "Заповніть всі обов'язкові поля." });
            return;
          }

          const entry = {
            id: Date.now().toString(),
            tourId: payload.tourId,
            tourName: payload.tourName,
            name: payload.name,
            email: payload.email,
            date: payload.date,
            guests: payload.guests,
            message: payload.message || "",
            createdAt: new Date().toISOString()
          };

          bookings.push(entry);
          fs.mkdirSync(path.dirname(bookingsPath), { recursive: true });
          fs.writeFileSync(bookingsPath, JSON.stringify(bookings, null, 2), "utf8");

          sendJson(res, 200, { success: true, message: "Бронювання успішно створено!" });
        } catch (error) {
          sendJson(res, 400, { success: false, message: "Некоректний запит" });
        }
      });
      return;
    }

    sendJson(res, 200, bookings);
    return;
  }

  if (requestUrl.pathname === "/api/health") {
    sendJson(res, 200, { status: "ok" });
    return;
  }

  const tourMatch = requestUrl.pathname.match(/^\/tour\/([^/]+)$/);
  if (tourMatch) {
    const tour = tours.find(item => item.id === tourMatch[1]);

    if (tour) {
      sendHtml(res, 200, renderTourPage(tour));
    } else {
      sendHtml(res, 404, "<h1>Тур не знайдено</h1>");
    }

    return;
  }

  let filePath = path.join(rootDir, requestUrl.pathname === "/" ? "index.html" : requestUrl.pathname);

  if (!path.extname(filePath)) {
    filePath = path.join(filePath, "index.html");
  }

  serveStaticFile(res, filePath);
});

server.listen(3000, () => {
  console.log("TravelWay backend is running on http://localhost:3000");
});
