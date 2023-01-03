const title = (str: string, splitChar: string) => {
  return str
    .split(splitChar)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
};

export { title };
