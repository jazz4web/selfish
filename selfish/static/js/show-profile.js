function showProfile() {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/profile',
    headers: tee,
    data: {
      username: username
    },
    success: function(data) {
      console.log(data);
      if (token) {
        if (!data.cu || data.cu.brkey != checkBrowser()) {
          window.localStorage.removeItem('token');
          window.location.reload();
        }
      }
      let dt = luxon.DateTime.now();
      data.year = dt.year;
      let html = Mustache.render($('#baset').html(), data);
      $('body').append(html);
      checkMC(800);
      $('body').on('click', '.close-top-flashed', closeTopFlashed);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#profilet').html(), data);
        $('#main-container').append(html);
        formatDateTime($('#profile .date-field'));
        renderLastSeen($('#profile .last-seen'));
      }
    },
    dataType: 'json'
  });
}
