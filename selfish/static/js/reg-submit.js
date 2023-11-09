function regSubmit(event) {
  $(this).blur();
  let tee = {
    address: $('#raddress').val(),
    cache: $('#rsuffix').val(),
    captcha: $('#rcaptcha').val(),
  };
  if (tee.address && tee.cache && tee.captcha) {
    $.ajax({
      method: 'POST',
      url: '/api/request-reg',
      data: tee,
      success: function(data) {
        if (data.done) {
          $('.navbar-brand')[0].click();
        } else {
          showError('#regf', data);
        }
      },
      dataType: 'json'
    });
  }
}
