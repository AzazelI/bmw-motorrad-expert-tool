// 🔍 SEARCH FUNCTION
async function search() {
    let query = document.getElementById("search").value.trim();
    if (!query) return;

    saveRecent(query);
    let result = document.getElementById("result");
    
    // Loading state & VIN detection notice
    result.innerHTML = query.length >= 10 ? 
        `<div class="loading-container fade-in"><div class="spinner"></div><p style="color:#2e8cff">🔍 VIN detected... decoding...</p></div>` : 
        `<div class="loading-container fade-in"><div class="spinner"></div><p style="color:#888">Searching official database...</p></div>`;

    // Advanced search filter values
    const filterEngineType = document.getElementById("filterEngineType").value;
    const filterFuel = document.getElementById("filterFuel").value;
    const filterWeightMin = parseFloat(document.getElementById("filterWeightMin").value) || null;
    const filterWeightMax = parseFloat(document.getElementById("filterWeightMax").value) || null;
    const filterHpMin = parseFloat(document.getElementById("filterHpMin").value) || null;
    const filterHpMax = parseFloat(document.getElementById("filterHpMax").value) || null;

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

        // Apply advanced filters client-side
        let filteredBikes = data;

        if (filterEngineType) {
            filteredBikes = filteredBikes.filter(bike => {
                const type = (bike.engine_type || "").toLowerCase();
                return type.includes(filterEngineType.toLowerCase());
            });
        }

        if (filterFuel) {
            filteredBikes = filteredBikes.filter(bike => {
                const fuel = (bike.fuel || "").toLowerCase();
                return fuel.toLowerCase() === filterFuel.toLowerCase();
            });
        }

        if (filterWeightMin !== null) {
            filteredBikes = filteredBikes.filter(bike => {
                const weight = parseFloat(bike.kerb_weight_kg);
                return !isNaN(weight) && weight >= filterWeightMin;
            });
        }
        if (filterWeightMax !== null) {
            filteredBikes = filteredBikes.filter(bike => {
                const weight = parseFloat(bike.kerb_weight_kg);
                return !isNaN(weight) && weight <= filterWeightMax;
            });
        }

        if (filterHpMin !== null) {
            filteredBikes = filteredBikes.filter(bike => {
                const hp = parseFloat(bike.horsepower);
                return !isNaN(hp) && hp >= filterHpMin;
            });
        }
        if (filterHpMax !== null) {
            filteredBikes = filteredBikes.filter(bike => {
                const hp = parseFloat(bike.horsepower);
                return !isNaN(hp) && hp <= filterHpMax;
            });
        }

        if (filteredBikes.length === 0) {
            result.innerHTML = "<p style='color:#999'>No results found matching your advanced filters.</p>";
            return;
        }

        let html = "";
        filteredBikes.forEach(bike => {
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
                
                <button class="btn-add-compare" onclick="addToCompare('${encodeURIComponent(JSON.stringify(bike))}')">
                    + Add to Compare
                </button>
            </div>`;
        });
        result.innerHTML = html;
    } catch (err) {
        console.error("Search error:", err);
        result.innerHTML = "<p style='color:red'>Server error</p>";
    }
}

// ✕ Toggle input clear button
function toggleClearButton() {
    const input = document.getElementById("search");
    const clearBtn = document.getElementById("clearBtn");
    if (input.value.trim().length > 0) {
        clearBtn.style.display = "inline";
    } else {
        clearBtn.style.display = "none";
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

// Close modal
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

// 🏠 NAVIGATION & HISTORY & CLEAR
function goHome() {
    document.getElementById("search").value = "";
    document.getElementById("clearBtn").style.display = "none";
    document.getElementById("result").innerHTML = "";
    document.getElementById("search").placeholder = "Enter Model, Type Code (K66) or VIN (4–7)";
    
    // Clear filters
    document.getElementById("filterEngineType").value = "";
    document.getElementById("filterFuel").value = "";
    document.getElementById("filterWeightMin").value = "";
    document.getElementById("filterWeightMax").value = "";
    document.getElementById("filterHpMin").value = "";
    document.getElementById("filterHpMax").value = "";
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
        html += `<div class="recent-item" onclick="document.getElementById('search').value='${r}'; toggleClearButton(); search()">${r}</div>`;
    });
    document.getElementById("result").innerHTML = html;
}

function clearLocalRecent() {
    if (confirm("Clear history?")) {
        localStorage.removeItem("recent");
        document.getElementById("result").innerHTML = "";
    }
}

// 🔮 ADVANCED SEARCH toggle
function toggleAdvanced() {
    const advFilters = document.getElementById("advFilters");
    if (advFilters.style.display === "none") {
        advFilters.style.display = "block";
        advFilters.classList.add("fade-in");
    } else {
        advFilters.style.display = "none";
    }
}

function sendEmail() {
    window.location.href = "mailto:givijananashvili40@gmail.com?subject=BMW Motorrad Tool Request";
}

// 📂 PDF MANUALS LOGIC
let loadedDocs = [];

async function openDocsModal() {
    openModal("docsModal");
    const listContainer = document.getElementById("docsList");
    listContainer.innerHTML = '<div class="loading-container fade-in"><div class="spinner"></div><p style="color:#2e8cff">Loading official manuals...</p></div>';
    
    try {
        const response = await fetch("/api/docs");
        loadedDocs = await response.json();
        renderDocs(loadedDocs);
    } catch (err) {
        console.error("Error fetching docs:", err);
        listContainer.innerHTML = '<p style="color:red">Failed to load manuals.</p>';
    }
}

function renderDocs(docs) {
    const listContainer = document.getElementById("docsList");
    if (!docs || docs.length === 0) {
        listContainer.innerHTML = '<p style="color:#888;">No manuals found in /static/docs/</p>';
        return;
    }
    
    let html = "";
    docs.forEach(doc => {
        html += `
        <div class="doc-item fade-in">
            <div class="doc-info">
                <span class="doc-icon">📄</span>
                <div>
                    <span class="doc-name">${doc.name}</span>
                    <span class="doc-size">${doc.size}</span>
                </div>
            </div>
            <a href="${doc.url}" target="_blank" class="btn-download-pdf">Open / Download</a>
        </div>`;
    });
    listContainer.innerHTML = html;
}

function filterDocs() {
    const query = document.getElementById("docsSearch").value.toLowerCase().trim();
    const filtered = loadedDocs.filter(doc => doc.name.toLowerCase().includes(query));
    renderDocs(filtered);
}

// ==========================================
// ⚖️ COMPARE MOTORCYCLES LOGIC
// ==========================================
let compareList = [];

function addToCompare(bikeStr) {
    const bike = JSON.parse(decodeURIComponent(bikeStr));
    
    if(compareList.find(b => b.id === bike.id)) {
        alert("⚠️ This motorcycle is already in your compare list.");
        return;
    }
    if(compareList.length >= 3) {
        alert("⚠️ You can only compare up to 3 motorcycles at a time.");
        return;
    }
    
    compareList.push(bike);
    updateCompareTray();
}

function updateCompareTray() {
    const tray = document.getElementById('compareTray');
    const countText = document.getElementById('compareCountText');
    
    if(compareList.length > 0) {
        tray.style.display = 'block';
        countText.innerHTML = `<strong style="color:#2e8cff; font-size:18px;">${compareList.length}</strong> motorcycle(s) selected`;
    } else {
        tray.style.display = 'none';
        closeModal('compareModal'); 
    }
}

function clearCompare() {
    compareList = [];
    updateCompareTray();
}

function removeCompareItem(index) {
    compareList.splice(index, 1);
    updateCompareTray();
    if(compareList.length > 0) {
        openCompareModal(); 
    } else {
        closeModal('compareModal');
    }
}

function openCompareModal() {
    if(compareList.length === 0) return;
    
    const table = document.getElementById('compareTable');
    
    // Find min weight and max horsepower to highlight
    let minWeight = Infinity;
    let maxHp = -Infinity;
    
    compareList.forEach(bike => {
        const w = parseFloat(bike.kerb_weight_kg);
        if(!isNaN(w) && w < minWeight) minWeight = w;
        
        const hp = parseFloat(bike.horsepower);
        if(!isNaN(hp) && hp > maxHp) maxHp = hp;
    });
    
    let html = `<tr><th>Specifications</th>`;
    compareList.forEach((bike, index) => {
        html += `<th>${bike.model} <br><button class="remove-bike-btn" onclick="removeCompareItem(${index})">Remove ✕</button></th>`;
    });
    html += `</tr>`;

    const rows = [
        { label: 'Type Code', key: 'type_code' },
        { label: 'Engine Type', key: 'engine_type' },
        { label: 'Engine CC', key: 'engine_cc', suffix: ' cc' },
        { label: 'Power', key: 'power_kw', suffix: ' kW' },
        { label: 'Horsepower', key: 'horsepower', suffix: ' hp', checkMax: true },
        { label: 'Kerb Weight', key: 'kerb_weight_kg', suffix: ' kg', checkMin: true },
        { label: 'Gross Weight', key: 'gross_weight_kg', suffix: ' kg' },
        { label: 'Payload', key: 'payload_kg', suffix: ' kg' },
        { label: 'Fuel', key: 'fuel' }
    ];

    rows.forEach(row => {
        html += `<tr><td>${row.label}</td>`;
        compareList.forEach(bike => {
            const valNum = parseFloat(bike[row.key]);
            let isHighlighted = false;
            
            if (row.checkMin && valNum === minWeight && minWeight !== Infinity && compareList.length > 1) {
                isHighlighted = true;
            }
            if (row.checkMax && valNum === maxHp && maxHp !== -Infinity && compareList.length > 1) {
                isHighlighted = true;
            }
            
            const val = (bike[row.key] && bike[row.key] !== "—" && bike[row.key] !== "") 
                        ? bike[row.key] + (row.suffix || '') 
                        : '<span style="color:#555;">—</span>';
            
            if (isHighlighted) {
                html += `<td style="color:#2ecc71; font-weight:bold; background: rgba(46, 204, 113, 0.08);">${val} ✨</td>`;
            } else {
                html += `<td>${val}</td>`;
            }
        });
        html += `</tr>`;
    });

    table.innerHTML = html;
    document.getElementById('compareModal').style.display = 'flex';
}