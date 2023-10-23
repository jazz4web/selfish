function createNewpwd() {
  $(this).blur();
  let tee = {
    passwd: $('#curpwd').val(),
    newpwd: $('#newpwd').val(),
    confirma: $('#newpwdconfirm').val(),
    auth: window.localStorage.getItem('token')
  };
  if (tee.passwd && tee.newpwd && tee.confirma && tee.auth) {
    $.ajax({
      method: 'POST',
      url: '/api/change-passwd',
      data: tee,
      success: function(data) {
        if (data.done) {
          $('.navbar-brand')[0].click();
        } else {
          showError('#changepwdf', data);
        }
      },
      dataType: 'json'
    });
  }
}
