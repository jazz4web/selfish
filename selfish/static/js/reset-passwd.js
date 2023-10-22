function resetPasswd(token) {
  $.ajax({
    method: 'GET',
    url: '/api/reset-passwd',
    headers: {
      'x-reg-token': token,
      'x-auth-token': window.localStorage.getItem('token')
    },
    success: function(data) {
      if (data.cu) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        if (!data.aid) {
          let html = Mustache.render($('#ealertt').html(), data);
          $('#main-container').append(html);
          slidePage('#ealert');
        } else {
          let html = Mustache.render($('#rspt').html(), data);
          $('#main-container').append(html);
          slidePage('#rspf');
        }
      }
    },
    dataType: 'json'
  });
}
