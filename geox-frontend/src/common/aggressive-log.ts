export function aggressiveLog(reducer: any, reducerName: string) {
  // log the input and output to the reducer
  return (state: any, action: any) => {
    window.location.hash === "#debug" &&
      console.log("reducer", reducerName, "action", action);
    const result = reducer(state, action);
    window.location.hash === "#debug" &&
      console.log("reducer", reducerName, "state", result);
    return result;
  };
}
