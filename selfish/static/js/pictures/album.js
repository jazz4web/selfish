$(function() {
  showAlbum(page, suffix);
  if (window.localStorage.getItem('token')) {
    $('body').on('change', '#image', {suffix: suffix}, uploadPicture);
  }
});
