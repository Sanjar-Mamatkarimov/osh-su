/**
 * UniTrack — ядро фронтенда: работа с API Django REST Framework.
 *
 * Токен и данные пользователя хранятся в localStorage,
 * все запросы идут к тому же домену с префиксом /api.
 */

const API = (function () {

    const BASE = "/api";
    const TOKEN_KEY = "unitrack_token";
    const USER_KEY = "unitrack_user";

    // --- Сессия ---

    function getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    function getUser() {
        try {
            return JSON.parse(localStorage.getItem(USER_KEY));
        } catch (e) {
            return null;
        }
    }

    function saveSession(token, user) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }

    function clearSession() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
    }

    /** Выход: чистим сессию и уходим на страницу входа. */
    function logout() {
        clearSession();
        window.location.href = "/";
    }

    /**
     * Базовый запрос к API.
     * options — как у fetch (method, body, formData и т.д.)
     */
    async function request(path, options = {}) {
        const headers = Object.assign({}, options.headers);

        // skipAuth: не прикладываем токен (например, к самому логину),
        // иначе протухший токен в localStorage даст 401 вместо входа
        const skipAuth = options.skipAuth === true;

        const token = getToken();
        if (token && !skipAuth) {
            headers["Authorization"] = "Token " + token;
        }

        // JSON-тело по умолчанию; FormData передаём как есть
        let body = options.body;
        if (body && !(body instanceof FormData) && typeof body !== "string") {
            headers["Content-Type"] = "application/json";
            body = JSON.stringify(body);
        }

        const res = await fetch(BASE + path, Object.assign({}, options, { headers, body }));

        let data = null;
        const text = await res.text();
        if (text) {
            try {
                data = JSON.parse(text);
            } catch (e) {
                data = null;
            }
        }

        if (res.status === 401) {
            // Протухший токен: чистим сессию. На самой странице входа
            // не редиректим и не показываем «Сессия истекла» —
            // пользователь как раз пытается войти.
            clearSession();
            if (window.location.pathname !== "/") {
                window.location.href = "/";
            }
            throw new Error(skipAuth
                ? (extractError(data) || "Ошибка авторизации")
                : "Сессия истекла, войдите заново");
        }

        if (!res.ok) {
            throw new Error(extractError(data) || "Ошибка запроса (" + res.status + ")");
        }

        return data;
    }

    /** Превращает ответы DRF (detail / поля сериализатора) в читаемый текст. */
    function extractError(data) {
        if (!data) return "";
        if (typeof data === "string") return data;
        if (data.detail) return data.detail;

        // Ошибки полей: { username: ["Это поле уже занято."] }
        const parts = [];
        Object.keys(data).forEach((key) => {
            const value = data[key];
            if (Array.isArray(value)) {
                parts.push(value.join(" "));
            } else if (typeof value === "string") {
                parts.push(value);
            }
        });
        return parts.join(" ");
    }

    function get(path) {
        return request(path, { method: "GET" });
    }

    function post(path, body, options = {}) {
        return request(path, Object.assign({ method: "POST", body: body }, options));
    }

    /** Запрещаем доступ без входа; при желании можно проверить роль. */
    function requireRole(role) {
        const user = getUser();
        if (!getToken() || !user) {
            window.location.href = "/";
            throw new Error("Не авторизован");
        }
        if (role && user.role !== role && user.role !== "admin") {
            window.location.href = user.role === "student"
                ? "/student/dashboard/"
                : "/teacher/dashboard/";
            throw new Error("Недостаточно прав");
        }
        return user;
    }

    // --- Утилиты для шаблонизатора на стороне страниц ---

    function escapeHtml(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    /** "2026-09-20T12:00:00Z" → "20.09.2026" */
    function formatDate(value) {
        if (!value) return "—";
        const d = new Date(value);
        if (isNaN(d)) return "—";
        return d.toLocaleDateString("ru-RU");
    }

    /** Инициалы из имени: "Аслан Байбалаев" → "АБ" */
    function initials(name) {
        if (!name) return "?";
        return name.trim().split(/\s+/).slice(0, 2)
            .map((w) => w.charAt(0).toUpperCase())
            .join("");
    }

    return {
        get,
        post,
        request,
        getToken,
        getUser,
        saveSession,
        clearSession,
        logout,
        requireRole,
        escapeHtml,
        formatDate,
        initials
    };

})();
