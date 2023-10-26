$(function() {
  showIndex();
  if (window.localStorage.getItem('token')) {
    if (window.location.hash === '#logout') {
      logout();
    }
    if (window.location.hash === '#logout-all') {
      logoutAll();
    }
  } else {
    if (window.location.hash === '#login') {
      login();
    }
    if (window.location.hash === '#get-password') {
      reg();
    }
    $('body').on('click', '#login-submit', loginSubmit);
    $('body').on('click', '#login-reg', loginReg);
    $('body').on('click', '#reg-submit', regSubmit);
    $('body').on(
      'click', '#lcaptcha-reload',
      {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
      captchaReload);
    $('body').on(
      'click', '#rcaptcha-reload',
      {field: '#rcaptcha-field', suffix: '#rsuffix', captcha: '#rcaptcha'},
      captchaReload);
    $('body').on('click', '#rsp-submit', resetPwd);
    $('body').on('click', '#crp-submit', createUser);
  }
  $(window).bind('hashchange', function() {
    let chem = parseHash(window.location.hash, '#change-email')
    if (chem) {
      changeEmail(chem);
    }
    if (window.localStorage.getItem('token')) {
      if (window.location.hash === '#logout') {
        logout();
      }
      if (window.location.hash === '#logout-all') {
        logoutAll();
      }
    } else {
      if (window.location.hash === '#login') {
        login();
      }
      if (window.location.hash === '#get-password') {
        reg();
      }
    }
    let rst = parseHash(window.location.hash, '#reset-password');
    if (rst) {
      resetPasswd(rst);
    }
    let crt = parseHash(window.location.hash, '#request-password');
    if (crt) {
      requestPasswd(crt);
    }
  });
  let rst = parseHash(window.location.hash, '#reset-password');
  if (rst) {
    resetPasswd(rst);
  }
  let crt = parseHash(window.location.hash, '#request-password');
  if (crt) {
    requestPasswd(crt);
  }
  let chem = parseHash(window.location.hash, '#change-email')
  if (chem) {
    changeEmail(chem);
  }
});
