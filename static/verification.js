function checkCode(evt) {
  var realCode = $('#textCode').data(); // get code from hidden div
  var userCode = $('#text-code').val(); // get user input

  if(realCode.name !== userCode) { // compare each 
    evt.preventDefault();
    $('#codeCompare').html("");
    $('#codeCompare').html("Not a match, try again!");
   } 
}

 $('#attempt').on('click', checkCode);