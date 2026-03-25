async function search(){

let query = document.getElementById("search").value.trim()

if(!query){
return
}

saveRecent(query)

let result = document.getElementById("result")

// 🔥 VIN MESSAGE (only for full VIN)
if(query.length >= 10){
result.innerHTML = `<p style="color:#2e8cff">Detected VIN → extracting code...</p>`
}

try{

let response = await fetch("/search",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({query:query})
})

let data = await response.json()

if(data.error){
result.innerHTML = "<p>Model not found</p>"
return
}

let html=""

data.forEach(bike => {

html += `

<h3>${bike.model}</h3>

<div class="spec">
<span>Type Code</span>
<span>${bike.type_code || "N/A"}</span>
</div>

<div class="spec">
<span>VIN Code</span>
<span>${bike.vin_code || "N/A"}</span>
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

<hr>
`
})

result.innerHTML = html

}catch(err){
console.error(err)
result.innerHTML = "<p>Error loading data</p>"
}

}


// 🔥 ENTER KEY
document.getElementById("search").addEventListener("keypress",function(e){
if(e.key==="Enter"){
search()
}
})


// 🔥 SAVE RECENT
function saveRecent(query){

let recent=JSON.parse(localStorage.getItem("recent"))||[]

recent.unshift(query)
recent=recent.slice(0,5)

localStorage.setItem("recent",JSON.stringify(recent))
}


// 🔥 SHOW RECENT (CLICKABLE)
function showRecent(){

let recent=JSON.parse(localStorage.getItem("recent"))||[]

let html="<h3>Recent Searches</h3>"

recent.forEach(r=>{
html+=`<div style="cursor:pointer; padding:5px 0;" onclick="document.getElementById('search').value='${r}'; search()">${r}</div>`
})

document.getElementById("result").innerHTML=html

}