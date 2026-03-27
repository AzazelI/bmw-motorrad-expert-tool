async function search() {

    let query = document.getElementById("search").value.trim()

    if (!query) return

    saveRecent(query)

    let result = document.getElementById("result")

    // 🔥 Loading / VIN detect
    if (query.length >= 10) {
        result.innerHTML = `<p style="color:#2e8cff">🔍 VIN detected... decoding...</p>`
    } else {
        result.innerHTML = `<p style="color:#888">Searching...</p>`
    }

    try {

        let response = await fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        })

        let data = await response.json()

        if (data.error || !data.length) {
            result.innerHTML = "<p style='color:#999'>No results found</p>"
            return
        }

        let html = ""

        data.forEach(bike => {

            html += `
            <div class="result-card">

                <h3>${bike.model}</h3>

                <div class="spec">
                    <span>Type Code</span>
                    <span>${bike.type_code || "N/A"}</span>
                </div>

                <div class="spec">
                    <span>Detected VIN Code</span>
                    <span style="color:#2e8cff">${bike.detected_vin || "—"}</span>
                </div>

                <div class="spec">
                    <span>Engine capacity</span>
                    <span>${bike.engine_cc || "N/A"} cc</span>
                </div>

                <div class="spec">
                    <span>Power</span>
                    <span>${bike.power_kw || "N/A"} kW</span>
                </div>

                <div class="spec">
                    <span>Horsepower</span>
                    <span>${bike.horsepower || "N/A"} hp</span>
                </div>

                <div class="spec">
                    <span>Kerb weight</span>
                    <span>${bike.kerb_weight_kg || "N/A"} kg</span>
                </div>

                <div class="spec">
                    <span>Gross weight</span>
                    <span>${bike.gross_weight_kg || "N/A"} kg</span>
                </div>

                <div class="spec">
                    <span>Payload</span>
                    <span>${bike.payload_kg || "N/A"} kg</span>
                </div>

                <div class="spec">
                    <span>Engine type</span>
                    <span>${bike.engine_type || "Unknown"}</span>
                </div>

                <div class="spec">
                    <span>Fuel</span>
                    <span>${bike.fuel || "N/A"}</span>
                </div>

            </div>
            <hr>
            `
        })

        result.innerHTML = html

    } catch (err) {
        console.error(err)
        result.innerHTML = "<p style='color:red'>Server error</p>"
    }
}


// 🔥 ENTER KEY SUPPORT
document.getElementById("search").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        search()
    }
})


// 🔥 HOME BUTTON (LOGO CLICK)
function goHome() {
    document.getElementById("search").value = ""
    document.getElementById("result").innerHTML = `
        <p style="color:#666; text-align:center;">
            Enter model, VIN or type code to begin
        </p>
    `
}


// 🔥 SAVE RECENT
function saveRecent(query) {
    let recent = JSON.parse(localStorage.getItem("recent")) || []

    // remove duplicates
    recent = recent.filter(r => r !== query)

    recent.unshift(query)
    recent = recent.slice(0, 5)

    localStorage.setItem("recent", JSON.stringify(recent))
}


// 🔥 SHOW RECENT
function showRecent() {

    let recent = JSON.parse(localStorage.getItem("recent")) || []

    if (recent.length === 0) {
        document.getElementById("result").innerHTML =
            "<p style='color:#888'>No recent searches</p>"
        return
    }

    let html = "<h3>Recent Searches</h3>"

    recent.forEach(r => {
        html += `
        <div class="recent-item"
            onclick="document.getElementById('search').value='${r}'; search()">
            ${r}
        </div>
        `
    })

    document.getElementById("result").innerHTML = html
}