async function search(){

let query = document.getElementById("search").value.trim()

if(!query){
return
}

saveRecent(query)

let response = await fetch("/search",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({query:query})

})

let data = await response.json()

let result = document.getElementById("result")

if(data.error){

result.innerHTML = "<p>Model not found</p>"
return

}

let html=""

data.forEach(bike => {

html += `

<h3>${bike.model}</h3>

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
<span>${bike.engine_type || "N/A"}</span>
</div>

<div class="spec">
<span>Fuel</span>
<span>${bike.fuel || "N/A"}</span>
</div>

<hr>

`

})

result.innerHTML = html

}

document.getElementById("search").addEventListener("keypress",function(e){

if(e.key==="Enter"){
search()
}

})

function toggleAdvanced(){

let panel=document.getElementById("advancedPanel")

if(panel.style.display==="none"){
panel.style.display="block"
}else{
panel.style.display="none"
}

}

async function advancedSearch(){

let engine=document.getElementById("engineFilter").value

let response=await fetch("/advanced-search",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({engine:engine})

})

let data=await response.json()

let result=document.getElementById("result")

if(data.error){

result.innerHTML="<p>No results</p>"
return

}

let html=""

data.forEach(bike=>{

html+=`<div>${bike.model}</div>`

})

result.innerHTML=html

}

function saveRecent(query){

let recent=JSON.parse(localStorage.getItem("recent"))||[]

recent.unshift(query)

recent=recent.slice(0,5)

localStorage.setItem("recent",JSON.stringify(recent))

}

function showRecent(){

let recent=JSON.parse(localStorage.getItem("recent"))||[]

let html="<h3>Recent Searches</h3>"

recent.forEach(r=>{
html+=`<div>${r}</div>`
})

document.getElementById("result").innerHTML=html

}
