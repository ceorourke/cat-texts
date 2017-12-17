function replaceStatus(results, evt) {
    if(results === "no") {
        evt.preventDefault();
        $('#codeCompare').html("");
        $('#codeCompare').html("Not a match, try again!"); 
    }
}

function checkCode() {
    $.get('/check_verification_code.json', {code: $('#text-code').val()}, replaceStatus);
}

 $('#attempt').on('click', checkCode);
