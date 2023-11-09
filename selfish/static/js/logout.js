function logout() {
  let tee = {token: window.localStorage.getItem('token')};
  $.ajax({
    method: 'POST',
    url: '/api/logout',
    data: tee,
    success: function(data) {
      if (data.result) {
        window.localStorage.removeItem('token');
        window.location.assign('/');
      }
    },
    dataType: 'json'
  });
}
