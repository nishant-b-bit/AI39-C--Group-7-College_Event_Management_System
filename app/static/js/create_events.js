const form = document.querySelector("form");

form.addEventListener("submit", function(e){

    const title = document.querySelector("[name='title']").value;

    if(title.length < 3){
        alert("Event title too short");
        e.preventDefault();
    }

});