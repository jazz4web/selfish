function changeEmail(token) {
  $.ajax({
    method: 'GET',
    url: '/api/change-email',
    headers: {
      'x-reg-token': token,
      'x-auth-token': window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.done) {
        $('.navbar-brand')[0].click();
      } else {
        let topf = $('.top-flashed-block');
        let ealert = $('#ealert');
        if (ealert.length) ealert.remove();
        if (topf.length) topf.remove();
        let bid = '#' + $('#main-container').children()[0].id;
        showError(bid, data);
      }
    },
    dataType: 'json',
  });
}
