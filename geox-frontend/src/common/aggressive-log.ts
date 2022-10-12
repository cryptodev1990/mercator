export function aggressiveLog(reducer: any) {
  // log the input and output to the reducer
  return (state: any, action: any) => {
    window.location.hash === "#debug" && console.log("action", action);
    const result = reducer(state, action);
    window.location.hash === "#debug" && console.log("state", result);
    return result;
  };
}
