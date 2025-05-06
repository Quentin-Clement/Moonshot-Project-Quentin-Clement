// formdata.d.ts
declare global {
    interface FormData {
      /**
       * React Native form-data append override:
       * allows { uri, name, type } objects as the second parameter.
       */
      append(
        name: string,
        file: { uri: string; name: string; type: string }
      ): void;
    }
  }
  // THIS EXPORT TURNS THIS FILE INTO A MODULE, 
  // so the above `declare global` is properly applied.
  export {};