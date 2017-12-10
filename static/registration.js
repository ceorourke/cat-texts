function replaceStatus(results) {
  $('#emailStatus').html(results);
}

function updateStatus() {
  $.get('/email_in_use', {email: $('#email').val()}, replaceStatus);
}

$('#email').on('keyup', updateStatus);



$('#password').on('keyup', function () {
  if ($('#password').val().length < 6) {
    $('#passwordStrength').removeClass("has-success");
    $('#passwordStrength').addClass("has-error");
    $('#passwordText').html("Password must be at least 6 characters.");
  } else {
    $('#passwordText').html("");  
    $('#passwordStrength').removeClass("has-error");
    $('#passwordStrength').addClass("has-success");  
  }
});


$('#password, #confirm-password').on('keyup', function () {
  if ($('#password').val() === $('#confirm-password').val()) {
    $('#confirmpw').removeClass("has-error");
    $('#confirmpw').addClass("has-success");
  } else {
    $('#confirmpw').removeClass("has-success");
    $('#confirmpw').addClass("has-error");
  } 
});
