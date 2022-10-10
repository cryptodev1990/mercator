export function aggressiveLog(reducer: any) {
  // log the input and output to the reducer
  return (state: any, action: any) => {
    console.log("action", action);
    const result = reducer(state, action);
    console.log("state", result);
    return result;
  };
}
