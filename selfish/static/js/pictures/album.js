$(function() {
  showAlbum(page, suffix);
  if (window.localStorage.getItem('token')) {
    $('body').on('click', '#show-rename-form', showRenameForm);
    $('body').on('click', '#show-state-form', showStateForm);
    $('body').on(
      'keyup blur', '#title-change',
      {min: 3, max: 100, block: '#rename-form'},
      markInputError);
    $('body').on('click', '#rename-album', {suffix: suffix}, renameAlbum);
    $('body').on('change', '#select-status', {suffix: suffix}, changeStatus);
    $('body').on('change', '#image', {suffix: suffix}, uploadPicture);
  }
});
