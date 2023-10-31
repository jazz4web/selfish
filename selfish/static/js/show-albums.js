function showAlbums() {
  let token = window.localStorage.getItem('token');
  let tee = token ? {'x-auth-token': token} : {};
  $.ajax({
    method: 'GET',
    url: '/api/pictures',
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
    },
    dataType: 'json'
  });

}
