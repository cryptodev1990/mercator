// choose one element at random from an arrray
function nab(arr: string[]) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export { nab };
