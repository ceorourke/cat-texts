function replaceEmailStatus(results) {
  $('#emailExistence').html(results);
}

function updateEmailStatus() {
  var text = $('#email').val();
  if (text.length > 5) { // shortest email could be a@a.a
    $.get('/email_exists.json', {email: $('#email').val()}, replaceEmailStatus);
  } else { 
    $('#emailExistence').html("");
  }
}

$('#email').on('keyup change', updateEmailStatus);

// ****************************************************************************

function replacePasswordStatus(results) {
  $('#passwordCorrectness').html(results);
}

function updatePasswordStatus() {
  var pWord = $('#password').val();
  if (pWord.length > 5) { // pw min length is 6
    $.get('/password_correctness.json', {password: $('#password').val(), 
                                        email: $('#email').val()}, 
                                        replacePasswordStatus);
  } else {
    $('#passwordCorrectness').html("");
  }
}

$('#password').on('keyup', updatePasswordStatus);