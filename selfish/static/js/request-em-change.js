function requestEmCh() {
  $(this).blur();
  let tee = {
    address: $('#chaddress').val(),
    passwd: $('#chapasswd').val(),
    auth: window.localStorage.getItem('token')
  };
  if (tee.address && tee.passwd && tee.auth) {
    $.ajax({
      method: 'POST',
      url: '/api/request-email-change',
      data: tee,
      success: function(data) {
        if (data.done) {
          $('.navbar-brand')[0].click();
        } else {
          showError('#changeemf', data);
        }
      },
      dataType: 'json'
    });
  }
}
