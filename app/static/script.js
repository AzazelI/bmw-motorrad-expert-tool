async function searchBike(){

let query = document.getElementById("searchBox").value;

let response = await fetch("/search",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({query:query})

});

let data = await response.json();

let result = document.getElementById("result");

if(data.error){

result.innerHTML = "Model not found";
return;

}

result.innerHTML = `

<h3>TECHNICAL DATA</h3>

Engine capacity: ${data.engine_cc} cc<br>
Power: ${data.power_kw} kW<br>
Horsepower: ${data.horsepower} hp<br>
Kerb weight: ${data.kerb_weight} kg<br>
Gross weight: ${data.gross_weight} kg<br>
Engine type: ${data.engine_type}<br>
Fuel: ${data.fuel}

`;

}