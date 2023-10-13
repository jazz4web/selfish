$(function() {
  showIndex();
  if (window.localStorage.getItem('token')) {

  } else {
    if (window.location.hash === '#login') {
      login();
    }
    if (window.location.hash === '#get-password') {
      reg();
    }
    $('body').on('click', '#login-submit', loginSubmit);
    $('body').on(
      'click', '#lcaptcha-reload',
      {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
      captchaReload);
    $('body').on(
      'click', '#rcaptcha-reload',
      {field: '#rcaptcha-field', suffix: '#rsuffix', captcha: '#rcaptcha'},
      captchaReload);
  }
  $(window).bind('hashchange', function() {
    if (window.localStorage.getItem('token')) {} else {
      if (window.location.hash === '#login') {
        login();
      }
      if (window.location.hash === '#get-password') {
        reg();
      }
    }
  });
});
