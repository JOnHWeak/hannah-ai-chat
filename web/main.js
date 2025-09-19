const apiBase = window.API_BASE || ""; // same origin by default

async function postJson(path, body) {
    const resp = await fetch(`${apiBase}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!resp.ok) throw new Error(await resp.text());
    return resp.json();
}

async function getJson(url) {
    const resp = await fetch(`${apiBase}${url}`);
    if (!resp.ok) throw new Error(await resp.text());
    return resp.json();
}

document.getElementById("sendBtn").addEventListener("click", async () => {
    const user_id = document.getElementById("userId").value || "demo-user";
    const session_id = document.getElementById("sessionId").value || null;
    const temperature = parseFloat(document.getElementById("temperature").value || "0.2");
    const message = document.getElementById("message").value;

    const out = document.getElementById("answer");
    out.textContent = "Đang gửi...";
    try {
        const data = await postJson("/chat", { user_id, session_id, temperature, message });
        out.textContent = `#${data.history_id}:\n\n` + data.answer;
        document.getElementById("historyId").value = data.history_id;
    } catch (e) {
        out.textContent = "Lỗi: " + e.message;
    }
});

document.getElementById("rateBtn").addEventListener("click", async () => {
    const history_id = parseInt(document.getElementById("historyId").value || "0", 10);
    const rating = parseInt(document.getElementById("rating").value || "0", 10);
    const out = document.getElementById("rateResult");
    out.textContent = "Đang gửi...";
    try {
        const data = await postJson("/rate", { history_id, rating });
        out.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        out.textContent = "Lỗi: " + e.message;
    }
});

document.getElementById("kbSearchBtn").addEventListener("click", async () => {
    const q = encodeURIComponent(document.getElementById("kbQuery").value || "");
    const list = document.getElementById("kbResults");
    list.innerHTML = "<li>Đang tìm...</li>";
    try {
        const data = await getJson(`/kb/search?q=${q}`);
        list.innerHTML = "";
        data.forEach(item => {
            const li = document.createElement("li");
            li.textContent = `${item.id} - ${item.title}`;
            list.appendChild(li);
        });
    } catch (e) {
        list.innerHTML = `<li>Lỗi: ${e.message}</li>`;
    }
});

document.getElementById("esSearchBtn").addEventListener("click", async () => {
    const query = document.getElementById("esQuery").value || "*";
    const catsStr = document.getElementById("esCategories").value || "";
    const categories = catsStr ? catsStr.split(",").map(s => s.trim()).filter(Boolean) : null;
    const top_n_per_category = parseInt(document.getElementById("esTopN").value || "5", 10);
    const save_to_postgres = document.getElementById("esSave").checked;
    const out = document.getElementById("esResults");
    out.textContent = "Đang chạy...";
    try {
        const data = await postJson("/es/search", { query, categories, top_n_per_category, save_to_postgres });
        out.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        out.textContent = "Lỗi: " + e.message;
    }
});


