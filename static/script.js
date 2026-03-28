async function search() {
    let query = document.getElementById("search").value.trim();
    if (!query) return;

    saveRecent(query);
    let result = document.getElementById("result");
    result.innerHTML = query.length >= 10 ? 
        `<p style="color:#2e8cff">🔍 VIN detected... decoding...</p>` : 
        `<p style="color:#888">Searching...</p>`;

    try {
        let response = await fetch("/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });
        let data = await response.json();

        if (data.error || !data.length) {
            result.innerHTML = "<p style='color:#999'>No results found</p>";
            return;
        }

        let html = "";
        data.forEach(bike => {
            html += `
            <div class="result-card">
                <h3>${bike.model} (${bike.year || "N/A"})</h3>
                <div class="spec"><span>Type Code</span><span>${bike.type_code || "N/A"}</span></div>
                <div class="spec"><span>Detected VIN</span><span style="color:#2e8cff">${bike.detected_vin || "—"}</span></div>
                <div class="spec"><span>Engine</span><span>${bike.engine_cc || "N/A"} cc</span></div>
                <div class="spec"><span>Power</span><span>${bike.power_kw || "N/A"} kW / ${bike.horsepower || "N/A"} hp</span></div>
                <div class="spec"><span>Weight (Kerb/Gross)</span><span>${bike.kerb_weight_kg || "N/A"} / ${bike.gross_weight_kg || "N/A"} kg</span></div>
                <div class="spec"><span>Engine Type</span><span>${bike.engine_type || "Unknown"}</span></div>
                <div class="spec"><span>Fuel</span><span>${bike.fuel || "N/A"}</span></div>
            </div><hr>`;
        });
        result.innerHTML = html;
    } catch (err) {
        result.innerHTML = "<p style='color:red'>Server error</p>";
    }
}

document.getElementById("search").addEventListener("keypress", (e) => { if (e.key === "Enter") search(); });

function goHome() {
    document.getElementById("search").value = "";
    document.getElementById("result").innerHTML = `<p style="color:#666; text-align:center;">Enter model, VIN or type code to begin</p>`;
}

function saveRecent(query) {
    let recent = JSON.parse(localStorage.getItem("recent")) || [];
    recent = recent.filter(r => r !== query);
    recent.unshift(query);
    localStorage.setItem("recent", JSON.stringify(recent.slice(0, 5)));
}

function clearLocalRecent() {
    if (confirm("Clear your local search history?")) {
        localStorage.removeItem("recent");
        showRecent(); // განაახლებს UI-ს
    }
}

function showRecent() {
    let recent = JSON.parse(localStorage.getItem("recent")) || [];
    if (recent.length === 0) {
        document.getElementById("result").innerHTML = "<p style='color:#888'>No recent searches</p>";
        return;
    }
    let html = `<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h3 style="margin:0;">Recent Searches</h3>
                    <button onclick="clearLocalRecent()" style="background:none; border:none; color:#ff4d4d; cursor:pointer; font-size:12px;">Clear All</button>
                </div>`;
    recent.forEach(r => {
        html += `<div class="recent-item" onclick="document.getElementById('search').value='${r}'; search()">${r}</div>`;
    });
    document.getElementById("result").innerHTML = html;
}