function showAlbums() {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/pictures',
    data: {
      page: page
    },
    headers: tee,
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
      checkMC(1152);
      $('body').on('click', '.close-top-flashed', closeTopFlashed);
      if (data.message) {
        let html = Mustache.render($('#ealertt').html(), data);
        $('#main-container').append(html);
        slidePage('#ealert');
      } else {
        let html = Mustache.render($('#albumst').html(), data);
        $('#main-container').append(html);
        let ust = Mustache.render($('#ustatt').html(), data);
        $('#right-panel').append(ust);
        formatDateTime($('.date-field'));
      }
    },
    dataType: 'json'
  });

}
