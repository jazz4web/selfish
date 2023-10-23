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
        let interval = setInterval(function() {
          if ($('#main-container').length) {
            $('#main-container').append(html);
            slidePage('#ealert');
            clearInterval(interval);
          }
        }, 10);
      } else {
        if (!data.aid) {
          let html = Mustache.render($('#ealertt').html(), data);
          let interval = setInterval(function() {
            if ($('#main-container').length) {
              $('#main-container').append(html);
              slidePage('#ealert');
              clearInterval(interval);
            }
          }, 10);
        } else {
          let html = Mustache.render($('#rspt').html(), data);
          let interval = setInterval(function() {
            if ($('#main-container').length) {
              $('#main-container').append(html);
              slidePage('#rspf');
              clearInterval(interval);
            }
          }, 10);
        }
      }
    },
    dataType: 'json'
  });
}
