$(function() {
  showProfile();
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#changeava', requestAvachange);
    $('body').on('click', '#changeavaf .avatar', function() {
      window.location.reload();
    });
    $('body').on('change', '#image', changeAva);
  }
});
