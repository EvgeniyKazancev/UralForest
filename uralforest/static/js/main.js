(function () {
    "use strict";

    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"));
        return match ? decodeURIComponent(match.pop()) : "";
    }

    function showToast(text) {
        const toast = document.getElementById("toast");
        if (!toast) return;
        toast.textContent = text;
        toast.classList.add("is-visible");
        clearTimeout(toast._t);
        toast._t = setTimeout(() => toast.classList.remove("is-visible"), 2600);
    }

    function updateCartCount(count) {
        document.querySelectorAll("[data-cart-count]").forEach((el) => (el.textContent = count));
    }

    /* Burger menu */
    const burger = document.getElementById("burger");
    const nav = document.getElementById("nav");
    if (burger && nav) {
        burger.addEventListener("click", () => nav.classList.toggle("is-open"));
        nav.querySelectorAll("a").forEach((a) =>
            a.addEventListener("click", () => nav.classList.remove("is-open"))
        );
    }

    /* Modals */
    document.querySelectorAll("[data-modal-open]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const modal = document.getElementById("modal-" + btn.dataset.modalOpen);
            if (modal) modal.classList.add("is-open");
        });
    });
    document.querySelectorAll("[data-modal-close]").forEach((el) => {
        el.addEventListener("click", () => el.closest(".modal").classList.remove("is-open"));
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll(".modal.is-open").forEach((m) => m.classList.remove("is-open"));
        }
    });

    /* AJAX add to cart */
    document.querySelectorAll("form.js-add-cart").forEach((form) => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const data = new FormData(form);
            fetch(form.action, {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken") },
                body: data,
            })
                .then((r) => r.json())
                .then((res) => {
                    if (res.ok) {
                        updateCartCount(res.count);
                        showToast(res.message || "Товар добавлен в корзину");
                    }
                })
                .catch(() => form.submit());
        });
    });

    /* AJAX lead forms */
    document.querySelectorAll("form[data-lead-form]").forEach((form) => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const note = form.querySelector("[data-lead-note]");
            fetch(form.action, {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCookie("csrftoken") },
                body: new FormData(form),
            })
                .then((r) => r.json())
                .then((res) => {
                    if (res.ok) {
                        form.reset();
                        if (note) { note.hidden = false; note.textContent = res.message; }
                        showToast(res.message);
                        const modal = form.closest(".modal");
                        if (modal) setTimeout(() => modal.classList.remove("is-open"), 1400);
                    } else if (note) {
                        note.hidden = false;
                        note.textContent = "Проверьте правильность заполнения формы.";
                    }
                })
                .catch(() => form.submit());
        });
    });

    /* Product gallery */
    const mainImage = document.getElementById("mainImage");
    document.querySelectorAll(".thumb").forEach((thumb) => {
        thumb.addEventListener("click", () => {
            if (!mainImage) return;
            mainImage.src = thumb.dataset.src;
            document.querySelectorAll(".thumb").forEach((t) => t.classList.remove("is-active"));
            thumb.classList.add("is-active");
        });
    });

    /* Simple phone mask */
    document.querySelectorAll("input[data-phone]").forEach((input) => {
        input.addEventListener("input", function () {
            let digits = this.value.replace(/\D/g, "");
            if (digits.startsWith("8")) digits = "7" + digits.slice(1);
            if (!digits.startsWith("7")) digits = "7" + digits;
            digits = digits.slice(0, 11);
            let out = "+7";
            if (digits.length > 1) out += " (" + digits.slice(1, 4);
            if (digits.length >= 4) out += ") " + digits.slice(4, 7);
            if (digits.length >= 7) out += "-" + digits.slice(7, 9);
            if (digits.length >= 9) out += "-" + digits.slice(9, 11);
            this.value = out;
        });
    });
})();
