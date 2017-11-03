"use strict";



function getName(evt){
    evt.preventDefault()
    console.log("hi2");
    $.get('/welcome');
}
$('#cat-btn').on('click', getName);