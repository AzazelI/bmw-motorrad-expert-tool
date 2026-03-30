// 🔍 SEARCH FUNCTION
async function search() {
    let query = document.getElementById("search").value.trim();
    if (!query) return;

    saveRecent(query);
    let result = document.getElementById("result");
    
    // Loading state & VIN detection notice
    result.innerHTML = query.length >= 10 ? 
        `<p style="color:#2e8cff" class="fade-in">🔍 VIN detected... decoding...</p>` : 
        `<p style="color:#888" class="fade-in">Searching official database...</p>`;

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
            <div class="result-card fade-in">
                <h3>${bike.model}</h3>
                <div class="spec"><span>Type Code</span><span>${bike.type_code || "N/A"}</span></div>
                
                ${bike.detected_vin ? `
                <div class="spec">
                    <span>Detected VIN</span>
                    <span style="color:#2e8cff; font-weight:bold; letter-spacing: 1px;">${bike.detected_vin}</span>
                </div>` : ''}
                
                <div class="spec"><span>Engine</span><span>${bike.engine_cc || "N/A"} cc</span></div>
                <div class="spec"><span>Power</span><span>${bike.power_kw || "N/A"} kW / ${bike.horsepower || "N/A"} hp</span></div>
                <div class="spec"><span>Kerb Weight</span><span style="color:#2e8cff; font-weight:bold;">${bike.kerb_weight_kg || "N/A"} kg</span></div>
                <div class="spec"><span>Gross Weight</span><span>${bike.gross_weight_kg || "N/A"} kg</span></div>
                <div class="spec"><span>Engine Type</span><span>${bike.engine_type || "Unknown"}</span></div>
                <div class="spec"><span>Fuel</span><span>${bike.fuel || "N/A"}</span></div>
            </div>`;
        });
        result.innerHTML = html;
    } catch (err) {
        console.error("Search error:", err);
        result.innerHTML = "<p style='color:red'>Server error</p>";
    }
}

// ⌨️ Enter Key Support
function handleKeyPress(event) {
    if (event.key === "Enter") {
        search();
    }
}

// 🪟 MODAL CONTROL
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "flex";
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "none";
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = "none";
    }
}

// 🏠 NAVIGATION & HISTORY
function goHome() {
    document.getElementById("search").value = "";
    document.getElementById("result").innerHTML = "";
    document.getElementById("search").placeholder = "Enter Model, Type Code (K66) or VIN (4–7)";
}

function saveRecent(query) {
    let recent = JSON.parse(localStorage.getItem("recent")) || [];
    recent = recent.filter(r => r !== query);
    recent.unshift(query);
    localStorage.setItem("recent", JSON.stringify(recent.slice(0, 5)));
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

function clearLocalRecent() {
    if (confirm("Clear history?")) {
        localStorage.removeItem("recent");
        document.getElementById("result").innerHTML = "";
    }
}

// 🔮 ADVANCED SEARCH & SUPPORT
function toggleAdvanced() {
    const searchInput = document.getElementById("search");
    searchInput.placeholder = "Try: 'Boxer', 'Inline-4', 'Single' or weight (e.g. 197)";
    searchInput.focus();
    searchInput.style.boxShadow = "0 0 15px rgba(46, 140, 255, 0.5)";
    setTimeout(() => { searchInput.style.boxShadow = "none"; }, 1500);
}

function sendEmail() {
    window.location.href = "mailto:givijananashvili40@gmail.com?subject=BMW Motorrad Tool Request";
}