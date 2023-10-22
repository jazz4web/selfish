function parseHash(hash, endpoint) {
  let parts = hash.split('/');
  if (parts.length == 2 && parts[0] === endpoint) {
    return parts[1];
  }
  return null;
}
