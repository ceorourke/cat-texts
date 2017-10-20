"use strict";

function getTexts(evt){
    evt.preventDefault()
    console.log("hi");
    $.post('/sms');
}
$('#cat-btn').on('click', getTexts);