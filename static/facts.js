"use strict";

function getTexts(evt){
    evt.preventDefault()
    console.log("hi");
    $.get('/welcome');
}
$('#cat-btn').on('click', getTexts);


function getName(evt){
    evt.preventDefault()
    console.log("hi2");
    $.get('/welcome');
}
$('#cat-btn').on('click', getName);