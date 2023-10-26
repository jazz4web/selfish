$(function() {
  showProfile();
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#changeava', requestAvachange);
    $('body').on('click', '#changeavaf .avatar', function() {
      window.location.reload();
    });
    $('body').on('change', '#image', changeAva);
    $('body').on('click', '#changepwd', changePWD);
    $('body').on('click', '#changepwd-submit', createNewpwd);
    $('body').on('click', '#emchange', requestEmF);
    $('body').on('click', '#chaddress-submit', requestEmCh);
  }
});
