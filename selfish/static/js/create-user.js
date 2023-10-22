function createUser() {
  $(this).blur();
  let tee = {
    username: $('#username').val(),
    passwd: $('#crpassword').val(),
    confirma: $('#confirmation').val(),
    aid: $(this).data().aid
  };
  if (tee.username && tee.passwd && tee.confirma && tee.aid) {
    $.ajax({
      method: 'POST',
      url: '/api/request-passwd',
      data: tee,
      success: function(data) {
        if (data.done) {
          $('.navbar-brand')[0].click();
        } else {
          showError('#crpf', data);
        }
      },
      dataType: 'json'
    });
  }
}
