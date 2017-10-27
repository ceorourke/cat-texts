"use strict";

function getTexts(evt){
    evt.preventDefault()
    console.log("hi");
    $.post('/welcome');
}
$('#cat-btn').on('click', getTexts);


function getName(evt){
    evt.preventDefault()
    console.log("hi2");
    $.post('/welcome');
}
$('#cat-btn').on('click', getName);